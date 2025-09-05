"""
Config（設定管理）ライブラリ

アプリケーション設定の統一管理機能を提供します。
JSON/YAML設定ファイルの読み書き、デフォルト値、バリデーション機能を含みます。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging


@dataclass
class AppConfig:
    """アプリケーション設定データクラス"""
    
    # アプリケーション基本設定
    app_name: str = "動画サムネイル抽出"
    app_version: str = "1.0.0"
    language: str = "ja"  # 言語設定
    
    # デフォルト処理設定
    default_thumbnail_count: int = 5
    default_output_width: int = 1920
    default_output_height: int = 1080
    default_quality_threshold: float = 0.7
    default_diversity_weight: float = 0.8
    
    # ファイル・パス設定
    default_output_directory: str = ""  # 空文字の場合はDownloads使用
    temp_directory: str = ""  # 空文字の場合はシステムデフォルト使用
    log_directory: str = ""  # 空文字の場合はアプリディレクトリ/logs使用
    
    # 処理性能設定
    max_frame_buffer_size: int = 100
    max_concurrent_jobs: int = 1
    processing_timeout_seconds: int = 300  # 5分
    
    # MediaPipe設定
    face_detection_confidence: float = 0.5
    min_face_size: float = 0.01
    
    # GUI設定
    window_width: int = 1200
    window_height: int = 800
    show_debug_info: bool = False
    auto_save_settings: bool = True
    
    # ログ設定
    log_level: str = "INFO"
    log_to_file: bool = True
    log_rotation_days: int = 7


class Config:
    """設定管理クラス"""
    
    DEFAULT_CONFIG_FILENAME = "app_config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Configを初期化
        
        Args:
            config_path: 設定ファイルのパス（Noneの場合はデフォルトパス使用）
        """
        self.logger = logging.getLogger(__name__)
        
        # 設定ファイルパスの決定
        if config_path is None:
            config_path = self._get_default_config_path()
        
        self.config_path = Path(config_path)
        self._config = AppConfig()
        
        # 設定の読み込み
        self._load_config()
        
        self.logger.info(f"設定管理初期化完了: {self.config_path}")
    
    def _get_default_config_path(self) -> Path:
        """デフォルト設定ファイルパスを取得"""
        # プラットフォーム別の設定ディレクトリ
        if os.name == 'nt':  # Windows
            config_dir = Path.home() / "AppData" / "Local" / "VideoThumbnailExtractor"
        elif os.name == 'posix':  # macOS/Linux
            config_dir = Path.home() / ".config" / "video_thumbnail_extractor"
        else:
            config_dir = Path.home() / ".video_thumbnail_extractor"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / self.DEFAULT_CONFIG_FILENAME
    
    def _load_config(self):
        """設定ファイルから設定を読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 設定データを適用（存在するキーのみ）
                for key, value in config_data.items():
                    if hasattr(self._config, key):
                        setattr(self._config, key, value)
                
                self.logger.info(f"設定ファイル読み込み完了: {self.config_path}")
            else:
                self.logger.info("設定ファイルが存在しません。デフォルト設定を使用します。")
                self.save()  # デフォルト設定でファイル作成
                
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            self.logger.info("デフォルト設定を使用します。")
    
    def save(self) -> bool:
        """設定をファイルに保存"""
        try:
            # ディレクトリ作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 設定データを辞書に変換
            config_data = asdict(self._config)
            
            # JSON形式で保存
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"設定ファイル保存完了: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定ファイル保存エラー: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return getattr(self._config, key, default)
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> bool:
        """設定値を更新"""
        try:
            if hasattr(self._config, key):
                # 型チェック（簡易版）
                current_value = getattr(self._config, key)
                if current_value is not None and type(value) != type(current_value):
                    self.logger.warning(f"設定値の型が異なります: {key} - 期待型: {type(current_value)}, 実際: {type(value)}")
                
                setattr(self._config, key, value)
                
                if save_immediately and self._config.auto_save_settings:
                    return self.save()
                return True
            else:
                self.logger.error(f"不明な設定キー: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"設定値更新エラー: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """全設定値を辞書として取得"""
        return asdict(self._config)
    
    def reset_to_defaults(self) -> bool:
        """設定をデフォルト値にリセット"""
        try:
            self._config = AppConfig()
            self.logger.info("設定をデフォルト値にリセットしました")
            return self.save()
        except Exception as e:
            self.logger.error(f"設定リセットエラー: {e}")
            return False
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """設定値の妥当性をチェック"""
        errors = []
        
        try:
            # 数値範囲チェック
            if not (1 <= self._config.default_thumbnail_count <= 20):
                errors.append("default_thumbnail_count は1-20の範囲である必要があります")
            
            if not (240 <= self._config.default_output_width <= 4096):
                errors.append("default_output_width は240-4096の範囲である必要があります")
            
            if not (240 <= self._config.default_output_height <= 4096):
                errors.append("default_output_height は240-4096の範囲である必要があります")
            
            if not (0.0 <= self._config.default_quality_threshold <= 1.0):
                errors.append("default_quality_threshold は0.0-1.0の範囲である必要があります")
            
            if not (0.0 <= self._config.default_diversity_weight <= 1.0):
                errors.append("default_diversity_weight は0.0-1.0の範囲である必要があります")
            
            if not (0.0 <= self._config.face_detection_confidence <= 1.0):
                errors.append("face_detection_confidence は0.0-1.0の範囲である必要があります")
            
            if not (0.0 <= self._config.min_face_size <= 1.0):
                errors.append("min_face_size は0.0-1.0の範囲である必要があります")
            
            # パス存在チェック
            if self._config.default_output_directory:
                output_path = Path(self._config.default_output_directory)
                if not output_path.exists():
                    errors.append(f"default_output_directory が存在しません: {output_path}")
            
            # ログレベルチェック
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if self._config.log_level not in valid_log_levels:
                errors.append(f"log_level は {valid_log_levels} のいずれかである必要があります")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"設定検証中にエラーが発生しました: {e}")
            return False, errors
    
    def get_resolved_paths(self) -> Dict[str, Path]:
        """解決済みパス（実際に使用されるパス）を取得"""
        paths = {}
        
        # 出力ディレクトリ
        if self._config.default_output_directory:
            paths['output_directory'] = Path(self._config.default_output_directory)
        else:
            paths['output_directory'] = Path.home() / "Downloads"
        
        # 一時ディレクトリ
        if self._config.temp_directory:
            paths['temp_directory'] = Path(self._config.temp_directory)
        else:
            import tempfile
            paths['temp_directory'] = Path(tempfile.gettempdir())
        
        # ログディレクトリ
        if self._config.log_directory:
            paths['log_directory'] = Path(self._config.log_directory)
        else:
            paths['log_directory'] = self.config_path.parent / "logs"
        
        return paths
    
    @property
    def config(self) -> AppConfig:
        """設定データオブジェクトを取得（読み取り専用推奨）"""
        return self._config


class ConfigManager:
    """設定管理マネージャー（シングルトンパターン）"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Config] = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = Config(config_path)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """シングルトンインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_config(cls) -> Config:
        """設定オブジェクトを取得"""
        instance = cls.get_instance()
        return cls._config
    
    @classmethod
    def reload_config(cls, config_path: Optional[Path] = None):
        """設定を再読み込み"""
        cls._instance = None
        cls._config = None
        cls._instance = cls(config_path)


# グローバル関数（便利関数）
def get_config() -> Config:
    """グローバル設定オブジェクトを取得"""
    return ConfigManager.get_config()


def get_setting(key: str, default: Any = None) -> Any:
    """設定値を取得（便利関数）"""
    return get_config().get(key, default)


def set_setting(key: str, value: Any, save_immediately: bool = True) -> bool:
    """設定値を更新（便利関数）"""
    return get_config().set(key, value, save_immediately)


def get_resolved_path(path_type: str) -> Path:
    """解決済みパスを取得（便利関数）"""
    paths = get_config().get_resolved_paths()
    return paths.get(path_type, Path.home())


# 設定プリセット
class ConfigPresets:
    """設定プリセット"""
    
    @staticmethod
    def high_quality() -> Dict[str, Any]:
        """高品質プリセット"""
        return {
            'default_thumbnail_count': 5,
            'default_output_width': 1920,
            'default_output_height': 1080,
            'default_quality_threshold': 0.8,
            'default_diversity_weight': 0.7,
            'face_detection_confidence': 0.7,
            'min_face_size': 0.02
        }
    
    @staticmethod
    def fast_generation() -> Dict[str, Any]:
        """高速生成プリセット"""
        return {
            'default_thumbnail_count': 3,
            'default_output_width': 1280,
            'default_output_height': 720,
            'default_quality_threshold': 0.6,
            'default_diversity_weight': 0.9,
            'face_detection_confidence': 0.5,
            'min_face_size': 0.01,
            'max_frame_buffer_size': 50
        }
    
    @staticmethod
    def high_diversity() -> Dict[str, Any]:
        """高多様性プリセット"""
        return {
            'default_thumbnail_count': 8,
            'default_output_width': 1920,
            'default_output_height': 1080,
            'default_quality_threshold': 0.6,
            'default_diversity_weight': 0.9,
            'face_detection_confidence': 0.5,
            'min_face_size': 0.005
        }
    
    @staticmethod
    def debug() -> Dict[str, Any]:
        """デバッグプリセット"""
        return {
            'log_level': 'DEBUG',
            'show_debug_info': True,
            'log_to_file': True,
            'auto_save_settings': False
        }
