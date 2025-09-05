"""
エラー処理ライブラリ

動画サムネイル抽出機能で使用するカスタム例外クラスを定義します。
ユーザーフレンドリーなエラーメッセージと詳細なログ情報を提供します。
"""

from typing import Optional, Dict, Any


class ThumbnailExtractionError(Exception):
    """サムネイル抽出機能の基底例外クラス"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
    
    def _generate_user_message(self) -> str:
        """ユーザー向けのわかりやすいエラーメッセージを生成"""
        return "処理中にエラーが発生しました。しばらく経ってから再度お試しください。"
    
    def to_dict(self) -> Dict[str, Any]:
        """エラー情報を辞書形式で返す"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'user_message': self.user_message,
            'details': self.details
        }


# =============================================================================
# 動画ファイル関連のエラー
# =============================================================================

class VideoProcessingError(ThumbnailExtractionError):
    """動画処理に関する例外"""
    
    def _generate_user_message(self) -> str:
        return "動画ファイルの処理中にエラーが発生しました。ファイルが破損していないか確認してください。"


class InvalidVideoFormatError(VideoProcessingError):
    """サポートされていない動画形式"""
    
    def _generate_user_message(self) -> str:
        return "この動画形式はサポートされていません。MP4形式の動画ファイルをご使用ください。"


class CorruptedVideoError(VideoProcessingError):
    """破損した動画ファイル"""
    
    def _generate_user_message(self) -> str:
        return "動画ファイルが破損している可能性があります。別の動画ファイルをお試しください。"


class UnsupportedCodecError(VideoProcessingError):
    """サポートされていないコーデック"""
    
    def _generate_user_message(self) -> str:
        return "この動画のコーデックはサポートされていません。一般的なMP4形式で再エンコードしてください。"


class InsufficientMemoryError(VideoProcessingError):
    """メモリ不足"""
    
    def _generate_user_message(self) -> str:
        return "メモリが不足しています。他のアプリケーションを終了するか、より小さな動画ファイルをお試しください。"


class VideoTooShortError(VideoProcessingError):
    """動画が短すぎる"""
    
    def _generate_user_message(self) -> str:
        return "動画が短すぎます（最低10秒必要）。より長い動画をご使用ください。"


class VideoTooLargeError(VideoProcessingError):
    """動画ファイルが大きすぎる"""
    
    def _generate_user_message(self) -> str:
        return "動画ファイルが大きすぎます（最大2GB）。より小さなファイルをご使用ください。"


# =============================================================================
# 顔検出関連のエラー
# =============================================================================

class FaceDetectionError(ThumbnailExtractionError):
    """顔検出に関する例外"""
    
    def _generate_user_message(self) -> str:
        return "顔検出中にエラーが発生しました。"


class NoFacesDetectedError(FaceDetectionError):
    """顔が検出されない"""
    
    def _generate_user_message(self) -> str:
        return "この動画からキャラクターの顔を検出できませんでした。顔が写っている動画をご使用ください。"


class InvalidFrameError(FaceDetectionError):
    """無効なフレーム"""
    
    def _generate_user_message(self) -> str:
        return "動画フレームが無効です。動画ファイルが正しく読み込まれていない可能性があります。"


class BatchProcessingError(FaceDetectionError):
    """バッチ処理エラー"""
    
    def _generate_user_message(self) -> str:
        return "複数フレームの顔検出中にエラーが発生しました。"


class InvalidFaceDataError(FaceDetectionError):
    """無効な顔データ"""
    
    def _generate_user_message(self) -> str:
        return "顔検出データが無効です。"


class InvalidConfidenceError(FaceDetectionError):
    """無効な信頼度"""
    
    def _generate_user_message(self) -> str:
        return "顔検出の信頼度設定が無効です。0.0から1.0の範囲で設定してください。"


class InvalidSizeRatioError(FaceDetectionError):
    """無効なサイズ比率"""
    
    def _generate_user_message(self) -> str:
        return "顔サイズの比率設定が無効です。0.0から1.0の範囲で設定してください。"


class LandmarkExtractionError(FaceDetectionError):
    """ランドマーク抽出エラー"""
    
    def _generate_user_message(self) -> str:
        return "顔のランドマーク抽出中にエラーが発生しました。"


# =============================================================================
# サムネイル生成関連のエラー
# =============================================================================

class ThumbnailGenerationError(ThumbnailExtractionError):
    """サムネイル生成に関する例外"""
    
    def _generate_user_message(self) -> str:
        return "サムネイル生成中にエラーが発生しました。"


class InsufficientFramesError(ThumbnailGenerationError):
    """フレーム数不足"""
    
    def _generate_user_message(self) -> str:
        return "サムネイル生成に十分なフレームがありません。より長い動画を使用するか、抽出枚数を減らしてください。"


class InvalidSettingsError(ThumbnailGenerationError):
    """無効な設定"""
    
    def _generate_user_message(self) -> str:
        return "サムネイル生成の設定が無効です。設定内容を確認してください。"


class DiversityCalculationError(ThumbnailGenerationError):
    """多様性計算エラー"""
    
    def _generate_user_message(self) -> str:
        return "フレーム多様性の計算中にエラーが発生しました。"


class InvalidCountError(ThumbnailGenerationError):
    """無効な枚数"""
    
    def _generate_user_message(self) -> str:
        return "サムネイル生成枚数が無効です。1以上の数値を設定してください。"


class InvalidWeightError(ThumbnailGenerationError):
    """無効な重み"""
    
    def _generate_user_message(self) -> str:
        return "多様性の重み設定が無効です。0.0から1.0の範囲で設定してください。"


class InvalidResolutionError(ThumbnailGenerationError):
    """無効な解像度"""
    
    def _generate_user_message(self) -> str:
        return "サムネイルの解像度設定が無効です。240p以上4K以下の解像度を設定してください。"


class ImageResizeError(ThumbnailGenerationError):
    """画像リサイズエラー"""
    
    def _generate_user_message(self) -> str:
        return "画像のリサイズ中にエラーが発生しました。"


class InvalidDimensionsError(ThumbnailGenerationError):
    """無効な寸法"""
    
    def _generate_user_message(self) -> str:
        return "画像の寸法が無効です。正の値を設定してください。"


class InvalidOrientationError(ThumbnailGenerationError):
    """無効な向き"""
    
    def _generate_user_message(self) -> str:
        return "サムネイルの向き設定が無効です。'landscape'、'portrait'、または'auto'を選択してください。"


class CropError(ThumbnailGenerationError):
    """切り抜きエラー"""
    
    def _generate_user_message(self) -> str:
        return "画像の切り抜き中にエラーが発生しました。"


# =============================================================================
# ファイル操作関連のエラー
# =============================================================================

class FileSaveError(ThumbnailExtractionError):
    """ファイル保存エラー"""
    
    def _generate_user_message(self) -> str:
        return "ファイルの保存中にエラーが発生しました。保存先フォルダの書き込み権限を確認してください。"


class BatchSaveError(FileSaveError):
    """一括保存エラー"""
    
    def _generate_user_message(self) -> str:
        return "複数ファイルの保存中にエラーが発生しました。ディスク容量と書き込み権限を確認してください。"


class DirectoryError(ThumbnailExtractionError):
    """ディレクトリエラー"""
    
    def _generate_user_message(self) -> str:
        return "指定されたフォルダにアクセスできません。フォルダが存在し、書き込み権限があることを確認してください。"


class DiskSpaceError(FileSaveError):
    """ディスク容量不足"""
    
    def _generate_user_message(self) -> str:
        return "ディスク容量が不足しています。空き容量を確保してから再度お試しください。"


class FilePermissionError(FileSaveError):
    """ファイル権限エラー"""
    
    def _generate_user_message(self) -> str:
        return "ファイルへの書き込み権限がありません。管理者権限で実行するか、別のフォルダを選択してください。"


# =============================================================================
# ジョブ管理関連のエラー
# =============================================================================

class JobCreationError(ThumbnailExtractionError):
    """ジョブ作成エラー"""
    
    def _generate_user_message(self) -> str:
        return "処理ジョブの作成中にエラーが発生しました。設定内容を確認してください。"


class JobExecutionError(ThumbnailExtractionError):
    """ジョブ実行エラー"""
    
    def _generate_user_message(self) -> str:
        return "処理の実行中にエラーが発生しました。"


class JobCancellationError(ThumbnailExtractionError):
    """ジョブキャンセルエラー"""
    
    def _generate_user_message(self) -> str:
        return "処理のキャンセル中にエラーが発生しました。"


class JobTimeoutError(JobExecutionError):
    """ジョブタイムアウト"""
    
    def _generate_user_message(self) -> str:
        return "処理がタイムアウトしました。より小さな動画ファイルを使用するか、サムネイル枚数を減らしてください。"


# =============================================================================
# GUI関連のエラー
# =============================================================================

class GUIError(ThumbnailExtractionError):
    """GUI関連の例外"""
    
    def _generate_user_message(self) -> str:
        return "アプリケーションの表示中にエラーが発生しました。"


class GUIInitializationError(GUIError):
    """GUI初期化エラー"""
    
    def _generate_user_message(self) -> str:
        return "アプリケーションの初期化中にエラーが発生しました。アプリケーションを再起動してください。"


class GUICleanupError(GUIError):
    """GUI終了処理エラー"""
    
    def _generate_user_message(self) -> str:
        return "アプリケーションの終了処理中にエラーが発生しました。"


class InvalidVideoError(GUIError):
    """無効な動画エラー"""
    
    def _generate_user_message(self) -> str:
        return "選択された動画ファイルが無効です。正しいMP4ファイルを選択してください。"


class InvalidProgressError(GUIError):
    """無効な進捗エラー"""
    
    def _generate_user_message(self) -> str:
        return "進捗情報が無効です。"


class ThumbnailDisplayError(GUIError):
    """サムネイル表示エラー"""
    
    def _generate_user_message(self) -> str:
        return "サムネイルの表示中にエラーが発生しました。"


class SelectionError(GUIError):
    """選択エラー"""
    
    def _generate_user_message(self) -> str:
        return "サムネイルの選択中にエラーが発生しました。"


class DialogError(GUIError):
    """ダイアログエラー"""
    
    def _generate_user_message(self) -> str:
        return "ダイアログの表示中にエラーが発生しました。"


class SettingsDialogError(DialogError):
    """設定ダイアログエラー"""
    
    def _generate_user_message(self) -> str:
        return "設定ダイアログの表示中にエラーが発生しました。"


class ValidationError(ThumbnailExtractionError):
    """バリデーションエラー"""
    
    def _generate_user_message(self) -> str:
        return "入力内容に誤りがあります。設定を確認してください。"


class GridDisplayError(GUIError):
    """グリッド表示エラー"""
    
    def _generate_user_message(self) -> str:
        return "グリッド表示中にエラーが発生しました。"


# =============================================================================
# 設定・バリデーション関連のエラー
# =============================================================================

class InvalidThresholdError(ThumbnailExtractionError):
    """無効な閾値"""
    
    def _generate_user_message(self) -> str:
        return "閾値の設定が無効です。0.0から1.0の範囲で設定してください。"


class InvalidFrameDataError(ThumbnailExtractionError):
    """無効なフレームデータ"""
    
    def _generate_user_message(self) -> str:
        return "フレームデータが無効です。動画ファイルを確認してください。"


# =============================================================================
# エラーハンドリングユーティリティ
# =============================================================================

def handle_error(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """
    エラーを統一的に処理し、ログ用の辞書を返す
    
    Args:
        error: 発生した例外
        context: エラーが発生したコンテキスト情報
    
    Returns:
        ログ用の辞書
    """
    if isinstance(error, ThumbnailExtractionError):
        error_info = error.to_dict()
    else:
        # 予期しないエラーの場合
        error_info = {
            'error_code': 'UnexpectedError',
            'message': str(error),
            'user_message': 'システムエラーが発生しました。管理者にお問い合わせください。',
            'details': {'error_type': type(error).__name__}
        }
    
    if context:
        error_info['context'] = context
    
    return error_info


def create_user_friendly_error(
    original_error: Exception,
    user_message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> ThumbnailExtractionError:
    """
    元の例外からユーザーフレンドリーなエラーを作成
    
    Args:
        original_error: 元の例外
        user_message: ユーザー向けメッセージ
        error_code: エラーコード
        details: 詳細情報
    
    Returns:
        ユーザーフレンドリーなエラー
    """
    error_details = details or {}
    error_details['original_error'] = {
        'type': type(original_error).__name__,
        'message': str(original_error)
    }
    
    return ThumbnailExtractionError(
        message=str(original_error),
        error_code=error_code or 'GeneralError',
        details=error_details,
        user_message=user_message
    )


def format_error_for_user(error: Exception) -> str:
    """
    エラーをユーザー向けの文字列にフォーマット
    
    Args:
        error: エラー例外
    
    Returns:
        ユーザー向けエラーメッセージ
    """
    if isinstance(error, ThumbnailExtractionError):
        return error.user_message
    else:
        return "予期しないエラーが発生しました。アプリケーションを再起動してお試しください。"


def format_error_for_log(error: Exception, context: Optional[str] = None) -> str:
    """
    エラーをログ向けの文字列にフォーマット
    
    Args:
        error: エラー例外
        context: コンテキスト情報
    
    Returns:
        ログ向けエラーメッセージ
    """
    error_info = handle_error(error, context)
    return f"[{error_info['error_code']}] {error_info['message']}"


# エラーコード定数
class ErrorCodes:
    """エラーコード定数クラス"""
    
    # 動画関連
    INVALID_VIDEO_FORMAT = "VIDEO_001"
    CORRUPTED_VIDEO = "VIDEO_002"
    UNSUPPORTED_CODEC = "VIDEO_003"
    VIDEO_TOO_SHORT = "VIDEO_004"
    VIDEO_TOO_LARGE = "VIDEO_005"
    
    # 顔検出関連
    NO_FACES_DETECTED = "FACE_001"
    INVALID_FRAME = "FACE_002"
    FACE_DETECTION_FAILED = "FACE_003"
    
    # サムネイル生成関連
    INSUFFICIENT_FRAMES = "THUMBNAIL_001"
    INVALID_SETTINGS = "THUMBNAIL_002"
    GENERATION_FAILED = "THUMBNAIL_003"
    
    # ファイル操作関連
    FILE_SAVE_FAILED = "FILE_001"
    DIRECTORY_ACCESS_DENIED = "FILE_002"
    DISK_SPACE_INSUFFICIENT = "FILE_003"
    
    # システム関連
    INSUFFICIENT_MEMORY = "SYSTEM_001"
    TIMEOUT = "SYSTEM_002"
    UNEXPECTED_ERROR = "SYSTEM_999"
