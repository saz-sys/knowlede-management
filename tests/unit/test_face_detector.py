"""
FaceDetectorのユニットテスト

顔検出サービスの各機能をテストします。
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import mediapipe as mp

from src.services.face_detector import FaceDetector
from src.models.frame import Frame
from src.models.face_detection_result import FaceDetectionResult
from src.models.bounding_box import BoundingBox
from src.models.point_2d import Point2D
from src.lib.errors import (
    FaceDetectionError,
    NoFacesDetectedError,
    InvalidFrameError,
    BatchProcessingError,
    InvalidFaceDataError,
    InvalidConfidenceError,
    InvalidSizeRatioError,
    LandmarkExtractionError
)


class TestFaceDetector:
    """FaceDetectorのテストクラス"""
    
    @pytest.fixture
    def detector(self):
        """FaceDetectorのインスタンスを作成"""
        return FaceDetector(detection_confidence=0.5, min_face_size=0.01)
    
    @pytest.fixture
    def sample_frame(self):
        """サンプルフレームデータ"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    @pytest.fixture
    def sample_frame_obj(self, sample_frame):
        """サンプルFrameオブジェクト"""
        return Frame(
            frame_data=sample_frame,
            timestamp_seconds=1.0,
            frame_index=30
        )
    
    @pytest.fixture
    def mock_detection_result(self):
        """モックの検出結果"""
        mock_detection = Mock()
        mock_detection.location_data.relative_bounding_box.xmin = 0.2
        mock_detection.location_data.relative_bounding_box.ymin = 0.3
        mock_detection.location_data.relative_bounding_box.width = 0.4
        mock_detection.location_data.relative_bounding_box.height = 0.5
        mock_detection.score = [0.8]
        return mock_detection

    def test_init_default_values(self):
        """デフォルト値での初期化テスト"""
        detector = FaceDetector()
        
        assert detector.detection_confidence == 0.5
        assert detector.min_face_size == 0.01
        assert detector.mp_face_detection is not None
        assert detector.logger is not None

    def test_init_custom_values(self):
        """カスタム値での初期化テスト"""
        detector = FaceDetector(detection_confidence=0.7, min_face_size=0.05)
        
        assert detector.detection_confidence == 0.7
        assert detector.min_face_size == 0.05

    def test_init_invalid_confidence(self):
        """無効な信頼度での初期化テスト"""
        with pytest.raises(InvalidConfidenceError):
            FaceDetector(detection_confidence=-0.1)
        
        with pytest.raises(InvalidConfidenceError):
            FaceDetector(detection_confidence=1.1)

    def test_init_invalid_min_face_size(self):
        """無効な最小顔サイズでの初期化テスト"""
        with pytest.raises(InvalidSizeRatioError):
            FaceDetector(min_face_size=-0.1)
        
        with pytest.raises(InvalidSizeRatioError):
            FaceDetector(min_face_size=1.1)

    @patch('mediapipe.solutions.face_detection.FaceDetection')
    def test_detect_faces_success(self, mock_face_detection_class, detector, sample_frame, mock_detection_result):
        """顔検出成功のテスト"""
        # モック設定
        mock_detector = Mock()
        mock_result = Mock()
        mock_result.detections = [mock_detection_result]
        mock_detector.process.return_value = mock_result
        mock_face_detection_class.return_value.__enter__.return_value = mock_detector
        
        # 実行
        results = detector.detect_faces(sample_frame)
        
        # 検証
        assert len(results) == 1
        assert isinstance(results[0], FaceDetectionResult)
        assert isinstance(results[0].bounding_box, BoundingBox)
        assert results[0].confidence == 0.8

    @patch('mediapipe.solutions.face_detection.FaceDetection')
    def test_detect_faces_no_faces(self, mock_face_detection_class, detector, sample_frame):
        """顔が検出されない場合のテスト"""
        # モック設定（検出結果なし）
        mock_detector = Mock()
        mock_result = Mock()
        mock_result.detections = None
        mock_detector.process.return_value = mock_result
        mock_face_detection_class.return_value.__enter__.return_value = mock_detector
        
        # 実行と検証
        with pytest.raises(NoFacesDetectedError):
            detector.detect_faces(sample_frame)

    def test_detect_faces_invalid_frame(self, detector):
        """無効なフレームでの顔検出テスト"""
        with pytest.raises(InvalidFrameError):
            detector.detect_faces(None)
        
        # 2Dフレーム（3Dである必要がある）
        frame_2d = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        with pytest.raises(InvalidFrameError):
            detector.detect_faces(frame_2d)

    @patch('mediapipe.solutions.face_detection.FaceDetection')
    def test_detect_faces_small_face_filtered(self, mock_face_detection_class, detector, sample_frame):
        """小さすぎる顔がフィルタされるテスト"""
        # 小さい顔の検出結果を作成
        mock_detection = Mock()
        mock_detection.location_data.relative_bounding_box.xmin = 0.4
        mock_detection.location_data.relative_bounding_box.ymin = 0.4
        mock_detection.location_data.relative_bounding_box.width = 0.005  # min_face_size以下
        mock_detection.location_data.relative_bounding_box.height = 0.005
        mock_detection.score = [0.8]
        
        mock_detector = Mock()
        mock_result = Mock()
        mock_result.detections = [mock_detection]
        mock_detector.process.return_value = mock_result
        mock_face_detection_class.return_value.__enter__.return_value = mock_detector
        
        # min_face_size = 0.01なので、0.005の顔は除外される
        with pytest.raises(NoFacesDetectedError):
            detector.detect_faces(sample_frame)

    @patch('mediapipe.solutions.face_detection.FaceDetection')
    def test_batch_detect_faces_success(self, mock_face_detection_class, detector, sample_frame, mock_detection_result):
        """バッチ顔検出成功のテスト"""
        frames = [sample_frame.copy() for _ in range(3)]
        
        # モック設定
        mock_detector = Mock()
        mock_result = Mock()
        mock_result.detections = [mock_detection_result]
        mock_detector.process.return_value = mock_result
        mock_face_detection_class.return_value.__enter__.return_value = mock_detector
        
        # 実行
        results = detector.batch_detect_faces(frames)
        
        # 検証
        assert len(results) == 3
        for result in results:
            assert len(result) == 1
            assert isinstance(result[0], FaceDetectionResult)

    def test_batch_detect_faces_empty_list(self, detector):
        """空のフレームリストでのバッチ検出テスト"""
        with pytest.raises(BatchProcessingError):
            detector.batch_detect_faces([])

    @patch('mediapipe.solutions.face_detection.FaceDetection')
    def test_batch_detect_faces_with_failures(self, mock_face_detection_class, detector, sample_frame):
        """一部失敗を含むバッチ検出テスト"""
        frames = [sample_frame.copy() for _ in range(3)]
        
        # モック設定（2回目の処理で例外）
        mock_detector = Mock()
        mock_detector.process.side_effect = [
            Mock(detections=None),  # 1回目：検出なし
            Exception("Processing error"),  # 2回目：エラー
            Mock(detections=None)   # 3回目：検出なし
        ]
        mock_face_detection_class.return_value.__enter__.return_value = mock_detector
        
        # 実行と検証
        with pytest.raises(BatchProcessingError):
            detector.batch_detect_faces(frames)

    @patch('mediapipe.solutions.face_mesh.FaceMesh')
    def test_extract_landmarks_success(self, mock_face_mesh_class, detector, sample_frame):
        """ランドマーク抽出成功のテスト"""
        # モック設定
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.6
        mock_landmark.z = 0.1
        
        mock_mesh_detector = Mock()
        mock_result = Mock()
        mock_result.multi_face_landmarks = [[mock_landmark]]
        mock_mesh_detector.process.return_value = mock_result
        mock_face_mesh_class.return_value.__enter__.return_value = mock_mesh_detector
        
        # 実行
        landmarks = detector.extract_landmarks(sample_frame)
        
        # 検証
        assert len(landmarks) == 1
        assert isinstance(landmarks[0], Point2D)
        assert landmarks[0].x == 0.5
        assert landmarks[0].y == 0.6

    @patch('mediapipe.solutions.face_mesh.FaceMesh')
    def test_extract_landmarks_no_landmarks(self, mock_face_mesh_class, detector, sample_frame):
        """ランドマークが検出されない場合のテスト"""
        mock_mesh_detector = Mock()
        mock_result = Mock()
        mock_result.multi_face_landmarks = None
        mock_mesh_detector.process.return_value = mock_result
        mock_face_mesh_class.return_value.__enter__.return_value = mock_mesh_detector
        
        with pytest.raises(LandmarkExtractionError):
            detector.extract_landmarks(sample_frame)

    def test_extract_landmarks_invalid_frame(self, detector):
        """無効なフレームでのランドマーク抽出テスト"""
        with pytest.raises(InvalidFrameError):
            detector.extract_landmarks(None)

    def test_calculate_face_quality_high_quality(self, detector):
        """高品質顔の品質評価テスト"""
        # 明確なエッジを持つ高コントラストのフレーム
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        frame[50:150, 50:150] = 255  # 白い正方形
        
        bounding_box = BoundingBox(
            top_left=Point2D(0.25, 0.25),
            bottom_right=Point2D(0.75, 0.75)
        )
        
        quality = detector.calculate_face_quality(frame, bounding_box)
        
        assert isinstance(quality, float)
        assert 0.0 <= quality <= 1.0
        assert quality > 0.5  # 高コントラストなので高品質

    def test_calculate_face_quality_low_quality(self, detector):
        """低品質顔の品質評価テスト"""
        # 低コントラストのフレーム
        frame = np.full((200, 200, 3), 128, dtype=np.uint8)
        
        bounding_box = BoundingBox(
            top_left=Point2D(0.25, 0.25),
            bottom_right=Point2D(0.75, 0.75)
        )
        
        quality = detector.calculate_face_quality(frame, bounding_box)
        
        assert isinstance(quality, float)
        assert 0.0 <= quality <= 1.0
        assert quality < 0.5  # 低コントラストなので低品質

    def test_calculate_face_quality_invalid_input(self, detector):
        """無効な入力での品質評価テスト"""
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        
        with pytest.raises(InvalidFrameError):
            detector.calculate_face_quality(None, Mock())
        
        with pytest.raises(InvalidFaceDataError):
            detector.calculate_face_quality(frame, None)

    def test_filter_overlapping_faces(self, detector):
        """重複する顔のフィルタリングテスト"""
        # 重複する検出結果を作成
        face1 = FaceDetectionResult(
            bounding_box=BoundingBox(
                top_left=Point2D(0.1, 0.1),
                bottom_right=Point2D(0.5, 0.5)
            ),
            confidence=0.8,
            landmarks=[]
        )
        
        face2 = FaceDetectionResult(
            bounding_box=BoundingBox(
                top_left=Point2D(0.15, 0.15),  # face1と重複
                bottom_right=Point2D(0.55, 0.55)
            ),
            confidence=0.6,  # face1より低い信頼度
            landmarks=[]
        )
        
        face3 = FaceDetectionResult(
            bounding_box=BoundingBox(
                top_left=Point2D(0.7, 0.7),  # 重複なし
                bottom_right=Point2D(0.9, 0.9)
            ),
            confidence=0.7,
            landmarks=[]
        )
        
        faces = [face1, face2, face3]
        filtered = detector.filter_overlapping_faces(faces, overlap_threshold=0.3)
        
        # face1とface3が残り、face2は除外される
        assert len(filtered) == 2
        assert face1 in filtered
        assert face3 in filtered
        assert face2 not in filtered

    def test_filter_overlapping_faces_empty_list(self, detector):
        """空リストのフィルタリングテスト"""
        result = detector.filter_overlapping_faces([])
        assert result == []

    def test_update_settings(self, detector):
        """設定更新のテスト"""
        # 新しい設定
        new_confidence = 0.7
        new_min_size = 0.05
        
        detector.update_settings(
            detection_confidence=new_confidence,
            min_face_size=new_min_size
        )
        
        assert detector.detection_confidence == new_confidence
        assert detector.min_face_size == new_min_size

    def test_update_settings_invalid_values(self, detector):
        """無効な値での設定更新テスト"""
        with pytest.raises(InvalidConfidenceError):
            detector.update_settings(detection_confidence=-0.1)
        
        with pytest.raises(InvalidSizeRatioError):
            detector.update_settings(min_face_size=1.1)

    def test_cleanup(self, detector):
        """クリーンアップのテスト"""
        # 実行（エラーが発生しないことを確認）
        detector.cleanup()
        
        # ログに記録されることを確認（実際のログ内容の検証は省略）
        assert True

    def test_get_detection_stats(self, detector):
        """検出統計情報取得のテスト"""
        stats = detector.get_detection_stats()
        
        expected_stats = {
            'detection_confidence': detector.detection_confidence,
            'min_face_size': detector.min_face_size,
            'model_complexity': 'auto',
            'total_processed_frames': 0,
            'total_detected_faces': 0,
            'average_faces_per_frame': 0.0
        }
        
        assert stats == expected_stats


class TestFaceDetectorIntegration:
    """FaceDetectorの統合テスト"""
    
    @pytest.fixture
    def detector(self):
        return FaceDetector(detection_confidence=0.5, min_face_size=0.01)
    
    def test_detect_and_filter_pipeline(self, detector):
        """検出→フィルタリングパイプラインのテスト"""
        # モックを使った完全なパイプライン
        with patch.object(detector, 'detect_faces') as mock_detect, \
             patch.object(detector, 'filter_overlapping_faces') as mock_filter:
            
            # モック設定
            sample_faces = [Mock(spec=FaceDetectionResult) for _ in range(3)]
            filtered_faces = sample_faces[:2]  # 1つフィルタされる
            
            mock_detect.return_value = sample_faces
            mock_filter.return_value = filtered_faces
            
            # パイプライン実行
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            faces = detector.detect_faces(frame)
            filtered = detector.filter_overlapping_faces(faces)
            
            # 検証
            assert faces == sample_faces
            assert filtered == filtered_faces
            mock_detect.assert_called_once_with(frame)
            mock_filter.assert_called_once_with(sample_faces, overlap_threshold=0.3)

    def test_batch_processing_with_quality_assessment(self, detector):
        """バッチ処理と品質評価の統合テスト"""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(3)]
        
        with patch.object(detector, 'batch_detect_faces') as mock_batch, \
             patch.object(detector, 'calculate_face_quality') as mock_quality:
            
            # モック設定
            faces_per_frame = [[Mock(spec=FaceDetectionResult)] for _ in range(3)]
            mock_batch.return_value = faces_per_frame
            mock_quality.return_value = 0.8
            
            # 実行
            batch_results = detector.batch_detect_faces(frames)
            qualities = [detector.calculate_face_quality(frame, Mock()) for frame in frames]
            
            # 検証
            assert len(batch_results) == 3
            assert len(qualities) == 3
            assert all(q == 0.8 for q in qualities)
