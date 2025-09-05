"""
VideoFile（動画ファイル）データモデル

動画ファイルの情報を表すクラスです。バリデーションと状態遷移機能を含みます。
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class VideoFileStatus(Enum):
    """動画ファイルの状態"""
    CREATED = "created"           # 作成済み
    VALIDATING = "validating"     # 検証中
    VALID = "valid"              # 有効
    INVALID = "invalid"          # 無効
    PROCESSING = "processing"     # 処理中
    COMPLETED = "completed"       # 処理完了
    FAILED = "failed"            # 処理失敗


@dataclass
class VideoFile:
    """動画ファイルを表すクラス"""
    
    file_path: Path                              # 動画ファイルの絶対パス
    file_name: str = ""                         # ファイル名（拡張子含む）
    file_size: int = 0                          # ファイルサイズ（バイト）
    duration: float = 0.0                       # 再生時間（秒）
    fps: float = 0.0                           # フレームレート
    width: int = 0                             # 動画幅（ピクセル）
    height: int = 0                            # 動画高さ（ピクセル）
    total_frames: int = 0                      # 総フレーム数
    is_valid: bool = False                     # 有効性フラグ
    created_at: datetime = field(default_factory=datetime.now)  # 読み込み時刻
    status: VideoFileStatus = VideoFileStatus.CREATED  # 現在の状態
    error_message: Optional[str] = None         # エラーメッセージ
    metadata: Dict[str, Any] = field(default_factory=dict)  # 追加メタデータ
    
    def __post_init__(self):
        """初期化後の処理"""
        # file_pathの型チェックと変換
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)
        elif not isinstance(self.file_path, Path):
            raise TypeError("file_pathはPathオブジェクトまたは文字列である必要があります")
        
        # 絶対パスに変換
        self.file_path = self.file_path.resolve()
        
        # ファイル名の自動設定
        if not self.file_name:
            self.file_name = self.file_path.name
        
        # 基本バリデーション
        self._validate_basic_properties()
        
        # 状態を検証中に変更
        if self.status == VideoFileStatus.CREATED:
            self.status = VideoFileStatus.VALIDATING
    
    def _validate_basic_properties(self):
        """基本プロパティのバリデーション"""
        try:
            # ファイル存在確認
            if not self.file_path.exists():
                raise FileNotFoundError(f"動画ファイルが見つかりません: {self.file_path}")
            
            if not self.file_path.is_file():
                raise ValueError(f"指定されたパスはファイルではありません: {self.file_path}")
            
            # MP4拡張子チェック
            if self.file_path.suffix.lower() != '.mp4':
                raise ValueError(f"MP4形式のファイルのみサポートしています: {self.file_path.suffix}")
            
            # ファイルサイズの取得と検証
            if self.file_size == 0:
                self.file_size = self.file_path.stat().st_size
            
            # ファイルサイズ制限（2GB）
            max_file_size = 2 * 1024 * 1024 * 1024  # 2GB
            if self.file_size > max_file_size:
                raise ValueError(f"ファイルサイズが大きすぎます: {self.file_size / (1024**3):.2f}GB > 2GB")
            
            if self.file_size == 0:
                raise ValueError("ファイルサイズが0です（空ファイル）")
            
        except Exception as e:
            self.error_message = str(e)
            self.is_valid = False
            self.status = VideoFileStatus.INVALID
            raise
    
    def validate_video_properties(self):
        """動画プロパティの詳細バリデーション"""
        try:
            # 数値型チェック
            if not isinstance(self.duration, (int, float)) or self.duration <= 0:
                raise ValueError(f"再生時間が無効です: {self.duration}")
            
            if not isinstance(self.fps, (int, float)) or self.fps <= 0:
                raise ValueError(f"フレームレートが無効です: {self.fps}")
            
            if not isinstance(self.width, int) or self.width <= 0:
                raise ValueError(f"動画幅が無効です: {self.width}")
            
            if not isinstance(self.height, int) or self.height <= 0:
                raise ValueError(f"動画高さが無効です: {self.height}")
            
            # 最低処理要件チェック
            if self.duration < 10.0:
                raise ValueError(f"動画が短すぎます（最低10秒必要）: {self.duration}秒")
            
            # 解像度チェック
            min_resolution = 240
            if self.width < min_resolution or self.height < min_resolution:
                raise ValueError(f"解像度が低すぎます（最低{min_resolution}p必要）: {self.width}x{self.height}")
            
            max_width, max_height = 4096, 4096  # 4K
            if self.width > max_width or self.height > max_height:
                raise ValueError(f"解像度が高すぎます（最大4K）: {self.width}x{self.height}")
            
            # フレームレート範囲チェック
            if not (1 <= self.fps <= 120):
                raise ValueError(f"フレームレートが範囲外です（1-120fps）: {self.fps}")
            
            # 総フレーム数の一貫性チェック
            expected_frames = int(self.duration * self.fps)
            if self.total_frames > 0 and abs(self.total_frames - expected_frames) > expected_frames * 0.1:
                # 10%以上の差がある場合は警告
                print(f"警告: 総フレーム数に不整合があります。期待値: {expected_frames}, 実際: {self.total_frames}")
            
            if self.total_frames == 0:
                self.total_frames = expected_frames
            
            # すべての検証をパス
            self.is_valid = True
            self.status = VideoFileStatus.VALID
            self.error_message = None
            
        except Exception as e:
            self.error_message = str(e)
            self.is_valid = False
            self.status = VideoFileStatus.INVALID
            raise
    
    @property
    def file_size_mb(self) -> float:
        """ファイルサイズをMB単位で返す"""
        return self.file_size / (1024 * 1024)
    
    @property
    def file_size_gb(self) -> float:
        """ファイルサイズをGB単位で返す"""
        return self.file_size / (1024 * 1024 * 1024)
    
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比（幅/高さ）"""
        if self.height == 0:
            return 0.0
        return self.width / self.height
    
    @property
    def resolution_category(self) -> str:
        """解像度カテゴリの取得"""
        if self.width >= 3840 and self.height >= 2160:
            return "4K"
        elif self.width >= 1920 and self.height >= 1080:
            return "FHD"
        elif self.width >= 1280 and self.height >= 720:
            return "HD"
        elif self.width >= 640 and self.height >= 480:
            return "SD"
        else:
            return "Low"
    
    @property
    def is_landscape(self) -> bool:
        """横向き動画かどうか"""
        return self.width > self.height
    
    @property
    def is_portrait(self) -> bool:
        """縦向き動画かどうか"""
        return self.height > self.width
    
    @property
    def duration_formatted(self) -> str:
        """フォーマットされた再生時間（MM:SS形式）"""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def estimated_processing_time(self) -> float:
        """推定処理時間（秒）- 研究結果に基づく"""
        # 1分の動画につき3秒の処理時間を想定
        base_time = (self.duration / 60.0) * 3.0
        
        # 解像度による補正
        resolution_factor = 1.0
        if self.resolution_category == "4K":
            resolution_factor = 2.0
        elif self.resolution_category == "FHD":
            resolution_factor = 1.5
        elif self.resolution_category == "HD":
            resolution_factor = 1.2
        
        return base_time * resolution_factor
    
    def start_processing(self):
        """処理開始状態に変更"""
        if self.status != VideoFileStatus.VALID:
            raise ValueError(f"処理開始できません。現在の状態: {self.status.value}")
        
        self.status = VideoFileStatus.PROCESSING
    
    def complete_processing(self):
        """処理完了状態に変更"""
        if self.status != VideoFileStatus.PROCESSING:
            raise ValueError(f"処理完了できません。現在の状態: {self.status.value}")
        
        self.status = VideoFileStatus.COMPLETED
    
    def fail_processing(self, error_message: str):
        """処理失敗状態に変更"""
        self.status = VideoFileStatus.FAILED
        self.error_message = error_message
        self.is_valid = False
    
    def reset_status(self):
        """状態をリセット（再処理用）"""
        if self.is_valid:
            self.status = VideoFileStatus.VALID
        else:
            self.status = VideoFileStatus.INVALID
        self.error_message = None
    
    def add_metadata(self, key: str, value: Any):
        """メタデータを追加"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """メタデータを取得"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを出力"""
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'duration': self.duration,
            'duration_formatted': self.duration_formatted,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'total_frames': self.total_frames,
            'aspect_ratio': self.aspect_ratio,
            'resolution_category': self.resolution_category,
            'is_landscape': self.is_landscape,
            'is_portrait': self.is_portrait,
            'is_valid': self.is_valid,
            'status': self.status.value,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'estimated_processing_time': self.estimated_processing_time,
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def from_file_path(cls, file_path: Path, validate: bool = True) -> 'VideoFile':
        """ファイルパスからVideoFileインスタンスを作成"""
        video_file = cls(file_path=file_path)
        
        if validate:
            # OpenCVなどを使用した詳細な動画プロパティ取得は、
            # 実際の実装では別のサービスクラスで行う
            # ここではプレースホルダー値を設定
            video_file.duration = 30.0
            video_file.fps = 24.0
            video_file.width = 1920
            video_file.height = 1080
            video_file.total_frames = int(video_file.duration * video_file.fps)
            
            video_file.validate_video_properties()
        
        return video_file
    
    def __str__(self) -> str:
        """文字列表現"""
        return (f"VideoFile({self.file_name}, {self.duration_formatted}, "
                f"{self.width}x{self.height}, {self.status.value})")
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"VideoFile(file_path={self.file_path!r}, duration={self.duration}, "
                f"resolution={self.width}x{self.height}, status={self.status.value})")
    
    def __eq__(self, other) -> bool:
        """等価比較（ファイルパスで判定）"""
        if not isinstance(other, VideoFile):
            return False
        return self.file_path == other.file_path
    
    def __hash__(self) -> int:
        """ハッシュ値（ファイルパスベース）"""
        return hash(self.file_path)
