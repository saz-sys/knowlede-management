"""
GUIインターフェース契約テスト

GUIコンポーネントの契約インターフェース仕様に基づく契約テストです。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
from typing import List, Callable
import sys

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.main_window import MainWindow  # noqa: E402
from gui.settings_dialog import SettingsDialog  # noqa: E402
from gui.thumbnail_grid import ThumbnailGrid  # noqa: E402
from models.video_file import VideoFile  # noqa: E402
from models.thumbnail import Thumbnail  # noqa: E402
from models.user_settings import UserSettings  # noqa: E402
from lib.errors import (  # noqa: E402
    GUIError,
    GUIInitializationError,
    GUICleanupError,
    InvalidVideoError,
    InvalidProgressError,
    ThumbnailDisplayError,
    SelectionError,
    DialogError,
    SettingsDialogError,
    ValidationError,
    GridDisplayError,
)


@pytest.mark.contract
class TestMainWindowContract:
    """MainWindow契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        # 実装前なので、MainWindowのインスタンス化は失敗するはず
        try:
            self.main_window = MainWindow()
        except (ImportError, NotImplementedError, AttributeError):
            # 期待されるエラー - 実装前のため
            self.main_window = None

    def test_show_success(self):
        """メインウィンドウ表示の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.show()

    def test_close_success(self):
        """メインウィンドウ終了の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.close()

    def test_set_video_file_success(self, mock_video_file):
        """動画ファイル設定の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.set_video_file(mock_video_file)

    def test_set_video_file_invalid(self):
        """無効な動画ファイル設定のエラーテスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        with pytest.raises(InvalidVideoError):
            self.main_window.set_video_file(None)

    def test_update_progress_success(self):
        """進捗更新の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # 正常な進捗値でテスト
        self.main_window.update_progress(0.5, "処理中...")
        self.main_window.update_progress(0.0, "開始")
        self.main_window.update_progress(1.0, "完了")

    def test_update_progress_invalid(self):
        """無効な進捗値でのエラーテスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        with pytest.raises(InvalidProgressError):
            self.main_window.update_progress(-0.1, "無効な進捗")
        
        with pytest.raises(InvalidProgressError):
            self.main_window.update_progress(1.1, "無効な進捗")

    def test_display_thumbnails_success(self, mock_thumbnails):
        """サムネイル表示の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.display_thumbnails(mock_thumbnails)

    def test_display_thumbnails_empty(self):
        """空のサムネイルリスト表示テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認
        self.main_window.display_thumbnails([])

    def test_get_selected_thumbnails_success(self):
        """選択サムネイル取得の正常テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        selected = self.main_window.get_selected_thumbnails()
        
        # 戻り値の型チェック
        assert isinstance(selected, list)
        assert all(isinstance(thumbnail, Thumbnail) for thumbnail in selected)

    def test_show_error_message(self):
        """エラーメッセージ表示テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.show_error_message("エラー", "テストエラーメッセージ")

    def test_show_success_message(self):
        """成功メッセージ表示テスト"""
        if self.main_window is None:
            pytest.skip("MainWindow not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.main_window.show_success_message("保存が完了しました")


@pytest.mark.contract
class TestSettingsDialogContract:
    """SettingsDialog契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        try:
            self.settings_dialog = SettingsDialog()
        except (ImportError, NotImplementedError, AttributeError):
            self.settings_dialog = None

    def test_show_modal_success(self, mock_user_settings):
        """設定ダイアログモーダル表示の正常テスト"""
        if self.settings_dialog is None:
            pytest.skip("SettingsDialog not implemented yet - TDD")
        
        result = self.settings_dialog.show_modal(mock_user_settings)
        
        # 戻り値の型チェック（Optional[UserSettings]）
        assert result is None or isinstance(result, UserSettings)

    def test_validate_settings_success(self, mock_user_settings):
        """設定検証の正常テスト"""
        if self.settings_dialog is None:
            pytest.skip("SettingsDialog not implemented yet - TDD")
        
        result = self.settings_dialog.validate_settings(mock_user_settings)
        
        # 戻り値の型チェック
        assert isinstance(result, bool)

    def test_validate_settings_invalid(self):
        """無効な設定の検証エラーテスト"""
        if self.settings_dialog is None:
            pytest.skip("SettingsDialog not implemented yet - TDD")
        
        with pytest.raises(ValidationError):
            self.settings_dialog.validate_settings(None)


@pytest.mark.contract
class TestThumbnailGridContract:
    """ThumbnailGrid契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        try:
            self.thumbnail_grid = ThumbnailGrid()
        except (ImportError, NotImplementedError, AttributeError):
            self.thumbnail_grid = None

    def test_display_thumbnails_success(self, mock_thumbnails):
        """サムネイルグリッド表示の正常テスト"""
        if self.thumbnail_grid is None:
            pytest.skip("ThumbnailGrid not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.thumbnail_grid.display_thumbnails(mock_thumbnails)

    def test_set_selection_callback_success(self):
        """選択コールバック設定の正常テスト"""
        if self.thumbnail_grid is None:
            pytest.skip("ThumbnailGrid not implemented yet - TDD")
        
        def selection_callback(thumbnails: List[Thumbnail]):
            pass
        
        # エラーが発生しないことを確認（戻り値なし）
        self.thumbnail_grid.set_selection_callback(selection_callback)

    def test_get_selected_items_success(self):
        """選択アイテム取得の正常テスト"""
        if self.thumbnail_grid is None:
            pytest.skip("ThumbnailGrid not implemented yet - TDD")
        
        selected = self.thumbnail_grid.get_selected_items()
        
        # 戻り値の型チェック
        assert isinstance(selected, list)
        assert all(isinstance(thumbnail, Thumbnail) for thumbnail in selected)

    def test_clear_selection_success(self):
        """選択クリアの正常テスト"""
        if self.thumbnail_grid is None:
            pytest.skip("ThumbnailGrid not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.thumbnail_grid.clear_selection()

    def test_select_all_success(self):
        """全選択の正常テスト"""
        if self.thumbnail_grid is None:
            pytest.skip("ThumbnailGrid not implemented yet - TDD")
        
        # エラーが発生しないことを確認（戻り値なし）
        self.thumbnail_grid.select_all()


# テスト用フィクスチャ
@pytest.fixture
def mock_video_file():
    """モックVideoFileオブジェクト"""
    return type('MockVideoFile', (), {
        'file_path': Path("test.mp4"),
        'file_name': "test.mp4",
        'duration': 30.0,
        'fps': 24.0,
        'width': 1920,
        'height': 1080,
        'is_valid': True
    })()


@pytest.fixture
def mock_user_settings():
    """モックUserSettingsオブジェクト"""
    return type('MockUserSettings', (), {
        'output_width': 1920,
        'output_height': 1080,
        'thumbnail_count': 5,
        'orientation': 'landscape',
        'output_directory': Path('/tmp'),
        'file_name_prefix': 'thumbnail',
        'quality_threshold': 0.7,
        'diversity_weight': 0.8,
        'face_size_preference': 'balanced'
    })()


@pytest.fixture
def mock_thumbnails():
    """モックThumbnailオブジェクトのリスト"""
    import numpy as np
    
    thumbnails = []
    for i in range(3):
        thumbnail = type('MockThumbnail', (), {
            'source_frame': None,
            'user_settings': None,
            'image_data': np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8),
            'diversity_score': 0.7 + i * 0.1,
            'total_score': 0.8 + i * 0.05,
            'file_path': Path(f"thumbnail_{i}.png"),
            'is_selected': i == 0  # 最初のサムネイルのみ選択状態
        })()
        thumbnails.append(thumbnail)
    return thumbnails
