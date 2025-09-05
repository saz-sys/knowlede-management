"""
VideoProcessorのユニットテスト

動画処理サービスの各機能をテストします。
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import cv2

from src.services.video_processor import VideoProcessor
from src.models.video_file import VideoFile, VideoFileStatus
from src.models.frame import Frame
from src.lib.errors import (
    VideoProcessingError,
    InvalidVideoFormatError,
    CorruptedVideoError,
    UnsupportedCodecError,
    InsufficientMemoryError,
    InvalidFrameDataError
)


class TestVideoProcessor:
    """VideoProcessorのテストクラス"""
    
    @pytest.fixture
    def processor(self):
        """VideoProcessorのインスタンスを作成"""
        return VideoProcessor()
    
    @pytest.fixture
    def sample_video_path(self):
        """サンプル動画パスを返す"""
        return Path("tests/fixtures/sample_video.mp4")
    
    @pytest.fixture
    def mock_video_capture(self):
        """モックのVideoCapture"""
        mock_cap = Mock(spec=cv2.VideoCapture)
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 1000,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }.get(prop, 0)
        return mock_cap
    
    @pytest.fixture
    def sample_frame(self):
        """サンプルフレームデータ"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def test_init(self, processor):
        """初期化のテスト"""
        assert processor._current_video_capture is None
        assert processor._frame_buffer == []
        assert processor._max_buffer_size == 100
        assert processor.logger is not None

    @patch('cv2.VideoCapture')
    def test_load_video_success(self, mock_cv_cap, processor, sample_video_path, mock_video_capture):
        """動画読み込み成功のテスト"""
        # モック設定
        mock_cv_cap.return_value = mock_video_capture
        
        with patch.object(sample_video_path, 'exists', return_value=True), \
             patch.object(sample_video_path, 'suffix', '.mp4'), \
             patch.object(sample_video_path, 'stat') as mock_stat:
            
            mock_stat.return_value.st_size = 10 * 1024 * 1024  # 10MB
            
            # 実行
            video_file = processor.load_video(sample_video_path)
            
            # 検証
            assert isinstance(video_file, VideoFile)
            assert video_file.file_path == sample_video_path
            assert video_file.status == VideoFileStatus.LOADED
            assert video_file.frame_count == 1000
            assert video_file.fps == 30.0
            assert video_file.duration == pytest.approx(33.33, rel=1e-2)

    def test_load_video_file_not_found(self, processor):
        """存在しないファイルのテスト"""
        non_existent_path = Path("non_existent_video.mp4")
        
        with pytest.raises(FileNotFoundError):
            processor.load_video(non_existent_path)

    def test_load_video_invalid_format(self, processor, sample_video_path):
        """無効な形式のファイルのテスト"""
        with patch.object(sample_video_path, 'exists', return_value=True), \
             patch.object(sample_video_path, 'suffix', '.avi'):
            
            with pytest.raises(InvalidVideoFormatError):
                processor.load_video(sample_video_path)

    @patch('cv2.VideoCapture')
    def test_load_video_corrupted(self, mock_cv_cap, processor, sample_video_path):
        """破損した動画ファイルのテスト"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_cv_cap.return_value = mock_cap
        
        with patch.object(sample_video_path, 'exists', return_value=True), \
             patch.object(sample_video_path, 'suffix', '.mp4'), \
             patch.object(sample_video_path, 'stat') as mock_stat:
            
            mock_stat.return_value.st_size = 10 * 1024 * 1024
            
            with pytest.raises(CorruptedVideoError):
                processor.load_video(sample_video_path)

    def test_extract_frames_by_count(self, processor):
        """フレーム数指定による抽出のテスト"""
        # モックVideoFileを作成
        video_file = Mock(spec=VideoFile)
        video_file.frame_count = 1000
        video_file.fps = 30.0
        
        # extract_frames_at_intervalsをモック
        expected_frames = [Mock(spec=Frame) for _ in range(5)]
        with patch.object(processor, 'extract_frames_at_intervals', return_value=expected_frames):
            frames = processor.extract_frames_by_count(video_file, 5)
            
            assert len(frames) == 5
            assert frames == expected_frames

    def test_extract_frames_by_count_invalid_count(self, processor):
        """無効なフレーム数のテスト"""
        video_file = Mock(spec=VideoFile)
        
        with pytest.raises(ValueError, match="フレーム数は1以上である必要があります"):
            processor.extract_frames_by_count(video_file, 0)
        
        with pytest.raises(ValueError, match="フレーム数は1以上である必要があります"):
            processor.extract_frames_by_count(video_file, -1)

    @patch('cv2.VideoCapture')
    def test_extract_frames_at_intervals(self, mock_cv_cap, processor, mock_video_capture, sample_frame):
        """指定間隔でのフレーム抽出テスト"""
        mock_cv_cap.return_value = mock_video_capture
        processor._current_video_capture = mock_video_capture
        
        # read()の戻り値を設定
        mock_video_capture.read.side_effect = [
            (True, sample_frame),
            (True, sample_frame),
            (True, sample_frame),
            (False, None)
        ]
        
        intervals = [100, 200, 300]
        frames = processor.extract_frames_at_intervals(intervals)
        
        assert len(frames) == 3
        for frame in frames:
            assert isinstance(frame, Frame)

    def test_calculate_scene_change_score(self, processor, sample_frame):
        """シーンチェンジスコア計算のテスト"""
        frame1 = sample_frame.copy()
        frame2 = sample_frame.copy()
        frame2[:, :] = [255, 255, 255]  # 白フレーム
        
        score = processor.calculate_scene_change_score(frame1, frame2)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # 大きく異なるフレームなので高いスコア
        assert score > 0.5

    def test_calculate_scene_change_score_same_frames(self, processor, sample_frame):
        """同じフレームのシーンチェンジスコア"""
        score = processor.calculate_scene_change_score(sample_frame, sample_frame)
        
        assert score == 0.0

    def test_calculate_scene_change_score_invalid_input(self, processor):
        """無効な入力のテスト"""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        invalid_frame = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        
        with pytest.raises(InvalidFrameDataError):
            processor.calculate_scene_change_score(frame, invalid_frame)

    def test_evaluate_frame_quality(self, processor, sample_frame):
        """フレーム品質評価のテスト"""
        score = processor.evaluate_frame_quality(sample_frame)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_evaluate_frame_quality_sharp_frame(self, processor):
        """鮮明なフレームの品質評価"""
        # 高コントラストのチェッカーボードパターン
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[::2, ::2] = 255  # チェッカーボード
        frame[1::2, 1::2] = 255
        
        score = processor.evaluate_frame_quality(frame)
        
        # 鮮明なパターンなので高いスコア
        assert score > 0.5

    def test_evaluate_frame_quality_blurry_frame(self, processor):
        """ぼやけたフレームの品質評価"""
        # 単色フレーム（コントラスト低）
        frame = np.full((480, 640, 3), 128, dtype=np.uint8)
        
        score = processor.evaluate_frame_quality(frame)
        
        # コントラストが低いので低いスコア
        assert score < 0.5

    def test_evaluate_frame_quality_invalid_frame(self, processor):
        """無効なフレームの品質評価"""
        with pytest.raises(InvalidFrameDataError):
            processor.evaluate_frame_quality(None)
        
        # 2Dフレーム（3Dである必要がある）
        frame_2d = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        with pytest.raises(InvalidFrameDataError):
            processor.evaluate_frame_quality(frame_2d)

    def test_get_video_info(self, processor, sample_video_path, mock_video_capture):
        """動画情報取得のテスト"""
        with patch('cv2.VideoCapture', return_value=mock_video_capture), \
             patch.object(sample_video_path, 'exists', return_value=True), \
             patch.object(sample_video_path, 'stat') as mock_stat:
            
            mock_stat.return_value.st_size = 10 * 1024 * 1024
            
            info = processor.get_video_info(sample_video_path)
            
            expected_info = {
                'file_path': str(sample_video_path),
                'file_size': 10 * 1024 * 1024,
                'frame_count': 1000,
                'fps': 30.0,
                'duration': pytest.approx(33.33, rel=1e-2),
                'width': 1920,
                'height': 1080,
                'codec': 'unknown'
            }
            
            assert info == expected_info

    def test_cleanup(self, processor, mock_video_capture):
        """クリーンアップのテスト"""
        processor._current_video_capture = mock_video_capture
        processor._frame_buffer = [np.zeros((100, 100, 3)) for _ in range(5)]
        
        processor.cleanup()
        
        mock_video_capture.release.assert_called_once()
        assert processor._current_video_capture is None
        assert processor._frame_buffer == []

    def test_cleanup_no_capture(self, processor):
        """VideoCapture未設定時のクリーンアップ"""
        processor._current_video_capture = None
        processor._frame_buffer = [np.zeros((100, 100, 3))]
        
        # エラーが発生しないことを確認
        processor.cleanup()
        
        assert processor._frame_buffer == []

    @patch('cv2.VideoCapture')
    def test_memory_management(self, mock_cv_cap, processor, mock_video_capture):
        """メモリ管理のテスト"""
        mock_cv_cap.return_value = mock_video_capture
        processor._current_video_capture = mock_video_capture
        
        # バッファサイズを超える量のフレームを追加
        large_frames = [np.zeros((1080, 1920, 3), dtype=np.uint8) for _ in range(150)]
        processor._frame_buffer = large_frames
        
        # バッファサイズ制限が適用されることを確認
        processor._manage_memory()
        
        assert len(processor._frame_buffer) <= processor._max_buffer_size

    def test_invalid_threshold_error(self, processor, sample_frame):
        """無効な閾値エラーのテスト"""
        # シーンチェンジ検出で無効な閾値
        with pytest.raises(InvalidThresholdError):
            processor.detect_scene_changes([], threshold=-0.1)
        
        with pytest.raises(InvalidThresholdError):
            processor.detect_scene_changes([], threshold=1.1)

    def test_insufficient_memory_error(self, processor):
        """メモリ不足エラーのテスト"""
        # 巨大なフレームバッファを設定
        with patch.object(processor, '_max_buffer_size', 1):
            processor._frame_buffer = [np.zeros((4096, 4096, 3), dtype=np.uint8) for _ in range(10)]
            
            with pytest.raises(InsufficientMemoryError):
                processor._manage_memory()


class TestVideoProcessorIntegration:
    """VideoProcessorの統合テスト"""
    
    @pytest.fixture
    def processor(self):
        return VideoProcessor()
    
    def test_full_processing_pipeline(self, processor):
        """完全な処理パイプラインのテスト"""
        # 実際のファイルは使用せず、すべてモック
        with patch.object(processor, 'load_video') as mock_load, \
             patch.object(processor, 'extract_frames_by_count') as mock_extract:
            
            # モック設定
            video_file = Mock(spec=VideoFile)
            frames = [Mock(spec=Frame) for _ in range(5)]
            mock_load.return_value = video_file
            mock_extract.return_value = frames
            
            # パイプライン実行
            video_path = Path("test.mp4")
            loaded_video = processor.load_video(video_path)
            extracted_frames = processor.extract_frames_by_count(loaded_video, 5)
            
            # 検証
            assert loaded_video == video_file
            assert len(extracted_frames) == 5
            mock_load.assert_called_once_with(video_path)
            mock_extract.assert_called_once_with(video_file, 5)
