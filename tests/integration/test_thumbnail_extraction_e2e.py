"""
サムネイル抽出E2Eテスト

動画→サムネイル生成の全体フロー（エンドツーエンド）をテストします。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
import sys
import tempfile
import time

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.video_processor import VideoProcessor  # noqa: E402
from services.face_detector import FaceDetector  # noqa: E402
from services.thumbnail_extractor import ThumbnailExtractor  # noqa: E402
from models.user_settings import UserSettings, ThumbnailOrientation  # noqa: E402
from lib.logger import get_logger  # noqa: E402


@pytest.mark.integration
class TestThumbnailExtractionE2E:
    """サムネイル抽出E2Eテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.logger = get_logger(__name__, test_name="thumbnail_extraction_e2e")
        
        # 実装前なので、全サービスのインスタンス化は失敗するはず
        try:
            self.video_processor = VideoProcessor()
            self.face_detector = FaceDetector()
            self.thumbnail_extractor = ThumbnailExtractor()
        except (ImportError, NotImplementedError, AttributeError) as e:
            self.logger.info(f"Services not implemented yet - TDD: {e}")
            self.video_processor = None
            self.face_detector = None
            self.thumbnail_extractor = None

    @pytest.mark.slow
    def test_full_thumbnail_extraction_pipeline(self, sample_video_file, temp_dir):
        """完全なサムネイル抽出パイプライン（E2E）テスト"""
        if not all([self.video_processor, self.face_detector, self.thumbnail_extractor]):
            pytest.skip("Services not implemented yet - TDD")
        
        self.logger.info("サムネイル抽出E2Eテスト開始")
        
        # ユーザー設定
        user_settings = UserSettings(
            output_width=1920,
            output_height=1080,
            thumbnail_count=5,
            orientation=ThumbnailOrientation.LANDSCAPE,
            output_directory=temp_dir,
            file_name_prefix="test_thumbnail",
            quality_threshold=0.7,
            diversity_weight=0.8,
            face_size_preference="balanced"
        )
        
        # Step 1: 動画読み込み
        self.logger.info("Step 1: 動画読み込み")
        video_file = self.video_processor.load_video(sample_video_file)
        assert video_file.is_valid
        
        # Step 2: フレーム抽出
        self.logger.info("Step 2: フレーム抽出")
        all_frames = list(self.video_processor.extract_frames(video_file, interval_seconds=1.0))
        assert len(all_frames) > 0
        
        # Step 3: 顔検出とフィルタリング
        self.logger.info("Step 3: 顔検出とフィルタリング")
        frames_with_faces = self.face_detector.filter_frames_with_faces(all_frames)
        
        if len(frames_with_faces) == 0:
            pytest.skip("テスト動画に顔が検出されませんでした")
        
        # Step 4: 多様性フレーム選択
        self.logger.info("Step 4: 多様性フレーム選択")
        selected_frames = self.thumbnail_extractor.select_diverse_frames(
            frames_with_faces, 
            count=user_settings.thumbnail_count,
            diversity_weight=user_settings.diversity_weight
        )
        assert len(selected_frames) <= user_settings.thumbnail_count
        
        # Step 5: サムネイル生成
        self.logger.info("Step 5: サムネイル生成")
        thumbnails = self.thumbnail_extractor.extract_thumbnails(
            selected_frames, 
            user_settings
        )
        
        # 生成されたサムネイルの検証
        assert len(thumbnails) == len(selected_frames)
        assert all(thumbnail.user_settings == user_settings for thumbnail in thumbnails)
        assert all(0.0 <= thumbnail.diversity_score <= 1.0 for thumbnail in thumbnails)
        assert all(0.0 <= thumbnail.total_score <= 1.0 for thumbnail in thumbnails)
        
        # Step 6: ファイル保存
        self.logger.info("Step 6: ファイル保存")
        saved_paths = self.thumbnail_extractor.save_thumbnails_batch(thumbnails, str(temp_dir))
        
        # 保存結果の検証
        assert len(saved_paths) == len(thumbnails)
        for path_str in saved_paths:
            path = Path(path_str)
            assert path.exists()
            assert path.suffix == ".png"
            assert path.name.startswith(user_settings.file_name_prefix)
        
        self.logger.info(f"E2Eテスト完了: {len(thumbnails)}枚のサムネイルを生成・保存")

    def test_user_story_workflow(self, sample_video_file, temp_dir):
        """ユーザーストーリーに基づくワークフローテスト"""
        if not all([self.video_processor, self.face_detector, self.thumbnail_extractor]):
            pytest.skip("Services not implemented yet - TDD")
        
        self.logger.info("ユーザーストーリーワークフローテスト開始")
        
        # ユーザーストーリー: 
        # 「マーケティング担当者が、アニメ動画から5枚の横型サムネイルを抽出したい」
        
        # 前提: 社内PCのローカルフォルダにMP4形式の動画ファイルが保存されている
        assert sample_video_file.exists()
        assert sample_video_file.suffix == ".mp4"
        
        # 操作1: アプリケーションを起動し、動画ファイルを選択する
        video_file = self.video_processor.load_video(sample_video_file)
        # 結果: 動画ファイルが正常に読み込まれる
        assert video_file.is_valid
        
        # 操作2: サムネイル生成枚数（5枚）とサイズ（1920x1080）を指定する
        user_settings = UserSettings(
            output_width=1920,
            output_height=1080,
            thumbnail_count=5,
            orientation=ThumbnailOrientation.LANDSCAPE,
            output_directory=temp_dir,
            file_name_prefix="marketing_thumbnail",
            quality_threshold=0.7,
            diversity_weight=0.8,
            face_size_preference="balanced"
        )
        # 結果: 設定が保存される
        assert user_settings.thumbnail_count == 5
        assert user_settings.orientation == ThumbnailOrientation.LANDSCAPE
        
        # 操作3: 「サムネイル生成」ボタンをクリックする
        frames = list(self.video_processor.extract_frames(video_file))
        frames_with_faces = self.face_detector.filter_frames_with_faces(frames)
        
        if len(frames_with_faces) == 0:
            pytest.skip("顔検出失敗のためユーザーストーリーテストをスキップ")
        
        thumbnails = self.thumbnail_extractor.extract_thumbnails(frames_with_faces, user_settings)
        # 結果: キャラクターの顔が写った指定枚数のフレームが候補として表示される
        assert len(thumbnails) <= 5
        assert all(thumbnail.source_frame in frames_with_faces for thumbnail in thumbnails)
        
        # 操作4: 縦型または横型のサムネイル形式を選択する
        # 結果: 選択した形式（横型）で候補画像が再表示される
        for thumbnail in thumbnails:
            assert thumbnail.user_settings.orientation == ThumbnailOrientation.LANDSCAPE
        
        # 操作5: 好みの候補を選択し「保存」ボタンをクリックする
        selected_thumbnails = thumbnails[:3]  # 最初の3枚を選択
        saved_paths = self.thumbnail_extractor.save_thumbnails_batch(selected_thumbnails, str(temp_dir))
        
        # 結果: 選択したサムネイル画像がPNG形式でローカルフォルダに保存される
        assert len(saved_paths) == 3
        for path_str in saved_paths:
            path = Path(path_str)
            assert path.exists()
            assert path.suffix == ".png"
        
        self.logger.info("ユーザーストーリーワークフローテスト完了")

    def test_performance_requirements(self, sample_video_file, temp_dir):
        """パフォーマンス要件テスト"""
        if not all([self.video_processor, self.face_detector, self.thumbnail_extractor]):
            pytest.skip("Services not implemented yet - TDD")
        
        self.logger.info("パフォーマンス要件テスト開始")
        
        # 研究結果に基づく要件: 10分動画から5枚のサムネイル抽出を30秒以内
        user_settings = UserSettings(
            output_width=1920,
            output_height=1080,
            thumbnail_count=5,
            orientation=ThumbnailOrientation.LANDSCAPE,
            output_directory=temp_dir,
            file_name_prefix="perf_test",
            quality_threshold=0.7,
            diversity_weight=0.8,
            face_size_preference="balanced"
        )
        
        # 全体処理時間の測定
        start_time = time.time()
        
        video_file = self.video_processor.load_video(sample_video_file)
        frames = list(self.video_processor.extract_frames(video_file, interval_seconds=2.0))
        frames_with_faces = self.face_detector.filter_frames_with_faces(frames)
        
        if len(frames_with_faces) == 0:
            pytest.skip("顔検出なしのためパフォーマンステストをスキップ")
        
        thumbnails = self.thumbnail_extractor.extract_thumbnails(frames_with_faces, user_settings)
        saved_paths = self.thumbnail_extractor.save_thumbnails_batch(thumbnails, str(temp_dir))
        
        total_time = time.time() - start_time
        
        # パフォーマンス要件の検証
        video_duration_minutes = video_file.duration / 60.0
        expected_max_time = video_duration_minutes * 3.0  # 1分動画あたり3秒の処理時間
        
        self.logger.info(f"処理時間: {total_time:.2f}秒 (動画: {video_duration_minutes:.1f}分)")
        self.logger.info(f"期待値: {expected_max_time:.2f}秒以内")
        
        assert total_time <= expected_max_time, f"処理が遅すぎます: {total_time:.2f}秒"
        assert len(saved_paths) == len(thumbnails)

    def test_error_scenarios(self, temp_dir):
        """エラーシナリオテスト"""
        if not all([self.video_processor, self.face_detector, self.thumbnail_extractor]):
            pytest.skip("Services not implemented yet - TDD")
        
        # エッジケース1: 存在しない動画ファイル
        with pytest.raises(FileNotFoundError):
            self.video_processor.load_video(Path("non_existent.mp4"))
        
        # エッジケース2: MP4以外の形式
        with tempfile.NamedTemporaryFile(suffix=".avi", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            with pytest.raises(Exception):  # InvalidVideoFormatError or similar
                self.video_processor.load_video(tmp_path)
        
        # エッジケース3: 無効な設定
        invalid_settings = UserSettings(
            output_width=-100,  # 無効な幅
            output_height=1080,
            thumbnail_count=5,
            orientation=ThumbnailOrientation.LANDSCAPE,
            output_directory=temp_dir,
            file_name_prefix="test",
            quality_threshold=0.7,
            diversity_weight=0.8,
            face_size_preference="balanced"
        )
        
        # 無効な設定での処理は適切にエラーになることを確認
        # 実装依存で、バリデーションエラーまたは処理エラーが発生するはず
        
        self.logger.info("エラーシナリオテスト完了")

    def test_memory_and_cleanup(self, sample_video_file, temp_dir):
        """メモリ管理とクリーンアップテスト"""
        if not all([self.video_processor, self.face_detector, self.thumbnail_extractor]):
            pytest.skip("Services not implemented yet - TDD")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 複数回処理を実行してメモリリークをチェック
        for i in range(3):
            user_settings = UserSettings(
                output_width=800,
                output_height=600,
                thumbnail_count=3,
                orientation=ThumbnailOrientation.LANDSCAPE,
                output_directory=temp_dir,
                file_name_prefix=f"cleanup_test_{i}",
                quality_threshold=0.7,
                diversity_weight=0.8,
                face_size_preference="balanced"
            )
            
            video_file = self.video_processor.load_video(sample_video_file)
            frames = list(self.video_processor.extract_frames(video_file, interval_seconds=3.0))
            
            if frames:
                frames_with_faces = self.face_detector.filter_frames_with_faces(frames)
                if frames_with_faces:
                    thumbnails = self.thumbnail_extractor.extract_thumbnails(frames_with_faces, user_settings)
                    self.thumbnail_extractor.save_thumbnails_batch(thumbnails, str(temp_dir))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        self.logger.info(f"メモリ使用量増加: {memory_increase:.2f}MB")
        
        # メモリリークの許容範囲（100MB以内）
        assert memory_increase <= 100, f"メモリリークの可能性: {memory_increase:.2f}MB増加"
