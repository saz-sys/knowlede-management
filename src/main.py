"""
メインアプリケーション

動画サムネイル抽出デスクトップアプリケーションのエントリーポイント。
GUI、サービス層、非同期処理を統合して提供します。
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from pathlib import Path
from typing import List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.lib import get_logger, get_config, ThumbnailExtractionError
from src.models import VideoFile, UserSettings, Thumbnail
from src.gui import MainWindow, ThumbnailGrid, SettingsDialog, init_gui_environment
from src.gui.async_worker import create_worker, thumbnail_extraction_worker
from src.services import VideoProcessor, FaceDetector, DiversitySelector, ThumbnailExtractor


class ThumbnailExtractionApp:
    """サムネイル抽出アプリケーションメインクラス"""
    
    def __init__(self):
        """アプリケーションを初期化"""
        # ログ設定
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # GUI環境初期化
        self.root = init_gui_environment()
        self.root.title("動画サムネイル抽出")
        
        # メインウィンドウ作成
        self.main_window = MainWindow(self.root)
        
        # サムネイルグリッド作成
        self.thumbnail_grid = ThumbnailGrid(self.root)
        
        # 非同期ワーカー
        self.worker = create_worker("thumbnail_extraction")
        
        # 状態管理
        self.current_video: Optional[VideoFile] = None
        self.current_thumbnails: List[Thumbnail] = []
        
        # イベントハンドリング設定
        self._setup_event_handlers()
        
        # パフォーマンス最適化設定
        self._setup_performance_optimization()
        
        self.logger.info("アプリケーション初期化完了")
    
    def _setup_event_handlers(self):
        """イベントハンドラーを設定"""
        # メインウィンドウのコールバック
        self.main_window.on_video_selected = self._on_video_selected
        self.main_window.on_extraction_start = self._on_extraction_start
        self.main_window.on_settings_changed = self._on_settings_changed
        
        # ワーカーのコールバック
        self.worker.on_progress = self._on_progress_update
        self.worker.on_completed = self._on_extraction_completed
        self.worker.on_error = self._on_extraction_error
        self.worker.on_cancelled = self._on_extraction_cancelled
        
        # サムネイルグリッドのコールバック
        self.thumbnail_grid.on_selection_changed = self._on_thumbnail_selection_changed
        
        # ウィンドウクローズイベント
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_performance_optimization(self):
        """パフォーマンス最適化設定"""
        try:
            # メモリ使用量制限
            import resource
            max_memory = self.config.get('max_frame_buffer_size', 100) * 1024 * 1024  # MB
            resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
        except:
            pass  # リソース制限が利用できない環境では無視
        
        # ガベージコレクション調整
        import gc
        gc.set_threshold(700, 10, 10)  # より頻繁なGC
        
        # OpenCVスレッド数制限
        try:
            import cv2
            cv2.setNumThreads(2)  # CPU使用量を制限
        except ImportError:
            pass
        
        self.logger.info("パフォーマンス最適化設定完了")
    
    def _on_video_selected(self, video_file: VideoFile):
        """動画ファイル選択時の処理"""
        try:
            self.current_video = video_file
            self.current_thumbnails.clear()
            
            # プレビューエリアをクリア
            self.thumbnail_grid.clear()
            
            # 動画情報を表示
            self._show_video_info(video_file)
            
            self.logger.info(f"動画ファイル選択: {video_file.file_path}")
            
        except Exception as e:
            self.logger.error(f"動画選択処理エラー: {e}")
            self._show_error("動画ファイル処理エラー", str(e))
    
    def _on_extraction_start(self, user_settings: UserSettings):
        """サムネイル抽出開始時の処理"""
        try:
            if not self.current_video:
                raise ValueError("動画ファイルが選択されていません")
            
            # 設定検証
            self._validate_extraction_settings(user_settings)
            
            # 非同期でサムネイル抽出開始
            success = self.worker.start(
                thumbnail_extraction_worker,
                self.current_video,
                user_settings
            )
            
            if not success:
                raise ThumbnailExtractionError("ワーカーの開始に失敗しました")
            
            self.logger.info("サムネイル抽出開始")
            
        except Exception as e:
            self.logger.error(f"抽出開始エラー: {e}")
            self._show_error("抽出開始エラー", str(e))
            self.main_window._reset_ui_state()
    
    def _on_settings_changed(self, user_settings: UserSettings):
        """設定変更時の処理"""
        try:
            # 設定を永続化
            self.config.set('default_thumbnail_count', user_settings.thumbnail_count)
            self.config.set('default_output_width', user_settings.output_width)
            self.config.set('default_output_height', user_settings.output_height)
            
            self.logger.info("設定変更を保存")
            
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
    
    def _on_progress_update(self, progress_update):
        """進捗更新時の処理"""
        try:
            # メインウィンドウの進捗表示を更新
            self.main_window.update_progress(
                progress_update.progress,
                progress_update.status_message
            )
            
            # UIを更新
            self.root.update_idletasks()
            
        except Exception as e:
            self.logger.error(f"進捗更新エラー: {e}")
    
    def _on_extraction_completed(self, worker_result):
        """サムネイル抽出完了時の処理"""
        try:
            thumbnails = worker_result.result
            
            if not thumbnails:
                raise ValueError("サムネイルが生成されませんでした")
            
            # 結果を保存
            self.current_thumbnails = thumbnails
            
            # サムネイルグリッドに表示
            self.thumbnail_grid.set_thumbnails(thumbnails)
            
            # メインウィンドウに結果を設定
            self.main_window.set_thumbnails(thumbnails)
            
            # メモリ最適化
            self._optimize_memory()
            
            self.logger.info(f"サムネイル抽出完了: {len(thumbnails)}個生成")
            
        except Exception as e:
            self.logger.error(f"抽出完了処理エラー: {e}")
            self._show_error("抽出完了処理エラー", str(e))
            self.main_window._reset_ui_state()
    
    def _on_extraction_error(self, error: Exception):
        """サムネイル抽出エラー時の処理"""
        self.logger.error(f"サムネイル抽出エラー: {error}")
        
        # ユーザーフレンドリーなエラーメッセージを生成
        user_message = self._create_user_friendly_error_message(error)
        self._show_error("サムネイル抽出エラー", user_message)
        
        # UI状態をリセット
        self.main_window._reset_ui_state()
    
    def _on_extraction_cancelled(self):
        """サムネイル抽出キャンセル時の処理"""
        self.logger.info("サムネイル抽出がキャンセルされました")
        self.main_window.update_progress(0.0, "キャンセルされました")
    
    def _on_thumbnail_selection_changed(self, selected_indices):
        """サムネイル選択変更時の処理"""
        try:
            selected_count = len(selected_indices)
            self.logger.debug(f"サムネイル選択変更: {selected_count}個選択")
            
        except Exception as e:
            self.logger.error(f"選択変更処理エラー: {e}")
    
    def _validate_extraction_settings(self, user_settings: UserSettings):
        """抽出設定のバリデーション"""
        errors = []
        
        if not (1 <= user_settings.thumbnail_count <= 20):
            errors.append("サムネイル枚数は1-20の範囲で指定してください")
        
        if not (240 <= user_settings.output_width <= 4096):
            errors.append("出力幅は240-4096の範囲で指定してください")
        
        if not (240 <= user_settings.output_height <= 4096):
            errors.append("出力高さは240-4096の範囲で指定してください")
        
        if errors:
            raise ValueError("\\n".join(errors))
    
    def _show_video_info(self, video_file: VideoFile):
        """動画情報を表示"""
        try:
            # 動画の基本情報を取得（実装されている場合）
            info_text = f"""動画ファイル情報:
ファイル名: {video_file.file_path.name}
ファイルサイズ: {video_file.file_size / (1024*1024):.1f} MB"""
            
            # ステータスバーに表示
            self.main_window.status_bar_var.set(f"動画読み込み完了: {video_file.file_path.name}")
            
        except Exception as e:
            self.logger.error(f"動画情報表示エラー: {e}")
    
    def _create_user_friendly_error_message(self, error: Exception) -> str:
        """ユーザーフレンドリーなエラーメッセージを生成"""
        error_type = type(error).__name__
        error_str = str(error)
        
        # エラータイプ別のメッセージ
        if "FileNotFoundError" in error_type:
            return "ファイルが見つかりません。ファイルパスを確認してください。"
        elif "PermissionError" in error_type:
            return "ファイルへのアクセス権限がありません。ファイルが他のプログラムで使用されていないか確認してください。"
        elif "MemoryError" in error_type:
            return "メモリ不足です。他のアプリケーションを終了するか、より小さな動画ファイルを使用してください。"
        elif "codec" in error_str.lower() or "format" in error_str.lower():
            return "サポートされていない動画形式です。MP4ファイルを使用してください。"
        elif "face" in error_str.lower():
            return "顔が検出されませんでした。人物が映っている動画を使用してください。"
        elif "timeout" in error_str.lower():
            return "処理がタイムアウトしました。より短い動画を使用するか、設定でタイムアウト時間を延長してください。"
        else:
            return f"処理中にエラーが発生しました: {error_str}"
    
    def _show_error(self, title: str, message: str):
        """エラーダイアログを表示"""
        try:
            messagebox.showerror(title, message)
        except Exception as e:
            self.logger.error(f"エラーダイアログ表示エラー: {e}")
    
    def _optimize_memory(self):
        """メモリ最適化"""
        try:
            import gc
            gc.collect()  # ガベージコレクション実行
            
            # OpenCVのキャッシュクリア
            try:
                import cv2
                cv2.destroyAllWindows()
            except ImportError:
                pass
            
            self.logger.debug("メモリ最適化実行")
            
        except Exception as e:
            self.logger.error(f"メモリ最適化エラー: {e}")
    
    def _on_closing(self):
        """アプリケーション終了時の処理"""
        try:
            # 実行中のワーカーをキャンセル
            if self.worker.is_running():
                self.worker.cancel()
            
            # 設定を保存
            self.config.save()
            
            # メモリクリーンアップ
            self._optimize_memory()
            
            # ウィンドウを閉じる
            self.root.quit()
            self.root.destroy()
            
            self.logger.info("アプリケーション終了")
            
        except Exception as e:
            self.logger.error(f"終了処理エラー: {e}")
            # 強制終了
            sys.exit(1)
    
    def run(self):
        """アプリケーションを実行"""
        try:
            self.logger.info("アプリケーション開始")
            
            # ウィンドウを表示
            self.logger.info("ウィンドウ表示を開始...")
            self.main_window.show()
            self.logger.info("ウィンドウ表示コマンド完了")
            
            # メインループを開始
            self.logger.info("メインループを開始...")
            self.root.mainloop()
            self.logger.info("メインループ終了")
            
        except KeyboardInterrupt:
            self.logger.info("ユーザーによる中断")
            self._on_closing()
        except Exception as e:
            self.logger.error(f"アプリケーション実行エラー: {e}")
            self._show_error("致命的エラー", f"アプリケーションでエラーが発生しました:\\n{e}")
            sys.exit(1)


def main():
    """メイン関数"""
    try:
        # コマンドライン引数の処理
        if len(sys.argv) > 1:
            if sys.argv[1] in ['-h', '--help']:
                print("動画サムネイル抽出アプリケーション")
                print("使用方法: python -m src.main")
                print("")
                print("このアプリケーションはGUIで動作します。")
                print("コマンドライン引数は不要です。")
                sys.exit(0)
            elif sys.argv[1] in ['-v', '--version']:
                from . import __version__
                print(f"動画サムネイル抽出アプリケーション v{__version__}")
                sys.exit(0)
        
        # アプリケーション実行
        app = ThumbnailExtractionApp()
        app.run()
        
    except Exception as e:
        logging.error(f"アプリケーション起動エラー: {e}", exc_info=True)
        
        # GUI初期化前のエラーの場合はコンソールに出力
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
