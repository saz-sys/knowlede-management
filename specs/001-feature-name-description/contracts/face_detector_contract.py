"""
顔検出サービスのAPI契約定義
FaceDetector クラスの公開インターフェース仕様
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Frame, FaceDetectionResult


class FaceDetectorContract(ABC):
    """顔検出サービスの契約インターフェース"""
    
    @abstractmethod
    def detect_faces(self, frame: Frame) -> List[FaceDetectionResult]:
        """
        フレーム内の顔を検出
        
        Args:
            frame: 顔検出対象のフレーム
            
        Returns:
            List[FaceDetectionResult]: 検出された顔のリスト
            
        Raises:
            FaceDetectionError: 顔検出処理に失敗
            InvalidFrameError: フレームデータが無効
        """
        pass
    
    @abstractmethod
    def detect_faces_batch(self, frames: List[Frame]) -> List[List[FaceDetectionResult]]:
        """
        複数フレームの顔を一括検出（効率化のため）
        
        Args:
            frames: 顔検出対象フレームのリスト
            
        Returns:
            List[List[FaceDetectionResult]]: 各フレームの検出結果
            
        Raises:
            FaceDetectionError: 顔検出処理に失敗
            BatchProcessingError: バッチ処理に失敗
        """
        pass
    
    @abstractmethod
    def filter_frames_with_faces(self, frames: List[Frame]) -> List[Frame]:
        """
        顔が検出されたフレームのみを抽出
        
        Args:
            frames: フィルタリング対象フレーム
            
        Returns:
            List[Frame]: 顔が検出されたフレーム
            
        Raises:
            FaceDetectionError: 顔検出処理に失敗
        """
        pass
    
    @abstractmethod
    def get_primary_face(self, frame: Frame) -> Optional[FaceDetectionResult]:
        """
        フレーム内の主要な顔（最も信頼度の高い顔）を取得
        
        Args:
            frame: 対象フレーム
            
        Returns:
            Optional[FaceDetectionResult]: 主要な顔、なければNone
            
        Raises:
            FaceDetectionError: 顔検出処理に失敗
        """
        pass
    
    @abstractmethod
    def calculate_face_quality(self, face_result: FaceDetectionResult, frame: Frame) -> float:
        """
        検出された顔の品質スコアを計算
        
        Args:
            face_result: 品質評価対象の顔検出結果
            frame: 顔が含まれるフレーム
            
        Returns:
            float: 顔品質スコア（0.0-1.0）
            
        Raises:
            InvalidFaceDataError: 顔データが無効
        """
        pass
    
    @abstractmethod
    def set_detection_confidence(self, confidence: float) -> None:
        """
        顔検出の信頼度閾値を設定
        
        Args:
            confidence: 信頼度閾値（0.0-1.0）
            
        Raises:
            InvalidConfidenceError: 信頼度が範囲外
        """
        pass
    
    @abstractmethod
    def set_min_face_size(self, min_size_ratio: float) -> None:
        """
        検出する最小顔サイズを設定（画面に占める割合）
        
        Args:
            min_size_ratio: 最小顔サイズ比率（0.0-1.0）
            
        Raises:
            InvalidSizeRatioError: サイズ比率が範囲外
        """
        pass
    
    @abstractmethod
    def get_face_landmarks(self, face_result: FaceDetectionResult) -> List[tuple]:
        """
        顔のランドマーク座標を取得
        
        Args:
            face_result: ランドマーク取得対象の顔
            
        Returns:
            List[tuple]: ランドマーク座標のリスト
            
        Raises:
            LandmarkExtractionError: ランドマーク抽出に失敗
        """
        pass


# カスタム例外クラス
class FaceDetectionError(Exception):
    """顔検出関連の基底例外"""
    pass


class InvalidFrameError(FaceDetectionError):
    """無効なフレームエラー"""
    pass


class BatchProcessingError(FaceDetectionError):
    """バッチ処理エラー"""
    pass


class InvalidFaceDataError(FaceDetectionError):
    """無効な顔データエラー"""
    pass


class InvalidConfidenceError(FaceDetectionError):
    """無効な信頼度エラー"""
    pass


class InvalidSizeRatioError(FaceDetectionError):
    """無効なサイズ比率エラー"""
    pass


class LandmarkExtractionError(FaceDetectionError):
    """ランドマーク抽出エラー"""
    pass
