"""
DiversitySelector（多様性選択）サービス

ORB特徴量、K-means、多様性スコア計算を使用して、
構図の異なるフレームを選択するサービスクラスです。
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

from ..models.frame import Frame
from ..lib.errors import (
    DiversityCalculationError,
    InvalidCountError,
    InvalidWeightError,
    InsufficientFramesError
)


class DiversitySelector:
    """多様性選択サービスクラス"""
    
    def __init__(self):
        """DiversitySelectorを初期化"""
        self.logger = logging.getLogger(__name__)
        
        # ORB特徴量検出器（研究結果に基づく設定）
        self.orb = cv2.ORB_create(
            nfeatures=500,          # 最大特徴点数
            scaleFactor=1.2,        # スケールファクター
            nlevels=8,              # ピラミッドレベル数
            edgeThreshold=31,       # エッジ閾値
            firstLevel=0,           # 最初のレベル
            WTA_K=2,               # WTA（Winner Take All）のK値
            scoreType=cv2.ORB_HARRIS_SCORE,  # スコア計算方式
            patchSize=31,          # パッチサイズ
            fastThreshold=20       # FAST検出器の閾値
        )
        
        self.logger.info("DiversitySelector初期化完了")
    
    def calculate_diversity_scores(self, frames: List[Frame]) -> List[float]:
        """
        フレーム間の構図多様性スコアを計算
        
        Args:
            frames: 多様性評価対象フレーム
            
        Returns:
            List[float]: 各フレームの多様性スコア（0.0-1.0）
            
        Raises:
            DiversityCalculationError: 多様性計算に失敗
        """
        if len(frames) < 2:
            return [1.0] * len(frames)  # フレームが少ない場合は全て最高スコア
        
        self.logger.info(f"多様性スコア計算開始: {len(frames)}フレーム")
        
        try:
            # 各フレームの特徴量を抽出
            feature_vectors = []
            color_histograms = []
            face_positions = []
            
            for frame in frames:
                # ORB特徴量
                orb_features = self._extract_orb_features(frame.image_data)
                feature_vectors.append(orb_features)
                
                # 色ヒストグラム
                color_hist = self._extract_color_histogram(frame.image_data)
                color_histograms.append(color_hist)
                
                # 顔位置情報
                face_pos = self._extract_face_position_features(frame)
                face_positions.append(face_pos)
            
            # 各特徴量での多様性を計算
            orb_diversity = self._calculate_feature_diversity(feature_vectors)
            color_diversity = self._calculate_histogram_diversity(color_histograms)
            face_diversity = self._calculate_face_position_diversity(face_positions)
            
            # 重み付き統合（研究結果に基づく重み）
            diversity_scores = []
            for i in range(len(frames)):
                combined_score = (
                    orb_diversity[i] * 0.4 +      # 特徴量の重み
                    color_diversity[i] * 0.3 +    # 色の重み  
                    face_diversity[i] * 0.3       # 顔位置の重み
                )
                diversity_scores.append(min(1.0, max(0.0, combined_score)))
            
            self.logger.info(f"多様性スコア計算完了: 平均スコア={np.mean(diversity_scores):.3f}")
            return diversity_scores
            
        except Exception as e:
            self.logger.error(f"多様性スコア計算エラー: {e}")
            raise DiversityCalculationError(
                f"多様性スコア計算中にエラーが発生しました: {e}",
                details={'frames_count': len(frames)}
            )
    
    def select_diverse_frames(self, 
                            frames: List[Frame], 
                            count: int,
                            diversity_weight: float = 0.7) -> List[Frame]:
        """
        多様性を考慮してフレームを選択
        
        Args:
            frames: 選択対象フレーム
            count: 選択するフレーム数
            diversity_weight: 多様性の重み（0.0-1.0）
            
        Returns:
            List[Frame]: 選択されたフレーム
            
        Raises:
            InvalidCountError: 選択数が無効
            InvalidWeightError: 重みが無効
            InsufficientFramesError: フレーム数が不足
        """
        if count <= 0:
            raise InvalidCountError(f"選択数は1以上である必要があります: {count}")
        
        if not (0.0 <= diversity_weight <= 1.0):
            raise InvalidWeightError(f"多様性重みは0.0-1.0の範囲である必要があります: {diversity_weight}")
        
        if len(frames) == 0:
            raise InsufficientFramesError("選択対象のフレームがありません")
        
        if len(frames) <= count:
            return frames.copy()
        
        self.logger.info(f"多様性フレーム選択開始: {len(frames)}→{count}フレーム, 重み={diversity_weight}")
        
        try:
            # 多様性スコアを計算
            diversity_scores = self.calculate_diversity_scores(frames)
            
            # 品質スコアも考慮した総合スコアを計算
            combined_scores = []
            for i, frame in enumerate(frames):
                quality_score = frame.quality_score
                diversity_score = diversity_scores[i]
                
                # 重み付き統合
                total_score = (
                    diversity_score * diversity_weight +
                    quality_score * (1.0 - diversity_weight)
                )
                combined_scores.append((total_score, i, frame))
            
            # スコア順にソート
            combined_scores.sort(key=lambda x: x[0], reverse=True)
            
            # K-meansクラスタリングによる多様性確保
            selected_frames = self._select_with_clustering(
                frames, combined_scores, count
            )
            
            self.logger.info(f"多様性フレーム選択完了: {len(selected_frames)}フレーム選出")
            return selected_frames
            
        except (InvalidCountError, InvalidWeightError, InsufficientFramesError):
            raise
        except Exception as e:
            self.logger.error(f"多様性フレーム選択エラー: {e}")
            raise DiversityCalculationError(
                f"多様性フレーム選択中にエラーが発生しました: {e}",
                details={'input_frames': len(frames), 'target_count': count}
            )
    
    def _extract_orb_features(self, image: np.ndarray) -> np.ndarray:
        """ORB特徴量を抽出"""
        try:
            # グレースケール変換
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # ORB特徴量検出
            keypoints, descriptors = self.orb.detectAndCompute(gray, None)
            
            if descriptors is None:
                # 特徴量が検出されない場合はゼロベクトル
                return np.zeros(500 * 32, dtype=np.float32)
            
            # 固定長ベクトルに変換（Bag of Visual Words風）
            feature_vector = np.zeros(500 * 32, dtype=np.float32)
            
            # descriptorsの各行を平坦化して格納
            max_features = min(len(descriptors), 500)
            for i in range(max_features):
                start_idx = i * 32
                end_idx = start_idx + 32
                feature_vector[start_idx:end_idx] = descriptors[i].astype(np.float32)
            
            # 正規化
            norm = np.linalg.norm(feature_vector)
            if norm > 0:
                feature_vector = feature_vector / norm
            
            return feature_vector
            
        except Exception as e:
            self.logger.warning(f"ORB特徴量抽出エラー: {e}")
            return np.zeros(500 * 32, dtype=np.float32)
    
    def _extract_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """色ヒストグラムを抽出"""
        try:
            # HSVに変換（色相が重要）
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # 各チャンネルのヒストグラムを計算
            hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])  # Hue
            hist_s = cv2.calcHist([hsv], [1], None, [60], [0, 256])  # Saturation
            hist_v = cv2.calcHist([hsv], [2], None, [60], [0, 256])  # Value
            
            # 正規化
            hist_h = hist_h.flatten() / (np.sum(hist_h) + 1e-8)
            hist_s = hist_s.flatten() / (np.sum(hist_s) + 1e-8)
            hist_v = hist_v.flatten() / (np.sum(hist_v) + 1e-8)
            
            # 結合
            color_histogram = np.concatenate([hist_h, hist_s, hist_v])
            
            return color_histogram.astype(np.float32)
            
        except Exception as e:
            self.logger.warning(f"色ヒストグラム抽出エラー: {e}")
            return np.zeros(170, dtype=np.float32)  # 50+60+60
    
    def _extract_face_position_features(self, frame: Frame) -> np.ndarray:
        """顔位置特徴量を抽出"""
        try:
            if not frame.has_faces:
                return np.zeros(6, dtype=np.float32)  # 顔なしの場合
            
            # 主要な顔の位置情報
            primary_face = frame.primary_face
            if primary_face is None:
                return np.zeros(6, dtype=np.float32)
            
            bbox = primary_face.bounding_box
            
            # 位置特徴量：中心位置、サイズ、アスペクト比
            features = np.array([
                bbox.center.x,           # 中心X座標
                bbox.center.y,           # 中心Y座標
                bbox.width,              # 幅
                bbox.height,             # 高さ
                bbox.aspect_ratio,       # アスペクト比
                primary_face.face_size   # 顔サイズ
            ], dtype=np.float32)
            
            return features
            
        except Exception as e:
            self.logger.warning(f"顔位置特徴量抽出エラー: {e}")
            return np.zeros(6, dtype=np.float32)
    
    def _calculate_feature_diversity(self, feature_vectors: List[np.ndarray]) -> List[float]:
        """特徴量ベースの多様性を計算"""
        try:
            if len(feature_vectors) < 2:
                return [1.0] * len(feature_vectors)
            
            # 特徴量行列を作成
            features_matrix = np.vstack(feature_vectors)
            
            # ペアワイズ距離を計算
            distances = pairwise_distances(features_matrix, metric='cosine')
            
            # 各フレームの平均距離を多様性スコアとする
            diversity_scores = []
            for i in range(len(feature_vectors)):
                # 自分以外のフレームとの平均距離
                other_distances = np.concatenate([distances[i][:i], distances[i][i+1:]])
                avg_distance = np.mean(other_distances) if len(other_distances) > 0 else 0.0
                diversity_scores.append(min(1.0, max(0.0, avg_distance)))
            
            return diversity_scores
            
        except Exception as e:
            self.logger.warning(f"特徴量多様性計算エラー: {e}")
            return [0.5] * len(feature_vectors)
    
    def _calculate_histogram_diversity(self, histograms: List[np.ndarray]) -> List[float]:
        """ヒストグラムベースの多様性を計算"""
        try:
            if len(histograms) < 2:
                return [1.0] * len(histograms)
            
            diversity_scores = []
            
            for i, hist in enumerate(histograms):
                total_distance = 0.0
                count = 0
                
                for j, other_hist in enumerate(histograms):
                    if i != j:
                        # ヒストグラム比較（相関係数）
                        correlation = cv2.compareHist(
                            hist.astype(np.float32), 
                            other_hist.astype(np.float32), 
                            cv2.HISTCMP_CORREL
                        )
                        distance = 1.0 - max(0.0, correlation)  # 距離に変換
                        total_distance += distance
                        count += 1
                
                avg_distance = total_distance / count if count > 0 else 0.0
                diversity_scores.append(min(1.0, max(0.0, avg_distance)))
            
            return diversity_scores
            
        except Exception as e:
            self.logger.warning(f"ヒストグラム多様性計算エラー: {e}")
            return [0.5] * len(histograms)
    
    def _calculate_face_position_diversity(self, face_positions: List[np.ndarray]) -> List[float]:
        """顔位置ベースの多様性を計算"""
        try:
            if len(face_positions) < 2:
                return [1.0] * len(face_positions)
            
            # 顔位置行列を作成
            positions_matrix = np.vstack(face_positions)
            
            # ユークリッド距離で多様性を計算
            distances = pairwise_distances(positions_matrix, metric='euclidean')
            
            # 正規化のための最大距離
            max_distance = np.sqrt(2.0)  # 正規化座標での最大距離
            
            diversity_scores = []
            for i in range(len(face_positions)):
                # 自分以外との平均距離
                other_distances = np.concatenate([distances[i][:i], distances[i][i+1:]])
                avg_distance = np.mean(other_distances) if len(other_distances) > 0 else 0.0
                
                # 正規化
                normalized_distance = min(1.0, avg_distance / max_distance)
                diversity_scores.append(normalized_distance)
            
            return diversity_scores
            
        except Exception as e:
            self.logger.warning(f"顔位置多様性計算エラー: {e}")
            return [0.5] * len(face_positions)
    
    def _select_with_clustering(self, 
                              frames: List[Frame], 
                              scored_frames: List[Tuple[float, int, Frame]], 
                              count: int) -> List[Frame]:
        """クラスタリングを使用した多様性確保選択"""
        try:
            if len(frames) <= count:
                return frames.copy()
            
            # 上位候補を多めに選択（count * 2）
            candidate_count = min(len(scored_frames), count * 2)
            candidates = [scored_frames[i][2] for i in range(candidate_count)]
            candidate_indices = [scored_frames[i][1] for i in range(candidate_count)]
            
            if len(candidates) <= count:
                return candidates
            
            # 候補フレームの特徴量を抽出
            candidate_features = []
            for frame in candidates:
                orb_features = self._extract_orb_features(frame.image_data)
                color_hist = self._extract_color_histogram(frame.image_data)
                face_pos = self._extract_face_position_features(frame)
                
                # 特徴量を結合
                combined_features = np.concatenate([
                    orb_features * 0.4,  # ORB特徴量
                    color_hist * 0.3,    # 色ヒストグラム
                    face_pos * 0.3       # 顔位置
                ])
                candidate_features.append(combined_features)
            
            # K-meansクラスタリング
            features_matrix = np.vstack(candidate_features)
            
            if count >= len(features_matrix):
                return candidates
            
            # クラスタ数を調整（最大でフレーム数まで）
            n_clusters = min(count, len(features_matrix))
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features_matrix)
            
            # 各クラスタから代表フレームを選択
            selected_frames = []
            for cluster_id in range(n_clusters):
                cluster_indices = np.where(cluster_labels == cluster_id)[0]
                
                if len(cluster_indices) == 0:
                    continue
                
                # クラスタ内で最高スコアのフレームを選択
                best_idx_in_cluster = None
                best_score = -1.0
                
                for idx in cluster_indices:
                    original_idx = candidate_indices[idx]
                    frame_score = scored_frames[original_idx][0]
                    
                    if frame_score > best_score:
                        best_score = frame_score
                        best_idx_in_cluster = idx
                
                if best_idx_in_cluster is not None:
                    selected_frames.append(candidates[best_idx_in_cluster])
            
            # 必要に応じて追加選択
            while len(selected_frames) < count and len(selected_frames) < len(candidates):
                for candidate in candidates:
                    if candidate not in selected_frames:
                        selected_frames.append(candidate)
                        if len(selected_frames) >= count:
                            break
            
            return selected_frames[:count]
            
        except Exception as e:
            self.logger.warning(f"クラスタリング選択エラー: {e}")
            # フォールバック：スコア順上位選択
            return [scored_frames[i][2] for i in range(min(count, len(scored_frames)))]
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        # ORBディテクターは特にクリーンアップ不要
        self.logger.info("DiversitySelector クリーンアップ完了")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()
