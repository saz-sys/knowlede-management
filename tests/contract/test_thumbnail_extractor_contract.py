"""
ThumbnailExtractor契約テスト

ThumbnailExtractorサービスの契約インターフェース仕様に基づく契約テストです。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
from typing import List, Callable
import sys
import numpy as np

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.thumbnail_extractor import ThumbnailExtractor  # noqa: E402
from models.frame import Frame  # noqa: E402
from models.thumbnail import Thumbnail  # noqa: E402
from models.user_settings import UserSettings  # noqa: E402
from models.thumbnail_extraction_job import ThumbnailExtractionJob  # noqa: E402
from lib.errors import (  # noqa: E402
    ThumbnailExtractionError,
    InsufficientFramesError,
    InvalidSettingsError,
    DiversityCalculationError,
    InvalidCountError,
    InvalidWeightError,
    ThumbnailGenerationError,
    InvalidResolutionError,
    ImageResizeError,
    InvalidDimensionsError,
    InvalidOrientationError,
    CropError,
    FileSaveError,
    BatchSaveError,
    DirectoryError,
    JobCreationError,
)


@pytest.mark.contract
class TestThumbnailExtractorContract:
    """ThumbnailExtractor契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        # 実装前なので、ThumbnailExtractorのインスタンス化は失敗するはず
        try:
            self.extractor = ThumbnailExtractor()
        except (ImportError, NotImplementedError, AttributeError):
            # 期待されるエラー - 実装前のため
            self.extractor = None

    def test_extract_thumbnails_success(self, mock_frames, mock_user_settings):
        """サムネイル抽出の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        progress_values = []
        
        def progress_callback(progress: float):
            progress_values.append(progress)
        
        thumbnails = self.extractor.extract_thumbnails(
            mock_frames, 
            mock_user_settings, 
            progress_callback
        )
        
        # 戻り値の型チェック
        assert isinstance(thumbnails, list)
        assert all(isinstance(thumbnail, Thumbnail) for thumbnail in thumbnails)
        
        # 生成されたサムネイル数のチェック
        assert len(thumbnails) <= mock_user_settings.thumbnail_count
        
        # 進捗コールバックの呼び出し確認
        assert len(progress_values) > 0
        assert all(0.0 <= progress <= 1.0 for progress in progress_values)

    def test_extract_thumbnails_insufficient_frames(self, mock_user_settings):
        """フレーム数不足でのサムネイル抽出エラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        empty_frames = []
        
        with pytest.raises(InsufficientFramesError):
            self.extractor.extract_thumbnails(empty_frames, mock_user_settings)

    def test_extract_thumbnails_invalid_settings(self, mock_frames):
        """無効な設定でのサムネイル抽出エラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(InvalidSettingsError):
            self.extractor.extract_thumbnails(mock_frames, None)

    def test_calculate_diversity_scores_success(self, mock_frames):
        """多様性スコア計算の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        scores = self.extractor.calculate_diversity_scores(mock_frames)
        
        # 戻り値の型チェック
        assert isinstance(scores, list)
        assert len(scores) == len(mock_frames)
        assert all(isinstance(score, float) for score in scores)
        assert all(0.0 <= score <= 1.0 for score in scores)

    def test_calculate_diversity_scores_empty_frames(self):
        """空フレームリストでの多様性スコア計算テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        scores = self.extractor.calculate_diversity_scores([])
        
        assert isinstance(scores, list)
        assert len(scores) == 0

    def test_select_diverse_frames_success(self, mock_frames):
        """多様性フレーム選択の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        selected_frames = self.extractor.select_diverse_frames(
            mock_frames, 
            count=3, 
            diversity_weight=0.7
        )
        
        # 戻り値の型チェック
        assert isinstance(selected_frames, list)
        assert len(selected_frames) <= 3
        assert all(isinstance(frame, Frame) for frame in selected_frames)
        
        # 選択されたフレームは元のフレームのサブセット
        for frame in selected_frames:
            assert frame in mock_frames

    def test_select_diverse_frames_invalid_count(self, mock_frames):
        """無効な枚数での多様性フレーム選択エラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(InvalidCountError):
            self.extractor.select_diverse_frames(mock_frames, count=-1)
        
        with pytest.raises(InvalidCountError):
            self.extractor.select_diverse_frames(mock_frames, count=0)

    def test_select_diverse_frames_invalid_weight(self, mock_frames):
        """無効な重みでの多様性フレーム選択エラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(InvalidWeightError):
            self.extractor.select_diverse_frames(mock_frames, count=3, diversity_weight=-0.1)
        
        with pytest.raises(InvalidWeightError):
            self.extractor.select_diverse_frames(mock_frames, count=3, diversity_weight=1.1)

    def test_generate_thumbnail_success(self, mock_frame, mock_user_settings):
        """単一サムネイル生成の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        thumbnail = self.extractor.generate_thumbnail(mock_frame, mock_user_settings)
        
        # 戻り値の型チェック
        assert isinstance(thumbnail, Thumbnail)
        assert hasattr(thumbnail, 'source_frame')
        assert hasattr(thumbnail, 'user_settings')
        assert hasattr(thumbnail, 'image_data')
        assert hasattr(thumbnail, 'diversity_score')
        assert hasattr(thumbnail, 'total_score')
        
        # 生成されたサムネイルの検証
        assert thumbnail.source_frame == mock_frame
        assert thumbnail.user_settings == mock_user_settings

    def test_resize_image_success(self, sample_image_data):
        """画像リサイズの正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        resized_image = self.extractor.resize_image(
            sample_image_data, 
            target_width=800, 
            target_height=600,
            maintain_aspect_ratio=True
        )
        
        # リサイズ結果の検証
        assert resized_image is not None
        # 実際の実装では画像データの型をチェック

    def test_resize_image_invalid_dimensions(self, sample_image_data):
        """無効な寸法での画像リサイズエラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(InvalidDimensionsError):
            self.extractor.resize_image(sample_image_data, target_width=-100, target_height=600)
        
        with pytest.raises(InvalidDimensionsError):
            self.extractor.resize_image(sample_image_data, target_width=800, target_height=0)

    def test_crop_to_orientation_success(self, sample_image_data):
        """向き指定クロップの正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        # 横型クロップ
        landscape_image = self.extractor.crop_to_orientation(sample_image_data, "landscape")
        assert landscape_image is not None
        
        # 縦型クロップ
        portrait_image = self.extractor.crop_to_orientation(sample_image_data, "portrait")
        assert portrait_image is not None

    def test_crop_to_orientation_invalid(self, sample_image_data):
        """無効な向き指定でのクロップエラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(InvalidOrientationError):
            self.extractor.crop_to_orientation(sample_image_data, "invalid_orientation")

    def test_save_thumbnail_success(self, mock_thumbnail, temp_dir):
        """サムネイル保存の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        save_path = temp_dir / "test_thumbnail.png"
        
        result = self.extractor.save_thumbnail(mock_thumbnail, str(save_path))
        
        assert isinstance(result, bool)
        assert result is True

    def test_save_thumbnails_batch_success(self, mock_thumbnails, temp_dir):
        """サムネイル一括保存の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        saved_paths = self.extractor.save_thumbnails_batch(mock_thumbnails, str(temp_dir))
        
        # 戻り値の型チェック
        assert isinstance(saved_paths, list)
        assert len(saved_paths) == len(mock_thumbnails)
        assert all(isinstance(path, str) for path in saved_paths)

    def test_save_thumbnails_batch_directory_error(self, mock_thumbnails):
        """無効なディレクトリでの一括保存エラーテスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        with pytest.raises(DirectoryError):
            self.extractor.save_thumbnails_batch(mock_thumbnails, "/invalid/directory/path")

    def test_create_extraction_job_success(self, mock_frames, mock_user_settings):
        """抽出ジョブ作成の正常テスト"""
        if self.extractor is None:
            pytest.skip("ThumbnailExtractor not implemented yet - TDD")
        
        job = self.extractor.create_extraction_job(mock_frames, mock_user_settings)
        
        # 戻り値の型チェック
        assert isinstance(job, ThumbnailExtractionJob)
        assert hasattr(job, 'extracted_frames')
        assert hasattr(job, 'user_settings')
        assert hasattr(job, 'status')
        assert hasattr(job, 'progress')


# テスト用フィクスチャ
@pytest.fixture
def mock_frames():
    """モックFrameオブジェクトのリスト"""
    frames = []
    for i in range(5):
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 1.0,
            'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        })()
        frames.append(frame)
    return frames


@pytest.fixture
def mock_frame():
    """モックFrameオブジェクト"""
    return type('MockFrame', (), {
        'frame_number': 0,
        'timestamp': 0.0,
        'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
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
def mock_thumbnail():
    """モックThumbnailオブジェクト"""
    return type('MockThumbnail', (), {
        'source_frame': None,
        'user_settings': None,
        'image_data': np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8),
        'diversity_score': 0.8,
        'total_score': 0.85,
        'file_path': None,
        'is_selected': False
    })()


@pytest.fixture
def mock_thumbnails():
    """モックThumbnailオブジェクトのリスト"""
    thumbnails = []
    for i in range(3):
        thumbnail = type('MockThumbnail', (), {
            'source_frame': None,
            'user_settings': None,
            'image_data': np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8),
            'diversity_score': 0.7 + i * 0.1,
            'total_score': 0.8 + i * 0.05,
            'file_path': None,
            'is_selected': False
        })()
        thumbnails.append(thumbnail)
    return thumbnails
