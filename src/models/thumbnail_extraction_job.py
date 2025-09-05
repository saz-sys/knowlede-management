"""
ThumbnailExtractionJob（サムネイル抽出ジョブ）データモデル

サムネイル抽出ジョブの状態と進捗を管理するクラスです。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING
from enum import Enum
import uuid

if TYPE_CHECKING:
    from .frame import Frame
    from .user_settings import UserSettings
    from .thumbnail import Thumbnail
    from .video_file import VideoFile


class JobStatus(Enum):
    """ジョブの状態"""
    CREATED = "created"           # 作成済み
    QUEUED = "queued"            # キュー待ち
    RUNNING = "running"          # 実行中
    PAUSED = "paused"            # 一時停止
    COMPLETED = "completed"       # 完了
    FAILED = "failed"            # 失敗
    CANCELLED = "cancelled"       # キャンセル


class JobPhase(Enum):
    """ジョブの実行フェーズ"""
    INITIALIZING = "initializing"           # 初期化
    EXTRACTING_FRAMES = "extracting_frames" # フレーム抽出
    DETECTING_FACES = "detecting_faces"     # 顔検出
    SELECTING_FRAMES = "selecting_frames"   # フレーム選択
    GENERATING_THUMBNAILS = "generating_thumbnails"  # サムネイル生成
    SAVING_FILES = "saving_files"           # ファイル保存
    FINALIZING = "finalizing"               # 最終処理


@dataclass
class JobProgress:
    """ジョブ進捗情報"""
    phase: JobPhase                    # 現在のフェーズ
    current_step: int = 0              # 現在のステップ
    total_steps: int = 0               # 総ステップ数
    progress_percentage: float = 0.0   # 進捗率（0-100）
    message: str = ""                  # 進捗メッセージ
    estimated_remaining_time: Optional[timedelta] = None  # 推定残り時間


@dataclass
class ThumbnailExtractionJob:
    """サムネイル抽出ジョブを表すクラス"""
    
    # 基本情報
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # ジョブID
    video_file: Optional['VideoFile'] = None            # 処理対象動画ファイル
    user_settings: Optional['UserSettings'] = None      # ユーザー設定
    
    # ジョブ状態
    status: JobStatus = JobStatus.CREATED               # ジョブ状態
    progress: JobProgress = field(default_factory=lambda: JobProgress(JobPhase.INITIALIZING))  # 進捗情報
    
    # 処理データ
    extracted_frames: List['Frame'] = field(default_factory=list)      # 抽出されたフレーム
    filtered_frames: List['Frame'] = field(default_factory=list)       # フィルタリング済みフレーム
    selected_frames: List['Frame'] = field(default_factory=list)       # 選択されたフレーム
    generated_thumbnails: List['Thumbnail'] = field(default_factory=list)  # 生成されたサムネイル
    
    # 時刻情報
    created_at: datetime = field(default_factory=datetime.now)         # ジョブ作成時刻
    started_at: Optional[datetime] = None                             # 開始時刻
    completed_at: Optional[datetime] = None                           # 完了時刻
    
    # エラー情報
    error_message: Optional[str] = None                               # エラーメッセージ
    error_details: Optional[Dict[str, Any]] = None                   # エラー詳細
    
    # 統計情報
    statistics: Dict[str, Any] = field(default_factory=dict)         # 処理統計
    
    # コールバック
    progress_callback: Optional[Callable[[JobProgress], None]] = None  # 進捗通知コールバック
    completion_callback: Optional[Callable[['ThumbnailExtractionJob'], None]] = None  # 完了通知コールバック
    
    # メタデータ
    metadata: Dict[str, Any] = field(default_factory=dict)           # 追加メタデータ
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        # job_idの検証
        if not isinstance(self.job_id, str) or not self.job_id.strip():
            raise ValueError("job_idは空でない文字列である必要があります")
        
        # 状態の型チェック
        if not isinstance(self.status, JobStatus):
            raise TypeError("statusはJobStatusである必要があります")
        
        if not isinstance(self.progress, JobProgress):
            raise TypeError("progressはJobProgressである必要があります")
        
        # リストの型チェック
        for attr_name, attr_value in [
            ("extracted_frames", self.extracted_frames),
            ("filtered_frames", self.filtered_frames),
            ("selected_frames", self.selected_frames),
            ("generated_thumbnails", self.generated_thumbnails)
        ]:
            if not isinstance(attr_value, list):
                raise TypeError(f"{attr_name}はリストである必要があります")
    
    @property
    def duration(self) -> Optional[timedelta]:
        """ジョブの実行時間"""
        if self.started_at is None:
            return None
        
        end_time = self.completed_at or datetime.now()
        return end_time - self.started_at
    
    @property
    def is_running(self) -> bool:
        """実行中かどうか"""
        return self.status == JobStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """完了済みかどうか"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    @property
    def is_successful(self) -> bool:
        """成功したかどうか"""
        return self.status == JobStatus.COMPLETED
    
    @property
    def has_error(self) -> bool:
        """エラーがあるかどうか"""
        return self.error_message is not None
    
    @property
    def frame_count(self) -> int:
        """抽出されたフレーム数"""
        return len(self.extracted_frames)
    
    @property
    def filtered_frame_count(self) -> int:
        """フィルタリング済みフレーム数"""
        return len(self.filtered_frames)
    
    @property
    def thumbnail_count(self) -> int:
        """生成されたサムネイル数"""
        return len(self.generated_thumbnails)
    
    @property
    def success_rate(self) -> float:
        """成功率（生成されたサムネイル数 / 目標枚数）"""
        if not self.user_settings:
            return 0.0
        
        target_count = self.user_settings.thumbnail_count
        if target_count == 0:
            return 1.0
        
        return min(1.0, self.thumbnail_count / target_count)
    
    @property
    def processing_speed(self) -> Optional[float]:
        """処理速度（フレーム/秒）"""
        duration = self.duration
        if duration is None or duration.total_seconds() == 0:
            return None
        
        return self.frame_count / duration.total_seconds()
    
    def start(self):
        """ジョブを開始"""
        if self.status != JobStatus.CREATED:
            raise ValueError(f"ジョブを開始できません。現在の状態: {self.status.value}")
        
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
        self.progress.phase = JobPhase.INITIALIZING
        self.progress.message = "ジョブを開始しています..."
        
        self._notify_progress()
    
    def pause(self):
        """ジョブを一時停止"""
        if self.status != JobStatus.RUNNING:
            raise ValueError(f"ジョブを一時停止できません。現在の状態: {self.status.value}")
        
        self.status = JobStatus.PAUSED
        self.progress.message = "ジョブが一時停止されました"
        
        self._notify_progress()
    
    def resume(self):
        """ジョブを再開"""
        if self.status != JobStatus.PAUSED:
            raise ValueError(f"ジョブを再開できません。現在の状態: {self.status.value}")
        
        self.status = JobStatus.RUNNING
        self.progress.message = "ジョブを再開しています..."
        
        self._notify_progress()
    
    def complete(self):
        """ジョブを完了"""
        if self.status not in [JobStatus.RUNNING, JobStatus.PAUSED]:
            raise ValueError(f"ジョブを完了できません。現在の状態: {self.status.value}")
        
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress.phase = JobPhase.FINALIZING
        self.progress.current_step = self.progress.total_steps
        self.progress.progress_percentage = 100.0
        self.progress.message = "ジョブが正常に完了しました"
        
        # 統計情報の更新
        self._update_statistics()
        
        self._notify_progress()
        self._notify_completion()
    
    def fail(self, error_message: str, error_details: Optional[Dict[str, Any]] = None):
        """ジョブを失敗状態にする"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        self.error_details = error_details or {}
        
        self.progress.message = f"ジョブが失敗しました: {error_message}"
        
        # 統計情報の更新
        self._update_statistics()
        
        self._notify_progress()
        self._notify_completion()
    
    def cancel(self):
        """ジョブをキャンセル"""
        if self.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            raise ValueError(f"ジョブをキャンセルできません。現在の状態: {self.status.value}")
        
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
        self.progress.message = "ジョブがキャンセルされました"
        
        # 統計情報の更新
        self._update_statistics()
        
        self._notify_progress()
        self._notify_completion()
    
    def update_progress(
        self,
        phase: Optional[JobPhase] = None,
        current_step: Optional[int] = None,
        total_steps: Optional[int] = None,
        message: Optional[str] = None,
        estimated_remaining_time: Optional[timedelta] = None
    ):
        """進捗情報を更新"""
        if phase is not None:
            self.progress.phase = phase
        
        if current_step is not None:
            self.progress.current_step = current_step
        
        if total_steps is not None:
            self.progress.total_steps = total_steps
        
        if message is not None:
            self.progress.message = message
        
        if estimated_remaining_time is not None:
            self.progress.estimated_remaining_time = estimated_remaining_time
        
        # 進捗率の計算
        if self.progress.total_steps > 0:
            self.progress.progress_percentage = (
                self.progress.current_step / self.progress.total_steps * 100.0
            )
        
        self._notify_progress()
    
    def add_extracted_frame(self, frame: 'Frame'):
        """抽出されたフレームを追加"""
        from .frame import Frame
        if not isinstance(frame, Frame):
            raise TypeError("frameはFrameインスタンスである必要があります")
        
        self.extracted_frames.append(frame)
    
    def add_filtered_frame(self, frame: 'Frame'):
        """フィルタリング済みフレームを追加"""
        from .frame import Frame
        if not isinstance(frame, Frame):
            raise TypeError("frameはFrameインスタンスである必要があります")
        
        self.filtered_frames.append(frame)
    
    def add_selected_frame(self, frame: 'Frame'):
        """選択されたフレームを追加"""
        from .frame import Frame
        if not isinstance(frame, Frame):
            raise TypeError("frameはFrameインスタンスである必要があります")
        
        self.selected_frames.append(frame)
    
    def add_generated_thumbnail(self, thumbnail: 'Thumbnail'):
        """生成されたサムネイルを追加"""
        from .thumbnail import Thumbnail
        if not isinstance(thumbnail, Thumbnail):
            raise TypeError("thumbnailはThumbnailインスタンスである必要があります")
        
        self.generated_thumbnails.append(thumbnail)
    
    def get_best_thumbnails(self, count: Optional[int] = None) -> List['Thumbnail']:
        """最高品質のサムネイルを取得"""
        if count is None:
            count = self.user_settings.thumbnail_count if self.user_settings else len(self.generated_thumbnails)
        
        # 総合スコア順にソート
        sorted_thumbnails = sorted(self.generated_thumbnails, key=lambda t: t.total_score, reverse=True)
        return sorted_thumbnails[:count]
    
    def get_most_diverse_thumbnails(self, count: Optional[int] = None) -> List['Thumbnail']:
        """最も多様性の高いサムネイルを取得"""
        if count is None:
            count = self.user_settings.thumbnail_count if self.user_settings else len(self.generated_thumbnails)
        
        # 多様性スコア順にソート
        sorted_thumbnails = sorted(self.generated_thumbnails, key=lambda t: t.diversity_score, reverse=True)
        return sorted_thumbnails[:count]
    
    def _update_statistics(self):
        """統計情報を更新"""
        duration = self.duration
        
        self.statistics.update({
            'total_extracted_frames': self.frame_count,
            'total_filtered_frames': self.filtered_frame_count,
            'total_selected_frames': len(self.selected_frames),
            'total_generated_thumbnails': self.thumbnail_count,
            'success_rate': self.success_rate,
            'processing_duration_seconds': duration.total_seconds() if duration else 0,
            'processing_speed_fps': self.processing_speed,
            'average_thumbnail_score': (
                sum(t.total_score for t in self.generated_thumbnails) / self.thumbnail_count
                if self.thumbnail_count > 0 else 0.0
            ),
            'average_diversity_score': (
                sum(t.diversity_score for t in self.generated_thumbnails) / self.thumbnail_count
                if self.thumbnail_count > 0 else 0.0
            )
        })
        
        # 動画ファイル情報
        if self.video_file:
            self.statistics.update({
                'video_duration': self.video_file.duration,
                'video_fps': self.video_file.fps,
                'video_resolution': f"{self.video_file.width}x{self.video_file.height}",
                'frames_per_second_processed': (
                    self.frame_count / self.video_file.duration if self.video_file.duration > 0 else 0
                )
            })
    
    def _notify_progress(self):
        """進捗コールバックを実行"""
        if self.progress_callback:
            try:
                self.progress_callback(self.progress)
            except Exception as e:
                print(f"進捗コールバックエラー: {e}")
    
    def _notify_completion(self):
        """完了コールバックを実行"""
        if self.completion_callback:
            try:
                self.completion_callback(self)
            except Exception as e:
                print(f"完了コールバックエラー: {e}")
    
    def add_metadata(self, key: str, value: Any):
        """メタデータを追加"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """メタデータを取得"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを出力"""
        return {
            # 基本情報
            'job_id': self.job_id,
            'video_file_path': str(self.video_file.file_path) if self.video_file else None,
            'status': self.status.value,
            
            # 進捗情報
            'progress': {
                'phase': self.progress.phase.value,
                'current_step': self.progress.current_step,
                'total_steps': self.progress.total_steps,
                'progress_percentage': self.progress.progress_percentage,
                'message': self.progress.message,
                'estimated_remaining_time': (
                    self.progress.estimated_remaining_time.total_seconds()
                    if self.progress.estimated_remaining_time else None
                )
            },
            
            # 処理結果
            'frame_count': self.frame_count,
            'filtered_frame_count': self.filtered_frame_count,
            'thumbnail_count': self.thumbnail_count,
            'success_rate': self.success_rate,
            
            # 時刻情報
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            
            # エラー情報
            'error_message': self.error_message,
            'error_details': self.error_details,
            
            # 統計情報
            'statistics': self.statistics.copy(),
            
            # メタデータ
            'metadata': self.metadata.copy(),
            
            # 生成されたサムネイル
            'thumbnails': [thumbnail.to_dict() for thumbnail in self.generated_thumbnails]
        }
    
    @classmethod
    def create(
        cls,
        video_file: 'VideoFile',
        user_settings: 'UserSettings',
        progress_callback: Optional[Callable[[JobProgress], None]] = None,
        completion_callback: Optional[Callable[['ThumbnailExtractionJob'], None]] = None
    ) -> 'ThumbnailExtractionJob':
        """新しいジョブを作成"""
        from .video_file import VideoFile
        from .user_settings import UserSettings
        
        if not isinstance(video_file, VideoFile):
            raise TypeError("video_fileはVideoFileインスタンスである必要があります")
        if not isinstance(user_settings, UserSettings):
            raise TypeError("user_settingsはUserSettingsインスタンスである必要があります")
        
        return cls(
            video_file=video_file,
            user_settings=user_settings,
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"Job({self.job_id[:8]}, {self.status.value}, {self.progress.progress_percentage:.1f}%)"
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"ThumbnailExtractionJob(job_id={self.job_id}, status={self.status.value}, "
                f"progress={self.progress.progress_percentage:.1f}%, thumbnails={self.thumbnail_count})")
    
    def __eq__(self, other) -> bool:
        """等価比較（ジョブIDで判定）"""
        if not isinstance(other, ThumbnailExtractionJob):
            return False
        return self.job_id == other.job_id
    
    def __hash__(self) -> int:
        """ハッシュ値（ジョブIDベース）"""
        return hash(self.job_id)
