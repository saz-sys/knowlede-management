# データモデル設計: 動画サムネイル抽出機能

**作成日**: 2025年9月5日
**関連**: [plan.md](plan.md) | [research.md](research.md)

## モデル概要
動画サムネイル抽出機能で使用するデータモデルを定義します。ローカル環境での効率的な処理と、ユーザーフレンドリーなインターフェースを重視した設計です。

## 1. VideoFile（動画ファイル）

### 属性
```python
@dataclass
class VideoFile:
    file_path: Path              # 動画ファイルの絶対パス
    file_name: str              # ファイル名（拡張子含む）
    file_size: int              # ファイルサイズ（バイト）
    duration: float             # 再生時間（秒）
    fps: float                  # フレームレート
    width: int                  # 動画幅（ピクセル）
    height: int                 # 動画高さ（ピクセル）
    total_frames: int           # 総フレーム数
    is_valid: bool              # 有効性フラグ
    created_at: datetime        # 読み込み時刻
```

### バリデーションルール
- **file_path**: 存在する有効なパス、MP4拡張子必須
- **duration**: 10秒以上（最低処理要件）
- **width/height**: 最小240p、最大4K
- **fps**: 1-120の範囲
- **file_size**: 最大2GB（メモリ制約）

### 状態遷移
```
CREATED → VALIDATING → VALID/INVALID
VALID → PROCESSING → COMPLETED/FAILED
```

## 2. Frame（フレーム）

### 属性
```python
@dataclass
class Frame:
    video_file: VideoFile        # 所属動画ファイル
    frame_number: int           # フレーム番号
    timestamp: float            # タイムスタンプ（秒）
    image_data: np.ndarray      # 画像データ（numpy配列）
    faces_detected: List[FaceDetectionResult]  # 検出された顔
    scene_score: float          # シーンチェンジスコア
    quality_score: float        # 画質スコア
    extracted_at: datetime      # 抽出時刻
```

### バリデーションルール
- **frame_number**: 0以上、total_frames未満
- **timestamp**: 0以上、duration以下
- **image_data**: 有効なnumpy配列、3チャンネル（RGB）
- **scene_score**: 0.0-1.0の範囲
- **quality_score**: 0.0-1.0の範囲

### 計算フィールド
```python
@property
def has_faces(self) -> bool:
    return len(self.faces_detected) > 0

@property
def primary_face(self) -> Optional[FaceDetectionResult]:
    return max(self.faces_detected, key=lambda f: f.confidence) if self.faces_detected else None
```

## 3. FaceDetectionResult（顔検出結果）

### 属性
```python
@dataclass
class FaceDetectionResult:
    bounding_box: BoundingBox   # 顔の境界ボックス
    confidence: float           # 検出信頼度
    landmarks: List[Point2D]    # 顔のランドマーク座標
    face_size: float           # 顔サイズ（画面に占める割合）
    face_angle: float          # 顔の角度
    quality_metrics: Dict[str, float]  # 品質指標
```

### バリデーションルール
- **confidence**: 0.5以上（研究結果に基づく閾値）
- **face_size**: 0.01以上（画面の1%以上）
- **bounding_box**: 画像境界内に収まる座標

### 品質指標
```python
quality_metrics = {
    'sharpness': float,      # 0-1, 高いほど鮮明
    'brightness': float,     # 0-1, 適度な明度
    'contrast': float,       # 0-1, 適度なコントラスト
    'symmetry': float        # 0-1, 顔の対称性
}
```

## 4. UserSettings（ユーザー設定）

### 属性
```python
@dataclass
class UserSettings:
    output_width: int           # 出力幅（ピクセル）
    output_height: int          # 出力高さ（ピクセル）
    thumbnail_count: int        # 生成枚数
    orientation: ThumbnailOrientation  # 縦横方向
    output_directory: Path      # 保存先ディレクトリ
    file_name_prefix: str      # ファイル名プレフィックス
    quality_threshold: float    # 品質閾値
    diversity_weight: float     # 多様性重み
    face_size_preference: FaceSizePreference  # 顔サイズ設定
```

### バリデーションルール
- **output_width/height**: 64-7680の範囲（最小64px、最大8K）
- **thumbnail_count**: 1-20の範囲
- **quality_threshold**: 0.0-1.0の範囲
- **diversity_weight**: 0.0-1.0の範囲
- **output_directory**: 書き込み可能なディレクトリ

### 列挙型定義
```python
class ThumbnailOrientation(Enum):
    LANDSCAPE = "landscape"     # 横型
    PORTRAIT = "portrait"       # 縦型
    AUTO = "auto"              # 自動判定

class FaceSizePreference(Enum):
    SMALL = "small"            # 小顔優先
    MEDIUM = "medium"          # 中程度
    LARGE = "large"            # 大顔優先
    BALANCED = "balanced"       # バランス重視
```

## 5. Thumbnail（サムネイル）

### 属性
```python
@dataclass
class Thumbnail:
    source_frame: Frame         # 元フレーム
    user_settings: UserSettings # 使用した設定
    image_data: np.ndarray     # リサイズ後画像データ
    diversity_score: float      # 多様性スコア
    total_score: float         # 総合スコア
    file_path: Optional[Path]   # 保存先パス
    is_selected: bool          # ユーザー選択フラグ
    generated_at: datetime     # 生成時刻
```

### バリデーションルール
- **diversity_score**: 0.0-1.0の範囲
- **total_score**: 0.0-1.0の範囲
- **image_data**: 指定サイズと一致

### 計算フィールド
```python
@property
def aspect_ratio(self) -> float:
    return self.user_settings.output_width / self.user_settings.output_height

@property
def file_name(self) -> str:
    if self.file_path:
        return self.file_path.name
    timestamp = self.source_frame.timestamp
    return f"{self.user_settings.file_name_prefix}_{timestamp:.2f}s.png"
```

## 6. ThumbnailExtractionJob（抽出ジョブ）

### 属性
```python
@dataclass
class ThumbnailExtractionJob:
    video_file: VideoFile       # 処理対象動画
    user_settings: UserSettings # 抽出設定
    status: JobStatus          # ジョブステータス
    progress: float            # 進捗率（0.0-1.0）
    extracted_frames: List[Frame]     # 抽出フレーム
    generated_thumbnails: List[Thumbnail]  # 生成サムネイル
    error_message: Optional[str]      # エラーメッセージ
    started_at: datetime       # 開始時刻
    completed_at: Optional[datetime]  # 完了時刻
```

### 状態遷移
```python
class JobStatus(Enum):
    CREATED = "created"
    EXTRACTING_FRAMES = "extracting_frames"
    DETECTING_FACES = "detecting_faces"
    GENERATING_THUMBNAILS = "generating_thumbnails"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### 進捗計算
```python
@property
def estimated_remaining_time(self) -> Optional[float]:
    if self.status == JobStatus.COMPLETED:
        return 0.0
    if self.progress > 0:
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return (elapsed / self.progress) * (1.0 - self.progress)
    return None
```

## 7. BoundingBox（境界ボックス）

### 属性
```python
@dataclass
class BoundingBox:
    x: float                   # 左上X座標（正規化済み）
    y: float                   # 左上Y座標（正規化済み）
    width: float               # 幅（正規化済み）
    height: float              # 高さ（正規化済み）
```

### バリデーションルール
- **全座標**: 0.0-1.0の範囲（正規化座標）
- **x + width**: 1.0以下
- **y + height**: 1.0以下

### ユーティリティメソッド
```python
def to_pixel_coordinates(self, image_width: int, image_height: int) -> 'PixelBoundingBox':
    return PixelBoundingBox(
        x=int(self.x * image_width),
        y=int(self.y * image_height),
        width=int(self.width * image_width),
        height=int(self.height * image_height)
    )

def area(self) -> float:
    return self.width * self.height

def center_point(self) -> Point2D:
    return Point2D(
        x=self.x + self.width / 2,
        y=self.y + self.height / 2
    )
```

## 8. Point2D（2D座標）

### 属性
```python
@dataclass
class Point2D:
    x: float                   # X座標
    y: float                   # Y座標
```

### ユーティリティメソッド
```python
def distance_to(self, other: 'Point2D') -> float:
    return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

def to_tuple(self) -> Tuple[float, float]:
    return (self.x, self.y)
```

## データ関係図

```
VideoFile (1) -----> (*) Frame
Frame (1) ---------> (*) FaceDetectionResult
Frame (1) ---------> (1) Thumbnail
UserSettings (1) --> (*) Thumbnail
ThumbnailExtractionJob (1) --> (1) VideoFile
ThumbnailExtractionJob (1) --> (1) UserSettings
ThumbnailExtractionJob (1) --> (*) Frame
ThumbnailExtractionJob (1) --> (*) Thumbnail
FaceDetectionResult (1) --> (1) BoundingBox
FaceDetectionResult (1) --> (*) Point2D
```

## 永続化戦略

### ファイルベース（JSONシリアライゼーション）
```python
# セッション情報の保存
session_data = {
    'user_settings': user_settings.to_dict(),
    'recent_videos': [video.to_dict() for video in recent_videos],
    'preferences': preferences.to_dict()
}
```

### 一時ファイル管理
- **フレーム画像**: temp_frames/フォルダに一時保存
- **生成サムネイル**: temp_thumbnails/フォルダに一時保存
- **セッション終了時**: 自動クリーンアップ

## パフォーマンス考慮事項

### メモリ最適化
- **画像データ**: numpy配列の効率的利用
- **バッチ処理**: フレーム処理時のチャンクサイズ制御
- **ガベージコレクション**: 明示的なオブジェクト削除

### 並列処理対応
- **フレーム抽出**: 並列読み込み可能
- **顔検出**: バッチ処理対応
- **サムネイル生成**: 独立処理可能

このデータモデル設計により、効率的で拡張性の高い動画サムネイル抽出システムの基盤が整備されます。
