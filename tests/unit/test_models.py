"""
全データモデルのユニットテスト

プロジェクトで使用される全データモデルクラスをテストします。
"""

import pytest
import numpy as np
from pathlib import Path
from datetime import datetime
from enum import Enum

from src.models.point_2d import Point2D
from src.models.bounding_box import BoundingBox
from src.models.frame import Frame
from src.models.face_detection_result import FaceDetectionResult
from src.models.thumbnail import Thumbnail
from src.models.user_settings import UserSettings, ThumbnailOrientation
from src.models.video_file import VideoFile, VideoFileStatus
from src.models.thumbnail_extraction_job import ThumbnailExtractionJob, JobStatus, JobPhase


class TestPoint2D:
    """Point2Dクラスのテスト"""
    
    def test_init_default(self):
        """デフォルト初期化のテスト"""
        point = Point2D()
        assert point.x == 0.0
        assert point.y == 0.0
    
    def test_init_with_values(self):
        """値指定初期化のテスト"""
        point = Point2D(3.5, 4.2)
        assert point.x == 3.5
        assert point.y == 4.2
    
    def test_distance_to(self):
        """距離計算のテスト"""
        point1 = Point2D(0.0, 0.0)
        point2 = Point2D(3.0, 4.0)
        
        distance = point1.distance_to(point2)
        assert distance == pytest.approx(5.0)
    
    def test_distance_to_same_point(self):
        """同一点との距離テスト"""
        point = Point2D(2.0, 3.0)
        distance = point.distance_to(point)
        assert distance == 0.0
    
    def test_midpoint(self):
        """中点計算のテスト"""
        point1 = Point2D(0.0, 0.0)
        point2 = Point2D(4.0, 6.0)
        
        midpoint = point1.midpoint(point2)
        assert midpoint.x == 2.0
        assert midpoint.y == 3.0
    
    def test_translate(self):
        """平行移動のテスト"""
        point = Point2D(2.0, 3.0)
        translated = point.translate(1.5, -0.5)
        
        assert translated.x == 3.5
        assert translated.y == 2.5
    
    def test_scale(self):
        """スケーリングのテスト"""
        point = Point2D(2.0, 3.0)
        scaled = point.scale(2.0, 1.5)
        
        assert scaled.x == 4.0
        assert scaled.y == 4.5
    
    def test_equality(self):
        """等価性のテスト"""
        point1 = Point2D(2.0, 3.0)
        point2 = Point2D(2.0, 3.0)
        point3 = Point2D(2.1, 3.0)
        
        assert point1 == point2
        assert point1 != point3
    
    def test_repr(self):
        """文字列表現のテスト"""
        point = Point2D(2.5, 3.7)
        repr_str = repr(point)
        assert "2.5" in repr_str
        assert "3.7" in repr_str


class TestBoundingBox:
    """BoundingBoxクラスのテスト"""
    
    @pytest.fixture
    def bbox(self):
        """テスト用BoundingBox"""
        return BoundingBox(
            top_left=Point2D(10.0, 20.0),
            bottom_right=Point2D(50.0, 60.0)
        )
    
    def test_init(self, bbox):
        """初期化のテスト"""
        assert bbox.top_left.x == 10.0
        assert bbox.top_left.y == 20.0
        assert bbox.bottom_right.x == 50.0
        assert bbox.bottom_right.y == 60.0
    
    def test_width_property(self, bbox):
        """幅プロパティのテスト"""
        assert bbox.width == 40.0
    
    def test_height_property(self, bbox):
        """高さプロパティのテスト"""
        assert bbox.height == 40.0
    
    def test_area_property(self, bbox):
        """面積プロパティのテスト"""
        assert bbox.area == 1600.0
    
    def test_center_property(self, bbox):
        """中心プロパティのテスト"""
        center = bbox.center
        assert center.x == 30.0
        assert center.y == 40.0
    
    def test_contains_point(self, bbox):
        """点を含むかのテスト"""
        inside_point = Point2D(30.0, 40.0)
        outside_point = Point2D(5.0, 15.0)
        edge_point = Point2D(10.0, 20.0)
        
        assert bbox.contains_point(inside_point)
        assert not bbox.contains_point(outside_point)
        assert bbox.contains_point(edge_point)
    
    def test_intersects_with(self, bbox):
        """他のボックスとの交差判定テスト"""
        overlapping_bbox = BoundingBox(
            top_left=Point2D(40.0, 50.0),
            bottom_right=Point2D(70.0, 80.0)
        )
        non_overlapping_bbox = BoundingBox(
            top_left=Point2D(60.0, 70.0),
            bottom_right=Point2D(80.0, 90.0)
        )
        
        assert bbox.intersects_with(overlapping_bbox)
        assert not bbox.intersects_with(non_overlapping_bbox)
    
    def test_intersection_area(self, bbox):
        """交差面積のテスト"""
        overlapping_bbox = BoundingBox(
            top_left=Point2D(40.0, 50.0),
            bottom_right=Point2D(70.0, 80.0)
        )
        
        intersection = bbox.intersection_area(overlapping_bbox)
        assert intersection == 100.0  # 10x10の交差
    
    def test_scale_coordinates(self, bbox):
        """座標スケーリングのテスト"""
        scaled = bbox.scale_coordinates(640, 480)
        
        # 相対座標での計算結果を確認
        expected_left = bbox.top_left.x * 640
        expected_top = bbox.top_left.y * 480
        
        assert scaled.top_left.x == expected_left
        assert scaled.top_left.y == expected_top
    
    def test_to_pixel_coordinates(self, bbox):
        """ピクセル座標変換のテスト"""
        # 正規化座標として扱う
        normalized_bbox = BoundingBox(
            top_left=Point2D(0.1, 0.2),
            bottom_right=Point2D(0.5, 0.6)
        )
        
        pixel_bbox = normalized_bbox.to_pixel_coordinates(800, 600)
        
        assert pixel_bbox.top_left.x == 80.0  # 0.1 * 800
        assert pixel_bbox.top_left.y == 120.0  # 0.2 * 600
        assert pixel_bbox.bottom_right.x == 400.0  # 0.5 * 800
        assert pixel_bbox.bottom_right.y == 360.0  # 0.6 * 600


class TestFrame:
    """Frameクラスのテスト"""
    
    @pytest.fixture
    def frame_data(self):
        """テスト用フレームデータ"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    @pytest.fixture
    def frame(self, frame_data):
        """テスト用Frame"""
        return Frame(
            frame_data=frame_data,
            timestamp_seconds=5.25,
            frame_index=157
        )
    
    def test_init(self, frame, frame_data):
        """初期化のテスト"""
        assert np.array_equal(frame.frame_data, frame_data)
        assert frame.timestamp_seconds == 5.25
        assert frame.frame_index == 157
    
    def test_width_property(self, frame):
        """幅プロパティのテスト"""
        assert frame.width == 640
    
    def test_height_property(self, frame):
        """高さプロパティのテスト"""
        assert frame.height == 480
    
    def test_channels_property(self, frame):
        """チャンネル数プロパティのテスト"""
        assert frame.channels == 3
    
    def test_aspect_ratio_property(self, frame):
        """アスペクト比プロパティのテスト"""
        expected_ratio = 640 / 480
        assert frame.aspect_ratio == pytest.approx(expected_ratio)
    
    def test_file_size_estimate_property(self, frame):
        """ファイルサイズ推定プロパティのテスト"""
        expected_size = 480 * 640 * 3  # height * width * channels
        assert frame.file_size_estimate == expected_size
    
    def test_is_valid_true(self, frame):
        """有効フレーム判定のテスト"""
        assert frame.is_valid()
    
    def test_is_valid_false(self):
        """無効フレーム判定のテスト"""
        invalid_frame = Frame(
            frame_data=None,
            timestamp_seconds=0.0,
            frame_index=0
        )
        assert not invalid_frame.is_valid()
    
    def test_to_grayscale(self, frame):
        """グレースケール変換のテスト"""
        grayscale = frame.to_grayscale()
        
        assert len(grayscale.shape) == 2  # グレースケールは2次元
        assert grayscale.shape == (480, 640)
    
    def test_resize(self, frame):
        """リサイズのテスト"""
        resized = frame.resize(320, 240)
        
        assert isinstance(resized, Frame)
        assert resized.width == 320
        assert resized.height == 240
    
    def test_crop(self, frame):
        """切り抜きのテスト"""
        bbox = BoundingBox(
            top_left=Point2D(100, 50),
            bottom_right=Point2D(300, 250)
        )
        
        cropped = frame.crop(bbox)
        
        assert isinstance(cropped, Frame)
        assert cropped.width == 200  # 300 - 100
        assert cropped.height == 200  # 250 - 50


class TestFaceDetectionResult:
    """FaceDetectionResultクラスのテスト"""
    
    @pytest.fixture
    def bbox(self):
        """テスト用BoundingBox"""
        return BoundingBox(
            top_left=Point2D(100.0, 150.0),
            bottom_right=Point2D(200.0, 250.0)
        )
    
    @pytest.fixture
    def landmarks(self):
        """テスト用ランドマーク"""
        return [
            Point2D(120.0, 170.0),  # 左目
            Point2D(180.0, 170.0),  # 右目
            Point2D(150.0, 190.0),  # 鼻
            Point2D(150.0, 220.0)   # 口
        ]
    
    @pytest.fixture
    def face_result(self, bbox, landmarks):
        """テスト用FaceDetectionResult"""
        return FaceDetectionResult(
            bounding_box=bbox,
            confidence=0.85,
            landmarks=landmarks
        )
    
    def test_init(self, face_result, bbox, landmarks):
        """初期化のテスト"""
        assert face_result.bounding_box == bbox
        assert face_result.confidence == 0.85
        assert face_result.landmarks == landmarks
    
    def test_face_area_property(self, face_result):
        """顔面積プロパティのテスト"""
        expected_area = 100.0 * 100.0  # width * height
        assert face_result.face_area == expected_area
    
    def test_face_center_property(self, face_result):
        """顔中心プロパティのテスト"""
        center = face_result.face_center
        assert center.x == 150.0
        assert center.y == 200.0
    
    def test_landmark_count_property(self, face_result):
        """ランドマーク数プロパティのテスト"""
        assert face_result.landmark_count == 4
    
    def test_is_high_confidence_true(self, face_result):
        """高信頼度判定（True）のテスト"""
        assert face_result.is_high_confidence()
    
    def test_is_high_confidence_false(self, bbox, landmarks):
        """高信頼度判定（False）のテスト"""
        low_confidence_result = FaceDetectionResult(
            bounding_box=bbox,
            confidence=0.3,
            landmarks=landmarks
        )
        assert not low_confidence_result.is_high_confidence()
    
    def test_is_high_confidence_custom_threshold(self, face_result):
        """カスタム閾値での高信頼度判定テスト"""
        assert not face_result.is_high_confidence(threshold=0.9)
        assert face_result.is_high_confidence(threshold=0.8)


class TestThumbnail:
    """Thumbnailクラスのテスト"""
    
    @pytest.fixture
    def thumbnail_image(self):
        """テスト用サムネイル画像"""
        return np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    
    @pytest.fixture
    def thumbnail(self, thumbnail_image):
        """テスト用Thumbnail"""
        return Thumbnail(
            image=thumbnail_image,
            timestamp_seconds=10.5,
            frame_index=315,
            quality_score=0.75
        )
    
    def test_init(self, thumbnail, thumbnail_image):
        """初期化のテスト"""
        assert np.array_equal(thumbnail.image, thumbnail_image)
        assert thumbnail.timestamp_seconds == 10.5
        assert thumbnail.frame_index == 315
        assert thumbnail.quality_score == 0.75
    
    def test_width_property(self, thumbnail):
        """幅プロパティのテスト"""
        assert thumbnail.width == 1280
    
    def test_height_property(self, thumbnail):
        """高さプロパティのテスト"""
        assert thumbnail.height == 720
    
    def test_aspect_ratio_property(self, thumbnail):
        """アスペクト比プロパティのテスト"""
        expected_ratio = 1280 / 720
        assert thumbnail.aspect_ratio == pytest.approx(expected_ratio)
    
    def test_file_size_estimate_property(self, thumbnail):
        """ファイルサイズ推定プロパティのテスト"""
        expected_size = 720 * 1280 * 3
        assert thumbnail.file_size_estimate == expected_size
    
    def test_is_high_quality_true(self, thumbnail):
        """高品質判定（True）のテスト"""
        assert thumbnail.is_high_quality()
    
    def test_is_high_quality_false(self, thumbnail_image):
        """高品質判定（False）のテスト"""
        low_quality_thumbnail = Thumbnail(
            image=thumbnail_image,
            timestamp_seconds=10.5,
            frame_index=315,
            quality_score=0.4
        )
        assert not low_quality_thumbnail.is_high_quality()
    
    def test_timestamp_formatted_property(self, thumbnail):
        """フォーマット済みタイムスタンプのテスト"""
        formatted = thumbnail.timestamp_formatted
        assert "00:10" in formatted or "10.5" in formatted


class TestUserSettings:
    """UserSettingsクラスのテスト"""
    
    def test_init_default(self):
        """デフォルト初期化のテスト"""
        settings = UserSettings()
        assert settings.thumbnail_count == 5
        assert settings.output_width == 1920
        assert settings.output_height == 1080
        assert settings.orientation == ThumbnailOrientation.AUTO
    
    def test_init_custom(self):
        """カスタム初期化のテスト"""
        settings = UserSettings(
            thumbnail_count=8,
            output_width=1280,
            output_height=720,
            orientation=ThumbnailOrientation.LANDSCAPE
        )
        assert settings.thumbnail_count == 8
        assert settings.output_width == 1280
        assert settings.output_height == 720
        assert settings.orientation == ThumbnailOrientation.LANDSCAPE
    
    def test_aspect_ratio_property(self):
        """アスペクト比プロパティのテスト"""
        settings = UserSettings(output_width=1920, output_height=1080)
        expected_ratio = 1920 / 1080
        assert settings.aspect_ratio == pytest.approx(expected_ratio)
    
    def test_total_pixels_property(self):
        """総ピクセル数プロパティのテスト"""
        settings = UserSettings(output_width=1920, output_height=1080)
        expected_pixels = 1920 * 1080
        assert settings.total_pixels == expected_pixels
    
    def test_is_valid_true(self):
        """有効設定判定（True）のテスト"""
        settings = UserSettings(
            thumbnail_count=5,
            output_width=1280,
            output_height=720
        )
        assert settings.is_valid()
    
    def test_is_valid_false_count(self):
        """有効設定判定（False：カウント）のテスト"""
        settings = UserSettings(thumbnail_count=0)
        assert not settings.is_valid()
    
    def test_is_valid_false_dimensions(self):
        """有効設定判定（False：サイズ）のテスト"""
        settings = UserSettings(output_width=0, output_height=720)
        assert not settings.is_valid()
    
    def test_to_dict(self):
        """辞書変換のテスト"""
        settings = UserSettings(
            thumbnail_count=3,
            output_width=800,
            output_height=600
        )
        
        settings_dict = settings.to_dict()
        
        assert settings_dict['thumbnail_count'] == 3
        assert settings_dict['output_width'] == 800
        assert settings_dict['output_height'] == 600
        assert 'orientation' in settings_dict
    
    def test_from_dict(self):
        """辞書からの復元テスト"""
        settings_dict = {
            'thumbnail_count': 7,
            'output_width': 1600,
            'output_height': 900,
            'orientation': 'PORTRAIT'
        }
        
        settings = UserSettings.from_dict(settings_dict)
        
        assert settings.thumbnail_count == 7
        assert settings.output_width == 1600
        assert settings.output_height == 900
        assert settings.orientation == ThumbnailOrientation.PORTRAIT


class TestVideoFile:
    """VideoFileクラスのテスト"""
    
    @pytest.fixture
    def video_path(self):
        """テスト用動画パス"""
        return Path("/test/sample_video.mp4")
    
    @pytest.fixture
    def video_file(self, video_path):
        """テスト用VideoFile"""
        return VideoFile(
            file_path=video_path,
            frame_count=3000,
            fps=30.0,
            duration=100.0,
            file_size=52428800  # 50MB
        )
    
    def test_init(self, video_file, video_path):
        """初期化のテスト"""
        assert video_file.file_path == video_path
        assert video_file.frame_count == 3000
        assert video_file.fps == 30.0
        assert video_file.duration == 100.0
        assert video_file.file_size == 52428800
        assert video_file.status == VideoFileStatus.CREATED
    
    def test_file_size_mb_property(self, video_file):
        """ファイルサイズ（MB）プロパティのテスト"""
        expected_mb = 52428800 / (1024 * 1024)
        assert video_file.file_size_mb == pytest.approx(expected_mb)
    
    def test_duration_formatted_property(self, video_file):
        """フォーマット済み時間プロパティのテスト"""
        formatted = video_file.duration_formatted
        assert "01:40" in formatted  # 100秒 = 1分40秒
    
    def test_average_frame_size_property(self, video_file):
        """平均フレームサイズプロパティのテスト"""
        expected_size = 52428800 / 3000
        assert video_file.average_frame_size == pytest.approx(expected_size)
    
    def test_is_valid_true(self, video_file):
        """有効ファイル判定（True）のテスト"""
        assert video_file.is_valid()
    
    def test_is_valid_false_frame_count(self, video_path):
        """有効ファイル判定（False：フレーム数）のテスト"""
        invalid_video = VideoFile(
            file_path=video_path,
            frame_count=0,
            fps=30.0,
            duration=100.0
        )
        assert not invalid_video.is_valid()
    
    def test_is_valid_false_fps(self, video_path):
        """有効ファイル判定（False：FPS）のテスト"""
        invalid_video = VideoFile(
            file_path=video_path,
            frame_count=3000,
            fps=0.0,
            duration=100.0
        )
        assert not invalid_video.is_valid()
    
    def test_update_status(self, video_file):
        """ステータス更新のテスト"""
        assert video_file.status == VideoFileStatus.CREATED
        
        video_file.update_status(VideoFileStatus.LOADING)
        assert video_file.status == VideoFileStatus.LOADING
        
        video_file.update_status(VideoFileStatus.LOADED)
        assert video_file.status == VideoFileStatus.LOADED
    
    def test_can_transition_to_true(self, video_file):
        """ステータス遷移可能判定（True）のテスト"""
        assert video_file.can_transition_to(VideoFileStatus.LOADING)
        
        video_file.update_status(VideoFileStatus.LOADING)
        assert video_file.can_transition_to(VideoFileStatus.LOADED)
    
    def test_can_transition_to_false(self, video_file):
        """ステータス遷移可能判定（False）のテスト"""
        video_file.update_status(VideoFileStatus.LOADED)
        assert not video_file.can_transition_to(VideoFileStatus.LOADING)


class TestThumbnailExtractionJob:
    """ThumbnailExtractionJobクラスのテスト"""
    
    @pytest.fixture
    def video_file(self):
        """テスト用VideoFile"""
        return VideoFile(
            file_path=Path("/test/video.mp4"),
            frame_count=1000,
            fps=30.0,
            duration=33.33
        )
    
    @pytest.fixture
    def user_settings(self):
        """テスト用UserSettings"""
        return UserSettings(
            thumbnail_count=5,
            output_width=1280,
            output_height=720
        )
    
    @pytest.fixture
    def job(self, video_file, user_settings):
        """テスト用ThumbnailExtractionJob"""
        return ThumbnailExtractionJob(
            video_file=video_file,
            settings=user_settings
        )
    
    def test_init(self, job, video_file, user_settings):
        """初期化のテスト"""
        assert job.video_file == video_file
        assert job.settings == user_settings
        assert job.status == JobStatus.PENDING
        assert job.phase == JobPhase.INITIALIZATION
        assert job.progress == 0.0
        assert job.thumbnails == []
    
    def test_estimated_duration_property(self, job):
        """推定時間プロパティのテスト"""
        estimated = job.estimated_duration
        assert isinstance(estimated, float)
        assert estimated > 0
    
    def test_progress_percentage_property(self, job):
        """進捗パーセンテージプロパティのテスト"""
        job.progress = 0.75
        assert job.progress_percentage == 75.0
    
    def test_is_completed_false(self, job):
        """完了判定（False）のテスト"""
        assert not job.is_completed()
    
    def test_is_completed_true(self, job):
        """完了判定（True）のテスト"""
        job.status = JobStatus.COMPLETED
        assert job.is_completed()
    
    def test_is_failed_false(self, job):
        """失敗判定（False）のテスト"""
        assert not job.is_failed()
    
    def test_is_failed_true(self, job):
        """失敗判定（True）のテスト"""
        job.status = JobStatus.FAILED
        assert job.is_failed()
    
    def test_start_job(self, job):
        """ジョブ開始のテスト"""
        job.start_job()
        
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
    
    def test_complete_job(self, job):
        """ジョブ完了のテスト"""
        job.start_job()
        
        thumbnail_image = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        thumbnails = [Thumbnail(
            image=thumbnail_image,
            timestamp_seconds=5.0,
            frame_index=150,
            quality_score=0.8
        )]
        
        job.complete_job(thumbnails)
        
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.progress == 1.0
        assert len(job.thumbnails) == 1
    
    def test_fail_job(self, job):
        """ジョブ失敗のテスト"""
        job.start_job()
        error_message = "Test error"
        
        job.fail_job(error_message)
        
        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert error_message in job.error_message
    
    def test_cancel_job(self, job):
        """ジョブキャンセルのテスト"""
        job.start_job()
        job.cancel_job()
        
        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
    
    def test_update_progress(self, job):
        """進捗更新のテスト"""
        job.start_job()
        job.update_progress(0.5, JobPhase.FACE_DETECTION, "Detecting faces...")
        
        assert job.progress == 0.5
        assert job.phase == JobPhase.FACE_DETECTION
        assert job.status_message == "Detecting faces..."
    
    def test_get_duration_no_completion(self, job):
        """未完了ジョブの実行時間取得テスト"""
        job.start_job()
        duration = job.get_duration()
        
        assert isinstance(duration, float)
        assert duration >= 0
    
    def test_get_duration_completed(self, job):
        """完了ジョブの実行時間取得テスト"""
        job.start_job()
        job.complete_job([])
        
        duration = job.get_duration()
        assert isinstance(duration, float)
        assert duration > 0
    
    def test_to_dict(self, job):
        """辞書変換のテスト"""
        job_dict = job.to_dict()
        
        required_keys = [
            'status', 'phase', 'progress', 'video_file', 'settings',
            'started_at', 'completed_at', 'status_message', 'error_message'
        ]
        
        assert all(key in job_dict for key in required_keys)


class TestEnums:
    """列挙型のテスト"""
    
    def test_thumbnail_orientation_values(self):
        """ThumbnailOrientation値のテスト"""
        assert ThumbnailOrientation.AUTO.value == "auto"
        assert ThumbnailOrientation.LANDSCAPE.value == "landscape"
        assert ThumbnailOrientation.PORTRAIT.value == "portrait"
    
    def test_video_file_status_values(self):
        """VideoFileStatus値のテスト"""
        assert VideoFileStatus.CREATED.value == "created"
        assert VideoFileStatus.LOADING.value == "loading"
        assert VideoFileStatus.LOADED.value == "loaded"
        assert VideoFileStatus.ERROR.value == "error"
    
    def test_job_status_values(self):
        """JobStatus値のテスト"""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"
    
    def test_job_phase_values(self):
        """JobPhase値のテスト"""
        assert JobPhase.INITIALIZATION.value == "initialization"
        assert JobPhase.VIDEO_LOADING.value == "video_loading"
        assert JobPhase.FRAME_EXTRACTION.value == "frame_extraction"
        assert JobPhase.FACE_DETECTION.value == "face_detection"
        assert JobPhase.DIVERSITY_ANALYSIS.value == "diversity_analysis"
        assert JobPhase.THUMBNAIL_GENERATION.value == "thumbnail_generation"
        assert JobPhase.FINALIZATION.value == "finalization"


class TestModelsIntegration:
    """モデル間の統合テスト"""
    
    def test_face_detection_with_frame(self):
        """フレームを使った顔検出結果のテスト"""
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        frame = Frame(
            frame_data=frame_data,
            timestamp_seconds=5.0,
            frame_index=150
        )
        
        bbox = BoundingBox(
            top_left=Point2D(100.0, 150.0),
            bottom_right=Point2D(200.0, 250.0)
        )
        
        face_result = FaceDetectionResult(
            bounding_box=bbox,
            confidence=0.8,
            landmarks=[]
        )
        
        # フレームとの整合性確認
        assert bbox.bottom_right.x <= frame.width
        assert bbox.bottom_right.y <= frame.height
    
    def test_thumbnail_from_frame(self):
        """フレームからサムネイル作成のテスト"""
        frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        frame = Frame(
            frame_data=frame_data,
            timestamp_seconds=10.0,
            frame_index=300
        )
        
        # フレームデータをリサイズしてサムネイル作成
        thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        thumbnail = Thumbnail(
            image=thumbnail_data,
            timestamp_seconds=frame.timestamp_seconds,
            frame_index=frame.frame_index,
            quality_score=0.9
        )
        
        assert thumbnail.timestamp_seconds == frame.timestamp_seconds
        assert thumbnail.frame_index == frame.frame_index
    
    def test_complete_extraction_workflow(self):
        """完全な抽出ワークフローのテスト"""
        # 1. 動画ファイル作成
        video_file = VideoFile(
            file_path=Path("/test/video.mp4"),
            frame_count=1000,
            fps=30.0,
            duration=33.33
        )
        
        # 2. ユーザー設定作成
        settings = UserSettings(
            thumbnail_count=3,
            output_width=1280,
            output_height=720
        )
        
        # 3. ジョブ作成
        job = ThumbnailExtractionJob(
            video_file=video_file,
            settings=settings
        )
        
        # 4. サムネイル作成
        thumbnails = []
        for i in range(3):
            thumbnail_data = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
            thumbnail = Thumbnail(
                image=thumbnail_data,
                timestamp_seconds=i * 10.0,
                frame_index=i * 300,
                quality_score=0.8 + i * 0.05
            )
            thumbnails.append(thumbnail)
        
        # 5. ジョブ完了
        job.start_job()
        job.complete_job(thumbnails)
        
        # 6. 整合性確認
        assert job.is_completed()
        assert len(job.thumbnails) == settings.thumbnail_count
        assert all(t.width == settings.output_width for t in job.thumbnails)
        assert all(t.height == settings.output_height for t in job.thumbnails)
