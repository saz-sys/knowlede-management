"""
FaceDetector（顔検出）サービス

MediaPipeを使用したアニメキャラクターの顔検出、
バッチ処理、設定調整を行うサービスクラスです。
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Optional
import logging

from ..models.frame import Frame
from ..models.face_detection_result import FaceDetectionResult
from ..models.bounding_box import BoundingBox
from ..models.point_2d import Point2D
from ..lib.errors import (
    FaceDetectionError,
    NoFacesDetectedError,
    InvalidFrameError,
    BatchProcessingError,
    InvalidFaceDataError,
    InvalidConfidenceError,
    InvalidSizeRatioError,
    LandmarkExtractionError
)


class FaceDetector:
    """顔検出サービスクラス（MediaPipe使用）"""
    
    def __init__(self, 
                 detection_confidence: float = 0.5, 
                 min_face_size: float = 0.01):
        """
        FaceDetectorを初期化
        
        Args:
            detection_confidence: 顔検出の信頼度閾値（0.0-1.0）
            min_face_size: 最小顔サイズ（画面に占める割合、0.0-1.0）
        """
        self.logger = logging.getLogger(__name__)
        
        # MediaPipe初期化
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 研究結果に基づく設定
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 2m以内の顔検出用（高速）
            min_detection_confidence=detection_confidence
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=5,  # 最大5個の顔を検出
            refine_landmarks=True,
            min_detection_confidence=detection_confidence
        )
        
        self.detection_confidence = detection_confidence
        self.min_face_size = min_face_size
        
        self.logger.info(f"FaceDetector初期化完了: confidence={detection_confidence}, min_size={min_face_size}")
    
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
        if frame is None or frame.image_data is None:
            raise InvalidFrameError("フレームまたは画像データが無効です")
        
        try:
            # RGB画像に変換（MediaPipeはRGBを期待）
            rgb_image = frame.image_data
            if rgb_image.shape[2] != 3:
                raise InvalidFrameError(f"画像は3チャンネル（RGB）である必要があります: {rgb_image.shape}")
            
            # MediaPipeで顔検出
            detection_results = self.face_detection.process(rgb_image)
            
            faces = []
            if detection_results.detections:
                for detection in detection_results.detections:
                    try:
                        face_result = self._create_face_result_from_detection(
                            detection, frame.width, frame.height, rgb_image
                        )
                        
                        # サイズフィルタリング
                        if face_result.face_size >= self.min_face_size:
                            faces.append(face_result)
                            
                    except Exception as e:
                        self.logger.warning(f"顔検出結果の処理でエラー: {e}")
                        continue
            
            # フレームに顔検出結果を追加
            frame.faces_detected = faces
            
            self.logger.debug(f"顔検出完了: フレーム{frame.frame_number}, {len(faces)}個の顔")
            return faces
            
        except InvalidFrameError:
            raise
        except Exception as e:
            self.logger.error(f"顔検出エラー: {e}")
            raise FaceDetectionError(
                f"顔検出処理中にエラーが発生しました: {e}",
                details={'frame_number': frame.frame_number}
            )
    
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
        if not frames:
            return []
        
        self.logger.info(f"バッチ顔検出開始: {len(frames)}フレーム")
        
        try:
            batch_results = []
            processed_count = 0
            error_count = 0
            
            for frame in frames:
                try:
                    faces = self.detect_faces(frame)
                    batch_results.append(faces)
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"フレーム{frame.frame_number}の顔検出でエラー: {e}")
                    batch_results.append([])  # 空のリストを追加
                    error_count += 1
            
            # エラー率が50%を超える場合はバッチ処理エラーとする
            error_rate = error_count / len(frames)
            if error_rate > 0.5:
                raise BatchProcessingError(
                    f"バッチ処理でエラー率が高すぎます: {error_rate:.2%}",
                    details={
                        'total_frames': len(frames),
                        'processed_frames': processed_count,
                        'error_count': error_count
                    }
                )
            
            self.logger.info(f"バッチ顔検出完了: {processed_count}/{len(frames)}フレーム成功")
            return batch_results
            
        except BatchProcessingError:
            raise
        except Exception as e:
            self.logger.error(f"バッチ顔検出エラー: {e}")
            raise FaceDetectionError(
                f"バッチ顔検出中にエラーが発生しました: {e}",
                details={'batch_size': len(frames)}
            )
    
    def filter_frames_with_faces(self, frames: List[Frame]) -> List[Frame]:
        """
        顔が検出されたフレームのみをフィルタリング
        
        Args:
            frames: フィルタリング対象フレーム
            
        Returns:
            List[Frame]: 顔が検出されたフレーム
        """
        if not frames:
            return []
        
        self.logger.info(f"顔フィルタリング開始: {len(frames)}フレーム")
        
        try:
            # バッチで顔検出
            batch_results = self.detect_faces_batch(frames)
            
            # 顔が検出されたフレームのみを抽出
            frames_with_faces = []
            for frame, faces in zip(frames, batch_results):
                if faces:  # 顔が検出された場合
                    frames_with_faces.append(frame)
            
            self.logger.info(f"顔フィルタリング完了: {len(frames_with_faces)}/{len(frames)}フレーム")
            return frames_with_faces
            
        except Exception as e:
            self.logger.error(f"顔フィルタリングエラー: {e}")
            raise FaceDetectionError(
                f"顔フィルタリング中にエラーが発生しました: {e}",
                details={'input_frames': len(frames)}
            )
    
    def get_primary_face(self, frame: Frame) -> Optional[FaceDetectionResult]:
        """
        フレーム内で最も重要な顔を取得
        
        Args:
            frame: 対象フレーム
            
        Returns:
            Optional[FaceDetectionResult]: 最も重要な顔（なければNone）
        """
        try:
            faces = self.detect_faces(frame)
            if not faces:
                return None
            
            # 信頼度とサイズの組み合わせで最適な顔を選択
            best_face = max(faces, key=lambda f: f.confidence * f.face_size)
            return best_face
            
        except Exception as e:
            self.logger.warning(f"主要顔取得エラー: {e}")
            return None
    
    def calculate_face_quality(self, face_result: FaceDetectionResult, frame: Frame) -> float:
        """
        顔の品質スコアを計算
        
        Args:
            face_result: 顔検出結果
            frame: 元フレーム
            
        Returns:
            float: 品質スコア（0.0-1.0）
            
        Raises:
            InvalidFaceDataError: 顔データが無効
        """
        if face_result is None or frame is None:
            raise InvalidFaceDataError("顔データまたはフレームが無効です")
        
        try:
            # 既存の品質メトリクスを使用
            if face_result.quality_metrics:
                metrics = face_result.quality_metrics
                
                # 重み付き平均で総合品質を計算
                weights = {
                    'sharpness': 0.3,
                    'brightness': 0.2,
                    'contrast': 0.2,
                    'symmetry': 0.3
                }
                
                total_score = 0.0
                total_weight = 0.0
                
                for metric, weight in weights.items():
                    if metric in metrics:
                        total_score += metrics[metric] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    quality_score = total_score / total_weight
                    # 信頼度も考慮
                    return (quality_score * 0.7 + face_result.confidence * 0.3)
            
            # メトリクスがない場合は信頼度を返す
            return face_result.confidence
            
        except Exception as e:
            self.logger.warning(f"顔品質計算エラー: {e}")
            return face_result.confidence
    
    def set_detection_confidence(self, confidence: float):
        """
        顔検出信頼度を設定
        
        Args:
            confidence: 信頼度（0.0-1.0）
            
        Raises:
            InvalidConfidenceError: 信頼度が範囲外
        """
        if not (0.0 <= confidence <= 1.0):
            raise InvalidConfidenceError(f"信頼度は0.0-1.0の範囲である必要があります: {confidence}")
        
        self.detection_confidence = confidence
        
        # MediaPipeインスタンスを再作成
        self.face_detection.close()
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=confidence
        )
        
        self.logger.info(f"検出信頼度を更新: {confidence}")
    
    def set_min_face_size(self, min_size: float):
        """
        最小顔サイズを設定
        
        Args:
            min_size: 最小顔サイズ（0.0-1.0）
            
        Raises:
            InvalidSizeRatioError: サイズ比率が範囲外
        """
        if not (0.0 <= min_size <= 1.0):
            raise InvalidSizeRatioError(f"顔サイズ比率は0.0-1.0の範囲である必要があります: {min_size}")
        
        self.min_face_size = min_size
        self.logger.info(f"最小顔サイズを更新: {min_size}")
    
    def get_face_landmarks(self, face_result: FaceDetectionResult) -> List[Point2D]:
        """
        顔のランドマークを取得
        
        Args:
            face_result: 顔検出結果
            
        Returns:
            List[Point2D]: ランドマーク座標のリスト
            
        Raises:
            LandmarkExtractionError: ランドマーク抽出に失敗
        """
        if face_result is None:
            raise LandmarkExtractionError("顔検出結果が無効です")
        
        try:
            # 既にランドマークがある場合はそれを返す
            if face_result.landmarks:
                return face_result.landmarks.copy()
            
            # MediaPipeでランドマーク検出（簡略実装）
            # 実際の実装では、元画像からランドマークを再検出する
            landmarks = []
            
            # 顔の境界ボックスから主要ランドマークを推定
            bbox = face_result.bounding_box
            center_x = bbox.x + bbox.width / 2
            center_y = bbox.y + bbox.height / 2
            
            # 簡単なランドマーク推定（目、鼻、口の大まかな位置）
            landmarks.extend([
                Point2D(center_x - bbox.width * 0.2, center_y - bbox.height * 0.1),  # 左目
                Point2D(center_x + bbox.width * 0.2, center_y - bbox.height * 0.1),  # 右目
                Point2D(center_x, center_y),  # 鼻
                Point2D(center_x - bbox.width * 0.15, center_y + bbox.height * 0.2),  # 口左
                Point2D(center_x + bbox.width * 0.15, center_y + bbox.height * 0.2),  # 口右
            ])
            
            return landmarks
            
        except Exception as e:
            self.logger.error(f"ランドマーク抽出エラー: {e}")
            raise LandmarkExtractionError(
                f"ランドマーク抽出中にエラーが発生しました: {e}",
                details={'face_confidence': face_result.confidence}
            )
    
    def _create_face_result_from_detection(self, 
                                         detection, 
                                         image_width: int, 
                                         image_height: int,
                                         rgb_image: np.ndarray) -> FaceDetectionResult:
        """MediaPipe検出結果からFaceDetectionResultを作成"""
        try:
            # 境界ボックスの取得（MediaPipeは正規化座標で返す）
            bbox_data = detection.location_data.relative_bounding_box
            
            # 正規化座標で境界ボックス作成
            bbox = BoundingBox(
                x=bbox_data.xmin,
                y=bbox_data.ymin,
                width=bbox_data.width,
                height=bbox_data.height
            )
            
            # 信頼度
            confidence = detection.score[0]
            
            # 顔サイズ（画面に占める割合）
            face_size = bbox.area
            
            # 品質メトリクスの計算
            quality_metrics = self._calculate_face_quality_metrics(
                bbox, rgb_image, image_width, image_height
            )
            
            # ランドマーク（簡略版）
            landmarks = self._extract_simple_landmarks(bbox)
            
            return FaceDetectionResult(
                bounding_box=bbox,
                confidence=confidence,
                landmarks=landmarks,
                face_size=face_size,
                face_angle=0.0,  # 簡略実装では0
                quality_metrics=quality_metrics
            )
            
        except Exception as e:
            raise FaceDetectionError(f"顔検出結果の作成でエラー: {e}")
    
    def _calculate_face_quality_metrics(self, 
                                      bbox: BoundingBox, 
                                      rgb_image: np.ndarray,
                                      image_width: int,
                                      image_height: int) -> dict:
        """顔の品質メトリクスを計算"""
        try:
            # 顔領域を切り出し
            x, y, w, h = bbox.to_pixel_coordinates(image_width, image_height)
            face_region = rgb_image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return {'sharpness': 0.5, 'brightness': 0.5, 'contrast': 0.5, 'symmetry': 0.5}
            
            # グレースケール変換
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
            
            # 鮮明度（ラプラシアン分散）
            laplacian = cv2.Laplacian(gray_face, cv2.CV_64F)
            sharpness = min(1.0, np.var(laplacian) / 1000.0)
            
            # 明度
            brightness = np.mean(gray_face) / 255.0
            
            # コントラスト
            contrast = min(1.0, np.std(gray_face) / 255.0)
            
            # 対称性（簡略計算）
            height, width = gray_face.shape
            if width > 1:
                left_half = gray_face[:, :width//2]
                right_half = cv2.flip(gray_face[:, width//2:], 1)
                min_width = min(left_half.shape[1], right_half.shape[1])
                if min_width > 0:
                    correlation = cv2.matchTemplate(
                        left_half[:, :min_width], 
                        right_half[:, :min_width], 
                        cv2.TM_CCOEFF_NORMED
                    )
                    symmetry = max(0.0, correlation[0, 0])
                else:
                    symmetry = 0.5
            else:
                symmetry = 0.5
            
            return {
                'sharpness': max(0.0, min(1.0, sharpness)),
                'brightness': max(0.0, min(1.0, brightness)),
                'contrast': max(0.0, min(1.0, contrast)),
                'symmetry': max(0.0, min(1.0, symmetry))
            }
            
        except Exception as e:
            self.logger.warning(f"品質メトリクス計算エラー: {e}")
            return {'sharpness': 0.5, 'brightness': 0.5, 'contrast': 0.5, 'symmetry': 0.5}
    
    def _extract_simple_landmarks(self, bbox: BoundingBox) -> List[Point2D]:
        """境界ボックスから簡単なランドマークを推定"""
        center_x = bbox.x + bbox.width / 2
        center_y = bbox.y + bbox.height / 2
        
        # 主要ランドマーク（目、鼻、口）の推定位置
        return [
            Point2D(center_x - bbox.width * 0.2, center_y - bbox.height * 0.1),  # 左目
            Point2D(center_x + bbox.width * 0.2, center_y - bbox.height * 0.1),  # 右目
            Point2D(center_x, center_y),  # 鼻
            Point2D(center_x - bbox.width * 0.15, center_y + bbox.height * 0.2),  # 口左
            Point2D(center_x + bbox.width * 0.15, center_y + bbox.height * 0.2),  # 口右
        ]
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.face_detection:
                self.face_detection.close()
            if self.face_mesh:
                self.face_mesh.close()
            self.logger.info("FaceDetector クリーンアップ完了")
        except Exception as e:
            self.logger.warning(f"クリーンアップエラー: {e}")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()
