"""
ログ管理システム

JSON形式でのログ出力、ファイル出力、エラーコンテキスト管理を提供します。
研究結果に基づく構造化ログ設計を実装しています。
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをJSON形式にフォーマット"""
        # 基本ログ情報
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # エラー情報を追加
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # 追加のコンテキスト情報
        if hasattr(record, "extra_context"):
            log_entry["context"] = record.extra_context
        
        # プロセス情報
        log_entry["process"] = {
            "pid": os.getpid(),
            "thread_name": record.threadName,
        }
        
        return json.dumps(log_entry, ensure_ascii=False, separators=(",", ":"))


class ContextAdapter(logging.LoggerAdapter):
    """コンテキスト情報を追加するログアダプター"""
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """ログメッセージにコンテキスト情報を追加"""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # アダプターのextraをマージ
        if self.extra:
            kwargs["extra"]["extra_context"] = {**self.extra, **kwargs["extra"].get("extra_context", {})}
        
        return msg, kwargs


class LoggerManager:
    """ログ管理クラス"""
    
    _instance: Optional["LoggerManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "LoggerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self) -> None:
        """ログシステムの初期設定"""
        # ログレベル設定
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        numeric_level = getattr(logging, log_level, logging.INFO)
        
        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # 既存のハンドラーをクリア
        root_logger.handlers.clear()
        
        # コンソール出力ハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # テスト環境では簡単な形式、本番では JSON 形式
        if os.getenv("TESTING") == "true":
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            console_formatter = JSONFormatter()
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # ファイル出力ハンドラー（テスト環境以外）
        if os.getenv("TESTING") != "true":
            self._setup_file_handler(root_logger, numeric_level)
    
    def _setup_file_handler(self, root_logger: logging.Logger, log_level: int) -> None:
        """ファイル出力ハンドラーの設定"""
        # ログディレクトリの作成
        log_dir = self._get_log_directory()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # ローテーションファイルハンドラー
        log_file = log_dir / "application.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
        
        # エラーログ用の別ファイル
        error_log_file = log_dir / "error.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
    
    def _get_log_directory(self) -> Path:
        """プラットフォーム固有のログディレクトリを取得"""
        app_name = "ThumbnailExtractor"
        
        if sys.platform == "win32":
            base_dir = Path(os.getenv("APPDATA", ""))
        elif sys.platform == "darwin":
            base_dir = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base_dir = Path.home() / ".local" / "share"
        
        return base_dir / app_name / "logs"
    
    def get_logger(self, name: str, **context: Any) -> ContextAdapter:
        """コンテキスト付きロガーを取得"""
        logger = logging.getLogger(name)
        return ContextAdapter(logger, context)
    
    def log_performance(self, operation: str, duration: float, **context: Any) -> None:
        """パフォーマンスログを記録"""
        perf_logger = self.get_logger("performance", operation=operation, **context)
        perf_logger.info(
            f"Operation '{operation}' completed in {duration:.3f}s",
            extra={"extra_context": {"duration_seconds": duration}}
        )
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, **context: Any) -> None:
        """ユーザーアクションログを記録"""
        action_logger = self.get_logger("user_action", action=action, user_id=user_id, **context)
        action_logger.info(f"User action: {action}")
    
    def log_error_with_context(
        self, 
        error: Exception, 
        operation: str, 
        **context: Any
    ) -> None:
        """エラーを詳細なコンテキストと共にログ記録"""
        error_logger = self.get_logger("error", operation=operation, **context)
        error_logger.error(
            f"Error in operation '{operation}': {str(error)}",
            exc_info=True,
            extra={"extra_context": {"error_type": type(error).__name__}}
        )


# グローバルロガーマネージャー
_logger_manager = LoggerManager()


def get_logger(name: str, **context: Any) -> ContextAdapter:
    """コンテキスト付きロガーを取得する便利関数"""
    return _logger_manager.get_logger(name, **context)


def log_performance(operation: str, duration: float, **context: Any) -> None:
    """パフォーマンスログを記録する便利関数"""
    _logger_manager.log_performance(operation, duration, **context)


def log_user_action(action: str, user_id: Optional[str] = None, **context: Any) -> None:
    """ユーザーアクションログを記録する便利関数"""
    _logger_manager.log_user_action(action, user_id, **context)


def log_error_with_context(error: Exception, operation: str, **context: Any) -> None:
    """エラーを詳細なコンテキストと共にログ記録する便利関数"""
    _logger_manager.log_error_with_context(error, operation, **context)


# 使用例
if __name__ == "__main__":
    # 基本ログ
    logger = get_logger(__name__)
    logger.info("アプリケーションが開始されました")
    
    # コンテキスト付きログ
    video_logger = get_logger(__name__, video_path="/path/to/video.mp4", user_id="user123")
    video_logger.info("動画処理を開始")
    
    # パフォーマンスログ
    log_performance("video_processing", 2.5, frames_processed=150)
    
    # ユーザーアクションログ
    log_user_action("video_selected", user_id="user123", file_size=1024000)
    
    # エラーログ
    try:
        raise ValueError("テストエラー")
    except ValueError as e:
        log_error_with_context(e, "test_operation", test_param="test_value")
