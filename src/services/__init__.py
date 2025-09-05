"""
サービスパッケージ

動画サムネイル抽出機能のコアサービスクラスを定義します。
OpenCV、MediaPipe、画像処理技術を活用した高品質なサムネイル生成を提供します。

サービス一覧:
- VideoProcessor: 動画処理・フレーム抽出・シーンチェンジ検出
- FaceDetector: 顔検出・MediaPipe統合・バッチ処理
- DiversitySelector: 多様性スコア計算・フレーム選択
- ThumbnailExtractor: サムネイル生成・リサイズ・PNG保存
"""

from .video_processor import VideoProcessor
from .face_detector import FaceDetector
from .diversity_selector import DiversitySelector
from .thumbnail_extractor import ThumbnailExtractor

__all__ = [
    "VideoProcessor",
    "FaceDetector", 
    "DiversitySelector",
    "ThumbnailExtractor",
]

# パッケージバージョン
__version__ = "1.0.0"

# パッケージメタデータ
__author__ = "s-anzai"
__description__ = "動画サムネイル抽出機能のコアサービス"