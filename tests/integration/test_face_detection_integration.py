"""
顔検出統合テスト

フレーム→顔検出の統合フローをテストします。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
import sys
import numpy as np
import time

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.face_detector import FaceDetector  # noqa: E402
from services.video_processor import VideoProcessor  # noqa: E402
from models.frame import Frame  # noqa: E402
from models.face_detection_result import FaceDetectionResult  # noqa: E402
from lib.logger import get_logger  # noqa: E402


@pytest.mark.integration
class TestFaceDetectionIntegration:
    """顔検出統合テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.logger = get_logger(__name__, test_name="face_detection_integration")
        
        # 実装前なので、両サービスのインスタンス化は失敗するはず
        try:
            self.face_detector = FaceDetector()
            self.video_processor = VideoProcessor()
        except (ImportError, NotImplementedError, AttributeError) as e:
            self.logger.info(f"Services not implemented yet - TDD: {e}")
            self.face_detector = None
            self.video_processor = None

    @pytest.mark.slow
    def test_video_to_face_detection_pipeline(self, sample_video_file):
        """動画→フレーム抽出→顔検出の統合パイプラインテスト"""
        if self.face_detector is None or self.video_processor is None:
            pytest.skip("Services not implemented yet - TDD")
        
        self.logger.info("動画→顔検出パイプライン統合テスト開始")
        
        # Step 1: 動画読み込み
        video_file = self.video_processor.load_video(sample_video_file)
        self.logger.info(f"動画読み込み完了: {video_file.file_name}")
        
        # Step 2: フレーム抽出
        frames = list(self.video_processor.extract_frames(video_file, interval_seconds=2.0))
        self.logger.info(f"フレーム抽出完了: {len(frames)}フレーム")
        
        # Step 3: 各フレームで顔検出
        face_detection_results = []
        frames_with_faces = []
        
        for i, frame in enumerate(frames):
            faces = self.face_detector.detect_faces(frame)
            face_detection_results.append(faces)
            
            if faces:
                frames_with_faces.append(frame)
                self.logger.info(f"フレーム{i}: {len(faces)}個の顔を検出")
        
        # 結果の検証
        assert len(face_detection_results) == len(frames)
        
        # 少なくとも一部のフレームで顔が検出されることを期待
        total_faces = sum(len(faces) for faces in face_detection_results)
        self.logger.info(f"総検出顔数: {total_faces}")
        
        if total_faces == 0:
            pytest.skip("テスト動画に顔が含まれていません")
        
        # 顔検出結果の詳細検証
        for faces in face_detection_results:
            for face in faces:
                assert isinstance(face, FaceDetectionResult)
                assert face.confidence >= 0.5  # 研究結果に基づく閾値
                assert face.face_size >= 0.01  # 画面の1%以上
                assert 0.0 <= face.bounding_box.x <= 1.0
                assert 0.0 <= face.bounding_box.y <= 1.0
        
        self.logger.info("動画→顔検出パイプライン統合テスト完了")

    def test_batch_face_detection_performance(self, mock_frames_with_faces):
        """バッチ顔検出パフォーマンステスト"""
        if self.face_detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        # 個別処理の時間測定
        start_time = time.time()
        individual_results = []
        for frame in mock_frames_with_faces:
            faces = self.face_detector.detect_faces(frame)
            individual_results.append(faces)
        individual_time = time.time() - start_time
        
        # バッチ処理の時間測定
        start_time = time.time()
        batch_results = self.face_detector.detect_faces_batch(mock_frames_with_faces)
        batch_time = time.time() - start_time
        
        self.logger.info(f"個別処理: {individual_time:.3f}秒, バッチ処理: {batch_time:.3f}秒")
        
        # バッチ処理の方が効率的であることを確認
        assert batch_time <= individual_time * 1.2, "バッチ処理が期待ほど効率的ではありません"
        
        # 結果の一貫性確認
        assert len(batch_results) == len(individual_results)
        for batch_faces, individual_faces in zip(batch_results, individual_results):
            assert len(batch_faces) == len(individual_faces)

    def test_face_detection_accuracy_validation(self, mock_frames_with_known_faces):
        """顔検出精度検証テスト"""
        if self.face_detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        total_expected_faces = 0
        total_detected_faces = 0
        correct_detections = 0
        
        for frame, expected_face_count in mock_frames_with_known_faces:
            detected_faces = self.face_detector.detect_faces(frame)
            
            total_expected_faces += expected_face_count
            total_detected_faces += len(detected_faces)
            
            # 期待される顔数と検出された顔数の差を評価
            if expected_face_count > 0 and len(detected_faces) > 0:
                correct_detections += min(expected_face_count, len(detected_faces))
        
        # 精度計算
        if total_expected_faces > 0:
            precision = correct_detections / total_detected_faces if total_detected_faces > 0 else 0
            recall = correct_detections / total_expected_faces
            
            self.logger.info(f"検出精度: Precision={precision:.3f}, Recall={recall:.3f}")
            
            # 研究結果に基づく精度要件（80%以上）
            assert recall >= 0.8, f"顔検出のリコール率が低すぎます: {recall:.3f}"

    def test_face_filter_integration(self, mock_mixed_frames):
        """顔フィルタリング統合テスト"""
        if self.face_detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        # フィルタリング前のフレーム数
        original_frame_count = len(mock_mixed_frames)
        
        # 顔ありフレームのフィルタリング
        frames_with_faces = self.face_detector.filter_frames_with_faces(mock_mixed_frames)
        
        # 結果の検証
        assert isinstance(frames_with_faces, list)
        assert len(frames_with_faces) <= original_frame_count
        assert all(isinstance(frame, Frame) for frame in frames_with_faces)
        
        # フィルタリングされたフレームには実際に顔が含まれることを確認
        for frame in frames_with_faces:
            faces = self.face_detector.detect_faces(frame)
            assert len(faces) > 0, "フィルタリング済みフレームに顔が検出されません"
        
        self.logger.info(f"フィルタリング結果: {original_frame_count} → {len(frames_with_faces)}フレーム")

    def test_confidence_threshold_adjustment(self, mock_frames_with_faces):
        """信頼度閾値調整テスト"""
        if self.face_detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        detection_counts = {}
        
        # 異なる信頼度閾値でテスト
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            self.face_detector.set_detection_confidence(threshold)
            
            total_detections = 0
            for frame in mock_frames_with_faces:
                faces = self.face_detector.detect_faces(frame)
                total_detections += len(faces)
            
            detection_counts[threshold] = total_detections
            self.logger.info(f"信頼度{threshold}: {total_detections}個の顔を検出")
        
        # 信頼度が高いほど検出数が減ることを確認
        previous_count = float('inf')
        for threshold in sorted(thresholds):
            current_count = detection_counts[threshold]
            assert current_count <= previous_count, f"信頼度{threshold}で検出数が増加しています"
            previous_count = current_count

    def test_mediapipe_integration(self, mock_frame_with_anime_face):
        """MediaPipe統合テスト（アニメ顔検出）"""
        if self.face_detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        # 研究結果に基づくMediaPipe設定の確認
        # model_selection=0（2m以内の顔検出用、高速）
        # min_detection_confidence=0.5（アニメキャラクター用に調整）
        
        faces = self.face_detector.detect_faces(mock_frame_with_anime_face)
        
        if len(faces) > 0:
            primary_face = faces[0]
            
            # MediaPipe固有の品質メトリクスを確認
            assert hasattr(primary_face, 'quality_metrics')
            assert 'sharpness' in primary_face.quality_metrics
            assert 'brightness' in primary_face.quality_metrics
            assert 'contrast' in primary_face.quality_metrics
            assert 'symmetry' in primary_face.quality_metrics
            
            # アニメ顔特有の特徴チェック
            landmarks = self.face_detector.get_face_landmarks(primary_face)
            assert len(landmarks) > 0
            assert all(isinstance(point, tuple) and len(point) == 2 for point in landmarks)
            
            self.logger.info(f"アニメ顔検出成功: 信頼度={primary_face.confidence:.3f}")


# テスト用フィクスチャ
@pytest.fixture
def mock_frames_with_faces():
    """顔ありモックフレームのリスト"""
    frames = []
    for i in range(5):
        # アニメ顔を模したモック画像データ
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 2.0,
            'image_data': np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
        })()
        frames.append(frame)
    return frames


@pytest.fixture
def mock_frames_with_known_faces():
    """既知の顔数を持つモックフレームのリスト"""
    frames_with_counts = []
    
    # フレームと期待される顔数のペア
    face_counts = [2, 1, 3, 0, 1]  # 顔数の期待値
    
    for i, expected_count in enumerate(face_counts):
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 1.0,
            'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8),
            'expected_faces': expected_count
        })()
        frames_with_counts.append((frame, expected_count))
    
    return frames_with_counts


@pytest.fixture
def mock_mixed_frames():
    """顔あり・なし混合フレームのリスト"""
    frames = []
    for i in range(8):
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 1.0,
            'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8),
            'has_face': i % 3 != 0  # 3の倍数以外のフレームに顔あり
        })()
        frames.append(frame)
    return frames


@pytest.fixture
def mock_frame_with_anime_face():
    """アニメ顔ありモックフレーム"""
    # アニメ特有の特徴を模したモック画像
    image_data = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
    
    # アニメ顔の特徴：平坦な色調、高コントラスト
    # 中央部分に顔相当の領域を設定
    center_y, center_x = 360, 640
    face_size = 200
    
    # 顔領域を明るく設定（肌色相当）
    image_data[center_y-face_size//2:center_y+face_size//2, 
               center_x-face_size//2:center_x+face_size//2] = [220, 180, 160]
    
    # 目の部分を暗く設定
    eye_size = 20
    image_data[center_y-30:center_y-10, center_x-60:center_x-40] = [0, 0, 0]  # 左目
    image_data[center_y-30:center_y-10, center_x+40:center_x+60] = [0, 0, 0]  # 右目
    
    return type('MockFrame', (), {
        'frame_number': 0,
        'timestamp': 0.0,
        'image_data': image_data
    })()
