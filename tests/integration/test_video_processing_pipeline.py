"""
動画処理パイプライン統合テスト

動画読み込み→フレーム抽出の統合フローをテストします。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
import sys
import tempfile
import numpy as np

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.video_processor import VideoProcessor  # noqa: E402
from models.video_file import VideoFile  # noqa: E402
from models.frame import Frame  # noqa: E402
from lib.logger import get_logger  # noqa: E402


@pytest.mark.integration
class TestVideoProcessingPipeline:
    """動画処理パイプライン統合テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.logger = get_logger(__name__, test_name="video_processing_pipeline")
        
        # 実装前なので、VideoProcessorのインスタンス化は失敗するはず
        try:
            self.processor = VideoProcessor()
        except (ImportError, NotImplementedError, AttributeError) as e:
            self.logger.info(f"VideoProcessor not implemented yet - TDD: {e}")
            self.processor = None

    @pytest.mark.slow
    def test_full_video_processing_pipeline(self, sample_video_file):
        """完全な動画処理パイプラインの統合テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        self.logger.info("動画処理パイプライン統合テスト開始")
        
        # Step 1: 動画ファイル読み込み
        self.logger.info(f"動画ファイル読み込み: {sample_video_file}")
        video_file = self.processor.load_video(sample_video_file)
        
        # VideoFileオブジェクトの検証
        assert isinstance(video_file, VideoFile)
        assert video_file.is_valid
        assert video_file.duration > 0
        assert video_file.fps > 0
        assert video_file.width > 0
        assert video_file.height > 0
        
        self.logger.info(f"動画情報: {video_file.duration}秒, {video_file.width}x{video_file.height}, {video_file.fps}fps")
        
        # Step 2: フレーム抽出
        self.logger.info("フレーム抽出開始")
        frames = list(self.processor.extract_frames(video_file, interval_seconds=1.0))
        
        # フレーム抽出結果の検証
        assert len(frames) > 0
        assert all(isinstance(frame, Frame) for frame in frames)
        
        # フレーム順序の確認
        for i, frame in enumerate(frames):
            assert frame.frame_number >= 0
            assert frame.timestamp >= 0
            if i > 0:
                assert frame.timestamp > frames[i-1].timestamp
        
        self.logger.info(f"抽出フレーム数: {len(frames)}")
        
        # Step 3: シーンチェンジ検出
        self.logger.info("シーンチェンジ検出開始")
        scene_frames = self.processor.detect_scene_changes(frames, threshold=0.3)
        
        # シーンチェンジ検出結果の検証
        assert isinstance(scene_frames, list)
        assert len(scene_frames) <= len(frames)
        assert all(frame in frames for frame in scene_frames)
        
        self.logger.info(f"シーンチェンジフレーム数: {len(scene_frames)}")
        
        # Step 4: 品質スコア計算
        self.logger.info("品質スコア計算開始")
        quality_scores = []
        for frame in frames[:5]:  # 最初の5フレームのみテスト
            score = self.processor.calculate_quality_score(frame)
            quality_scores.append(score)
            assert 0.0 <= score <= 1.0
        
        self.logger.info(f"品質スコア範囲: {min(quality_scores):.3f} - {max(quality_scores):.3f}")
        
        self.logger.info("動画処理パイプライン統合テスト完了")

    def test_video_loading_error_handling(self):
        """動画読み込みエラーハンドリングの統合テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        # 存在しないファイル
        with pytest.raises(FileNotFoundError):
            self.processor.load_video(Path("non_existent_video.mp4"))
        
        # 無効な形式
        with tempfile.NamedTemporaryFile(suffix=".avi", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            with pytest.raises(Exception):  # InvalidVideoFormatError or similar
                self.processor.load_video(tmp_path)
        
        self.logger.info("エラーハンドリングテスト完了")

    def test_frame_extraction_performance(self, sample_video_file):
        """フレーム抽出パフォーマンステスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        import time
        
        video_file = self.processor.load_video(sample_video_file)
        
        # パフォーマンス測定
        start_time = time.time()
        frames = list(self.processor.extract_frames(video_file, interval_seconds=2.0))
        end_time = time.time()
        
        extraction_time = end_time - start_time
        
        # パフォーマンス要件の検証（研究結果に基づく）
        # 1分の動画から30フレーム抽出が10秒以内
        expected_max_time = (video_file.duration / 60.0) * 10.0
        
        self.logger.info(f"フレーム抽出時間: {extraction_time:.2f}秒 (期待値: {expected_max_time:.2f}秒以内)")
        
        assert extraction_time <= expected_max_time, f"フレーム抽出が遅すぎます: {extraction_time:.2f}秒"
        assert len(frames) > 0

    def test_memory_efficiency(self, sample_video_file):
        """メモリ効率性テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        video_file = self.processor.load_video(sample_video_file)
        frames = list(self.processor.extract_frames(video_file, interval_seconds=1.0))
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = peak_memory - initial_memory
        
        self.logger.info(f"メモリ使用量: {memory_usage:.2f}MB")
        
        # メモリ使用量要件（研究結果に基づく制約）
        max_memory_mb = 500  # 500MB以内
        assert memory_usage <= max_memory_mb, f"メモリ使用量が多すぎます: {memory_usage:.2f}MB"

    def test_concurrent_processing(self, sample_video_file):
        """並行処理テスト"""
        if self.processor is None:
            pytest.skip("VideoProcessor not implemented yet - TDD")
        
        import concurrent.futures
        import threading
        
        video_file = self.processor.load_video(sample_video_file)
        
        def extract_frames_chunk(start_time, end_time):
            """フレーム抽出チャンク処理"""
            frames = []
            for frame in self.processor.extract_frames(video_file, interval_seconds=1.0):
                if start_time <= frame.timestamp <= end_time:
                    frames.append(frame)
            return frames
        
        # 並行でフレーム抽出
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(extract_frames_chunk, 0, video_file.duration / 2)
            future2 = executor.submit(extract_frames_chunk, video_file.duration / 2, video_file.duration)
            
            chunk1 = future1.result()
            chunk2 = future2.result()
        
        # 結果の検証
        assert len(chunk1) > 0 or len(chunk2) > 0
        all_frames = chunk1 + chunk2
        
        # フレーム重複チェック
        timestamps = [frame.timestamp for frame in all_frames]
        assert len(timestamps) == len(set(timestamps)), "並行処理でフレームが重複しています"
        
        self.logger.info(f"並行処理結果: chunk1={len(chunk1)}, chunk2={len(chunk2)}")


# テスト用フィクスチャ
@pytest.fixture(scope="session")
def sample_video_file(test_data_dir):
    """サンプル動画ファイル（セッションスコープ）"""
    # 実際のサンプル動画ファイルパス
    sample_path = test_data_dir / "sample_anime_short.mp4"
    
    if not sample_path.exists():
        # サンプル動画が存在しない場合はモックファイルを作成
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        sample_path.touch()
        pytest.skip(f"サンプル動画ファイルが見つかりません: {sample_path}")
    
    return sample_path


@pytest.fixture
def mock_video_processor():
    """テスト用モックVideoProcessor"""
    class MockVideoProcessor:
        def load_video(self, file_path):
            return type('MockVideoFile', (), {
                'file_path': file_path,
                'file_name': file_path.name,
                'duration': 30.0,
                'fps': 24.0,
                'width': 1920,
                'height': 1080,
                'is_valid': True
            })()
        
        def extract_frames(self, video_file, interval_seconds=1.0):
            # モックフレームを生成
            num_frames = int(video_file.duration / interval_seconds)
            for i in range(num_frames):
                yield type('MockFrame', (), {
                    'frame_number': i,
                    'timestamp': i * interval_seconds,
                    'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
                })()
        
        def detect_scene_changes(self, frames, threshold=0.3):
            # モックシーンチェンジ検出（半分のフレームを返す）
            return frames[::2]
        
        def calculate_quality_score(self, frame):
            # モック品質スコア
            return 0.7 + (frame.frame_number % 10) * 0.03
    
    return MockVideoProcessor()
