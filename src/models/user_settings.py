"""
UserSettings（ユーザー設定）データモデル

ユーザーの設定情報を表すクラスです。列挙型とバリデーション機能を含みます。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class ThumbnailOrientation(Enum):
    """サムネイルの向き"""
    LANDSCAPE = "landscape"  # 横型
    PORTRAIT = "portrait"    # 縦型
    AUTO = "auto"           # 自動選択


class FaceSizePreference(Enum):
    """顔サイズの優先度"""
    LARGE = "large"         # 大きい顔を優先
    MEDIUM = "medium"       # 中程度の顔を優先
    SMALL = "small"         # 小さい顔も含める
    BALANCED = "balanced"   # バランス重視


@dataclass
class UserSettings:
    """ユーザー設定を表すクラス"""
    
    # 出力設定
    output_width: int = 1920                           # 出力幅（ピクセル）
    output_height: int = 1080                          # 出力高さ（ピクセル）
    thumbnail_count: int = 5                           # サムネイル生成枚数
    # 向きは output_width と output_height から自動判定（幅 < 高さ = 縦型、幅 > 高さ = 横型）
    
    # ファイル設定
    output_directory: Path = field(default_factory=lambda: Path.home() / "Downloads")  # 出力ディレクトリ
    file_name_prefix: str = "thumbnail"                # ファイル名プレフィックス
    output_format: str = "PNG"                         # 出力形式（PNG固定）
    
    # 品質設定
    quality_threshold: float = 0.7                     # 品質閾値
    diversity_weight: float = 0.8                      # 多様性重み
    face_size_preference: FaceSizePreference = FaceSizePreference.BALANCED  # 顔サイズ優先度
    
    # 処理設定
    frame_interval: float = 1.0                        # フレーム抽出間隔（秒）
    scene_change_threshold: float = 0.3                # シーンチェンジ閾値
    face_confidence_threshold: float = 0.5             # 顔検出信頼度閾値
    
    # メタデータ
    created_at: Optional[str] = None                   # 設定作成日時
    custom_settings: Dict[str, Any] = field(default_factory=dict)  # カスタム設定
    
    @property
    def is_portrait_output(self) -> bool:
        """出力が縦型かどうか（幅 < 高さ）"""
        return self.output_width < self.output_height
    
    @property
    def is_landscape_output(self) -> bool:
        """出力が横型かどうか（幅 > 高さ）"""
        return self.output_width > self.output_height

    def __post_init__(self):
        """初期化後のバリデーション"""
        self._validate_output_settings()
        self._validate_file_settings()
        self._validate_quality_settings()
        self._validate_processing_settings()
        
        # output_directoryをPathオブジェクトに変換
        if isinstance(self.output_directory, str):
            self.output_directory = Path(self.output_directory)
        elif not isinstance(self.output_directory, Path):
            raise TypeError("output_directoryはPathオブジェクトまたは文字列である必要があります")
        
        # 出力ディレクトリの絶対パス化
        self.output_directory = self.output_directory.resolve()
    
    def _validate_output_settings(self):
        """出力設定のバリデーション"""
        # 出力サイズの検証
        if not isinstance(self.output_width, int) or self.output_width <= 0:
            raise ValueError(f"output_widthは正の整数である必要があります: {self.output_width}")
        if not isinstance(self.output_height, int) or self.output_height <= 0:
            raise ValueError(f"output_heightは正の整数である必要があります: {self.output_height}")
        
        # 解像度の範囲チェック
        min_size = 240
        max_size = 4096
        if self.output_width < min_size or self.output_width > max_size:
            raise ValueError(f"output_widthは{min_size}-{max_size}の範囲である必要があります: {self.output_width}")
        if self.output_height < min_size or self.output_height > max_size:
            raise ValueError(f"output_heightは{min_size}-{max_size}の範囲である必要があります: {self.output_height}")
        
        # サムネイル枚数の検証
        if not isinstance(self.thumbnail_count, int) or self.thumbnail_count <= 0:
            raise ValueError(f"thumbnail_countは正の整数である必要があります: {self.thumbnail_count}")
        if self.thumbnail_count > 20:
            raise ValueError(f"thumbnail_countは20以下である必要があります: {self.thumbnail_count}")
        
        # 向きの検証
        if not isinstance(self.orientation, ThumbnailOrientation):
            raise TypeError("orientationはThumbnailOrientationである必要があります")
    
    def _validate_file_settings(self):
        """ファイル設定のバリデーション"""
        # ファイル名プレフィックスの検証
        if not isinstance(self.file_name_prefix, str):
            raise TypeError("file_name_prefixは文字列である必要があります")
        if not self.file_name_prefix.strip():
            raise ValueError("file_name_prefixは空文字列にできません")
        
        # 無効な文字のチェック
        invalid_chars = '<>:"/\\|?*'
        if any(char in self.file_name_prefix for char in invalid_chars):
            raise ValueError(f"file_name_prefixに無効な文字が含まれています: {invalid_chars}")
        
        # 出力形式の検証（PNG固定）
        if not isinstance(self.output_format, str):
            raise TypeError("output_formatは文字列である必要があります")
        if self.output_format.upper() != "PNG":
            raise ValueError(f"output_formatはPNGのみサポートしています: {self.output_format}")
    
    def _validate_quality_settings(self):
        """品質設定のバリデーション"""
        # 品質閾値の検証
        if not isinstance(self.quality_threshold, (int, float)):
            raise TypeError("quality_thresholdは数値である必要があります")
        if not (0.0 <= self.quality_threshold <= 1.0):
            raise ValueError(f"quality_thresholdは0-1の範囲である必要があります: {self.quality_threshold}")
        
        # 多様性重みの検証
        if not isinstance(self.diversity_weight, (int, float)):
            raise TypeError("diversity_weightは数値である必要があります")
        if not (0.0 <= self.diversity_weight <= 1.0):
            raise ValueError(f"diversity_weightは0-1の範囲である必要があります: {self.diversity_weight}")
        
        # 顔サイズ優先度の検証
        if not isinstance(self.face_size_preference, FaceSizePreference):
            raise TypeError("face_size_preferenceはFaceSizePreferenceである必要があります")
    
    def _validate_processing_settings(self):
        """処理設定のバリデーション"""
        # フレーム間隔の検証
        if not isinstance(self.frame_interval, (int, float)):
            raise TypeError("frame_intervalは数値である必要があります")
        if self.frame_interval <= 0:
            raise ValueError(f"frame_intervalは正の値である必要があります: {self.frame_interval}")
        if self.frame_interval > 10.0:
            raise ValueError(f"frame_intervalは10秒以下である必要があります: {self.frame_interval}")
        
        # シーンチェンジ閾値の検証
        if not isinstance(self.scene_change_threshold, (int, float)):
            raise TypeError("scene_change_thresholdは数値である必要があります")
        if not (0.0 <= self.scene_change_threshold <= 1.0):
            raise ValueError(f"scene_change_thresholdは0-1の範囲である必要があります: {self.scene_change_threshold}")
        
        # 顔検出信頼度閾値の検証
        if not isinstance(self.face_confidence_threshold, (int, float)):
            raise TypeError("face_confidence_thresholdは数値である必要があります")
        if not (0.0 <= self.face_confidence_threshold <= 1.0):
            raise ValueError(f"face_confidence_thresholdは0-1の範囲である必要があります: {self.face_confidence_threshold}")
    
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比"""
        return self.output_width / self.output_height
    
    @property
    def resolution_category(self) -> str:
        """解像度カテゴリ"""
        if self.output_width >= 3840 and self.output_height >= 2160:
            return "4K"
        elif self.output_width >= 1920 and self.output_height >= 1080:
            return "FHD"
        elif self.output_width >= 1280 and self.output_height >= 720:
            return "HD"
        else:
            return "SD"
    
    @property
    def is_landscape_output(self) -> bool:
        """横型出力かどうか"""
        return self.output_width > self.output_height
    
    @property
    def is_portrait_output(self) -> bool:
        """縦型出力かどうか"""
        return self.output_height > self.output_width
    
    @property
    def estimated_file_size_mb(self) -> float:
        """推定ファイルサイズ（MB）- PNG形式"""
        # PNGの場合、圧縮率を考慮した推定
        pixels = self.output_width * self.output_height
        bytes_per_pixel = 3  # RGB
        compression_ratio = 0.7  # PNG圧縮率
        
        estimated_bytes = pixels * bytes_per_pixel * compression_ratio
        return estimated_bytes / (1024 * 1024)
    
    @property
    def total_estimated_file_size_mb(self) -> float:
        """全サムネイルの推定ファイルサイズ（MB）"""
        return self.estimated_file_size_mb * self.thumbnail_count
    
    def create_output_directory(self) -> bool:
        """出力ディレクトリを作成"""
        try:
            self.output_directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"出力ディレクトリ作成エラー: {e}")
            return False
    
    def validate_output_directory(self) -> bool:
        """出力ディレクトリの書き込み権限をチェック"""
        try:
            # ディレクトリが存在しない場合は作成を試行
            if not self.output_directory.exists():
                if not self.create_output_directory():
                    return False
            
            # 書き込み権限のテスト
            test_file = self.output_directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
            
        except Exception:
            return False
    
    def get_output_filename(self, index: int, timestamp: float = None) -> str:
        """出力ファイル名を生成"""
        if timestamp is not None:
            # タイムスタンプ付きファイル名
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            return f"{self.file_name_prefix}_{index:03d}_{minutes:02d}m{seconds:02d}s.png"
        else:
            # インデックスのみのファイル名
            return f"{self.file_name_prefix}_{index:03d}.png"
    
    def get_output_filepath(self, index: int, timestamp: float = None) -> Path:
        """出力ファイルパスを生成"""
        filename = self.get_output_filename(index, timestamp)
        return self.output_directory / filename
    
    def apply_face_size_filter(self, min_size: float) -> float:
        """顔サイズ優先度に基づいてフィルタリング閾値を調整"""
        base_size = min_size
        
        if self.face_size_preference == FaceSizePreference.LARGE:
            return base_size * 2.0  # より大きい顔のみ
        elif self.face_size_preference == FaceSizePreference.MEDIUM:
            return base_size * 1.5  # 中程度以上の顔
        elif self.face_size_preference == FaceSizePreference.SMALL:
            return base_size * 0.5  # 小さい顔も含める
        else:  # BALANCED
            return base_size
    
    def get_diversity_config(self) -> Dict[str, float]:
        """多様性選択の設定を取得"""
        return {
            'diversity_weight': self.diversity_weight,
            'quality_weight': 1.0 - self.diversity_weight,
            'face_weight': 0.3,
            'scene_weight': 0.2,
            'color_weight': 0.2,
            'composition_weight': 0.3
        }
    
    def add_custom_setting(self, key: str, value: Any):
        """カスタム設定を追加"""
        self.custom_settings[key] = value
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """カスタム設定を取得"""
        return self.custom_settings.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを出力"""
        return {
            # 出力設定
            'output_width': self.output_width,
            'output_height': self.output_height,
            'thumbnail_count': self.thumbnail_count,
            'orientation': self.orientation.value,
            'aspect_ratio': self.aspect_ratio,
            'resolution_category': self.resolution_category,
            
            # ファイル設定
            'output_directory': str(self.output_directory),
            'file_name_prefix': self.file_name_prefix,
            'output_format': self.output_format,
            
            # 品質設定
            'quality_threshold': self.quality_threshold,
            'diversity_weight': self.diversity_weight,
            'face_size_preference': self.face_size_preference.value,
            
            # 処理設定
            'frame_interval': self.frame_interval,
            'scene_change_threshold': self.scene_change_threshold,
            'face_confidence_threshold': self.face_confidence_threshold,
            
            # 推定値
            'estimated_file_size_mb': self.estimated_file_size_mb,
            'total_estimated_file_size_mb': self.total_estimated_file_size_mb,
            
            # メタデータ
            'created_at': self.created_at,
            'custom_settings': self.custom_settings.copy()
        }
    
    @classmethod
    def create_preset(cls, preset_name: str) -> 'UserSettings':
        """プリセット設定を作成"""
        presets = {
            'high_quality': cls(
                output_width=1920,
                output_height=1080,
                thumbnail_count=5,
                quality_threshold=0.8,
                diversity_weight=0.7,
                face_size_preference=FaceSizePreference.LARGE
            ),
            'fast_generation': cls(
                output_width=1280,
                output_height=720,
                thumbnail_count=3,
                quality_threshold=0.6,
                diversity_weight=0.9,
                frame_interval=2.0
            ),
            'high_diversity': cls(
                output_width=1920,
                output_height=1080,
                thumbnail_count=8,
                quality_threshold=0.6,
                diversity_weight=0.9,
                face_size_preference=FaceSizePreference.BALANCED
            ),
            'portrait_mode': cls(
                output_width=1080,
                output_height=1920,
                orientation=ThumbnailOrientation.PORTRAIT,
                thumbnail_count=4,
                quality_threshold=0.7,
                diversity_weight=0.8
            )
        }
        
        if preset_name not in presets:
            raise ValueError(f"不明なプリセット: {preset_name}. 利用可能: {list(presets.keys())}")
        
        return presets[preset_name]
    
    def copy(self) -> 'UserSettings':
        """設定のコピーを作成"""
        from copy import deepcopy
        return deepcopy(self)
    
    def __str__(self) -> str:
        """文字列表現"""
        return (f"UserSettings({self.output_width}x{self.output_height}, "
                f"count={self.thumbnail_count}, {self.orientation.value})")
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"UserSettings(output_size={self.output_width}x{self.output_height}, "
                f"count={self.thumbnail_count}, orientation={self.orientation.value})")
    
    def __eq__(self, other) -> bool:
        """等価比較"""
        if not isinstance(other, UserSettings):
            return False
        
        # 主要な設定項目で比較
        return (self.output_width == other.output_width and
                self.output_height == other.output_height and
                self.thumbnail_count == other.thumbnail_count and
                self.orientation == other.orientation and
                self.quality_threshold == other.quality_threshold and
                self.diversity_weight == other.diversity_weight)
