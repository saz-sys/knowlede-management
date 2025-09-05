"""
SettingsDialog（設定ダイアログ）実装

アプリケーション設定の詳細設定ダイアログを実装します。
サイズ・枚数入力、バリデーション、プリセット管理などの機能を提供します。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import logging

from ..lib import get_logger, get_config, ConfigPresets, ValidationError
from . import get_gui_font, get_color, get_config as get_gui_config


class SettingsDialog:
    """設定ダイアログクラス"""
    
    def __init__(self, parent: tk.Tk, config_changed_callback: Optional[Callable] = None):
        """
        設定ダイアログを初期化
        
        Args:
            parent: 親ウィンドウ
            config_changed_callback: 設定変更時のコールバック関数
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.parent = parent
        self.config_changed_callback = config_changed_callback
        
        # ダイアログウィンドウ作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("設定")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 中央配置
        self._center_dialog()
        
        # 設定値保持用変数
        self._setup_variables()
        
        # GUI構築
        self._setup_ui()
        
        # 現在の設定値を読み込み
        self._load_current_settings()
        
        # イベントハンドリング
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self.logger.info("設定ダイアログ初期化完了")
    
    def _center_dialog(self):
        """ダイアログを親ウィンドウの中央に配置"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        dialog_w = self.dialog.winfo_width()
        dialog_h = self.dialog.winfo_height()
        
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
    
    def _setup_variables(self):
        """設定値保持用変数を初期化"""
        # 基本設定
        self.thumbnail_count_var = tk.IntVar()
        self.output_width_var = tk.IntVar()
        self.output_height_var = tk.IntVar()
        self.quality_threshold_var = tk.DoubleVar()
        self.diversity_weight_var = tk.DoubleVar()
        
        # パス設定
        self.output_directory_var = tk.StringVar()
        self.temp_directory_var = tk.StringVar()
        
        # 処理設定
        self.max_frame_buffer_var = tk.IntVar()
        self.timeout_var = tk.IntVar()
        self.face_confidence_var = tk.DoubleVar()
        self.min_face_size_var = tk.DoubleVar()
        
        # GUI設定
        self.window_width_var = tk.IntVar()
        self.window_height_var = tk.IntVar()
        self.auto_save_var = tk.BooleanVar()
        self.show_debug_var = tk.BooleanVar()
        
        # ログ設定
        self.log_level_var = tk.StringVar()
        self.log_to_file_var = tk.BooleanVar()
        self.log_rotation_var = tk.IntVar()
    
    def _setup_ui(self):
        """UIを構築"""
        # メインコンテナ
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # タブ管理
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # 各タブを作成
        self._create_basic_tab(notebook)
        self._create_advanced_tab(notebook)
        self._create_paths_tab(notebook)
        self._create_performance_tab(notebook)
        self._create_gui_tab(notebook)
        self._create_logging_tab(notebook)
        
        # ボタンエリア
        self._create_button_area(main_frame)
    
    def _create_basic_tab(self, notebook):
        """基本設定タブ"""
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本設定")
        
        # サムネイル設定
        thumb_frame = ttk.LabelFrame(basic_frame, text="サムネイル設定", padding="5")
        thumb_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(thumb_frame, text="枚数:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(thumb_frame, from_=1, to=20, width=10,
                   textvariable=self.thumbnail_count_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(thumb_frame, text="幅:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(thumb_frame, from_=240, to=4096, width=10,
                   textvariable=self.output_width_var).grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(thumb_frame, text="高さ:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(thumb_frame, from_=240, to=4096, width=10,
                   textvariable=self.output_height_var).grid(row=2, column=1, sticky="ew", padx=(5, 0))
        
        thumb_frame.columnconfigure(1, weight=1)
        
        # 品質設定
        quality_frame = ttk.LabelFrame(basic_frame, text="品質設定", padding="5")
        quality_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(quality_frame, text="品質閾値:").grid(row=0, column=0, sticky="w", pady=2)
        quality_scale = ttk.Scale(quality_frame, from_=0.0, to=1.0, orient="horizontal",
                                variable=self.quality_threshold_var)
        quality_scale.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        quality_value = ttk.Label(quality_frame, text="0.70")
        quality_value.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Label(quality_frame, text="多様性重み:").grid(row=1, column=0, sticky="w", pady=2)
        diversity_scale = ttk.Scale(quality_frame, from_=0.0, to=1.0, orient="horizontal",
                                  variable=self.diversity_weight_var)
        diversity_scale.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        diversity_value = ttk.Label(quality_frame, text="0.80")
        diversity_value.grid(row=1, column=2, padx=(5, 0))
        
        quality_frame.columnconfigure(1, weight=1)
        
        # スケールの値表示を更新する関数
        def update_quality_label(*args):
            quality_value.config(text=f"{self.quality_threshold_var.get():.2f}")
        
        def update_diversity_label(*args):
            diversity_value.config(text=f"{self.diversity_weight_var.get():.2f}")
        
        self.quality_threshold_var.trace('w', update_quality_label)
        self.diversity_weight_var.trace('w', update_diversity_label)
        
        # プリセット適用
        preset_frame = ttk.LabelFrame(basic_frame, text="プリセット", padding="5")
        preset_frame.pack(fill="x")
        
        button_frame = ttk.Frame(preset_frame)
        button_frame.pack(fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="高品質",
                  command=lambda: self._apply_preset("high_quality")).grid(row=0, column=0, sticky="ew", padx=1)
        ttk.Button(button_frame, text="高速",
                  command=lambda: self._apply_preset("fast_generation")).grid(row=0, column=1, sticky="ew", padx=1)
        ttk.Button(button_frame, text="高多様性",
                  command=lambda: self._apply_preset("high_diversity")).grid(row=0, column=2, sticky="ew", padx=1)
    
    def _create_advanced_tab(self, notebook):
        """高度な設定タブ"""
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="高度な設定")
        
        # 顔検出設定
        face_frame = ttk.LabelFrame(advanced_frame, text="顔検出設定", padding="5")
        face_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(face_frame, text="検出信頼度:").grid(row=0, column=0, sticky="w", pady=2)
        face_conf_scale = ttk.Scale(face_frame, from_=0.0, to=1.0, orient="horizontal",
                                  variable=self.face_confidence_var)
        face_conf_scale.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        face_conf_value = ttk.Label(face_frame, text="0.50")
        face_conf_value.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Label(face_frame, text="最小顔サイズ:").grid(row=1, column=0, sticky="w", pady=2)
        face_size_scale = ttk.Scale(face_frame, from_=0.001, to=0.1, orient="horizontal",
                                  variable=self.min_face_size_var)
        face_size_scale.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        face_size_value = ttk.Label(face_frame, text="0.010")
        face_size_value.grid(row=1, column=2, padx=(5, 0))
        
        face_frame.columnconfigure(1, weight=1)
        
        # スケールの値表示更新
        def update_face_conf_label(*args):
            face_conf_value.config(text=f"{self.face_confidence_var.get():.2f}")
        
        def update_face_size_label(*args):
            face_size_value.config(text=f"{self.min_face_size_var.get():.3f}")
        
        self.face_confidence_var.trace('w', update_face_conf_label)
        self.min_face_size_var.trace('w', update_face_size_label)
    
    def _create_paths_tab(self, notebook):
        """パス設定タブ"""
        paths_frame = ttk.Frame(notebook, padding="10")
        notebook.add(paths_frame, text="パス設定")
        
        # 出力ディレクトリ
        output_frame = ttk.LabelFrame(paths_frame, text="出力ディレクトリ", padding="5")
        output_frame.pack(fill="x", pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        entry_frame1 = ttk.Frame(output_frame)
        entry_frame1.pack(fill="x")
        entry_frame1.columnconfigure(0, weight=1)
        
        ttk.Entry(entry_frame1, textvariable=self.output_directory_var).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(entry_frame1, text="参照...", 
                  command=lambda: self._browse_directory(self.output_directory_var)).grid(row=0, column=1)
        
        ttk.Label(output_frame, text="※空欄の場合はダウンロードフォルダを使用",
                 font=get_gui_font(-1)).pack(anchor="w", pady=(5, 0))
        
        # 一時ディレクトリ
        temp_frame = ttk.LabelFrame(paths_frame, text="一時ディレクトリ", padding="5")
        temp_frame.pack(fill="x")
        temp_frame.columnconfigure(0, weight=1)
        
        entry_frame2 = ttk.Frame(temp_frame)
        entry_frame2.pack(fill="x")
        entry_frame2.columnconfigure(0, weight=1)
        
        ttk.Entry(entry_frame2, textvariable=self.temp_directory_var).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(entry_frame2, text="参照...",
                  command=lambda: self._browse_directory(self.temp_directory_var)).grid(row=0, column=1)
        
        ttk.Label(temp_frame, text="※空欄の場合はシステムデフォルトを使用",
                 font=get_gui_font(-1)).pack(anchor="w", pady=(5, 0))
    
    def _create_performance_tab(self, notebook):
        """パフォーマンス設定タブ"""
        perf_frame = ttk.Frame(notebook, padding="10")
        notebook.add(perf_frame, text="パフォーマンス")
        
        # メモリ設定
        memory_frame = ttk.LabelFrame(perf_frame, text="メモリ設定", padding="5")
        memory_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(memory_frame, text="最大フレームバッファ:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(memory_frame, from_=10, to=1000, width=10,
                   textvariable=self.max_frame_buffer_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ttk.Label(memory_frame, text="フレーム").grid(row=0, column=2, padx=(5, 0))
        
        memory_frame.columnconfigure(1, weight=1)
        
        # タイムアウト設定
        timeout_frame = ttk.LabelFrame(perf_frame, text="タイムアウト設定", padding="5")
        timeout_frame.pack(fill="x")
        
        ttk.Label(timeout_frame, text="処理タイムアウト:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(timeout_frame, from_=60, to=1800, width=10,
                   textvariable=self.timeout_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ttk.Label(timeout_frame, text="秒").grid(row=0, column=2, padx=(5, 0))
        
        timeout_frame.columnconfigure(1, weight=1)
    
    def _create_gui_tab(self, notebook):
        """GUI設定タブ"""
        gui_frame = ttk.Frame(notebook, padding="10")
        notebook.add(gui_frame, text="GUI設定")
        
        # ウィンドウサイズ
        window_frame = ttk.LabelFrame(gui_frame, text="ウィンドウサイズ", padding="5")
        window_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(window_frame, text="幅:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(window_frame, from_=800, to=2560, width=10,
                   textvariable=self.window_width_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(window_frame, text="高さ:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(window_frame, from_=600, to=1440, width=10,
                   textvariable=self.window_height_var).grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        window_frame.columnconfigure(1, weight=1)
        
        # その他のGUI設定
        other_frame = ttk.LabelFrame(gui_frame, text="その他", padding="5")
        other_frame.pack(fill="x")
        
        ttk.Checkbutton(other_frame, text="設定を自動保存",
                       variable=self.auto_save_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(other_frame, text="デバッグ情報を表示",
                       variable=self.show_debug_var).pack(anchor="w", pady=2)
    
    def _create_logging_tab(self, notebook):
        """ログ設定タブ"""
        log_frame = ttk.Frame(notebook, padding="10")
        notebook.add(log_frame, text="ログ設定")
        
        # ログレベル
        level_frame = ttk.LabelFrame(log_frame, text="ログレベル", padding="5")
        level_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(level_frame, text="レベル:").grid(row=0, column=0, sticky="w", pady=2)
        level_combo = ttk.Combobox(level_frame, textvariable=self.log_level_var,
                                 values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                 state="readonly")
        level_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        level_frame.columnconfigure(1, weight=1)
        
        # ログ出力設定
        output_frame = ttk.LabelFrame(log_frame, text="出力設定", padding="5")
        output_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Checkbutton(output_frame, text="ファイルに出力",
                       variable=self.log_to_file_var).pack(anchor="w", pady=2)
        
        rotation_frame = ttk.Frame(output_frame)
        rotation_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(rotation_frame, text="ローテーション:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(rotation_frame, from_=1, to=30, width=10,
                   textvariable=self.log_rotation_var).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ttk.Label(rotation_frame, text="日").grid(row=0, column=2, padx=(5, 0))
        
        rotation_frame.columnconfigure(1, weight=1)
    
    def _create_button_area(self, parent):
        """ボタンエリア作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        # 右寄せのボタン配置
        inner_frame = ttk.Frame(button_frame)
        inner_frame.pack(side="right")
        
        ttk.Button(inner_frame, text="キャンセル",
                  command=self._on_cancel).pack(side="right", padx=(5, 0))
        ttk.Button(inner_frame, text="OK",
                  command=self._on_ok).pack(side="right")
        ttk.Button(inner_frame, text="適用",
                  command=self._on_apply).pack(side="right", padx=(0, 5))
        ttk.Button(inner_frame, text="デフォルトに戻す",
                  command=self._on_reset).pack(side="right", padx=(0, 10))
    
    def _browse_directory(self, var: tk.StringVar):
        """ディレクトリ選択ダイアログ"""
        directory = filedialog.askdirectory(
            title="ディレクトリを選択",
            initialdir=var.get() or str(Path.home())
        )
        if directory:
            var.set(directory)
    
    def _apply_preset(self, preset_name: str):
        """プリセットを適用"""
        try:
            if preset_name == "high_quality":
                preset = ConfigPresets.high_quality()
            elif preset_name == "fast_generation":
                preset = ConfigPresets.fast_generation()
            elif preset_name == "high_diversity":
                preset = ConfigPresets.high_diversity()
            else:
                return
            
            # プリセット値を設定
            for key, value in preset.items():
                if hasattr(self, f"{key}_var"):
                    var = getattr(self, f"{key}_var")
                    var.set(value)
            
            messagebox.showinfo("完了", f"{preset_name} プリセットを適用しました。")
            
        except Exception as e:
            self.logger.error(f"プリセット適用エラー: {e}")
            messagebox.showerror("エラー", f"プリセットの適用に失敗しました: {e}")
    
    def _load_current_settings(self):
        """現在の設定値を読み込み"""
        try:
            config_data = self.config.get_all()
            
            # 各変数に設定値を適用
            setting_mappings = {
                'default_thumbnail_count': self.thumbnail_count_var,
                'default_output_width': self.output_width_var,
                'default_output_height': self.output_height_var,
                'default_quality_threshold': self.quality_threshold_var,
                'default_diversity_weight': self.diversity_weight_var,
                'default_output_directory': self.output_directory_var,
                'temp_directory': self.temp_directory_var,
                'max_frame_buffer_size': self.max_frame_buffer_var,
                'processing_timeout_seconds': self.timeout_var,
                'face_detection_confidence': self.face_confidence_var,
                'min_face_size': self.min_face_size_var,
                'window_width': self.window_width_var,
                'window_height': self.window_height_var,
                'auto_save_settings': self.auto_save_var,
                'show_debug_info': self.show_debug_var,
                'log_level': self.log_level_var,
                'log_to_file': self.log_to_file_var,
                'log_rotation_days': self.log_rotation_var,
            }
            
            for setting_key, var in setting_mappings.items():
                value = config_data.get(setting_key)
                if value is not None:
                    var.set(value)
            
            self.logger.info("設定値読み込み完了")
            
        except Exception as e:
            self.logger.error(f"設定値読み込みエラー: {e}")
            messagebox.showerror("エラー", f"設定値の読み込みに失敗しました: {e}")
    
    def _save_settings(self) -> bool:
        """設定を保存"""
        try:
            # バリデーション
            is_valid, errors = self._validate_settings()
            if not is_valid:
                messagebox.showerror("入力エラー", "\\n".join(errors))
                return False
            
            # 設定値を更新
            setting_mappings = {
                'default_thumbnail_count': self.thumbnail_count_var.get(),
                'default_output_width': self.output_width_var.get(),
                'default_output_height': self.output_height_var.get(),
                'default_quality_threshold': self.quality_threshold_var.get(),
                'default_diversity_weight': self.diversity_weight_var.get(),
                'default_output_directory': self.output_directory_var.get(),
                'temp_directory': self.temp_directory_var.get(),
                'max_frame_buffer_size': self.max_frame_buffer_var.get(),
                'processing_timeout_seconds': self.timeout_var.get(),
                'face_detection_confidence': self.face_confidence_var.get(),
                'min_face_size': self.min_face_size_var.get(),
                'window_width': self.window_width_var.get(),
                'window_height': self.window_height_var.get(),
                'auto_save_settings': self.auto_save_var.get(),
                'show_debug_info': self.show_debug_var.get(),
                'log_level': self.log_level_var.get(),
                'log_to_file': self.log_to_file_var.get(),
                'log_rotation_days': self.log_rotation_var.get(),
            }
            
            for key, value in setting_mappings.items():
                self.config.set(key, value, save_immediately=False)
            
            # 一括保存
            if self.config.save():
                # コールバック実行
                if self.config_changed_callback:
                    self.config_changed_callback()
                
                self.logger.info("設定保存完了")
                return True
            else:
                messagebox.showerror("エラー", "設定の保存に失敗しました。")
                return False
                
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
            messagebox.showerror("エラー", f"設定の保存中にエラーが発生しました: {e}")
            return False
    
    def _validate_settings(self) -> tuple[bool, list[str]]:
        """設定値のバリデーション"""
        errors = []
        
        # 数値範囲チェック
        if not (1 <= self.thumbnail_count_var.get() <= 20):
            errors.append("サムネイル枚数は1-20の範囲で入力してください。")
        
        if not (240 <= self.output_width_var.get() <= 4096):
            errors.append("出力幅は240-4096の範囲で入力してください。")
        
        if not (240 <= self.output_height_var.get() <= 4096):
            errors.append("出力高さは240-4096の範囲で入力してください。")
        
        # パス存在チェック
        output_dir = self.output_directory_var.get()
        if output_dir and not Path(output_dir).exists():
            errors.append(f"出力ディレクトリが存在しません: {output_dir}")
        
        temp_dir = self.temp_directory_var.get()
        if temp_dir and not Path(temp_dir).exists():
            errors.append(f"一時ディレクトリが存在しません: {temp_dir}")
        
        return len(errors) == 0, errors
    
    def _on_ok(self):
        """OKボタン処理"""
        if self._save_settings():
            self.dialog.destroy()
    
    def _on_apply(self):
        """適用ボタン処理"""
        if self._save_settings():
            messagebox.showinfo("完了", "設定を保存しました。")
    
    def _on_cancel(self):
        """キャンセルボタン処理"""
        self.dialog.destroy()
    
    def _on_reset(self):
        """リセットボタン処理"""
        if messagebox.askyesno("確認", "すべての設定をデフォルト値に戻しますか？"):
            try:
                self.config.reset_to_defaults()
                self._load_current_settings()
                messagebox.showinfo("完了", "設定をデフォルト値に戻しました。")
            except Exception as e:
                self.logger.error(f"設定リセットエラー: {e}")
                messagebox.showerror("エラー", f"設定のリセットに失敗しました: {e}")
    
    def show(self):
        """ダイアログを表示"""
        self.dialog.wait_window()


def show_settings_dialog(parent: tk.Tk, config_changed_callback: Optional[Callable] = None):
    """設定ダイアログを表示する便利関数"""
    dialog = SettingsDialog(parent, config_changed_callback)
    dialog.show()
