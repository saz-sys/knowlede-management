"""
GUI（グラフィカルユーザーインターフェース）パッケージ

動画サムネイル抽出アプリケーションのデスクトップGUI機能を提供します。
tkinterベースの直感的なユーザーインターフェースを実装しています。

GUI構成:
- main_window: メインウィンドウ（ファイル選択、進捗表示、操作メニュー）
- settings_dialog: 設定ダイアログ（サイズ・枚数設定、バリデーション）
- thumbnail_grid: サムネイル表示グリッド（複数候補表示、選択機能）
- async_worker: 非同期ワーカー（重い処理の非同期実行）

特徴:
- レスポンシブな非同期処理でUIブロッキングを防止
- リアルタイム進捗表示とステータス更新
- ユーザーフレンドリーなエラーメッセージ
- 設定の永続化とプリセット機能
- 高解像度ディスプレイ対応
"""

# 循環インポート回避のため、後でインポート

__all__ = [
    # メインコンポーネント
    "MainWindow",
    "SettingsDialog", 
    "ThumbnailGrid",
    "AsyncWorker",
]

# GUIパッケージバージョン
__version__ = "1.0.0"

# GUIメタデータ
__author__ = "s-anzai"
__description__ = "動画サムネイル抽出デスクトップアプリケーションGUI"

# 推奨フォント（プラットフォーム別）
import sys
if sys.platform == "darwin":  # macOS
    DEFAULT_FONT_FAMILY = "Helvetica Neue"
    DEFAULT_FONT_SIZE = 13
elif sys.platform.startswith("win"):  # Windows
    DEFAULT_FONT_FAMILY = "Segoe UI"
    DEFAULT_FONT_SIZE = 9
else:  # Linux
    DEFAULT_FONT_FAMILY = "Ubuntu"
    DEFAULT_FONT_SIZE = 10

# GUIカラーテーマ
GUI_COLORS = {
    "primary": "#007AFF",      # メインアクション
    "secondary": "#5856D6",    # サブアクション
    "success": "#34C759",      # 成功状態
    "warning": "#FF9500",      # 警告状態
    "error": "#FF3B30",        # エラー状態
    "background": "#F2F2F7",   # 背景色
    "surface": "#FFFFFF",      # サーフェス色
    "text_primary": "#000000", # プライマリテキスト
    "text_secondary": "#8E8E93",  # セカンダリテキスト
    "border": "#C6C6C8",       # ボーダー色
}

# GUI設定
GUI_CONFIG = {
    "window_min_width": 800,
    "window_min_height": 600,
    "thumbnail_size": (150, 150),
    "grid_padding": 10,
    "dialog_width": 400,
    "dialog_height": 300,
    "progress_update_interval": 100,  # ミリ秒
    "max_thumbnails_display": 20,
}

def init_gui_environment():
    """GUI環境を初期化"""
    import tkinter as tk
    from tkinter import ttk
    
    # Tkinter設定
    root = tk.Tk()
    root.withdraw()  # 初期化時は非表示
    
    # 高DPI対応
    try:
        root.tk.call('tk', 'scaling', 2.0)
    except:
        pass
    
    # スタイル設定
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    
    return root

def get_gui_font(size_offset: int = 0) -> tuple:
    """GUIフォントを取得"""
    return (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + size_offset)

def get_color(color_name: str, fallback: str = "#000000") -> str:
    """カラーテーマから色を取得"""
    return GUI_COLORS.get(color_name, fallback)

def get_config(config_name: str, fallback=None):
    """GUI設定を取得"""
    return GUI_CONFIG.get(config_name, fallback)


# 循環インポート回避のため、最後にインポート
from gui.main_window import MainWindow
from gui.settings_dialog import SettingsDialog
from gui.thumbnail_grid import ThumbnailGrid
from gui.async_worker import AsyncWorker