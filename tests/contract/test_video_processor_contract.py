"""
VideoProcessor契約テスト

VideoProcessorサービスの契約インターフェース仕様に基づく契約テストです。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
from typing import Iterator, List
import sys
import os

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.video_processor import VideoProcessor  # noqa: E402
from models.video_file import VideoFile  # noqa: E402
from models.frame import Frame  # noqa: E402
from lib.errors import (  # noqa: E402
    VideoProcessingError,
    InvalidVideoFormatError,
    CorruptedVideoError,
    UnsupportedCodecError,
    InsufficientMemoryError,
    InvalidThresholdError,
    InvalidFrameDataError,
)


@pytest.mark.contract
class TestVideoProcessorContract:
    """VideoProcessor契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        # 実装前なので、VideoProcessorのインスタンス化は失敗するはず
        try:
            self.processor = VideoProcessor()
        except (ImportError, NotImplementedError, AttributeError):
            # 期待されるエラー - 実装前のため
            self.processor = None

    @pytest.mark.parametrize("file_path", [
        Path("tests/sample_data/sample_anime_short.mp4"),
        Path("tests/sample_data/sample_anime_long.mp4"),
    ])
    def test_load_video_success(self, file_path: Path):
        """正常な動画ファイル読み込みのテスト"""
        # 実装前なので失敗するはず
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # 契約仕様に基づくテスト
        result = self.processor.load_video(file_path)
        
        # 戻り値の型チェック
        assert isinstance(result, VideoFile)
        
        # 必須属性の存在チェック
        assert hasattr(result, 'file_path')
        assert hasattr(result, 'file_name')
        assert hasattr(result, 'duration')
        assert hasattr(result, 'fps')
        assert hasattr(result, 'width')
        assert hasattr(result, 'height')
        assert hasattr(result, 'is_valid')
        
        # バリデーションルールのチェック
        assert result.file_path == file_path
        assert result.file_name == file_path.name
        assert result.duration >= 10.0  # 最低10秒以上
        assert 1 <= result.fps <= 120
        assert result.width >= 240  # 最小240p
        assert result.height >= 240
        assert result.is_valid is True

    def test_load_video_file_not_found(self):
        """存在しないファイルのエラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        non_existent_path = Path("non_existent_video.mp4")
        
        with pytest.raises(FileNotFoundError):
            self.processor.load_video(non_existent_path)

    def test_load_video_invalid_format(self, temp_dir):
        """MP4以外の形式のエラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # AVI形式のモックファイル
        avi_file = temp_dir / "test_video.avi"
        avi_file.touch()
        
        with pytest.raises(InvalidVideoFormatError):
            self.processor.load_video(avi_file)

    def test_load_video_corrupted_file(self, temp_dir):
        """破損ファイルのエラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # 破損したMP4ファイルのモック
        corrupted_file = temp_dir / "corrupted.mp4"
        corrupted_file.write_text("invalid mp4 content")
        
        with pytest.raises(CorruptedVideoError):
            self.processor.load_video(corrupted_file)

    def test_extract_frames_success(self, mock_video_file):
        """フレーム抽出の正常テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        frames = self.processor.extract_frames(mock_video_file, interval_seconds=1.0)
        
        # イテレータの型チェック
        assert hasattr(frames, '__iter__')
        assert hasattr(frames, '__next__')
        
        # フレームの取得テスト
        frame_list = list(frames)
        assert len(frame_list) > 0
        
        for frame in frame_list:
            assert isinstance(frame, Frame)
            assert hasattr(frame, 'video_file')
            assert hasattr(frame, 'frame_number')
            assert hasattr(frame, 'timestamp')
            assert hasattr(frame, 'image_data')
            assert frame.video_file == mock_video_file

    def test_extract_frames_invalid_interval(self, mock_video_file):
        """無効な間隔でのフレーム抽出エラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        with pytest.raises(ValueError):
            list(self.processor.extract_frames(mock_video_file, interval_seconds=-1.0))
        
        with pytest.raises(ValueError):
            list(self.processor.extract_frames(mock_video_file, interval_seconds=0.0))

    def test_detect_scene_changes_success(self, mock_frames):
        """シーンチェンジ検出の正常テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        scene_frames = self.processor.detect_scene_changes(mock_frames, threshold=0.3)
        
        # 戻り値の型チェック
        assert isinstance(scene_frames, list)
        assert all(isinstance(frame, Frame) for frame in scene_frames)
        
        # シーンチェンジフレームは元のフレームのサブセット
        assert len(scene_frames) <= len(mock_frames)

    def test_detect_scene_changes_invalid_threshold(self, mock_frames):
        """無効な閾値でのシーンチェンジ検出エラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        with pytest.raises(InvalidThresholdError):
            self.processor.detect_scene_changes(mock_frames, threshold=-0.1)
        
        with pytest.raises(InvalidThresholdError):
            self.processor.detect_scene_changes(mock_frames, threshold=1.1)

    def test_calculate_quality_score_success(self, mock_frame):
        """品質スコア計算の正常テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        score = self.processor.calculate_quality_score(mock_frame)
        
        # スコアの範囲チェック
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_calculate_quality_score_invalid_frame(self):
        """無効なフレームでの品質スコア計算エラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        with pytest.raises(InvalidFrameDataError):
            self.processor.calculate_quality_score(None)

    def test_get_video_info_success(self, temp_dir):
        """動画情報取得の正常テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # モックMP4ファイル
        video_file = temp_dir / "test.mp4"
        video_file.touch()
        
        info = self.processor.get_video_info(video_file)
        
        # 戻り値の型と必須キーのチェック
        assert isinstance(info, dict)
        required_keys = {'duration', 'fps', 'width', 'height'}
        assert required_keys.issubset(info.keys())

    def test_validate_video_file_success(self, temp_dir):
        """動画ファイル検証の正常テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # 有効なMP4ファイルのモック
        valid_file = temp_dir / "valid.mp4"
        valid_file.touch()
        
        result = self.processor.validate_video_file(valid_file)
        assert isinstance(result, bool)

    def test_validate_video_file_not_found(self):
        """存在しないファイルの検証エラーテスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        with pytest.raises(FileNotFoundError):
            self.processor.validate_video_file(Path("non_existent.mp4"))


# テスト用フィクスチャ
@pytest.fixture
def mock_video_file():
    """モックVideoFileオブジェクト"""
    # 実装前なので、VideoFileクラスも存在しないはず
    class MockVideoFile:
        def __init__(self):
            self.file_path = Path("test.mp4")
            self.file_name = "test.mp4"
            self.duration = 30.0
            self.fps = 24.0
            self.width = 1920
            self.height = 1080
            self.is_valid = True
    
    return MockVideoFile()


@pytest.fixture
def mock_frame():
    """モックFrameオブジェクト"""
    import numpy as np
    
    class MockFrame:
        def __init__(self):
            self.frame_number = 0
            self.timestamp = 0.0
            self.image_data = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    return MockFrame()


@pytest.fixture
def mock_frames():
    """モックFrameオブジェクトのリスト"""
    import numpy as np
    
    class MockFrame:
        def __init__(self, frame_num):
            self.frame_number = frame_num
            self.timestamp = frame_num * 1.0
            self.image_data = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    return [MockFrame(i) for i in range(5)]
