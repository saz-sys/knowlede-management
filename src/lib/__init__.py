"""
ユーティリティライブラリパッケージ

動画サムネイル抽出機能で使用する横断的機能を提供します。
設定管理、ログ処理、エラー処理などの共通ライブラリを統合します。

ライブラリ一覧:
- logger: 構造化ログ機能（既存）
- config: 設定管理（JSON/YAML、デフォルト値、バリデーション）
- errors: カスタム例外クラス（ユーザーフレンドリーメッセージ）
"""

from .logger import get_logger
from .config import Config, ConfigManager, get_config, get_setting, set_setting, get_resolved_path, ConfigPresets
from .errors import *  # 全てのエラークラスをインポート

__all__ = [
    # ログ関連
    "get_logger",
    
    # 設定管理
    "Config",
    "ConfigManager",
    "get_config",
    "get_setting", 
    "set_setting",
    "get_resolved_path",
    "ConfigPresets",
    
    # エラー処理（errors.pyから全てエクスポート）
    "ThumbnailExtractionError",
    "VideoProcessingError",
    "FaceDetectionError", 
    "ThumbnailGenerationError",
    "FileSaveError",
    "JobExecutionError",
    "GUIError",
    "ValidationError",
    "handle_error",
    "create_user_friendly_error",
    "format_error_for_user",
    "format_error_for_log",
    "ErrorCodes",
]

# パッケージバージョン
__version__ = "1.0.0"

# パッケージメタデータ
__author__ = "s-anzai"
__description__ = "動画サムネイル抽出機能のユーティリティライブラリ"