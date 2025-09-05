"""
動画サムネイル抽出アプリケーション

AIを活用した多様なサムネイル抽出機能を提供するデスクトップアプリケーション。
ローカル環境での安全な処理とユーザーフレンドリーなインターフェースを特徴とします。
"""

__version__ = "1.0.0"
__author__ = "s-anzai"
__description__ = "動画サムネイル抽出デスクトップアプリケーション"

# パッケージメタデータ
__all__ = [
    "__version__",
    "__author__", 
    "__description__",
]

# 主要モジュールの再エクスポート
from .models import *
from .services import *
from .gui import *
from .lib import *