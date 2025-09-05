"""
GUIインターフェースのAPI契約定義
デスクトップアプリケーションのGUIコンポーネント仕様
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from pathlib import Path
from ..models import VideoFile, Thumbnail, UserSettings, ThumbnailExtractionJob


class MainWindowContract(ABC):
    """メインウィンドウの契約インターフェース"""
    
    @abstractmethod
    def show(self) -> None:
        """
        メインウィンドウを表示
        
        Raises:
            GUIInitializationError: GUI初期化に失敗
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        メインウィンドウを閉じる
        
        Raises:
            GUICleanupError: GUI終了処理に失敗
        """
        pass
    
    @abstractmethod
    def set_video_file(self, video_file: VideoFile) -> None:
        """
        選択された動画ファイルを設定
        
        Args:
            video_file: 設定する動画ファイル
            
        Raises:
            InvalidVideoError: 動画ファイルが無効
        """
        pass
    
    @abstractmethod
    def update_progress(self, progress: float, status_message: str) -> None:
        """
        進捗バーと状態メッセージを更新
        
        Args:
            progress: 進捗率（0.0-1.0）
            status_message: 状態メッセージ
            
        Raises:
            InvalidProgressError: 進捗値が範囲外
        """
        pass
    
    @abstractmethod
    def display_thumbnails(self, thumbnails: List[Thumbnail]) -> None:
        """
        サムネイル一覧を表示
        
        Args:
            thumbnails: 表示するサムネイルリスト
            
        Raises:
            ThumbnailDisplayError: サムネイル表示に失敗
        """
        pass
    
    @abstractmethod
    def get_selected_thumbnails(self) -> List[Thumbnail]:
        """
        ユーザーが選択したサムネイルを取得
        
        Returns:
            List[Thumbnail]: 選択されたサムネイル
            
        Raises:
            SelectionError: 選択状態の取得に失敗
        """
        pass
    
    @abstractmethod
    def show_error_message(self, title: str, message: str) -> None:
        """
        エラーメッセージダイアログを表示
        
        Args:
            title: エラーダイアログのタイトル
            message: エラーメッセージ
        """
        pass
    
    @abstractmethod
    def show_success_message(self, message: str) -> None:
        """
        成功メッセージを表示
        
        Args:
            message: 成功メッセージ
        """
        pass


class FileDialogContract(ABC):
    """ファイルダイアログの契約インターフェース"""
    
    @abstractmethod
    def select_video_file(self) -> Optional[Path]:
        """
        動画ファイル選択ダイアログを表示
        
        Returns:
            Optional[Path]: 選択されたファイルパス、キャンセル時はNone
            
        Raises:
            DialogError: ダイアログ表示に失敗
        """
        pass
    
    @abstractmethod
    def select_output_directory(self) -> Optional[Path]:
        """
        出力ディレクトリ選択ダイアログを表示
        
        Returns:
            Optional[Path]: 選択されたディレクトリパス、キャンセル時はNone
            
        Raises:
            DialogError: ダイアログ表示に失敗
        """
        pass


class SettingsDialogContract(ABC):
    """設定ダイアログの契約インターフェース"""
    
    @abstractmethod
    def show_modal(self, current_settings: UserSettings) -> Optional[UserSettings]:
        """
        設定ダイアログをモーダル表示
        
        Args:
            current_settings: 現在の設定値
            
        Returns:
            Optional[UserSettings]: 更新された設定、キャンセル時はNone
            
        Raises:
            SettingsDialogError: ダイアログ表示に失敗
        """
        pass
    
    @abstractmethod
    def validate_settings(self, settings: UserSettings) -> bool:
        """
        設定値の妥当性を検証
        
        Args:
            settings: 検証対象設定
            
        Returns:
            bool: 有効な場合True
            
        Raises:
            ValidationError: 検証処理に失敗
        """
        pass


class ThumbnailGridContract(ABC):
    """サムネイル表示グリッドの契約インターフェース"""
    
    @abstractmethod
    def display_thumbnails(self, thumbnails: List[Thumbnail]) -> None:
        """
        サムネイルをグリッド表示
        
        Args:
            thumbnails: 表示するサムネイル
            
        Raises:
            GridDisplayError: グリッド表示に失敗
        """
        pass
    
    @abstractmethod
    def set_selection_callback(self, callback: Callable[[List[Thumbnail]], None]) -> None:
        """
        選択変更時のコールバックを設定
        
        Args:
            callback: 選択変更時に呼び出される関数
        """
        pass
    
    @abstractmethod
    def get_selected_items(self) -> List[Thumbnail]:
        """
        選択されたアイテムを取得
        
        Returns:
            List[Thumbnail]: 選択されたサムネイル
        """
        pass
    
    @abstractmethod
    def clear_selection(self) -> None:
        """
        選択状態をクリア
        """
        pass
    
    @abstractmethod
    def select_all(self) -> None:
        """
        すべてのアイテムを選択
        """
        pass


class ProgressBarContract(ABC):
    """プログレスバーの契約インターフェース"""
    
    @abstractmethod
    def set_progress(self, value: float) -> None:
        """
        進捗値を設定
        
        Args:
            value: 進捗値（0.0-1.0）
            
        Raises:
            InvalidProgressError: 進捗値が範囲外
        """
        pass
    
    @abstractmethod
    def set_status_text(self, text: str) -> None:
        """
        状態テキストを設定
        
        Args:
            text: 状態テキスト
        """
        pass
    
    @abstractmethod
    def show_indeterminate(self) -> None:
        """
        不定進捗表示に切り替え
        """
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """
        プログレスバーを非表示
        """
        pass


# カスタム例外クラス
class GUIError(Exception):
    """GUI関連の基底例外"""
    pass


class GUIInitializationError(GUIError):
    """GUI初期化エラー"""
    pass


class GUICleanupError(GUIError):
    """GUI終了処理エラー"""
    pass


class InvalidVideoError(GUIError):
    """無効な動画エラー"""
    pass


class InvalidProgressError(GUIError):
    """無効な進捗エラー"""
    pass


class ThumbnailDisplayError(GUIError):
    """サムネイル表示エラー"""
    pass


class SelectionError(GUIError):
    """選択状態エラー"""
    pass


class DialogError(GUIError):
    """ダイアログエラー"""
    pass


class SettingsDialogError(GUIError):
    """設定ダイアログエラー"""
    pass


class ValidationError(GUIError):
    """検証エラー"""
    pass


class GridDisplayError(GUIError):
    """グリッド表示エラー"""
    pass
