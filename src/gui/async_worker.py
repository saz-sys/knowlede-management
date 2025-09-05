"""
AsyncWorker（非同期ワーカー）実装

重い処理を非同期で実行し、UIの応答性を維持します。
threading、進捗コールバック、エラーハンドリングを提供します。
"""

import threading
import queue
import time
from typing import Callable, Optional, Any, Dict
import logging
from dataclasses import dataclass
from enum import Enum

from ..lib import get_logger


class WorkerStatus(Enum):
    """ワーカーステータス"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProgressUpdate:
    """進捗更新データ"""
    progress: float  # 0.0-100.0
    status_message: str
    details: Optional[Dict[str, Any]] = None
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None


@dataclass
class WorkerResult:
    """ワーカー実行結果"""
    status: WorkerStatus
    result: Optional[Any] = None
    error: Optional[Exception] = None
    elapsed_time: float = 0.0
    progress_history: list = None


class AsyncWorker:
    """非同期ワーカークラス"""
    
    def __init__(self, name: str = "AsyncWorker"):
        """
        非同期ワーカーを初期化
        
        Args:
            name: ワーカー名（ログ用）
        """
        self.name = name
        self.logger = get_logger(__name__)
        
        # 状態管理
        self.status = WorkerStatus.IDLE
        self.thread: Optional[threading.Thread] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # 制御フラグ
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        
        # 結果とエラー
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        
        # 進捗管理
        self.progress_queue = queue.Queue()
        self.progress_history: list[ProgressUpdate] = []
        
        # コールバック関数
        self.on_progress: Optional[Callable[[ProgressUpdate], None]] = None
        self.on_completed: Optional[Callable[[WorkerResult], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_cancelled: Optional[Callable, None] = None
        
        self.logger.info(f"非同期ワーカー '{name}' 初期化完了")
    
    def start(self, target_function: Callable, *args, **kwargs) -> bool:
        """
        非同期実行を開始
        
        Args:
            target_function: 実行する関数
            *args, **kwargs: 関数の引数
            
        Returns:
            bool: 開始成功フラグ
        """
        if self.status == WorkerStatus.RUNNING:
            self.logger.warning("ワーカーは既に実行中です")
            return False
        
        try:
            # 状態をリセット
            self._reset_state()
            
            # 新しいスレッドで実行
            self.thread = threading.Thread(
                target=self._worker_wrapper,
                args=(target_function, args, kwargs),
                name=f"{self.name}-Thread",
                daemon=True
            )
            
            self.status = WorkerStatus.RUNNING
            self.start_time = time.time()
            
            self.thread.start()
            
            # 進捗監視を開始
            self._start_progress_monitor()
            
            self.logger.info(f"ワーカー '{self.name}' 開始")
            return True
            
        except Exception as e:
            self.logger.error(f"ワーカー開始エラー: {e}")
            self.status = WorkerStatus.ERROR
            self.error = e
            return False
    
    def cancel(self) -> bool:
        """
        実行をキャンセル
        
        Returns:
            bool: キャンセル成功フラグ
        """
        if self.status != WorkerStatus.RUNNING:
            return False
        
        self.logger.info(f"ワーカー '{self.name}' キャンセル要求")
        self._cancel_event.set()
        
        # スレッドの終了を待機（最大5秒）
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
            
            if self.thread.is_alive():
                self.logger.warning("ワーカースレッドが正常に終了しませんでした")
                return False
        
        self.status = WorkerStatus.CANCELLED
        self.end_time = time.time()
        
        if self.on_cancelled:
            try:
                self.on_cancelled()
            except Exception as e:
                self.logger.error(f"キャンセルコールバックエラー: {e}")
        
        return True
    
    def pause(self) -> bool:
        """
        実行を一時停止
        
        Returns:
            bool: 一時停止成功フラグ
        """
        if self.status != WorkerStatus.RUNNING:
            return False
        
        self.status = WorkerStatus.PAUSED
        self._pause_event.set()
        self.logger.info(f"ワーカー '{self.name}' 一時停止")
        return True
    
    def resume(self) -> bool:
        """
        実行を再開
        
        Returns:
            bool: 再開成功フラグ
        """
        if self.status != WorkerStatus.PAUSED:
            return False
        
        self.status = WorkerStatus.RUNNING
        self._pause_event.clear()
        self.logger.info(f"ワーカー '{self.name}' 再開")
        return True
    
    def is_running(self) -> bool:
        """実行中かどうかを確認"""
        return self.status == WorkerStatus.RUNNING
    
    def is_finished(self) -> bool:
        """完了しているかどうかを確認"""
        return self.status in [WorkerStatus.COMPLETED, WorkerStatus.CANCELLED, WorkerStatus.ERROR]
    
    def get_elapsed_time(self) -> float:
        """経過時間を取得"""
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def get_result(self) -> WorkerResult:
        """実行結果を取得"""
        return WorkerResult(
            status=self.status,
            result=self.result,
            error=self.error,
            elapsed_time=self.get_elapsed_time(),
            progress_history=self.progress_history.copy()
        )
    
    def report_progress(self, progress: float, status_message: str, 
                       details: Optional[Dict[str, Any]] = None,
                       estimated_remaining: Optional[float] = None):
        """
        進捗を報告（ワーカー内で呼び出す）
        
        Args:
            progress: 進捗率（0.0-100.0）
            status_message: ステータスメッセージ
            details: 詳細情報
            estimated_remaining: 推定残り時間（秒）
        """
        if self.status != WorkerStatus.RUNNING:
            return
        
        # 進捗データ作成
        progress_update = ProgressUpdate(
            progress=max(0.0, min(100.0, progress)),
            status_message=status_message,
            details=details,
            elapsed_time=self.get_elapsed_time(),
            estimated_remaining=estimated_remaining
        )
        
        # キューに追加
        try:
            self.progress_queue.put_nowait(progress_update)
        except queue.Full:
            # キューが満杯の場合は古いデータを破棄
            try:
                self.progress_queue.get_nowait()
                self.progress_queue.put_nowait(progress_update)
            except queue.Empty:
                pass
    
    def check_cancellation(self) -> bool:
        """
        キャンセル要求をチェック（ワーカー内で定期的に呼び出す）
        
        Returns:
            bool: キャンセルされた場合True
        """
        return self._cancel_event.is_set()
    
    def wait_if_paused(self):
        """一時停止中の場合は待機（ワーカー内で呼び出す）"""
        if self._pause_event.is_set():
            self.logger.info("ワーカー一時停止中...")
            while self._pause_event.is_set() and not self._cancel_event.is_set():
                time.sleep(0.1)
    
    def _reset_state(self):
        """状態をリセット"""
        self.status = WorkerStatus.IDLE
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.progress_history.clear()
        
        # イベントをクリア
        self._cancel_event.clear()
        self._pause_event.clear()
        
        # キューをクリア
        while not self.progress_queue.empty():
            try:
                self.progress_queue.get_nowait()
            except queue.Empty:
                break
    
    def _worker_wrapper(self, target_function: Callable, args: tuple, kwargs: dict):
        """ワーカー関数のラッパー"""
        try:
            self.logger.info(f"ワーカー実行開始: {target_function.__name__}")
            
            # 対象関数を実行
            # ワーカーオブジェクト自体を引数として渡す
            if 'worker' not in kwargs:
                kwargs['worker'] = self
            
            result = target_function(*args, **kwargs)
            
            # 正常終了
            if not self._cancel_event.is_set():
                self.result = result
                self.status = WorkerStatus.COMPLETED
                self.end_time = time.time()
                
                self.logger.info(f"ワーカー実行完了: {self.get_elapsed_time():.2f}秒")
                
                if self.on_completed:
                    try:
                        self.on_completed(self.get_result())
                    except Exception as e:
                        self.logger.error(f"完了コールバックエラー: {e}")
            
        except Exception as e:
            # エラー終了
            self.error = e
            self.status = WorkerStatus.ERROR
            self.end_time = time.time()
            
            self.logger.error(f"ワーカー実行エラー: {e}", exc_info=True)
            
            if self.on_error:
                try:
                    self.on_error(e)
                except Exception as callback_error:
                    self.logger.error(f"エラーコールバックエラー: {callback_error}")
    
    def _start_progress_monitor(self):
        """進捗監視を開始"""
        def monitor():
            while self.status == WorkerStatus.RUNNING:
                try:
                    # 進捗更新をチェック
                    progress_update = self.progress_queue.get(timeout=0.1)
                    
                    # 履歴に追加
                    self.progress_history.append(progress_update)
                    
                    # コールバック実行
                    if self.on_progress:
                        try:
                            self.on_progress(progress_update)
                        except Exception as e:
                            self.logger.error(f"進捗コールバックエラー: {e}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"進捗監視エラー: {e}")
                    break
        
        monitor_thread = threading.Thread(
            target=monitor,
            name=f"{self.name}-ProgressMonitor",
            daemon=True
        )
        monitor_thread.start()


class WorkerPool:
    """複数ワーカーの管理クラス"""
    
    def __init__(self, max_workers: int = 4):
        """
        ワーカープールを初期化
        
        Args:
            max_workers: 最大ワーカー数
        """
        self.max_workers = max_workers
        self.workers: Dict[str, AsyncWorker] = {}
        self.logger = get_logger(__name__)
        
        self.logger.info(f"ワーカープール初期化: 最大{max_workers}ワーカー")
    
    def create_worker(self, name: str) -> AsyncWorker:
        """新しいワーカーを作成"""
        if name in self.workers:
            raise ValueError(f"ワーカー '{name}' は既に存在します")
        
        worker = AsyncWorker(name)
        self.workers[name] = worker
        
        self.logger.info(f"ワーカー '{name}' を作成")
        return worker
    
    def get_worker(self, name: str) -> Optional[AsyncWorker]:
        """ワーカーを取得"""
        return self.workers.get(name)
    
    def remove_worker(self, name: str) -> bool:
        """ワーカーを削除"""
        if name not in self.workers:
            return False
        
        worker = self.workers[name]
        if worker.is_running():
            worker.cancel()
        
        del self.workers[name]
        self.logger.info(f"ワーカー '{name}' を削除")
        return True
    
    def cancel_all(self):
        """すべてのワーカーをキャンセル"""
        for worker in self.workers.values():
            if worker.is_running():
                worker.cancel()
        
        self.logger.info("すべてのワーカーをキャンセル")
    
    def get_active_count(self) -> int:
        """アクティブなワーカー数を取得"""
        return sum(1 for worker in self.workers.values() if worker.is_running())
    
    def get_status_summary(self) -> Dict[str, int]:
        """ステータス別のワーカー数を取得"""
        summary = {}
        for worker in self.workers.values():
            status = worker.status.value
            summary[status] = summary.get(status, 0) + 1
        return summary


# グローバルワーカープールインスタンス
_global_worker_pool: Optional[WorkerPool] = None


def get_worker_pool() -> WorkerPool:
    """グローバルワーカープールを取得"""
    global _global_worker_pool
    if _global_worker_pool is None:
        _global_worker_pool = WorkerPool()
    return _global_worker_pool


def create_worker(name: str) -> AsyncWorker:
    """新しいワーカーを作成（便利関数）"""
    return get_worker_pool().create_worker(name)


def get_worker(name: str) -> Optional[AsyncWorker]:
    """ワーカーを取得（便利関数）"""
    return get_worker_pool().get_worker(name)


# サムネイル抽出専用ワーカー関数
def thumbnail_extraction_worker(video_file, user_settings, worker: AsyncWorker):
    """
    サムネイル抽出ワーカー関数
    
    Args:
        video_file: VideoFileオブジェクト
        user_settings: UserSettingsオブジェクト
        worker: AsyncWorkerオブジェクト
        
    Returns:
        List[Thumbnail]: 生成されたサムネイルリスト
    """
    try:
        from ..services import VideoProcessor, FaceDetector, DiversitySelector, ThumbnailExtractor
        from ..models import ThumbnailExtractionJob
        from ..lib.errors import NoFacesDetectedError
        
        # 処理開始
        worker.report_progress(0.0, "動画ファイルを読み込んでいます...")
        
        # VideoProcessorで動画を処理
        video_processor = VideoProcessor()
        # ユーザー設定のフレーム間隔を反映しつつ、進捗計算のためにリスト化
        frames = list(video_processor.extract_frames(
            video_file,
            interval_seconds=getattr(user_settings, 'frame_interval', 1.0)
        ))
        
        if worker.check_cancellation():
            return []
        
        worker.report_progress(25.0, f"{len(frames)}個のフレームを抽出しました")
        
        # FaceDetectorで顔検出
        worker.report_progress(30.0, "顔検出を実行しています...")
        face_detector = FaceDetector()
        
        frames_with_faces = []
        total_frames = len(frames) if len(frames) > 0 else 1
        for i, frame in enumerate(frames):
            worker.wait_if_paused()
            if worker.check_cancellation():
                return []
            
            # 顔検出（APIは単一Frameを取る）
            faces = face_detector.detect_faces(frame)
            if faces:  # 顔が検出された場合
                # モデルは複数の顔を返す可能性があるためフレームに保持
                frame.faces_detected = faces
                frames_with_faces.append(frame)
            
            # 進捗更新
            progress = 30.0 + (i / total_frames) * 30.0
            worker.report_progress(progress, f"顔検出中... ({i+1}/{len(frames)})")
        
        if not frames_with_faces:
            raise NoFacesDetectedError("顔が検出されたフレームがありません")
        
        worker.report_progress(60.0, f"{len(frames_with_faces)}個のフレームで顔を検出")
        
        # DiversitySelectorで多様性選択
        worker.report_progress(65.0, "多様性スコアを計算しています...")
        diversity_selector = DiversitySelector()
        
        selected_frames = diversity_selector.select_diverse_frames(
            frames_with_faces, user_settings.thumbnail_count
        )
        
        if worker.check_cancellation():
            return []
        
        worker.report_progress(80.0, f"{len(selected_frames)}個の候補フレームを選択")
        
        # ThumbnailExtractorでサムネイル生成
        worker.report_progress(85.0, "サムネイルを生成しています...")
        thumbnail_extractor = ThumbnailExtractor()
        
        thumbnails = []
        total_selected = len(selected_frames) if len(selected_frames) > 0 else 1
        for i, frame in enumerate(selected_frames):
            worker.wait_if_paused()
            if worker.check_cancellation():
                return []
            
            # サムネイル生成（正しいAPI名と引数）
            thumbnail = thumbnail_extractor.generate_thumbnail(
                frame, user_settings
            )
            thumbnails.append(thumbnail)
            
            # 進捗更新
            progress = 85.0 + (i / total_selected) * 15.0
            worker.report_progress(progress, f"サムネイル生成中... ({i+1}/{len(selected_frames)})")
        
        worker.report_progress(100.0, f"{len(thumbnails)}個のサムネイル生成完了")
        
        return thumbnails
        
    except Exception as e:
        worker.logger.error(f"サムネイル抽出エラー: {e}")
        raise
