"""
データモデルパッケージ

動画サムネイル抽出機能で使用するデータモデルを定義します。
ローカル環境での効率的な処理と、ユーザーフレンドリーなインターフェースを重視した設計です。

モデル一覧:
- Point2D: 2D座標点
- BoundingBox: 境界ボックス
- FaceDetectionResult: 顔検出結果
- VideoFile: 動画ファイル
- Frame: フレーム
- UserSettings: ユーザー設定
- Thumbnail: サムネイル
- ThumbnailExtractionJob: サムネイル抽出ジョブ
"""

from .point_2d import Point2D
from .bounding_box import BoundingBox
from .face_detection_result import FaceDetectionResult
from .video_file import VideoFile
from .frame import Frame
from .user_settings import UserSettings, ThumbnailOrientation
from .thumbnail import Thumbnail
from .thumbnail_extraction_job import ThumbnailExtractionJob, JobStatus

__all__ = [
    # 基本座標・境界クラス
    "Point2D",
    "BoundingBox",
    
    # 検出結果クラス
    "FaceDetectionResult",
    
    # 動画関連クラス
    "VideoFile",
    "Frame",
    
    # 設定・UI関連クラス
    "UserSettings",
    "ThumbnailOrientation",
    
    # 出力関連クラス
    "Thumbnail",
    "ThumbnailExtractionJob",
    "JobStatus",
]

# パッケージバージョン
__version__ = "1.0.0"

# パッケージメタデータ
__author__ = "s-anzai"
__description__ = "動画サムネイル抽出機能のデータモデル"