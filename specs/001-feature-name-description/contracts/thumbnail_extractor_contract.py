"""
サムネイル抽出サービスのAPI契約定義
ThumbnailExtractor クラスの公開インターフェース仕様
"""

from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Callable
from ..models import Frame, Thumbnail, UserSettings, ThumbnailExtractionJob


class ThumbnailExtractorContract(ABC):
    """サムネイル抽出サービスの契約インターフェース"""
    
    @abstractmethod
    def extract_thumbnails(
        self, 
        frames: List[Frame], 
        settings: UserSettings,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[Thumbnail]:
        """
        フレームからサムネイルを抽出
        
        Args:
            frames: サムネイル抽出対象フレーム
            settings: ユーザー設定
            progress_callback: 進捗通知コールバック
            
        Returns:
            List[Thumbnail]: 生成されたサムネイル
            
        Raises:
            ThumbnailExtractionError: サムネイル抽出に失敗
            InsufficientFramesError: フレーム数が不足
            InvalidSettingsError: 設定が無効
        """
        pass
    
    @abstractmethod
    def calculate_diversity_scores(self, frames: List[Frame]) -> List[float]:
        """
        フレーム間の構図多様性スコアを計算
        
        Args:
            frames: 多様性評価対象フレーム
            
        Returns:
            List[float]: 各フレームの多様性スコア
            
        Raises:
            DiversityCalculationError: 多様性計算に失敗
        """
        pass
    
    @abstractmethod
    def select_diverse_frames(
        self, 
        frames: List[Frame], 
        count: int,
        diversity_weight: float = 0.7
    ) -> List[Frame]:
        """
        多様性を考慮してフレームを選出
        
        Args:
            frames: 選出対象フレーム
            count: 選出する枚数
            diversity_weight: 多様性の重み（0.0-1.0）
            
        Returns:
            List[Frame]: 選出されたフレーム
            
        Raises:
            InvalidCountError: 選出枚数が無効
            InvalidWeightError: 重みが範囲外
        """
        pass
    
    @abstractmethod
    def generate_thumbnail(self, frame: Frame, settings: UserSettings) -> Thumbnail:
        """
        単一フレームからサムネイルを生成
        
        Args:
            frame: サムネイル生成元フレーム
            settings: 生成設定
            
        Returns:
            Thumbnail: 生成されたサムネイル
            
        Raises:
            ThumbnailGenerationError: サムネイル生成に失敗
            InvalidResolutionError: 解像度設定が無効
        """
        pass
    
    @abstractmethod
    def resize_image(
        self, 
        image_data, 
        target_width: int, 
        target_height: int,
        maintain_aspect_ratio: bool = True
    ):
        """
        画像をリサイズ
        
        Args:
            image_data: リサイズ対象画像データ
            target_width: 目標幅
            target_height: 目標高さ
            maintain_aspect_ratio: アスペクト比維持フラグ
            
        Returns:
            リサイズ後画像データ
            
        Raises:
            ImageResizeError: リサイズに失敗
            InvalidDimensionsError: 寸法が無効
        """
        pass
    
    @abstractmethod
    def crop_to_orientation(self, image_data, orientation: str):
        """
        指定した向き（縦型/横型）に画像をクロップ
        
        Args:
            image_data: クロップ対象画像データ
            orientation: 目標向き（"portrait" or "landscape"）
            
        Returns:
            クロップ後画像データ
            
        Raises:
            InvalidOrientationError: 向き指定が無効
            CropError: クロップに失敗
        """
        pass
    
    @abstractmethod
    def save_thumbnail(self, thumbnail: Thumbnail, file_path: str) -> bool:
        """
        サムネイルをPNGファイルとして保存
        
        Args:
            thumbnail: 保存対象サムネイル
            file_path: 保存先パス
            
        Returns:
            bool: 保存成功時True
            
        Raises:
            FileSaveError: ファイル保存に失敗
            PermissionError: 書き込み権限なし
        """
        pass
    
    @abstractmethod
    def save_thumbnails_batch(self, thumbnails: List[Thumbnail], directory: str) -> List[str]:
        """
        複数サムネイルを一括保存
        
        Args:
            thumbnails: 保存対象サムネイルリスト
            directory: 保存先ディレクトリ
            
        Returns:
            List[str]: 保存されたファイルパスのリスト
            
        Raises:
            BatchSaveError: 一括保存に失敗
            DirectoryError: ディレクトリアクセスエラー
        """
        pass
    
    @abstractmethod
    def create_extraction_job(
        self, 
        frames: List[Frame], 
        settings: UserSettings
    ) -> ThumbnailExtractionJob:
        """
        サムネイル抽出ジョブを作成
        
        Args:
            frames: 処理対象フレーム
            settings: 抽出設定
            
        Returns:
            ThumbnailExtractionJob: 作成されたジョブ
            
        Raises:
            JobCreationError: ジョブ作成に失敗
        """
        pass


# カスタム例外クラス
class ThumbnailExtractionError(Exception):
    """サムネイル抽出関連の基底例外"""
    pass


class InsufficientFramesError(ThumbnailExtractionError):
    """フレーム数不足エラー"""
    pass


class InvalidSettingsError(ThumbnailExtractionError):
    """無効な設定エラー"""
    pass


class DiversityCalculationError(ThumbnailExtractionError):
    """多様性計算エラー"""
    pass


class InvalidCountError(ThumbnailExtractionError):
    """無効な枚数エラー"""
    pass


class InvalidWeightError(ThumbnailExtractionError):
    """無効な重みエラー"""
    pass


class ThumbnailGenerationError(ThumbnailExtractionError):
    """サムネイル生成エラー"""
    pass


class InvalidResolutionError(ThumbnailExtractionError):
    """無効な解像度エラー"""
    pass


class ImageResizeError(ThumbnailExtractionError):
    """画像リサイズエラー"""
    pass


class InvalidDimensionsError(ThumbnailExtractionError):
    """無効な寸法エラー"""
    pass


class InvalidOrientationError(ThumbnailExtractionError):
    """無効な向きエラー"""
    pass


class CropError(ThumbnailExtractionError):
    """クロップエラー"""
    pass


class FileSaveError(ThumbnailExtractionError):
    """ファイル保存エラー"""
    pass


class BatchSaveError(ThumbnailExtractionError):
    """一括保存エラー"""
    pass


class DirectoryError(ThumbnailExtractionError):
    """ディレクトリエラー"""
    pass


class JobCreationError(ThumbnailExtractionError):
    """ジョブ作成エラー"""
    pass
