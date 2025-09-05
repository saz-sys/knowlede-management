"""
ThumbnailExtractorのユニットテスト

サムネイル抽出サービスの各機能をテストします。
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import os

from src.services.thumbnail_extractor import ThumbnailExtractor
from src.models.frame import Frame
from src.models.thumbnail import Thumbnail
from src.models.user_settings import UserSettings, ThumbnailOrientation
from src.models.thumbnail_extraction_job import ThumbnailExtractionJob, JobStatus, JobPhase
from src.lib.errors import (
    ThumbnailExtractionError,
    InsufficientFramesError,
    InvalidSettingsError,
    ThumbnailGenerationError,
    InvalidResolutionError,
    ImageResizeError,
    InvalidDimensionsError,
    InvalidOrientationError,
    CropError,
    FileSaveError,
    BatchSaveError,
    DirectoryError,
    DiskSpaceError,
    FilePermissionError
)


class TestThumbnailExtractor:
    """ThumbnailExtractorのテストクラス"""
    
    @pytest.fixture
    def extractor(self):
        """ThumbnailExtractorのインスタンスを作成"""
        return ThumbnailExtractor()
    
    @pytest.fixture
    def sample_frames(self):
        """サンプルフレームリスト"""
        frames = []
        for i in range(5):
            frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60
            )
            frames.append(frame)
        return frames
    
    @pytest.fixture
    def user_settings(self):
        """ユーザー設定"""
        return UserSettings(
            thumbnail_count=5,
            output_width=1280,
            output_height=720
        )
    
    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリ"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_init(self, extractor):
        """初期化のテスト"""
        assert extractor.logger is not None

    def test_extract_thumbnails_success(self, extractor, sample_frames, user_settings):
        """サムネイル抽出成功のテスト"""
        progress_calls = []
        
        def progress_callback(progress):
            progress_calls.append(progress)
        
        # 実行
        thumbnails = extractor.extract_thumbnails(
            frames=sample_frames,
            settings=user_settings,
            progress_callback=progress_callback
        )
        
        # 検証
        assert len(thumbnails) == 5
        for thumbnail in thumbnails:
            assert isinstance(thumbnail, Thumbnail)
            assert thumbnail.image.shape[:2] == (720, 1280)  # (height, width)
        
        # プログレスコールバックが呼ばれたことを確認
        assert len(progress_calls) > 0
        assert progress_calls[-1] == 1.0  # 最後は100%

    def test_extract_thumbnails_insufficient_frames(self, extractor, user_settings):
        """フレーム不足のテスト"""
        empty_frames = []
        
        with pytest.raises(InsufficientFramesError):
            extractor.extract_thumbnails(empty_frames, user_settings)

    def test_extract_thumbnails_invalid_settings(self, extractor, sample_frames):
        """無効な設定のテスト"""
        invalid_settings = UserSettings(
            thumbnail_count=0,  # 無効な値
            output_width=1280,
            output_height=720
        )
        
        with pytest.raises(InvalidSettingsError):
            extractor.extract_thumbnails(sample_frames, invalid_settings)

    def test_resize_image_success(self, extractor):
        """画像リサイズ成功のテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        target_width = 1280
        target_height = 720
        
        resized = extractor.resize_image(source_image, target_width, target_height)
        
        assert resized.shape == (720, 1280, 3)
        assert resized.dtype == np.uint8

    def test_resize_image_maintain_aspect_ratio(self, extractor):
        """アスペクト比維持リサイズのテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        target_width = 800
        target_height = 800  # 正方形
        
        resized = extractor.resize_image(
            source_image, target_width, target_height, maintain_aspect_ratio=True
        )
        
        # アスペクト比を維持してリサイズされることを確認
        assert resized.shape[:2] == (600, 800)  # 元の4:3比を維持

    def test_resize_image_invalid_dimensions(self, extractor):
        """無効なサイズでのリサイズテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with pytest.raises(InvalidDimensionsError):
            extractor.resize_image(source_image, 0, 720)
        
        with pytest.raises(InvalidDimensionsError):
            extractor.resize_image(source_image, 1280, -720)

    def test_resize_image_invalid_input(self, extractor):
        """無効な入力画像でのリサイズテスト"""
        with pytest.raises(ImageResizeError):
            extractor.resize_image(None, 1280, 720)

    def test_crop_image_center(self, extractor):
        """中央切り抜きのテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        crop_width = 320
        crop_height = 240
        
        cropped = extractor.crop_image(source_image, crop_width, crop_height)
        
        assert cropped.shape == (240, 320, 3)

    def test_crop_image_with_position(self, extractor):
        """指定位置での切り抜きテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        crop_width = 200
        crop_height = 150
        start_x = 100
        start_y = 80
        
        cropped = extractor.crop_image(
            source_image, crop_width, crop_height, start_x, start_y
        )
        
        assert cropped.shape == (150, 200, 3)

    def test_crop_image_out_of_bounds(self, extractor):
        """範囲外切り抜きのテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with pytest.raises(CropError):
            extractor.crop_image(source_image, 800, 600)  # 元画像より大きい

    def test_crop_image_invalid_dimensions(self, extractor):
        """無効なサイズでの切り抜きテスト"""
        source_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        with pytest.raises(InvalidDimensionsError):
            extractor.crop_image(source_image, 0, 240)
        
        with pytest.raises(InvalidDimensionsError):
            extractor.crop_image(source_image, 320, -240)

    def test_apply_orientation_landscape(self, extractor):
        """横向き変換のテスト"""
        portrait_image = np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8)
        
        landscape = extractor.apply_orientation(portrait_image, ThumbnailOrientation.LANDSCAPE)
        
        # 横長になることを確認
        assert landscape.shape[1] > landscape.shape[0]

    def test_apply_orientation_portrait(self, extractor):
        """縦向き変換のテスト"""
        landscape_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        
        portrait = extractor.apply_orientation(landscape_image, ThumbnailOrientation.PORTRAIT)
        
        # 縦長になることを確認
        assert portrait.shape[0] > portrait.shape[1]

    def test_apply_orientation_auto(self, extractor):
        """自動向き変換のテスト"""
        landscape_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        
        result = extractor.apply_orientation(landscape_image, ThumbnailOrientation.AUTO)
        
        # 元の向きが維持される
        assert result.shape == landscape_image.shape

    def test_apply_orientation_invalid(self, extractor):
        """無効な向き指定のテスト"""
        image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        
        with pytest.raises(InvalidOrientationError):
            extractor.apply_orientation(image, "invalid_orientation")

    @patch('cv2.imwrite')
    def test_save_thumbnail_success(self, mock_imwrite, extractor, temp_dir):
        """サムネイル保存成功のテスト"""
        mock_imwrite.return_value = True
        
        thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        thumbnail = Thumbnail(
            image=thumbnail_data,
            timestamp_seconds=5.0,
            frame_index=150,
            quality_score=0.8
        )
        
        output_path = temp_dir / "thumbnail.png"
        
        saved_path = extractor.save_thumbnail(thumbnail, output_path)
        
        assert saved_path == output_path
        mock_imwrite.assert_called_once()

    @patch('cv2.imwrite')
    def test_save_thumbnail_write_failure(self, mock_imwrite, extractor, temp_dir):
        """保存失敗のテスト"""
        mock_imwrite.return_value = False
        
        thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        thumbnail = Thumbnail(
            image=thumbnail_data,
            timestamp_seconds=5.0,
            frame_index=150,
            quality_score=0.8
        )
        
        output_path = temp_dir / "thumbnail.png"
        
        with pytest.raises(FileSaveError):
            extractor.save_thumbnail(thumbnail, output_path)

    def test_save_thumbnail_invalid_directory(self, extractor):
        """存在しないディレクトリへの保存テスト"""
        thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        thumbnail = Thumbnail(
            image=thumbnail_data,
            timestamp_seconds=5.0,
            frame_index=150,
            quality_score=0.8
        )
        
        invalid_path = Path("/non_existent_directory/thumbnail.png")
        
        with pytest.raises(DirectoryError):
            extractor.save_thumbnail(thumbnail, invalid_path)

    @patch('cv2.imwrite')
    def test_batch_save_thumbnails_success(self, mock_imwrite, extractor, temp_dir):
        """バッチ保存成功のテスト"""
        mock_imwrite.return_value = True
        
        thumbnails = []
        for i in range(3):
            thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
            thumbnail = Thumbnail(
                image=thumbnail_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60,
                quality_score=0.8
            )
            thumbnails.append(thumbnail)
        
        filename_template = "thumbnail_{index:03d}.png"
        
        saved_paths = extractor.batch_save_thumbnails(
            thumbnails, temp_dir, filename_template
        )
        
        assert len(saved_paths) == 3
        assert all(path.exists() for path in saved_paths)

    @patch('cv2.imwrite')
    def test_batch_save_thumbnails_partial_failure(self, mock_imwrite, extractor, temp_dir):
        """バッチ保存部分失敗のテスト"""
        # 2回目の保存で失敗
        mock_imwrite.side_effect = [True, False, True]
        
        thumbnails = []
        for i in range(3):
            thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
            thumbnail = Thumbnail(
                image=thumbnail_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60,
                quality_score=0.8
            )
            thumbnails.append(thumbnail)
        
        filename_template = "thumbnail_{index:03d}.png"
        
        with pytest.raises(BatchSaveError):
            extractor.batch_save_thumbnails(thumbnails, temp_dir, filename_template)

    def test_validate_settings_valid(self, extractor):
        """有効な設定の検証テスト"""
        valid_settings = UserSettings(
            thumbnail_count=5,
            output_width=1280,
            output_height=720
        )
        
        # 例外が発生しないことを確認
        extractor.validate_settings(valid_settings)

    def test_validate_settings_invalid_count(self, extractor):
        """無効なサムネイル数の検証テスト"""
        invalid_settings = UserSettings(
            thumbnail_count=0,
            output_width=1280,
            output_height=720
        )
        
        with pytest.raises(InvalidSettingsError):
            extractor.validate_settings(invalid_settings)

    def test_validate_settings_invalid_resolution(self, extractor):
        """無効な解像度の検証テスト"""
        invalid_settings = UserSettings(
            thumbnail_count=5,
            output_width=0,
            output_height=720
        )
        
        with pytest.raises(InvalidResolutionError):
            extractor.validate_settings(invalid_settings)

    def test_calculate_optimal_size(self, extractor):
        """最適サイズ計算のテスト"""
        source_width = 1920
        source_height = 1080
        target_width = 1280
        target_height = 720
        
        optimal_width, optimal_height = extractor.calculate_optimal_size(
            source_width, source_height, target_width, target_height
        )
        
        assert optimal_width <= target_width
        assert optimal_height <= target_height
        
        # アスペクト比が維持されることを確認
        source_ratio = source_width / source_height
        optimal_ratio = optimal_width / optimal_height
        assert abs(source_ratio - optimal_ratio) < 0.01

    def test_generate_filename(self, extractor):
        """ファイル名生成のテスト"""
        template = "thumbnail_{index:03d}_{timestamp:.1f}s.png"
        index = 5
        timestamp = 12.3
        
        filename = extractor.generate_filename(template, index, timestamp)
        
        assert filename == "thumbnail_005_12.3s.png"

    def test_generate_filename_invalid_template(self, extractor):
        """無効なテンプレートでのファイル名生成テスト"""
        invalid_template = "thumbnail_{invalid_key}.png"
        
        with pytest.raises(ValueError):
            extractor.generate_filename(invalid_template, 1, 1.0)

    def test_cleanup(self, extractor):
        """クリーンアップのテスト"""
        # 実行（エラーが発生しないことを確認）
        extractor.cleanup()
        
        # ログに記録されることを確認（実際の検証は省略）
        assert True

    def test_get_processing_stats(self, extractor):
        """処理統計情報取得のテスト"""
        stats = extractor.get_processing_stats()
        
        expected_keys = [
            'total_thumbnails_generated',
            'total_processing_time',
            'average_processing_time_per_thumbnail',
            'total_saved_files',
            'total_save_errors'
        ]
        
        assert all(key in stats for key in expected_keys)
        assert all(isinstance(stats[key], (int, float)) for key in expected_keys)


class TestThumbnailExtractorIntegration:
    """ThumbnailExtractorの統合テスト"""
    
    @pytest.fixture
    def extractor(self):
        return ThumbnailExtractor()
    
    def test_full_extraction_pipeline(self, extractor):
        """完全な抽出パイプラインのテスト"""
        # テストデータ準備
        frames = []
        for i in range(5):
            frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60
            )
            frames.append(frame)
        
        settings = UserSettings(
            thumbnail_count=3,
            output_width=800,
            output_height=450
        )
        
        # パイプライン実行
        thumbnails = extractor.extract_thumbnails(frames, settings)
        
        # 検証
        assert len(thumbnails) == 3
        for thumbnail in thumbnails:
            assert isinstance(thumbnail, Thumbnail)
            assert thumbnail.image.shape[:2] == (450, 800)
    
    @patch('cv2.imwrite')
    def test_extract_and_save_pipeline(self, mock_imwrite, extractor, temp_dir):
        """抽出→保存パイプラインのテスト"""
        mock_imwrite.return_value = True
        
        # フレーム準備
        frames = []
        for i in range(3):
            frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60
            )
            frames.append(frame)
        
        settings = UserSettings(
            thumbnail_count=3,
            output_width=640,
            output_height=480
        )
        
        # 抽出
        thumbnails = extractor.extract_thumbnails(frames, settings)
        
        # 保存
        saved_paths = extractor.batch_save_thumbnails(
            thumbnails, temp_dir, "thumb_{index:02d}.png"
        )
        
        # 検証
        assert len(saved_paths) == 3
        assert all(path.suffix == ".png" for path in saved_paths)
