"""
動画処理サービスのAPI契約定義
VideoProcessor クラスの公開インターフェース仕様
"""

from abc import ABC, abstractmethod
from typing import List, Iterator, Optional
from pathlib import Path
from ..models import VideoFile, Frame


class VideoProcessorContract(ABC):
    """動画処理サービスの契約インターフェース"""
    
    @abstractmethod
    def load_video(self, file_path: Path) -> VideoFile:
        """
        動画ファイルを読み込んで VideoFile オブジェクトを作成
        
        Args:
            file_path: 動画ファイルのパス
            
        Returns:
            VideoFile: 動画ファイル情報
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            InvalidVideoFormatError: MP4以外の形式
            CorruptedVideoError: 動画ファイルが破損
            UnsupportedCodecError: 対応していないコーデック
        """
        pass
    
    @abstractmethod
    def extract_frames(self, video_file: VideoFile, interval_seconds: float = 1.0) -> Iterator[Frame]:
        """
        動画からフレームを抽出（ジェネレータとして返す）
        
        Args:
            video_file: 処理対象の動画ファイル
            interval_seconds: フレーム抽出間隔（秒）
            
        Yields:
            Frame: 抽出されたフレーム
            
        Raises:
            VideoProcessingError: フレーム抽出に失敗
            InsufficientMemoryError: メモリ不足
        """
        pass
    
    @abstractmethod
    def detect_scene_changes(self, frames: List[Frame], threshold: float = 0.3) -> List[Frame]:
        """
        シーンチェンジを検出して重要フレームを選出
        
        Args:
            frames: 解析対象フレームのリスト
            threshold: シーンチェンジ検出の閾値
            
        Returns:
            List[Frame]: シーンチェンジが検出されたフレーム
            
        Raises:
            InvalidThresholdError: 閾値が範囲外
        """
        pass
    
    @abstractmethod
    def calculate_quality_score(self, frame: Frame) -> float:
        """
        フレームの品質スコアを計算
        
        Args:
            frame: 評価対象フレーム
            
        Returns:
            float: 品質スコア（0.0-1.0）
            
        Raises:
            InvalidFrameDataError: フレームデータが無効
        """
        pass
    
    @abstractmethod
    def get_video_info(self, file_path: Path) -> dict:
        """
        動画ファイルの詳細情報を取得
        
        Args:
            file_path: 動画ファイルのパス
            
        Returns:
            dict: 動画情報（duration, fps, width, height等）
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            InvalidVideoFormatError: 無効な動画形式
        """
        pass
    
    @abstractmethod
    def validate_video_file(self, file_path: Path) -> bool:
        """
        動画ファイルの有効性を検証
        
        Args:
            file_path: 検証対象ファイルのパス
            
        Returns:
            bool: 有効な場合True
            
        Raises:
            FileNotFoundError: ファイルが存在しない
        """
        pass


# カスタム例外クラス
class VideoProcessingError(Exception):
    """動画処理関連の基底例外"""
    pass


class InvalidVideoFormatError(VideoProcessingError):
    """無効な動画形式エラー"""
    pass


class CorruptedVideoError(VideoProcessingError):
    """破損した動画ファイルエラー"""
    pass


class UnsupportedCodecError(VideoProcessingError):
    """対応していないコーデックエラー"""
    pass


class InsufficientMemoryError(VideoProcessingError):
    """メモリ不足エラー"""
    pass


class InvalidThresholdError(VideoProcessingError):
    """無効な閾値エラー"""
    pass


class InvalidFrameDataError(VideoProcessingError):
    """無効なフレームデータエラー"""
    pass
