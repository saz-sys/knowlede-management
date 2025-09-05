"""
DiversitySelectorのユニットテスト

多様性選択サービスの各機能をテストします。
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import cv2
from sklearn.cluster import KMeans

from src.services.diversity_selector import DiversitySelector
from src.models.frame import Frame
from src.lib.errors import (
    DiversityCalculationError,
    InvalidCountError,
    InvalidWeightError,
    InsufficientFramesError
)


class TestDiversitySelector:
    """DiversitySelectorのテストクラス"""
    
    @pytest.fixture
    def selector(self):
        """DiversitySelectorのインスタンスを作成"""
        return DiversitySelector()
    
    @pytest.fixture
    def sample_frames(self):
        """サンプルフレームリスト"""
        frames = []
        for i in range(10):
            # 各フレームで異なるパターンを作成
            frame_data = np.zeros((480, 640, 3), dtype=np.uint8)
            if i % 2 == 0:
                frame_data[:, :] = [100, 100, 100]  # グレー
            else:
                frame_data[:, :] = [200, 200, 200]  # ライトグレー
            
            # 位置を変えてパターンを追加
            start_x = (i * 50) % 500
            start_y = (i * 30) % 400
            frame_data[start_y:start_y+50, start_x:start_x+50] = [255, 255, 255]
            
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 2.0,
                frame_index=i * 60
            )
            frames.append(frame)
        return frames
    
    @pytest.fixture
    def identical_frames(self):
        """同一パターンのフレームリスト"""
        frames = []
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for i in range(5):
            frame = Frame(
                frame_data=frame_data.copy(),
                timestamp_seconds=i * 2.0,
                frame_index=i * 60
            )
            frames.append(frame)
        return frames

    def test_init(self, selector):
        """初期化のテスト"""
        assert selector.orb is not None
        assert selector.logger is not None

    def test_calculate_diversity_scores_success(self, selector, sample_frames):
        """多様性スコア計算成功のテスト"""
        scores = selector.calculate_diversity_scores(sample_frames)
        
        assert len(scores) == len(sample_frames)
        assert all(isinstance(score, float) for score in scores)
        assert all(score >= 0.0 for score in scores)

    def test_calculate_diversity_scores_identical_frames(self, selector, identical_frames):
        """同一フレームの多様性スコアテスト"""
        scores = selector.calculate_diversity_scores(identical_frames)
        
        # 同一フレームなので低いスコア
        assert all(score < 0.5 for score in scores)

    def test_calculate_diversity_scores_insufficient_frames(self, selector):
        """フレーム不足のテスト"""
        single_frame = [Frame(
            frame_data=np.zeros((480, 640, 3), dtype=np.uint8),
            timestamp_seconds=0.0,
            frame_index=0
        )]
        
        with pytest.raises(InsufficientFramesError):
            selector.calculate_diversity_scores(single_frame)

    def test_calculate_diversity_scores_empty_frames(self, selector):
        """空フレームリストのテスト"""
        with pytest.raises(InsufficientFramesError):
            selector.calculate_diversity_scores([])

    def test_select_diverse_frames_success(self, selector, sample_frames):
        """多様フレーム選択成功のテスト"""
        count = 5
        selected = selector.select_diverse_frames(sample_frames, count)
        
        assert len(selected) == count
        assert all(isinstance(frame, Frame) for frame in selected)
        assert len(set(id(frame) for frame in selected)) == count  # 重複なし

    def test_select_diverse_frames_more_than_available(self, selector, sample_frames):
        """利用可能数以上の選択テスト"""
        count = len(sample_frames) + 5
        selected = selector.select_diverse_frames(sample_frames, count)
        
        # 利用可能な分だけ返される
        assert len(selected) == len(sample_frames)

    def test_select_diverse_frames_invalid_count(self, selector, sample_frames):
        """無効なカウントのテスト"""
        with pytest.raises(InvalidCountError):
            selector.select_diverse_frames(sample_frames, 0)
        
        with pytest.raises(InvalidCountError):
            selector.select_diverse_frames(sample_frames, -1)

    def test_select_diverse_frames_insufficient_input(self, selector):
        """入力フレーム不足のテスト"""
        empty_frames = []
        
        with pytest.raises(InsufficientFramesError):
            selector.select_diverse_frames(empty_frames, 3)

    @patch('cv2.ORB_create')
    def test_extract_features_success(self, mock_orb_create, selector):
        """特徴量抽出成功のテスト"""
        # モック設定
        mock_orb = Mock()
        mock_keypoints = [Mock() for _ in range(100)]
        mock_descriptors = np.random.randint(0, 255, (100, 32), dtype=np.uint8)
        mock_orb.detectAndCompute.return_value = (mock_keypoints, mock_descriptors)
        mock_orb_create.return_value = mock_orb
        
        # テスト用フレーム
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 実行
        features = selector.extract_features(frame_data)
        
        # 検証
        assert features is not None
        assert features.shape == (100, 32)

    @patch('cv2.ORB_create')
    def test_extract_features_no_features(self, mock_orb_create, selector):
        """特徴量が検出されない場合のテスト"""
        mock_orb = Mock()
        mock_orb.detectAndCompute.return_value = ([], None)
        mock_orb_create.return_value = mock_orb
        
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        features = selector.extract_features(frame_data)
        
        # 特徴量なしの場合は空の配列を返す
        assert features is not None
        assert features.shape[0] == 0

    def test_extract_features_invalid_frame(self, selector):
        """無効なフレームでの特徴量抽出テスト"""
        with pytest.raises(ValueError):
            selector.extract_features(None)

    def test_compute_similarity_matrix_success(self, selector):
        """類似度行列計算成功のテスト"""
        # テスト用特徴量リスト
        features_list = [
            np.random.randint(0, 255, (50, 32), dtype=np.uint8),
            np.random.randint(0, 255, (60, 32), dtype=np.uint8),
            np.random.randint(0, 255, (40, 32), dtype=np.uint8)
        ]
        
        similarity_matrix = selector.compute_similarity_matrix(features_list)
        
        assert similarity_matrix.shape == (3, 3)
        assert np.allclose(similarity_matrix, similarity_matrix.T)  # 対称行列
        assert np.allclose(np.diag(similarity_matrix), 1.0)  # 対角成分は1

    def test_compute_similarity_matrix_empty_features(self, selector):
        """空特徴量での類似度行列計算テスト"""
        features_list = [
            np.array([]).reshape(0, 32),
            np.array([]).reshape(0, 32)
        ]
        
        similarity_matrix = selector.compute_similarity_matrix(features_list)
        
        # 特徴量がない場合は0の類似度
        assert similarity_matrix.shape == (2, 2)
        assert np.allclose(similarity_matrix, 0.0)

    def test_compute_similarity_matrix_single_feature(self, selector):
        """単一特徴量での類似度行列計算テスト"""
        features_list = [
            np.random.randint(0, 255, (50, 32), dtype=np.uint8)
        ]
        
        similarity_matrix = selector.compute_similarity_matrix(features_list)
        
        assert similarity_matrix.shape == (1, 1)
        assert similarity_matrix[0, 0] == 1.0

    @patch('sklearn.cluster.KMeans')
    def test_cluster_frames_success(self, mock_kmeans_class, selector, sample_frames):
        """フレームクラスタリング成功のテスト"""
        # モック設定
        mock_kmeans = Mock()
        mock_kmeans.labels_ = np.array([0, 1, 0, 1, 2, 0, 1, 2, 0, 1])
        mock_kmeans.cluster_centers_ = np.random.rand(3, 100)
        mock_kmeans_class.return_value = mock_kmeans
        
        n_clusters = 3
        clusters = selector.cluster_frames(sample_frames, n_clusters)
        
        assert len(clusters) == n_clusters
        assert all(isinstance(cluster, list) for cluster in clusters)
        total_frames = sum(len(cluster) for cluster in clusters)
        assert total_frames == len(sample_frames)

    def test_cluster_frames_invalid_clusters(self, selector, sample_frames):
        """無効なクラスタ数のテスト"""
        with pytest.raises(InvalidCountError):
            selector.cluster_frames(sample_frames, 0)
        
        with pytest.raises(InvalidCountError):
            selector.cluster_frames(sample_frames, -1)

    def test_cluster_frames_more_clusters_than_frames(self, selector):
        """フレーム数よりも多いクラスタ数のテスト"""
        few_frames = [Frame(
            frame_data=np.zeros((480, 640, 3), dtype=np.uint8),
            timestamp_seconds=0.0,
            frame_index=0
        )]
        
        with pytest.raises(InvalidCountError):
            selector.cluster_frames(few_frames, 5)

    def test_calculate_frame_distances_success(self, selector, sample_frames):
        """フレーム間距離計算成功のテスト"""
        distances = selector.calculate_frame_distances(sample_frames)
        
        n_frames = len(sample_frames)
        assert distances.shape == (n_frames, n_frames)
        assert np.allclose(distances, distances.T)  # 対称行列
        assert np.allclose(np.diag(distances), 0.0)  # 対角成分は0

    def test_calculate_frame_distances_insufficient_frames(self, selector):
        """フレーム不足での距離計算テスト"""
        single_frame = [Frame(
            frame_data=np.zeros((480, 640, 3), dtype=np.uint8),
            timestamp_seconds=0.0,
            frame_index=0
        )]
        
        with pytest.raises(InsufficientFramesError):
            selector.calculate_frame_distances(single_frame)

    def test_weighted_selection_success(self, selector, sample_frames):
        """重み付き選択成功のテスト"""
        diversity_weight = 0.7
        quality_weight = 0.3
        quality_scores = [0.8, 0.6, 0.9, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7, 0.5]
        count = 5
        
        selected = selector.weighted_selection(
            sample_frames, count, diversity_weight, quality_weight, quality_scores
        )
        
        assert len(selected) == count
        assert all(isinstance(frame, Frame) for frame in selected)

    def test_weighted_selection_invalid_weights(self, selector, sample_frames):
        """無効な重みでの選択テスト"""
        quality_scores = [0.8] * len(sample_frames)
        
        # 重みの合計が1でない
        with pytest.raises(InvalidWeightError):
            selector.weighted_selection(
                sample_frames, 3, 0.6, 0.5, quality_scores  # 合計1.1
            )
        
        # 負の重み
        with pytest.raises(InvalidWeightError):
            selector.weighted_selection(
                sample_frames, 3, -0.3, 1.3, quality_scores
            )

    def test_weighted_selection_mismatched_scores(self, selector, sample_frames):
        """品質スコア数不一致のテスト"""
        quality_scores = [0.8, 0.6, 0.9]  # フレーム数より少ない
        
        with pytest.raises(ValueError):
            selector.weighted_selection(
                sample_frames, 3, 0.7, 0.3, quality_scores
            )

    def test_optimize_diversity_success(self, selector, sample_frames):
        """多様性最適化成功のテスト"""
        target_count = 5
        optimized = selector.optimize_diversity(sample_frames, target_count)
        
        assert len(optimized) == target_count
        assert all(isinstance(frame, Frame) for frame in optimized)
        
        # 元のフレームリストのサブセット
        original_ids = set(id(frame) for frame in sample_frames)
        optimized_ids = set(id(frame) for frame in optimized)
        assert optimized_ids.issubset(original_ids)

    def test_optimize_diversity_greedy_selection(self, selector, sample_frames):
        """グリーディ選択での多様性最適化テスト"""
        target_count = 3
        optimized = selector.optimize_diversity(
            sample_frames, target_count, method="greedy"
        )
        
        assert len(optimized) == target_count

    def test_optimize_diversity_invalid_method(self, selector, sample_frames):
        """無効な手法での最適化テスト"""
        with pytest.raises(ValueError):
            selector.optimize_diversity(sample_frames, 3, method="invalid_method")

    def test_cleanup(self, selector):
        """クリーンアップのテスト"""
        # 実行（エラーが発生しないことを確認）
        selector.cleanup()
        
        # ログに記録されることを確認（実際の検証は省略）
        assert True

    def test_get_diversity_stats(self, selector):
        """多様性統計情報取得のテスト"""
        stats = selector.get_diversity_stats()
        
        expected_keys = [
            'total_processed_frames',
            'total_feature_extractions',
            'average_features_per_frame',
            'total_diversity_calculations',
            'average_diversity_score'
        ]
        
        assert all(key in stats for key in expected_keys)
        assert all(isinstance(stats[key], (int, float)) for key in expected_keys)


class TestDiversitySelectorIntegration:
    """DiversitySelectorの統合テスト"""
    
    @pytest.fixture
    def selector(self):
        return DiversitySelector()
    
    def test_full_diversity_pipeline(self, selector):
        """完全な多様性選択パイプラインのテスト"""
        # 多様なフレームセットを作成
        frames = []
        for i in range(10):
            # 各フレームで大きく異なるパターンを作成
            frame_data = np.zeros((240, 320, 3), dtype=np.uint8)
            
            if i < 3:
                frame_data[:, :] = [255, 0, 0]  # 赤
            elif i < 6:
                frame_data[:, :] = [0, 255, 0]  # 緑
            else:
                frame_data[:, :] = [0, 0, 255]  # 青
            
            # 位置に応じてパターン追加
            pattern_x = (i * 40) % 200
            pattern_y = (i * 30) % 150
            frame_data[pattern_y:pattern_y+40, pattern_x:pattern_x+40] = [255, 255, 255]
            
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 1.0,
                frame_index=i * 30
            )
            frames.append(frame)
        
        # パイプライン実行
        diversity_scores = selector.calculate_diversity_scores(frames)
        selected_frames = selector.select_diverse_frames(frames, 5)
        optimized_frames = selector.optimize_diversity(frames, 5)
        
        # 検証
        assert len(diversity_scores) == len(frames)
        assert len(selected_frames) == 5
        assert len(optimized_frames) == 5
        
        # 選択されたフレームは元のセットのサブセット
        original_ids = set(id(frame) for frame in frames)
        selected_ids = set(id(frame) for frame in selected_frames)
        optimized_ids = set(id(frame) for frame in optimized_frames)
        
        assert selected_ids.issubset(original_ids)
        assert optimized_ids.issubset(original_ids)

    def test_clustering_and_selection_pipeline(self, selector):
        """クラスタリング→選択パイプラインのテスト"""
        # フレーム準備
        frames = []
        for i in range(12):
            frame_data = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 1.0,
                frame_index=i * 30
            )
            frames.append(frame)
        
        # クラスタリング実行
        n_clusters = 4
        clusters = selector.cluster_frames(frames, n_clusters)
        
        # 各クラスタから代表フレームを選択
        representatives = []
        for cluster in clusters:
            if cluster:  # 空でないクラスタのみ
                diversity_scores = selector.calculate_diversity_scores(cluster)
                best_idx = np.argmax(diversity_scores)
                representatives.append(cluster[best_idx])
        
        # 検証
        assert len(clusters) == n_clusters
        assert len(representatives) <= n_clusters
        assert all(isinstance(frame, Frame) for frame in representatives)

    def test_quality_weighted_diversity_selection(self, selector):
        """品質重み付き多様性選択のテスト"""
        # フレームと品質スコアを準備
        frames = []
        quality_scores = []
        
        for i in range(8):
            frame_data = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
            frame = Frame(
                frame_data=frame_data,
                timestamp_seconds=i * 1.0,
                frame_index=i * 30
            )
            frames.append(frame)
            quality_scores.append(0.5 + (i % 3) * 0.2)  # 0.5, 0.7, 0.9の繰り返し
        
        # 重み付き選択実行
        selected = selector.weighted_selection(
            frames, 4, diversity_weight=0.6, quality_weight=0.4, quality_scores=quality_scores
        )
        
        # 検証
        assert len(selected) == 4
        assert all(isinstance(frame, Frame) for frame in selected)
        
        # 選択されたフレームは元のセットのサブセット
        original_ids = set(id(frame) for frame in frames)
        selected_ids = set(id(frame) for frame in selected)
        assert selected_ids.issubset(original_ids)
