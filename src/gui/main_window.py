"""
MainWindow（メインウィンドウ）実装

動画サムネイル抽出アプリケーションのメインウィンドウを実装します。
ファイル選択、進捗表示、操作メニューなどの主要機能を提供します。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable, List
import logging
import threading

from ..models import VideoFile, UserSettings, ThumbnailExtractionJob
from ..lib import get_logger, get_config, ValidationError
from . import get_gui_font, get_color, get_config as get_gui_config


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, master: Optional[tk.Tk] = None):
        """
        メインウィンドウを初期化
        
        Args:
            master: 親ウィンドウ（Noneの場合は新規作成）
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # ウィンドウ設定
        if master is None:
            self.root = tk.Tk()
        else:
            self.root = master
            
        self.root.title("動画サムネイル抽出")
        self.root.geometry(f"{self.config.get('window_width', 1200)}x{self.config.get('window_height', 800)}")
        self.root.minsize(
            get_gui_config("window_min_width", 800),
            get_gui_config("window_min_height", 600)
        )
        
        # 状態管理
        self.current_video: Optional[VideoFile] = None
        self.current_job: Optional[ThumbnailExtractionJob] = None
        self.is_processing = False
        
        # コールバック関数
        self.on_video_selected: Optional[Callable[[VideoFile], None]] = None
        self.on_extraction_start: Optional[Callable[[UserSettings], None]] = None
        self.on_settings_changed: Optional[Callable[[UserSettings], None]] = None
        
        # GUI構築
        self._setup_menu()
        self._setup_main_frame()
        self._setup_status_bar()
        self._setup_keyboard_shortcuts()
        
        self.logger.info("メインウィンドウ初期化完了")
    
    def _setup_menu(self):
        """メニューバーを設定"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="動画を開く...", command=self._open_video_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="設定...", command=self._open_settings, accelerator="Ctrl+,")
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self._on_closing, accelerator="Ctrl+Q")
        
        # 編集メニュー
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="編集", menu=edit_menu)
        edit_menu.add_command(label="設定をリセット", command=self._reset_settings)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self._show_help)
        help_menu.add_command(label="バージョン情報", command=self._show_about)
    
    def _setup_main_frame(self):
        """メインフレームを設定"""
        # メインコンテナ
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # グリッド重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # 左側パネル（操作エリア）
        self._setup_control_panel(main_container)
        
        # 右側パネル（プレビューエリア）
        self._setup_preview_panel(main_container)
    
    def _setup_control_panel(self, parent):
        """左側の操作パネルを設定"""
        control_frame = ttk.LabelFrame(parent, text="操作", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5))
        control_frame.columnconfigure(0, weight=1)
        
        # 動画ファイル選択
        video_frame = ttk.LabelFrame(control_frame, text="動画ファイル", padding="5")
        video_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        
        self.video_path_var = tk.StringVar(value="動画ファイルが選択されていません")
        video_label = ttk.Label(video_frame, textvariable=self.video_path_var, 
                               font=get_gui_font(), wraplength=250)
        video_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        select_button = ttk.Button(video_frame, text="動画を選択...", 
                                 command=self._open_video_file)
        select_button.grid(row=1, column=0, sticky="ew")
        
        # 設定エリア
        settings_frame = ttk.LabelFrame(control_frame, text="設定", padding="5")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # サムネイル枚数
        ttk.Label(settings_frame, text="サムネイル枚数:").grid(row=0, column=0, sticky="w", pady=2)
        self.thumbnail_count_var = tk.IntVar(value=self.config.get('default_thumbnail_count', 5))
        thumbnail_spin = ttk.Spinbox(settings_frame, from_=1, to=20, width=10,
                                   textvariable=self.thumbnail_count_var)
        thumbnail_spin.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # 出力サイズ
        ttk.Label(settings_frame, text="幅:").grid(row=1, column=0, sticky="w", pady=2)
        self.width_var = tk.IntVar(value=self.config.get('default_output_width', 1920))
        width_spin = ttk.Spinbox(settings_frame, from_=240, to=4096, width=10,
                               textvariable=self.width_var)
        width_spin.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(settings_frame, text="高さ:").grid(row=2, column=0, sticky="w", pady=2)
        self.height_var = tk.IntVar(value=self.config.get('default_output_height', 1080))
        height_spin = ttk.Spinbox(settings_frame, from_=240, to=4096, width=10,
                                textvariable=self.height_var)
        height_spin.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # プリセットボタン
        preset_frame = ttk.Frame(settings_frame)
        preset_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        preset_frame.columnconfigure(0, weight=1)
        preset_frame.columnconfigure(1, weight=1)
        
        ttk.Button(preset_frame, text="高品質", 
                  command=lambda: self._apply_preset("high_quality")).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(preset_frame, text="高速", 
                  command=lambda: self._apply_preset("fast_generation")).grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # 実行ボタン
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        
        self.extract_button = ttk.Button(button_frame, text="サムネイル抽出開始",
                                       command=self._start_extraction)
        self.extract_button.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="キャンセル",
                                      command=self._cancel_extraction, state="disabled")
        self.cancel_button.grid(row=1, column=0, sticky="ew")
        
        # 進捗表示
        progress_frame = ttk.LabelFrame(control_frame, text="進捗", padding="5")
        progress_frame.grid(row=3, column=0, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                          maximum=100.0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.status_var = tk.StringVar(value="待機中")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var,
                               font=get_gui_font())
        status_label.grid(row=1, column=0, sticky="w")
    
    def _setup_preview_panel(self, parent):
        """右側のプレビューパネルを設定"""
        preview_frame = ttk.LabelFrame(parent, text="プレビュー・結果", padding="10")
        preview_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # スクロール可能なキャンバス
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.grid(row=0, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white")
        self.preview_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", 
                                             command=self.preview_canvas.yview)
        self.preview_canvas.configure(yscrollcommand=self.preview_scrollbar.set)
        
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        self.preview_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 初期表示
        self._show_welcome_message()
        
        # 保存ボタン
        save_frame = ttk.Frame(preview_frame)
        save_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        save_frame.columnconfigure(0, weight=1)
        
        self.save_button = ttk.Button(save_frame, text="選択したサムネイルを保存",
                                    command=self._save_thumbnails, state="disabled")
        self.save_button.grid(row=0, column=0, sticky="ew")
    
    def _setup_status_bar(self):
        """ステータスバーを設定"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        self.status_bar_var = tk.StringVar(value="準備完了")
        status_label = ttk.Label(status_frame, textvariable=self.status_bar_var,
                               font=get_gui_font(-1), relief=tk.SUNKEN)
        status_label.grid(row=0, column=0, sticky="ew", padx=2, pady=1)
    
    def _setup_keyboard_shortcuts(self):
        """キーボードショートカットを設定"""
        self.root.bind('<Control-o>', lambda e: self._open_video_file())
        self.root.bind('<Control-comma>', lambda e: self._open_settings())
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F1>', lambda e: self._show_help())
        self.root.bind('<Return>', lambda e: self._start_extraction() if not self.is_processing else None)
        self.root.bind('<Escape>', lambda e: self._cancel_extraction() if self.is_processing else None)
    
    def _show_welcome_message(self):
        """ウェルカムメッセージを表示"""
        self.preview_canvas.delete("all")
        
        canvas_width = self.preview_canvas.winfo_width() or 400
        canvas_height = self.preview_canvas.winfo_height() or 300
        
        # 中央にメッセージ表示
        text_lines = [
            "動画サムネイル抽出アプリケーション",
            "",
            "1. 左側の「動画を選択...」ボタンでMP4ファイルを選択",
            "2. サムネイル枚数とサイズを設定",
            "3. 「サムネイル抽出開始」ボタンをクリック",
            "4. 生成されたサムネイルから保存したいものを選択",
            "",
            "ショートカットキー:",
            "Ctrl+O: 動画を開く",
            "Ctrl+,: 設定",
            "F1: ヘルプ"
        ]
        
        y_start = canvas_height // 2 - len(text_lines) * 10
        for i, line in enumerate(text_lines):
            self.preview_canvas.create_text(
                canvas_width // 2, y_start + i * 20,
                text=line, font=get_gui_font(), anchor="center",
                fill=get_color("text_primary")
            )
    
    def _open_video_file(self):
        """動画ファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="動画ファイルを選択",
            filetypes=[
                ("MP4 動画", "*.mp4"),
                ("すべてのファイル", "*.*")
            ],
            initialdir=self.config.get('default_output_directory') or str(Path.home())
        )
        
        if file_path:
            try:
                # VideoFileオブジェクト作成
                video_file = VideoFile(file_path=Path(file_path))
                
                self.current_video = video_file
                self.video_path_var.set(f"{video_file.file_path.name}")
                self.status_bar_var.set(f"動画ファイル選択: {video_file.file_path.name}")
                
                # ボタン状態更新
                self.extract_button.config(state="normal")
                
                # コールバック実行
                if self.on_video_selected:
                    self.on_video_selected(video_file)
                
                self.logger.info(f"動画ファイル選択: {file_path}")
                
            except Exception as e:
                self.logger.error(f"動画ファイル読み込みエラー: {e}")
                messagebox.showerror("エラー", f"動画ファイルの読み込みに失敗しました:\\n{e}")
    
    def _apply_preset(self, preset_name: str):
        """設定プリセットを適用"""
        try:
            from ..lib import ConfigPresets
            
            if preset_name == "high_quality":
                preset = ConfigPresets.high_quality()
            elif preset_name == "fast_generation":
                preset = ConfigPresets.fast_generation()
            else:
                return
            
            # GUI設定を更新
            self.thumbnail_count_var.set(preset.get('default_thumbnail_count', 5))
            self.width_var.set(preset.get('default_output_width', 1920))
            self.height_var.set(preset.get('default_output_height', 1080))
            
            self.status_bar_var.set(f"{preset_name} プリセットを適用しました")
            self.logger.info(f"プリセット適用: {preset_name}")
            
        except Exception as e:
            self.logger.error(f"プリセット適用エラー: {e}")
            messagebox.showwarning("警告", f"プリセットの適用に失敗しました: {e}")
    
    def _start_extraction(self):
        """サムネイル抽出を開始"""
        if not self.current_video:
            messagebox.showwarning("警告", "動画ファイルを選択してください。")
            return
        
        if self.is_processing:
            return
        
        try:
            # UserSettings作成
            settings = UserSettings(
                thumbnail_count=self.thumbnail_count_var.get(),
                output_width=self.width_var.get(),
                output_height=self.height_var.get()
            )
            
            # UI状態更新
            self.is_processing = True
            self.extract_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.progress_var.set(0.0)
            self.status_var.set("処理を開始しています...")
            
            # コールバック実行
            if self.on_extraction_start:
                # 非同期で実行（UIをブロックしない）
                threading.Thread(
                    target=lambda: self.on_extraction_start(settings),
                    daemon=True
                ).start()
            
            self.logger.info("サムネイル抽出開始")
            
        except Exception as e:
            self.logger.error(f"抽出開始エラー: {e}")
            messagebox.showerror("エラー", f"処理の開始に失敗しました:\\n{e}")
            self._reset_ui_state()
    
    def _cancel_extraction(self):
        """サムネイル抽出をキャンセル"""
        if not self.is_processing:
            return
        
        self.logger.info("サムネイル抽出キャンセル")
        self._reset_ui_state()
        self.status_var.set("キャンセルされました")
        self.status_bar_var.set("キャンセル完了")
    
    def _reset_ui_state(self):
        """UI状態をリセット"""
        self.is_processing = False
        self.extract_button.config(state="normal" if self.current_video else "disabled")
        self.cancel_button.config(state="disabled")
        self.progress_var.set(0.0)
    
    def _save_thumbnails(self):
        """選択されたサムネイルを保存"""
        # ThumbnailGridで実装される選択機能と連携
        messagebox.showinfo("情報", "サムネイル保存機能は ThumbnailGrid と連携して実装されます。")
    
    def _open_settings(self):
        """設定ダイアログを開く"""
        # SettingsDialogで実装
        messagebox.showinfo("情報", "設定ダイアログは SettingsDialog クラスで実装されます。")
    
    def _reset_settings(self):
        """設定をリセット"""
        try:
            self.config.reset_to_defaults()
            
            # GUI値も更新
            self.thumbnail_count_var.set(self.config.get('default_thumbnail_count', 5))
            self.width_var.set(self.config.get('default_output_width', 1920))
            self.height_var.set(self.config.get('default_output_height', 1080))
            
            self.status_bar_var.set("設定をデフォルト値にリセットしました")
            messagebox.showinfo("完了", "設定をデフォルト値にリセットしました。")
            
        except Exception as e:
            self.logger.error(f"設定リセットエラー: {e}")
            messagebox.showerror("エラー", f"設定のリセットに失敗しました: {e}")
    
    def _show_help(self):
        """ヘルプを表示"""
        help_text = """動画サムネイル抽出アプリケーション ヘルプ

使用方法:
1. 「動画を選択...」ボタンでMP4ファイルを選択
2. サムネイル枚数と出力サイズを設定
3. 「サムネイル抽出開始」をクリック
4. 生成されたサムネイル候補から保存したいものを選択
5. 「選択したサムネイルを保存」で保存

ショートカットキー:
- Ctrl+O: 動画ファイルを開く
- Ctrl+,: 設定を開く
- Ctrl+Q: アプリケーション終了
- F1: このヘルプを表示
- Enter: 抽出開始（動画選択済みの場合）
- Esc: 処理キャンセル

対応フォーマット:
- 動画: MP4のみ
- 出力: PNG形式

お問い合わせ:
技術的な問題がある場合は、ログファイルを確認してください。"""
        
        messagebox.showinfo("ヘルプ", help_text)
    
    def _show_about(self):
        """バージョン情報を表示"""
        from .. import __version__ as app_version
        from . import __version__ as gui_version
        
        about_text = f"""動画サムネイル抽出アプリケーション

アプリケーションバージョン: {app_version}
GUIバージョン: {gui_version}

開発者: s-anzai
技術スタック: Python, tkinter, OpenCV, MediaPipe

機能:
- AI顔検出による高品質なサムネイル抽出
- 多様性を重視した候補生成
- ローカル処理によるプライバシー保護

© 2024 All rights reserved."""
        
        messagebox.showinfo("バージョン情報", about_text)
    
    def _on_closing(self):
        """ウィンドウを閉じる際の処理"""
        if self.is_processing:
            if messagebox.askyesno("確認", "処理中です。終了しますか？"):
                self._cancel_extraction()
                self.root.quit()
        else:
            self.root.quit()
    
    # パブリックメソッド（外部から呼び出し可能）
    
    def show(self):
        """ウィンドウを表示"""
        self.root.deiconify()
        self.root.mainloop()
    
    def close(self):
        """ウィンドウを閉じる"""
        self._on_closing()
    
    def update_progress(self, progress: float, status_message: str):
        """進捗を更新"""
        if self.root.winfo_exists():
            self.progress_var.set(min(100.0, max(0.0, progress)))
            self.status_var.set(status_message)
            self.status_bar_var.set(f"進捗: {progress:.1f}% - {status_message}")
            self.root.update_idletasks()
    
    def set_thumbnails(self, thumbnails: List['Thumbnail']):
        """サムネイル結果を設定"""
        # ThumbnailGridと連携して実装
        self.save_button.config(state="normal")
        self._reset_ui_state()
        self.status_var.set(f"完了 - {len(thumbnails)}個のサムネイルを生成")
        self.status_bar_var.set("サムネイル生成完了")
    
    def show_error(self, error_message: str):
        """エラーメッセージを表示"""
        self._reset_ui_state()
        self.status_var.set("エラーが発生しました")
        self.status_bar_var.set("エラー")
        messagebox.showerror("エラー", error_message)
