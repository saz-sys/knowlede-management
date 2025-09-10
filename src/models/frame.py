"""
Frame（フレーム）データモデル

動画フレームの情報を表すクラスです。計算プロパティを含みます。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .video_file import VideoFile
    from .face_detection_result import FaceDetectionResult


@dataclass
class Frame:
    """動画フレームを表すクラス"""
    
    video_file: 'VideoFile'                     # 所属動画ファイル
    frame_number: int                           # フレーム番号
    timestamp: float                            # タイムスタンプ（秒）
    image_data: np.ndarray                      # 画像データ（numpy配列）
    faces_detected: List['FaceDetectionResult'] = field(default_factory=list)  # 検出された顔
    scene_score: float = 0.0                    # シーンチェンジスコア
    quality_score: float = 0.0                  # 画質スコア
    extracted_at: datetime = field(default_factory=datetime.now)  # 抽出時刻
    metadata: Dict[str, Any] = field(default_factory=dict)  # 追加メタデータ
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        # video_fileの型チェック（循環importを避けるため遅延評価）
        from .video_file import VideoFile
        if not isinstance(self.video_file, VideoFile):
            raise TypeError("video_fileはVideoFileインスタンスである必要があります")
        
        # フレーム番号のバリデーション
        if not isinstance(self.frame_number, int):
            raise TypeError("frame_numberは整数である必要があります")
        if self.frame_number < 0:
            raise ValueError(f"frame_numberは0以上である必要があります: {self.frame_number}")
        if self.video_file.total_frames > 0 and self.frame_number >= self.video_file.total_frames:
            raise ValueError(f"frame_numberが範囲外です: {self.frame_number} >= {self.video_file.total_frames}")
        
        # タイムスタンプのバリデーション
        if not isinstance(self.timestamp, (int, float)):
            raise TypeError("timestampは数値である必要があります")
        if self.timestamp < 0:
            raise ValueError(f"timestampは0以上である必要があります: {self.timestamp}")
        if self.video_file.duration > 0 and self.timestamp > self.video_file.duration:
            raise ValueError(f"timestampが動画の長さを超えています: {self.timestamp} > {self.video_file.duration}")
        
        # 画像データのバリデーション
        if not isinstance(self.image_data, np.ndarray):
            raise TypeError("image_dataはnumpy.ndarrayである必要があります")
        
        # 画像データの形状チェック（高さ, 幅, チャンネル）
        if len(self.image_data.shape) != 3:
            raise ValueError(f"image_dataは3次元配列である必要があります: {self.image_data.shape}")
        
        height, width, channels = self.image_data.shape
        if channels != 3:
            raise ValueError(f"image_dataは3チャンネル（RGB）である必要があります: {channels}チャンネル")
        
        # 画像データのサイズ整合性チェック
        if self.video_file.width > 0 and self.video_file.height > 0:
            if width != self.video_file.width or height != self.video_file.height:
                # 警告のみ（リサイズされたフレームの可能性）
                print(f"警告: フレームサイズが動画設定と異なります。"
                      f"フレーム: {width}x{height}, 動画: {self.video_file.width}x{self.video_file.height}")
        
        # スコアのバリデーション
        if not isinstance(self.scene_score, (int, float)):
            raise TypeError("scene_scoreは数値である必要があります")
        if not (0.0 <= self.scene_score <= 1.0):
            raise ValueError(f"scene_scoreは0-1の範囲である必要があります: {self.scene_score}")
        
        if not isinstance(self.quality_score, (int, float)):
            raise TypeError("quality_scoreは数値である必要があります")
        if not (0.0 <= self.quality_score <= 1.0):
            raise ValueError(f"quality_scoreは0-1の範囲である必要があります: {self.quality_score}")
        
        # 顔検出結果のバリデーション
        if not isinstance(self.faces_detected, list):
            raise TypeError("faces_detectedはリストである必要があります")
        
        for i, face in enumerate(self.faces_detected):
            from .face_detection_result import FaceDetectionResult
            if not isinstance(face, FaceDetectionResult):
                raise TypeError(f"faces_detected[{i}]はFaceDetectionResultインスタンスである必要があります")
    
    @property
    def width(self) -> int:
        """フレーム幅"""
        return self.image_data.shape[1]
    
    @property
    def height(self) -> int:
        """フレーム高さ"""
        return self.image_data.shape[0]
    
    @property
    def channels(self) -> int:
        """チャンネル数"""
        return self.image_data.shape[2]
    
    @property
    def has_faces(self) -> bool:
        """顔が検出されているかどうか"""
        return len(self.faces_detected) > 0
    
    @property
    def face_count(self) -> int:
        """検出された顔の数"""
        return len(self.faces_detected)
    
    @property
    def primary_face(self) -> Optional['FaceDetectionResult']:
        """最も信頼度の高い顔を返す"""
        if not self.faces_detected:
            return None
        return max(self.faces_detected, key=lambda f: f.confidence)
    
    @property
    def largest_face(self) -> Optional['FaceDetectionResult']:
        """最も大きい顔を返す"""
        if not self.faces_detected:
            return None
        return max(self.faces_detected, key=lambda f: f.face_size)
    
    @property
    def high_quality_faces(self) -> List['FaceDetectionResult']:
        """高品質な顔のリストを返す"""
        return [face for face in self.faces_detected if face.is_high_quality]
    
    @property
    def timestamp_formatted(self) -> str:
        """フォーマットされたタイムスタンプ（MM:SS.mmm形式）"""
        minutes = int(self.timestamp // 60)
        seconds = self.timestamp % 60
        return f"{minutes:02d}:{seconds:06.3f}"
    
    @property
    def is_scene_change(self) -> bool:
        """シーンチェンジフレームかどうか（閾値0.3以上）"""
        return self.scene_score >= 0.3
    
    @property
    def is_high_quality(self) -> bool:
        """高品質フレームかどうか（閾値0.7以上）"""
        return self.quality_score >= 0.7
    
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比"""
        return self.width / self.height if self.height > 0 else 0.0
    
    @property
    def pixel_count(self) -> int:
        """総ピクセル数"""
        return self.width * self.height
    
    @property
    def estimated_processing_time(self) -> float:
        """推定処理時間（秒）- 解像度に基づく"""
        # 1920x1080を基準として、解像度に比例した処理時間
        base_pixels = 1920 * 1080
        time_per_megapixel = 0.1  # 1MP当たり0.1秒
        
        processing_time = (self.pixel_count / base_pixels) * time_per_megapixel
        return max(0.01, processing_time)  # 最低0.01秒
    
    def calculate_brightness(self) -> float:
        """フレームの平均輝度を計算（0-1）"""
        # RGBから輝度に変換（ITU-R BT.709係数）
        gray = np.dot(self.image_data, [0.2126, 0.7152, 0.0722])
        return float(np.mean(gray) / 255.0)
    
    def calculate_contrast(self) -> float:
        """フレームのコントラストを計算（0-1）"""
        # グレースケール変換
        gray = np.dot(self.image_data, [0.2126, 0.7152, 0.0722])
        
        # 標準偏差ベースのコントラスト
        contrast = float(np.std(gray) / 255.0)
        return min(1.0, contrast)
    
    def calculate_sharpness(self) -> float:
        """フレームの鮮明度を計算（ラプラシアンフィルタベース）"""
        # グレースケール変換
        gray = np.dot(self.image_data, [0.2126, 0.7152, 0.0722]).astype(np.uint8)
        
        # ラプラシアンフィルタを適用
        import cv2
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(np.var(laplacian))
        
        # 正規化（経験的な値）
        normalized_sharpness = min(1.0, sharpness / 1000.0)
        return normalized_sharpness
    
    def update_quality_metrics(self):
        """品質メトリクスを更新"""
        brightness = self.calculate_brightness()
        contrast = self.calculate_contrast()
        sharpness = self.calculate_sharpness()
        
        # 総合品質スコアの計算
        self.quality_score = (
            brightness * 0.2 +      # 明度（20%）
            contrast * 0.3 +        # コントラスト（30%）
            sharpness * 0.5         # 鮮明度（50%）
        )
        
        # メタデータに個別スコアを保存
        self.metadata.update({
            'brightness': brightness,
            'contrast': contrast,
            'sharpness': sharpness
        })
    
    def get_face_by_confidence(self, min_confidence: float = 0.5) -> List['FaceDetectionResult']:
        """指定した信頼度以上の顔を取得"""
        return [face for face in self.faces_detected if face.confidence >= min_confidence]
    
    def get_face_by_size(self, min_size: float = 0.01) -> List['FaceDetectionResult']:
        """指定したサイズ以上の顔を取得"""
        return [face for face in self.faces_detected if face.face_size >= min_size]
    
    def get_centered_faces(self, max_distance: float = 0.3) -> List['FaceDetectionResult']:
        """画面中央近くの顔を取得"""
        from .point_2d import Point2D
        center = Point2D(0.5, 0.5)
        return [face for face in self.faces_detected 
                if face.distance_from_center(center) <= max_distance]
    
    def add_metadata(self, key: str, value: Any):
        """メタデータを追加"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """メタデータを取得"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを出力"""
        return {
            'video_file_path': str(self.video_file.file_path),
            'frame_number': self.frame_number,
            'timestamp': self.timestamp,
            'timestamp_formatted': self.timestamp_formatted,
            'width': self.width,
            'height': self.height,
            'channels': self.channels,
            'aspect_ratio': self.aspect_ratio,
            'pixel_count': self.pixel_count,
            'has_faces': self.has_faces,
            'face_count': self.face_count,
            'scene_score': self.scene_score,
            'quality_score': self.quality_score,
            'is_scene_change': self.is_scene_change,
            'is_high_quality': self.is_high_quality,
            'extracted_at': self.extracted_at.isoformat(),
            'estimated_processing_time': self.estimated_processing_time,
            'metadata': self.metadata.copy(),
            'faces': [face.to_dict() for face in self.faces_detected]
        }
    
    def save_image(self, output_path: str, format: str = 'PNG') -> bool:
        """フレーム画像をファイルに保存"""
        try:
            import cv2
            # OpenCVはBGR順なので、RGB→BGR変換
            bgr_image = cv2.cvtColor(self.image_data, cv2.COLOR_RGB2BGR)
            return cv2.imwrite(output_path, bgr_image)
        except Exception as e:
            print(f"画像保存エラー: {e}")
            return False
    
    @classmethod
    def create_from_opencv(
        cls,
        video_file: 'VideoFile',
        frame_number: int,
        timestamp: float,
        opencv_frame: np.ndarray
    ) -> 'Frame':
        """OpenCVフレームからFrameインスタンスを作成"""
        # OpenCVはBGR順なので、RGB順に変換
        import cv2
        rgb_frame = cv2.cvtColor(opencv_frame, cv2.COLOR_BGR2RGB)
        
        # 回転メタデータに基づき画像を回転
        try:
            rotation = video_file.get_metadata('rotation', None)
            if rotation in (90, 180, 270):
                if rotation == 90:
                    rgb_frame = cv2.rotate(rgb_frame, cv2.ROTATE_90_CLOCKWISE)
                elif rotation == 180:
                    rgb_frame = cv2.rotate(rgb_frame, cv2.ROTATE_180)
                elif rotation == 270:
                    rgb_frame = cv2.rotate(rgb_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except Exception:
            pass
        
        return cls(
            video_file=video_file,
            frame_number=frame_number,
            timestamp=timestamp,
            image_data=rgb_frame
        )
    
    def __str__(self) -> str:
        """文字列表現"""
        return (f"Frame({self.frame_number}, {self.timestamp_formatted}, "
                f"{self.width}x{self.height}, faces={self.face_count})")
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"Frame(frame_number={self.frame_number}, timestamp={self.timestamp}, "
                f"resolution={self.width}x{self.height}, faces={self.face_count})")
    
    def __eq__(self, other) -> bool:
        """等価比較（動画ファイルとフレーム番号で判定）"""
        if not isinstance(other, Frame):
            return False
        return (self.video_file == other.video_file and 
                self.frame_number == other.frame_number)
    
    def __hash__(self) -> int:
        """ハッシュ値（動画ファイルとフレーム番号ベース）"""
        return hash((self.video_file.file_path, self.frame_number))
