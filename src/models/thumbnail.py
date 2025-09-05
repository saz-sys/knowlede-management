"""
Thumbnail（サムネイル）データモデル

生成されたサムネイルの情報を表すクラスです。
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .frame import Frame
    from .user_settings import UserSettings


@dataclass
class Thumbnail:
    """サムネイルを表すクラス"""
    
    source_frame: 'Frame'                       # 元となるフレーム
    user_settings: 'UserSettings'               # 生成時の設定
    image_data: np.ndarray                      # サムネイル画像データ
    diversity_score: float = 0.0                # 多様性スコア
    total_score: float = 0.0                   # 総合スコア
    file_path: Optional[Path] = None            # 保存ファイルパス
    is_selected: bool = False                   # ユーザー選択状態
    created_at: datetime = field(default_factory=datetime.now)  # 生成時刻
    metadata: Dict[str, Any] = field(default_factory=dict)  # 追加メタデータ
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        # source_frameの型チェック（循環importを避けるため遅延評価）
        from .frame import Frame
        if not isinstance(self.source_frame, Frame):
            raise TypeError("source_frameはFrameインスタンスである必要があります")
        
        # user_settingsの型チェック
        from .user_settings import UserSettings
        if not isinstance(self.user_settings, UserSettings):
            raise TypeError("user_settingsはUserSettingsインスタンスである必要があります")
        
        # 画像データのバリデーション
        if not isinstance(self.image_data, np.ndarray):
            raise TypeError("image_dataはnumpy.ndarrayである必要があります")
        
        # 画像データの形状チェック（高さ, 幅, チャンネル）
        if len(self.image_data.shape) != 3:
            raise ValueError(f"image_dataは3次元配列である必要があります: {self.image_data.shape}")
        
        height, width, channels = self.image_data.shape
        if channels != 3:
            raise ValueError(f"image_dataは3チャンネル（RGB）である必要があります: {channels}チャンネル")
        
        # 設定との整合性チェック
        if width != self.user_settings.output_width or height != self.user_settings.output_height:
            print(f"警告: サムネイルサイズが設定と異なります。"
                  f"実際: {width}x{height}, 設定: {self.user_settings.output_width}x{self.user_settings.output_height}")
        
        # スコアのバリデーション
        if not isinstance(self.diversity_score, (int, float)):
            raise TypeError("diversity_scoreは数値である必要があります")
        if not (0.0 <= self.diversity_score <= 1.0):
            raise ValueError(f"diversity_scoreは0-1の範囲である必要があります: {self.diversity_score}")
        
        if not isinstance(self.total_score, (int, float)):
            raise TypeError("total_scoreは数値である必要があります")
        if not (0.0 <= self.total_score <= 1.0):
            raise ValueError(f"total_scoreは0-1の範囲である必要があります: {self.total_score}")
        
        # ファイルパスの型チェックと変換
        if self.file_path is not None:
            if isinstance(self.file_path, str):
                self.file_path = Path(self.file_path)
            elif not isinstance(self.file_path, Path):
                raise TypeError("file_pathはPathオブジェクト、文字列、またはNoneである必要があります")
    
    @property
    def width(self) -> int:
        """サムネイル幅"""
        return self.image_data.shape[1]
    
    @property
    def height(self) -> int:
        """サムネイル高さ"""
        return self.image_data.shape[0]
    
    @property
    def channels(self) -> int:
        """チャンネル数"""
        return self.image_data.shape[2]
    
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比"""
        return self.width / self.height if self.height > 0 else 0.0
    
    @property
    def pixel_count(self) -> int:
        """総ピクセル数"""
        return self.width * self.height
    
    @property
    def is_landscape(self) -> bool:
        """横型かどうか"""
        return self.width > self.height
    
    @property
    def is_portrait(self) -> bool:
        """縦型かどうか"""
        return self.height > self.width
    
    @property
    def is_square(self) -> bool:
        """正方形かどうか"""
        return self.width == self.height
    
    @property
    def file_name(self) -> Optional[str]:
        """ファイル名"""
        return self.file_path.name if self.file_path else None
    
    @property
    def file_size_bytes(self) -> Optional[int]:
        """ファイルサイズ（バイト）"""
        if self.file_path and self.file_path.exists():
            return self.file_path.stat().st_size
        return None
    
    @property
    def file_size_mb(self) -> Optional[float]:
        """ファイルサイズ（MB）"""
        size_bytes = self.file_size_bytes
        return size_bytes / (1024 * 1024) if size_bytes else None
    
    @property
    def is_saved(self) -> bool:
        """ファイルに保存済みかどうか"""
        return self.file_path is not None and self.file_path.exists()
    
    @property
    def source_timestamp(self) -> float:
        """元フレームのタイムスタンプ"""
        return self.source_frame.timestamp
    
    @property
    def source_timestamp_formatted(self) -> str:
        """フォーマットされた元フレームのタイムスタンプ"""
        return self.source_frame.timestamp_formatted
    
    @property
    def has_faces(self) -> bool:
        """元フレームに顔があるかどうか"""
        return self.source_frame.has_faces
    
    @property
    def face_count(self) -> int:
        """元フレームの顔数"""
        return self.source_frame.face_count
    
    @property
    def quality_category(self) -> str:
        """品質カテゴリ"""
        if self.total_score >= 0.8:
            return "Excellent"
        elif self.total_score >= 0.6:
            return "Good"
        elif self.total_score >= 0.4:
            return "Fair"
        else:
            return "Poor"
    
    @property
    def diversity_category(self) -> str:
        """多様性カテゴリ"""
        if self.diversity_score >= 0.8:
            return "Highly Diverse"
        elif self.diversity_score >= 0.6:
            return "Diverse"
        elif self.diversity_score >= 0.4:
            return "Moderately Diverse"
        else:
            return "Similar"
    
    def calculate_brightness(self) -> float:
        """サムネイルの平均輝度を計算（0-1）"""
        # RGBから輝度に変換（ITU-R BT.709係数）
        gray = np.dot(self.image_data, [0.2126, 0.7152, 0.0722])
        return float(np.mean(gray) / 255.0)
    
    def calculate_contrast(self) -> float:
        """サムネイルのコントラストを計算（0-1）"""
        # グレースケール変換
        gray = np.dot(self.image_data, [0.2126, 0.7152, 0.0722])
        
        # 標準偏差ベースのコントラスト
        contrast = float(np.std(gray) / 255.0)
        return min(1.0, contrast)
    
    def calculate_color_richness(self) -> float:
        """色の豊かさを計算（0-1）"""
        # 各チャンネルの標準偏差を使用
        r_std = np.std(self.image_data[:, :, 0])
        g_std = np.std(self.image_data[:, :, 1])
        b_std = np.std(self.image_data[:, :, 2])
        
        # 正規化された色の豊かさ
        avg_color_std = (r_std + g_std + b_std) / 3.0
        return min(1.0, avg_color_std / 255.0)
    
    def update_quality_metrics(self):
        """品質メトリクスを更新"""
        brightness = self.calculate_brightness()
        contrast = self.calculate_contrast()
        color_richness = self.calculate_color_richness()
        
        # メタデータに保存
        self.metadata.update({
            'brightness': brightness,
            'contrast': contrast,
            'color_richness': color_richness,
            'face_quality': self.source_frame.primary_face.overall_quality_score if self.has_faces else 0.0
        })
        
        # 総合スコアの再計算（多様性スコアと品質メトリクスを組み合わせ）
        quality_metrics_score = (brightness * 0.2 + contrast * 0.3 + color_richness * 0.2)
        frame_quality_score = self.source_frame.quality_score * 0.3
        
        self.total_score = (
            self.diversity_score * self.user_settings.diversity_weight +
            (quality_metrics_score + frame_quality_score) * (1 - self.user_settings.diversity_weight)
        )
    
    def save(self, output_path: Optional[Path] = None, overwrite: bool = False) -> bool:
        """サムネイルをファイルに保存"""
        try:
            # 保存パスの決定
            if output_path:
                save_path = Path(output_path)
            elif self.file_path:
                save_path = self.file_path
            else:
                # デフォルトファイル名を生成
                timestamp_int = int(self.source_timestamp)
                filename = self.user_settings.get_output_filename(0, self.source_timestamp)
                save_path = self.user_settings.output_directory / filename
            
            # 既存ファイルの確認
            if save_path.exists() and not overwrite:
                print(f"ファイルが既に存在します: {save_path}")
                return False
            
            # ディレクトリの作成
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # OpenCVを使用してPNG形式で保存
            import cv2
            # RGB → BGR変換
            bgr_image = cv2.cvtColor(self.image_data, cv2.COLOR_RGB2BGR)
            
            # PNG圧縮設定（高品質）
            compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 3]  # 0-9, 3は良いバランス
            
            success = cv2.imwrite(str(save_path), bgr_image, compression_params)
            
            if success:
                self.file_path = save_path
                return True
            else:
                print(f"画像保存に失敗しました: {save_path}")
                return False
                
        except Exception as e:
            print(f"サムネイル保存エラー: {e}")
            return False
    
    def load_from_file(self, file_path: Path) -> bool:
        """ファイルからサムネイル画像を読み込み"""
        try:
            import cv2
            
            # ファイル存在確認
            if not file_path.exists():
                print(f"ファイルが見つかりません: {file_path}")
                return False
            
            # 画像読み込み
            bgr_image = cv2.imread(str(file_path))
            if bgr_image is None:
                print(f"画像読み込みに失敗しました: {file_path}")
                return False
            
            # BGR → RGB変換
            self.image_data = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
            self.file_path = file_path
            
            return True
            
        except Exception as e:
            print(f"サムネイル読み込みエラー: {e}")
            return False
    
    def delete_file(self) -> bool:
        """保存されたファイルを削除"""
        try:
            if self.file_path and self.file_path.exists():
                self.file_path.unlink()
                self.file_path = None
                return True
            return False
        except Exception as e:
            print(f"ファイル削除エラー: {e}")
            return False
    
    def copy(self) -> 'Thumbnail':
        """サムネイルのコピーを作成"""
        from copy import deepcopy
        
        # image_dataは新しい配列として複製
        new_image_data = self.image_data.copy()
        
        return Thumbnail(
            source_frame=self.source_frame,  # フレームは共有
            user_settings=self.user_settings,  # 設定は共有
            image_data=new_image_data,
            diversity_score=self.diversity_score,
            total_score=self.total_score,
            file_path=self.file_path,
            is_selected=self.is_selected,
            created_at=self.created_at,
            metadata=deepcopy(self.metadata)
        )
    
    def resize(self, new_width: int, new_height: int) -> 'Thumbnail':
        """リサイズされたサムネイルを作成"""
        try:
            import cv2
            
            # リサイズ実行
            resized_image = cv2.resize(
                self.image_data, 
                (new_width, new_height), 
                interpolation=cv2.INTER_LANCZOS4
            )
            
            # 新しいサムネイルを作成
            new_thumbnail = self.copy()
            new_thumbnail.image_data = resized_image
            new_thumbnail.file_path = None  # リサイズ後は未保存状態
            
            return new_thumbnail
            
        except Exception as e:
            print(f"リサイズエラー: {e}")
            return self
    
    def add_metadata(self, key: str, value: Any):
        """メタデータを追加"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """メタデータを取得"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを出力"""
        return {
            # 基本情報
            'width': self.width,
            'height': self.height,
            'aspect_ratio': self.aspect_ratio,
            'pixel_count': self.pixel_count,
            'is_landscape': self.is_landscape,
            'is_portrait': self.is_portrait,
            
            # スコア情報
            'diversity_score': self.diversity_score,
            'total_score': self.total_score,
            'quality_category': self.quality_category,
            'diversity_category': self.diversity_category,
            
            # 元フレーム情報
            'source_frame_number': self.source_frame.frame_number,
            'source_timestamp': self.source_timestamp,
            'source_timestamp_formatted': self.source_timestamp_formatted,
            'has_faces': self.has_faces,
            'face_count': self.face_count,
            
            # ファイル情報
            'file_path': str(self.file_path) if self.file_path else None,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'file_size_mb': self.file_size_mb,
            'is_saved': self.is_saved,
            'is_selected': self.is_selected,
            
            # メタデータ
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def create_from_frame(
        cls,
        source_frame: 'Frame',
        user_settings: 'UserSettings',
        image_data: Optional[np.ndarray] = None
    ) -> 'Thumbnail':
        """フレームからサムネイルを作成"""
        if image_data is None:
            image_data = source_frame.image_data
        
        # 設定に合わせてリサイズ
        if (image_data.shape[1] != user_settings.output_width or 
            image_data.shape[0] != user_settings.output_height):
            
            import cv2
            image_data = cv2.resize(
                image_data,
                (user_settings.output_width, user_settings.output_height),
                interpolation=cv2.INTER_LANCZOS4
            )
        
        thumbnail = cls(
            source_frame=source_frame,
            user_settings=user_settings,
            image_data=image_data
        )
        
        # 品質メトリクスを計算
        thumbnail.update_quality_metrics()
        
        return thumbnail
    
    def __str__(self) -> str:
        """文字列表現"""
        return (f"Thumbnail({self.width}x{self.height}, score={self.total_score:.3f}, "
                f"t={self.source_timestamp_formatted})")
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"Thumbnail(size={self.width}x{self.height}, "
                f"diversity={self.diversity_score:.3f}, total={self.total_score:.3f}, "
                f"frame={self.source_frame.frame_number})")
    
    def __eq__(self, other) -> bool:
        """等価比較（元フレームとサイズで判定）"""
        if not isinstance(other, Thumbnail):
            return False
        return (self.source_frame == other.source_frame and
                self.width == other.width and
                self.height == other.height)
    
    def __hash__(self) -> int:
        """ハッシュ値（元フレームとサイズベース）"""
        return hash((self.source_frame, self.width, self.height))
    
    def __lt__(self, other) -> bool:
        """並び替え用（総合スコア降順）"""
        if not isinstance(other, Thumbnail):
            return NotImplemented
        return self.total_score > other.total_score  # 高いスコアが先
