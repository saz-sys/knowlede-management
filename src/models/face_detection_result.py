"""
FaceDetectionResult（顔検出結果）データモデル

顔検出の結果を表すクラスです。MediaPipeの検出結果を構造化して保持します。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .bounding_box import BoundingBox
from .point_2d import Point2D


@dataclass
class FaceDetectionResult:
    """顔検出結果を表すクラス"""
    
    bounding_box: BoundingBox                    # 顔の境界ボックス
    confidence: float                            # 検出信頼度
    landmarks: List[Point2D] = field(default_factory=list)  # 顔のランドマーク座標
    face_size: float = 0.0                      # 顔サイズ（画面に占める割合）
    face_angle: float = 0.0                     # 顔の角度（ラジアン）
    quality_metrics: Dict[str, float] = field(default_factory=dict)  # 品質指標
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        # 境界ボックスの型チェック
        if not isinstance(self.bounding_box, BoundingBox):
            raise TypeError("bounding_boxはBoundingBoxインスタンスである必要があります")
        
        # 信頼度のバリデーション（研究結果に基づく閾値）
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidenceは数値である必要があります")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidenceは0-1の範囲である必要があります: {self.confidence}")
        if self.confidence < 0.5:
            raise ValueError(f"信頼度が低すぎます（0.5以上必要）: {self.confidence}")
        
        # 顔サイズのバリデーション
        if not isinstance(self.face_size, (int, float)):
            raise TypeError("face_sizeは数値である必要があります")
        if not (0.0 <= self.face_size <= 1.0):
            raise ValueError(f"face_sizeは0-1の範囲である必要があります: {self.face_size}")
        if self.face_size < 0.01:
            raise ValueError(f"顔サイズが小さすぎます（画面の1%以上必要）: {self.face_size}")
        
        # 顔角度のバリデーション
        if not isinstance(self.face_angle, (int, float)):
            raise TypeError("face_angleは数値である必要があります")
        
        # ランドマークのバリデーション
        if not isinstance(self.landmarks, list):
            raise TypeError("landmarksはリストである必要があります")
        for i, landmark in enumerate(self.landmarks):
            if not isinstance(landmark, Point2D):
                raise TypeError(f"landmarks[{i}]はPoint2Dインスタンスである必要があります")
            if not landmark.is_within_normalized_bounds():
                raise ValueError(f"landmarks[{i}]は正規化座標範囲内である必要があります: {landmark}")
        
        # 品質指標のバリデーション
        if not isinstance(self.quality_metrics, dict):
            raise TypeError("quality_metricsは辞書である必要があります")
        
        valid_metrics = {'sharpness', 'brightness', 'contrast', 'symmetry'}
        for key, value in self.quality_metrics.items():
            if key not in valid_metrics:
                raise ValueError(f"無効な品質指標: {key}. 有効な指標: {valid_metrics}")
            if not isinstance(value, (int, float)):
                raise TypeError(f"品質指標{key}の値は数値である必要があります")
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"品質指標{key}は0-1の範囲である必要があります: {value}")
    
    @property
    def face_center(self) -> Point2D:
        """顔の中心座標"""
        return self.bounding_box.center
    
    @property
    def is_high_quality(self) -> bool:
        """高品質な顔かどうか（複数の品質指標を総合評価）"""
        if not self.quality_metrics:
            return False
        
        # 基本的な品質指標の閾値
        quality_thresholds = {
            'sharpness': 0.6,
            'brightness': 0.4,
            'contrast': 0.5,
            'symmetry': 0.6
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, threshold in quality_thresholds.items():
            if metric in self.quality_metrics:
                value = self.quality_metrics[metric]
                if value >= threshold:
                    total_score += value
                    total_weight += 1.0
        
        if total_weight == 0:
            return False
        
        average_quality = total_score / total_weight
        return average_quality >= 0.7 and self.confidence >= 0.7
    
    @property
    def overall_quality_score(self) -> float:
        """総合品質スコア（0-1）"""
        if not self.quality_metrics:
            return self.confidence
        
        # 各品質指標の重み
        weights = {
            'sharpness': 0.3,
            'brightness': 0.2,
            'contrast': 0.2,
            'symmetry': 0.3
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in self.quality_metrics:
                weighted_sum += self.quality_metrics[metric] * weight
                total_weight += weight
        
        # 品質指標がない場合は信頼度のみ
        if total_weight == 0:
            return self.confidence
        
        # 品質指標と信頼度を組み合わせ
        quality_score = weighted_sum / total_weight
        return (quality_score * 0.7 + self.confidence * 0.3)
    
    @property
    def landmark_count(self) -> int:
        """ランドマーク数"""
        return len(self.landmarks)
    
    @property
    def has_sufficient_landmarks(self) -> bool:
        """十分なランドマークがあるか（MediaPipeは468個のランドマークを提供）"""
        return self.landmark_count >= 5  # 最低限の主要ランドマーク（両目、鼻、口角）
    
    def get_eye_landmarks(self) -> List[Point2D]:
        """目のランドマークを取得（MediaPipe基準）"""
        if len(self.landmarks) < 468:
            # 簡略版：最初の4つを目のランドマークと仮定
            return self.landmarks[:4] if len(self.landmarks) >= 4 else []
        
        # MediaPipeの目のランドマークインデックス（簡略版）
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        eye_landmarks = []
        for idx in left_eye_indices + right_eye_indices:
            if idx < len(self.landmarks):
                eye_landmarks.append(self.landmarks[idx])
        
        return eye_landmarks
    
    def get_mouth_landmarks(self) -> List[Point2D]:
        """口のランドマークを取得（MediaPipe基準）"""
        if len(self.landmarks) < 468:
            # 簡略版：後半の一部を口のランドマークと仮定
            return self.landmarks[-4:] if len(self.landmarks) >= 4 else []
        
        # MediaPipeの口のランドマークインデックス（簡略版）
        mouth_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        
        mouth_landmarks = []
        for idx in mouth_indices:
            if idx < len(self.landmarks):
                mouth_landmarks.append(self.landmarks[idx])
        
        return mouth_landmarks
    
    def calculate_face_symmetry(self) -> float:
        """顔の対称性を計算（0-1、1が完全対称）"""
        if len(self.landmarks) < 10:
            return self.quality_metrics.get('symmetry', 0.5)
        
        # 顔の中心線（垂直）
        face_center_x = self.face_center.x
        
        # 左右対称なランドマークペアを比較
        symmetry_scores = []
        
        for i in range(0, min(len(self.landmarks), 20), 2):
            if i + 1 < len(self.landmarks):
                left_point = self.landmarks[i]
                right_point = self.landmarks[i + 1]
                
                # 中心からの距離の対称性
                left_distance = abs(left_point.x - face_center_x)
                right_distance = abs(right_point.x - face_center_x)
                
                if left_distance + right_distance > 0:
                    symmetry = 1.0 - abs(left_distance - right_distance) / (left_distance + right_distance)
                    symmetry_scores.append(symmetry)
        
        if not symmetry_scores:
            return self.quality_metrics.get('symmetry', 0.5)
        
        return sum(symmetry_scores) / len(symmetry_scores)
    
    def is_frontal_face(self, angle_threshold: float = 0.5) -> bool:
        """正面向きの顔かどうか判定（ラジアン）"""
        return abs(self.face_angle) <= angle_threshold
    
    def distance_from_center(self, image_center: Point2D = None) -> float:
        """画像中心からの距離"""
        if image_center is None:
            image_center = Point2D(0.5, 0.5)  # 正規化座標での中心
        
        return self.face_center.distance_to(image_center)
    
    def to_dict(self) -> Dict:
        """辞書形式でデータを出力"""
        return {
            'bounding_box': {
                'x': self.bounding_box.x,
                'y': self.bounding_box.y,
                'width': self.bounding_box.width,
                'height': self.bounding_box.height
            },
            'confidence': self.confidence,
            'face_size': self.face_size,
            'face_angle': self.face_angle,
            'landmark_count': self.landmark_count,
            'quality_metrics': self.quality_metrics.copy(),
            'overall_quality_score': self.overall_quality_score,
            'is_high_quality': self.is_high_quality,
            'is_frontal_face': self.is_frontal_face()
        }
    
    @classmethod
    def from_mediapipe_detection(
        cls,
        detection_result,
        image_width: int,
        image_height: int,
        landmarks: Optional[List[Point2D]] = None
    ) -> 'FaceDetectionResult':
        """MediaPipe検出結果からFaceDetectionResultを作成"""
        # MediaPipeの検出結果からbounding_boxを抽出
        # 実際の実装では、MediaPipeの具体的なAPIに依存
        
        # プレースホルダー実装（実際のMediaPipe連携時に更新）
        bbox = BoundingBox(x=0.2, y=0.2, width=0.3, height=0.3)
        confidence = 0.8
        face_size = bbox.area
        
        quality_metrics = {
            'sharpness': 0.7,
            'brightness': 0.6,
            'contrast': 0.8,
            'symmetry': 0.7
        }
        
        return cls(
            bounding_box=bbox,
            confidence=confidence,
            landmarks=landmarks or [],
            face_size=face_size,
            face_angle=0.0,
            quality_metrics=quality_metrics
        )
    
    def __str__(self) -> str:
        """文字列表現"""
        return (f"FaceDetectionResult(confidence={self.confidence:.3f}, "
                f"size={self.face_size:.3f}, quality={self.overall_quality_score:.3f})")
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"FaceDetectionResult(bounding_box={self.bounding_box!r}, "
                f"confidence={self.confidence}, landmarks={len(self.landmarks)} points)")
