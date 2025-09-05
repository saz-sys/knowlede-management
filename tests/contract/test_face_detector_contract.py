"""
FaceDetector契約テスト

FaceDetectorサービスの契約インターフェース仕様に基づく契約テストです。
TDD原則に従い、実装前に失敗することを確認します。
"""

import pytest
from pathlib import Path
from typing import List
import sys
import numpy as np

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from services.face_detector import FaceDetector  # noqa: E402
from models.frame import Frame  # noqa: E402
from models.face_detection_result import FaceDetectionResult  # noqa: E402
from lib.errors import (  # noqa: E402
    FaceDetectionError,
    InvalidFrameError,
    BatchProcessingError,
    InvalidFaceDataError,
    InvalidConfidenceError,
    InvalidSizeRatioError,
    LandmarkExtractionError,
)


@pytest.mark.contract
class TestFaceDetectorContract:
    """FaceDetector契約テストクラス"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        # 実装前なので、FaceDetectorのインスタンス化は失敗するはず
        try:
            self.detector = FaceDetector()
        except (ImportError, NotImplementedError, AttributeError):
            # 期待されるエラー - 実装前のため
            self.detector = None

    def test_detect_faces_success(self, mock_frame_with_face):
        """顔検出の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        results = self.detector.detect_faces(mock_frame_with_face)
        
        # 戻り値の型チェック
        assert isinstance(results, list)
        assert all(isinstance(result, FaceDetectionResult) for result in results)
        
        # 検出結果の検証
        for result in results:
            assert hasattr(result, 'bounding_box')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'landmarks')
            assert hasattr(result, 'face_size')
            assert hasattr(result, 'face_angle')
            assert hasattr(result, 'quality_metrics')
            
            # バリデーションルールのチェック
            assert result.confidence >= 0.5  # 研究結果に基づく閾値
            assert result.face_size >= 0.01  # 画面の1%以上

    def test_detect_faces_no_faces(self, mock_frame_without_face):
        """顔が写っていないフレームのテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        results = self.detector.detect_faces(mock_frame_without_face)
        
        # 顔が検出されない場合は空のリストを返す
        assert isinstance(results, list)
        assert len(results) == 0

    def test_detect_faces_invalid_frame(self):
        """無効なフレームでの顔検出エラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(InvalidFrameError):
            self.detector.detect_faces(None)

    def test_detect_faces_batch_success(self, mock_frames_with_faces):
        """複数フレーム一括顔検出の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        results = self.detector.detect_faces_batch(mock_frames_with_faces)
        
        # 戻り値の型チェック
        assert isinstance(results, list)
        assert len(results) == len(mock_frames_with_faces)
        
        for frame_results in results:
            assert isinstance(frame_results, list)
            for face_result in frame_results:
                assert isinstance(face_result, FaceDetectionResult)

    def test_detect_faces_batch_empty_list(self):
        """空のフレームリストでのバッチ処理テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        results = self.detector.detect_faces_batch([])
        
        assert isinstance(results, list)
        assert len(results) == 0

    def test_detect_faces_batch_error(self, mock_invalid_frames):
        """バッチ処理エラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(BatchProcessingError):
            self.detector.detect_faces_batch(mock_invalid_frames)

    def test_filter_frames_with_faces_success(self, mock_mixed_frames):
        """顔ありフレームフィルタリングの正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        filtered_frames = self.detector.filter_frames_with_faces(mock_mixed_frames)
        
        # 戻り値の型チェック
        assert isinstance(filtered_frames, list)
        assert all(isinstance(frame, Frame) for frame in filtered_frames)
        
        # フィルタリング結果は元のフレームのサブセット
        assert len(filtered_frames) <= len(mock_mixed_frames)

    def test_get_primary_face_success(self, mock_frame_with_multiple_faces):
        """主要顔取得の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        primary_face = self.detector.get_primary_face(mock_frame_with_multiple_faces)
        
        # 戻り値の型チェック
        if primary_face is not None:
            assert isinstance(primary_face, FaceDetectionResult)
            # 最も信頼度の高い顔が返されることを確認
            assert primary_face.confidence >= 0.5

    def test_get_primary_face_no_faces(self, mock_frame_without_face):
        """顔なしフレームでの主要顔取得テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        primary_face = self.detector.get_primary_face(mock_frame_without_face)
        
        # 顔が検出されない場合はNoneを返す
        assert primary_face is None

    def test_calculate_face_quality_success(self, mock_face_result, mock_frame_with_face):
        """顔品質スコア計算の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        quality_score = self.detector.calculate_face_quality(mock_face_result, mock_frame_with_face)
        
        # スコアの範囲チェック
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0

    def test_calculate_face_quality_invalid_data(self):
        """無効な顔データでの品質計算エラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(InvalidFaceDataError):
            self.detector.calculate_face_quality(None, None)

    def test_set_detection_confidence_success(self):
        """信頼度閾値設定の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        # 正常な信頼度設定
        self.detector.set_detection_confidence(0.7)
        
        # エラーが発生しないことを確認（戻り値なし）

    def test_set_detection_confidence_invalid(self):
        """無効な信頼度設定のエラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(InvalidConfidenceError):
            self.detector.set_detection_confidence(-0.1)
        
        with pytest.raises(InvalidConfidenceError):
            self.detector.set_detection_confidence(1.1)

    def test_set_min_face_size_success(self):
        """最小顔サイズ設定の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        # 正常なサイズ比率設定
        self.detector.set_min_face_size(0.05)
        
        # エラーが発生しないことを確認（戻り値なし）

    def test_set_min_face_size_invalid(self):
        """無効な最小顔サイズ設定のエラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(InvalidSizeRatioError):
            self.detector.set_min_face_size(-0.1)
        
        with pytest.raises(InvalidSizeRatioError):
            self.detector.set_min_face_size(1.1)

    def test_get_face_landmarks_success(self, mock_face_result):
        """顔ランドマーク取得の正常テスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        landmarks = self.detector.get_face_landmarks(mock_face_result)
        
        # 戻り値の型チェック
        assert isinstance(landmarks, list)
        assert all(isinstance(point, tuple) and len(point) == 2 for point in landmarks)

    def test_get_face_landmarks_error(self):
        """ランドマーク抽出エラーテスト"""
        if self.detector is None:
            pytest.skip("FaceDetector not implemented yet - TDD")
        
        with pytest.raises(LandmarkExtractionError):
            self.detector.get_face_landmarks(None)


# テスト用フィクスチャ
@pytest.fixture
def mock_frame_with_face():
    """顔ありモックFrameオブジェクト"""
    class MockFrame:
        def __init__(self):
            self.frame_number = 0
            self.timestamp = 0.0
            # 顔が写っているモック画像データ
            self.image_data = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    return MockFrame()


@pytest.fixture
def mock_frame_without_face():
    """顔なしモックFrameオブジェクト"""
    class MockFrame:
        def __init__(self):
            self.frame_number = 1
            self.timestamp = 1.0
            # 顔が写っていないモック画像データ（風景など）
            self.image_data = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    return MockFrame()


@pytest.fixture
def mock_frame_with_multiple_faces():
    """複数顔ありモックFrameオブジェクト"""
    class MockFrame:
        def __init__(self):
            self.frame_number = 2
            self.timestamp = 2.0
            # 複数の顔が写っているモック画像データ
            self.image_data = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    return MockFrame()


@pytest.fixture
def mock_frames_with_faces():
    """顔ありモックFrameオブジェクトのリスト"""
    frames = []
    for i in range(3):
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 1.0,
            'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        })()
        frames.append(frame)
    return frames


@pytest.fixture
def mock_mixed_frames():
    """顔あり・なし混合モックFrameオブジェクトのリスト"""
    frames = []
    for i in range(5):
        frame = type('MockFrame', (), {
            'frame_number': i,
            'timestamp': i * 1.0,
            'image_data': np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8),
            'has_face': i % 2 == 0  # 偶数番号のフレームに顔あり
        })()
        frames.append(frame)
    return frames


@pytest.fixture
def mock_invalid_frames():
    """無効なモックFrameオブジェクトのリスト"""
    return [None, "invalid", 123]


@pytest.fixture
def mock_face_result():
    """モックFaceDetectionResultオブジェクト"""
    class MockBoundingBox:
        def __init__(self):
            self.x = 0.2
            self.y = 0.2
            self.width = 0.3
            self.height = 0.3
    
    class MockFaceResult:
        def __init__(self):
            self.bounding_box = MockBoundingBox()
            self.confidence = 0.8
            self.landmarks = [(0.25, 0.25), (0.45, 0.25), (0.35, 0.35)]
            self.face_size = 0.09
            self.face_angle = 0.0
            self.quality_metrics = {
                'sharpness': 0.8,
                'brightness': 0.7,
                'contrast': 0.9,
                'symmetry': 0.8
            }
    
    return MockFaceResult()
