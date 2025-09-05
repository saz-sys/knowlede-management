#!/usr/bin/env python3
"""
Video Thumbnail Extractor - Rich Modern UI
CustomTkinterを使用した超モダンなUIデザイン
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import time
import threading
from pathlib import Path
from PIL import Image, ImageTk
import json

# CustomTkinter設定
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "dark-blue", "green"

class RichVideoThumbnailApp:
    """超リッチなVideo Thumbnail Extractorアプリケーション"""
    
    def __init__(self):
        self.app_state = {
            'selected_file': None,
            'thumbnail_count': 5,
            'output_size': '1280x720',
            'output_directory': None,
            'dark_mode': True,
            'processing': False
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI初期化"""
        # メインウィンドウ
        self.root = ctk.CTk()
        self.root.title("🎬 Video Thumbnail Extractor - Rich Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # ウィンドウアイコン設定（もしアイコンファイルがあれば）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        print("✅ メインウィンドウ作成完了")
        
        # レイアウト構築
        self.create_layout()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # キーボードショートカット
        self.setup_shortcuts()
        
        print("✅ Rich Modern UI構築完了")
    
    def create_layout(self):
        """基本レイアウト構築"""
        # サイドバー
        self.sidebar = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # メインコンテンツエリア
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)
        
        print("✅ 基本レイアウト作成完了")
    
    def create_sidebar(self):
        """サイドバー作成"""
        # ロゴセクション
        logo_frame = ctk.CTkFrame(self.sidebar, corner_radius=10)
        logo_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🎬\nVideo Thumbnail\nExtractor",
            font=ctk.CTkFont(size=20, weight="bold"),
            justify="center"
        )
        logo_label.pack(pady=20)
        
        version_label = ctk.CTkLabel(
            logo_frame,
            text="v2.0 Rich Edition",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        version_label.pack(pady=(0, 15))
        
        # ナビゲーション
        nav_frame = ctk.CTkFrame(self.sidebar, corner_radius=10)
        nav_frame.pack(fill="x", padx=20, pady=10)
        
        nav_title = ctk.CTkLabel(
            nav_frame,
            text="Navigation",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        nav_title.pack(pady=(15, 10))
        
        # ナビゲーションボタン
        nav_buttons = [
            ("📁 Import Video", self.import_video, "Import video files"),
            ("⚙️ Settings", self.open_settings, "Configure generation settings"),
            ("🖼️ Preview", self.show_preview, "Preview generated thumbnails"),
            ("💾 Export", self.export_thumbnails, "Export thumbnails"),
            ("📊 Analytics", self.show_analytics, "View generation statistics"),
            ("🎨 Themes", self.change_theme, "Switch between themes"),
            ("ℹ️ About", self.show_about, "About this application")
        ]
        
        self.nav_buttons = {}
        for text, command, tooltip in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                width=240,
                height=40,
                font=ctk.CTkFont(size=13),
                corner_radius=8,
                anchor="w"
            )
            btn.pack(pady=3, padx=15)
            self.nav_buttons[text] = btn
            
            # ツールチップ（簡易版）
            self.create_tooltip(btn, tooltip)
        
        # 設定パネル
        settings_frame = ctk.CTkFrame(self.sidebar, corner_radius=10)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Quick Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_title.pack(pady=(15, 10))
        
        # ダークモード切り替え
        self.theme_switch = ctk.CTkSwitch(
            settings_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.pack(pady=5)
        self.theme_switch.select()  # デフォルトでON
        
        # 自動保存
        self.autosave_switch = ctk.CTkSwitch(
            settings_frame,
            text="Auto Save",
            font=ctk.CTkFont(size=12)
        )
        self.autosave_switch.pack(pady=5)
        
        # 高品質モード
        self.hq_switch = ctk.CTkSwitch(
            settings_frame,
            text="High Quality",
            font=ctk.CTkFont(size=12)
        )
        self.hq_switch.pack(pady=(5, 15))
        
        print("✅ サイドバー作成完了")
    
    def create_main_content(self):
        """メインコンテンツエリア作成"""
        # ヘッダー
        header_frame = ctk.CTkFrame(self.main_container, height=80, corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # タイトルとコントロール
        title_label = ctk.CTkLabel(
            header_frame,
            text="Video Thumbnail Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=25)
        
        # ヘッダーボタン群
        header_btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_btn_frame.pack(side="right", padx=20, pady=15)
        
        help_btn = ctk.CTkButton(
            header_btn_frame,
            text="❓",
            width=40,
            height=40,
            corner_radius=20,
            command=self.show_help
        )
        help_btn.pack(side="right", padx=5)
        
        minimize_btn = ctk.CTkButton(
            header_btn_frame,
            text="−",
            width=40,
            height=40,
            corner_radius=20,
            command=self.minimize_window
        )
        minimize_btn.pack(side="right", padx=5)
        
        # メインコンテンツ（タブ形式）
        self.tabview = ctk.CTkTabview(self.main_container, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # タブ作成
        self.tab_import = self.tabview.add("📁 Import")
        self.tab_process = self.tabview.add("⚙️ Process")
        self.tab_preview = self.tabview.add("👁️ Preview")
        self.tab_export = self.tabview.add("💾 Export")
        
        # タブ内容作成
        self.create_import_tab()
        self.create_process_tab()
        self.create_preview_tab()
        self.create_export_tab()
        
        print("✅ メインコンテンツ作成完了")
    
    def create_import_tab(self):
        """インポートタブ"""
        # ファイルドロップエリア
        self.drop_frame = ctk.CTkFrame(self.tab_import, height=250, corner_radius=15)
        self.drop_frame.pack(fill="x", padx=20, pady=20)
        self.drop_frame.pack_propagate(False)
        
        # ドロップエリア装飾
        drop_icon = ctk.CTkLabel(
            self.drop_frame,
            text="📤",
            font=ctk.CTkFont(size=60)
        )
        drop_icon.place(relx=0.5, rely=0.3, anchor="center")
        
        drop_title = ctk.CTkLabel(
            self.drop_frame,
            text="Drag & Drop Video File Here",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        drop_title.place(relx=0.5, rely=0.5, anchor="center")
        
        drop_subtitle = ctk.CTkLabel(
            self.drop_frame,
            text="Support formats: MP4, AVI, MOV, MKV, WMV, FLV",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        drop_subtitle.place(relx=0.5, rely=0.65, anchor="center")
        
        # ボタンエリア
        button_frame = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        button_frame.place(relx=0.5, rely=0.85, anchor="center")
        
        browse_btn = ctk.CTkButton(
            button_frame,
            text="📁 Browse Files",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=20,
            command=self.browse_video_file
        )
        browse_btn.pack(side="left", padx=10)
        
        recent_btn = ctk.CTkButton(
            button_frame,
            text="🕒 Recent Files",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=20,
            command=self.show_recent_files
        )
        recent_btn.pack(side="left", padx=10)
        
        # 選択ファイル情報
        self.file_info_frame = ctk.CTkFrame(self.tab_import, corner_radius=10)
        self.file_info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.selected_file_label = ctk.CTkLabel(
            self.file_info_frame,
            text="No file selected",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.selected_file_label.pack(fill="x", padx=20, pady=15)
        
        # ドラッグ&ドロップイベント（簡易実装）
        self.drop_frame.bind("<Button-1>", lambda e: self.browse_video_file())
        
        print("✅ インポートタブ作成完了")
    
    def create_process_tab(self):
        """処理タブ"""
        # 設定グループ
        settings_group = ctk.CTkFrame(self.tab_process, corner_radius=10)
        settings_group.pack(fill="x", padx=20, pady=20)
        
        settings_title = ctk.CTkLabel(
            settings_group,
            text="Generation Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_title.pack(pady=(20, 15))
        
        # サムネイル数設定
        count_frame = ctk.CTkFrame(settings_group, fg_color="transparent")
        count_frame.pack(fill="x", padx=20, pady=10)
        
        count_label = ctk.CTkLabel(
            count_frame,
            text="Number of Thumbnails",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        count_label.pack(anchor="w")
        
        count_info_frame = ctk.CTkFrame(count_frame, fg_color="transparent")
        count_info_frame.pack(fill="x", pady=(5, 0))
        
        self.count_slider = ctk.CTkSlider(
            count_info_frame,
            from_=1,
            to=50,
            number_of_steps=49,
            width=300,
            command=self.update_count_value
        )
        self.count_slider.pack(side="left")
        self.count_slider.set(self.app_state['thumbnail_count'])
        
        self.count_value_label = ctk.CTkLabel(
            count_info_frame,
            text=f"{self.app_state['thumbnail_count']} thumbnails",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100
        )
        self.count_value_label.pack(side="right", padx=(20, 0))
        
        # 出力サイズ設定
        size_frame = ctk.CTkFrame(settings_group, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=10)
        
        size_label = ctk.CTkLabel(
            size_frame,
            text="Output Resolution",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        size_label.pack(anchor="w")
        
        self.size_var = ctk.StringVar(value=self.app_state['output_size'])
        size_menu = ctk.CTkOptionMenu(
            size_frame,
            variable=self.size_var,
            values=["640x360 (360p)", "1280x720 (720p)", "1920x1080 (1080p)", "3840x2160 (4K)"],
            width=300,
            font=ctk.CTkFont(size=12)
        )
        size_menu.pack(anchor="w", pady=(5, 0))
        
        # 詳細設定
        advanced_frame = ctk.CTkFrame(settings_group, fg_color="transparent")
        advanced_frame.pack(fill="x", padx=20, pady=(15, 20))
        
        advanced_label = ctk.CTkLabel(
            advanced_frame,
            text="Advanced Options",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        advanced_label.pack(anchor="w")
        
        options_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(5, 0))
        
        # チェックボックス群
        self.face_detection_var = ctk.BooleanVar(value=True)
        face_check = ctk.CTkCheckBox(
            options_frame,
            text="Enable Face Detection",
            variable=self.face_detection_var,
            font=ctk.CTkFont(size=12)
        )
        face_check.pack(anchor="w", pady=2)
        
        self.diversity_var = ctk.BooleanVar(value=True)
        diversity_check = ctk.CTkCheckBox(
            options_frame,
            text="Maximize Diversity",
            variable=self.diversity_var,
            font=ctk.CTkFont(size=12)
        )
        diversity_check.pack(anchor="w", pady=2)
        
        self.timestamp_var = ctk.BooleanVar(value=False)
        timestamp_check = ctk.CTkCheckBox(
            options_frame,
            text="Add Timestamp",
            variable=self.timestamp_var,
            font=ctk.CTkFont(size=12)
        )
        timestamp_check.pack(anchor="w", pady=2)
        
        # 処理ボタン
        process_btn_frame = ctk.CTkFrame(self.tab_process, fg_color="transparent")
        process_btn_frame.pack(pady=30)
        
        self.process_btn = ctk.CTkButton(
            process_btn_frame,
            text="🚀 Generate Thumbnails",
            width=250,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=25,
            command=self.start_processing
        )
        self.process_btn.pack()
        
        print("✅ 処理タブ作成完了")
    
    def create_preview_tab(self):
        """プレビュータブ"""
        # プレビューエリア
        preview_frame = ctk.CTkScrollableFrame(self.tab_preview, corner_radius=10)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # プレースホルダー
        placeholder = ctk.CTkLabel(
            preview_frame,
            text="🖼️\n\nThumbnail previews will appear here\nafter generation",
            font=ctk.CTkFont(size=18),
            text_color=("gray60", "gray40")
        )
        placeholder.pack(expand=True, pady=100)
        
        print("✅ プレビュータブ作成完了")
    
    def create_export_tab(self):
        """エクスポートタブ"""
        # エクスポート設定
        export_frame = ctk.CTkFrame(self.tab_export, corner_radius=10)
        export_frame.pack(fill="x", padx=20, pady=20)
        
        export_title = ctk.CTkLabel(
            export_frame,
            text="Export Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        export_title.pack(pady=(20, 15))
        
        # 保存先設定
        path_frame = ctk.CTkFrame(export_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=10)
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="Output Directory",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        path_label.pack(anchor="w")
        
        path_select_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_select_frame.pack(fill="x", pady=(5, 0))
        
        self.output_path_var = ctk.StringVar(value="Same as video file")
        path_entry = ctk.CTkEntry(
            path_select_frame,
            textvariable=self.output_path_var,
            width=300,
            font=ctk.CTkFont(size=12)
        )
        path_entry.pack(side="left")
        
        browse_path_btn = ctk.CTkButton(
            path_select_frame,
            text="Browse",
            width=80,
            command=self.browse_output_path
        )
        browse_path_btn.pack(side="right", padx=(10, 0))
        
        # エクスポートボタン
        export_btn_frame = ctk.CTkFrame(self.tab_export, fg_color="transparent")
        export_btn_frame.pack(pady=30)
        
        export_btn = ctk.CTkButton(
            export_btn_frame,
            text="💾 Export All Thumbnails",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=22,
            command=self.export_all_thumbnails
        )
        export_btn.pack()
        
        print("✅ エクスポートタブ作成完了")
    
    def create_status_bar(self):
        """ステータスバー作成"""
        self.status_frame = ctk.CTkFrame(self.main_container, height=40, corner_radius=0)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        # ステータス情報
        self.status_var = ctk.StringVar(value="Ready - Select a video file to begin")
        status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        status_label.pack(side="left", padx=15, pady=10)
        
        # プログレスバー
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            width=200,
            height=15
        )
        self.progress_bar.pack(side="right", padx=15, pady=12)
        self.progress_bar.set(0)
        
        print("✅ ステータスバー作成完了")
    
    def create_tooltip(self, widget, text):
        """簡易ツールチップ"""
        def on_enter(event):
            # ツールチップ表示（簡易実装）
            pass
        
        def on_leave(event):
            # ツールチップ非表示
            pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def setup_shortcuts(self):
        """キーボードショートカット設定"""
        self.root.bind("<Control-o>", lambda e: self.browse_video_file())
        self.root.bind("<Control-s>", lambda e: self.export_all_thumbnails())
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
    
    # イベントハンドラー
    def browse_video_file(self):
        """動画ファイル選択"""
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("MP4 files", "*.mp4"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=file_types
        )
        
        if filename:
            self.app_state['selected_file'] = filename
            file_info = f"📄 {Path(filename).name} ({self.get_file_size(filename)})"
            self.selected_file_label.configure(text=file_info)
            self.status_var.set("✅ Video file selected - Ready to generate thumbnails")
            
            # Import タブを Process タブに切り替え
            self.tabview.set("⚙️ Process")
            
            print(f"📁 Selected: {filename}")
    
    def get_file_size(self, filepath):
        """ファイルサイズ取得"""
        try:
            size_bytes = os.path.getsize(filepath)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes/(1024**2):.1f} MB"
            else:
                return f"{size_bytes/(1024**3):.1f} GB"
        except:
            return "Unknown size"
    
    def update_count_value(self, value):
        """スライダー値更新"""
        count = int(value)
        self.app_state['thumbnail_count'] = count
        self.count_value_label.configure(text=f"{count} thumbnails")
    
    def start_processing(self):
        """サムネイル生成開始"""
        if not self.app_state['selected_file']:
            messagebox.showwarning("Warning", "Please select a video file first.")
            return
        
        if self.app_state['processing']:
            return
        
        self.app_state['processing'] = True
        self.process_btn.configure(text="🔄 Processing...", state="disabled")
        self.status_var.set("🔄 Generating thumbnails...")
        
        # 別スレッドで処理実行
        threading.Thread(target=self.process_thumbnails, daemon=True).start()
    
    def process_thumbnails(self):
        """サムネイル生成処理（デモ版）"""
        try:
            count = self.app_state['thumbnail_count']
            
            # プログレス更新
            for i in range(count + 1):
                progress = i / count
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                self.root.after(0, lambda i=i, c=count: self.status_var.set(f"🔄 Processing... ({i}/{c})"))
                time.sleep(0.5)  # デモ用の遅延
            
            # 完了処理
            self.root.after(0, self.processing_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))
    
    def processing_complete(self):
        """処理完了"""
        self.app_state['processing'] = False
        self.process_btn.configure(text="🚀 Generate Thumbnails", state="normal")
        self.status_var.set("✅ Thumbnails generated successfully")
        self.progress_bar.set(1.0)
        
        # Preview タブに切り替え
        self.tabview.set("👁️ Preview")
        
        messagebox.showinfo(
            "Complete", 
            f"Successfully generated {self.app_state['thumbnail_count']} thumbnails!\n"
            f"(Demo version - actual files not created)"
        )
        
        print(f"✅ Generated {self.app_state['thumbnail_count']} thumbnails")
    
    def processing_error(self, error_msg):
        """処理エラー"""
        self.app_state['processing'] = False
        self.process_btn.configure(text="🚀 Generate Thumbnails", state="normal")
        self.status_var.set("❌ Processing failed")
        self.progress_bar.set(0)
        
        messagebox.showerror("Error", f"Processing failed:\n{error_msg}")
    
    # その他のイベントハンドラー
    def import_video(self):
        self.tabview.set("📁 Import")
    
    def open_settings(self):
        self.tabview.set("⚙️ Process")
    
    def show_preview(self):
        self.tabview.set("👁️ Preview")
    
    def export_thumbnails(self):
        self.tabview.set("💾 Export")
    
    def show_analytics(self):
        messagebox.showinfo("Analytics", "Analytics feature coming soon!")
    
    def change_theme(self):
        self.toggle_theme()
    
    def show_about(self):
        about_text = """
🎬 Video Thumbnail Extractor - Rich Edition v2.0

A modern, feature-rich application for generating 
high-quality video thumbnails with AI-powered 
face detection and diversity optimization.

Features:
• Advanced face detection
• Diversity maximization
• Multiple output formats
• Batch processing
• Modern UI design

Built with CustomTkinter
© 2024 Video Thumbnail Extractor Team
        """
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        help_text = """
🔗 Keyboard Shortcuts:

Ctrl+O - Open video file
Ctrl+S - Export thumbnails
F1 - Show this help
Ctrl+Q - Quit application

📋 How to use:
1. Import a video file
2. Configure generation settings
3. Generate thumbnails
4. Preview and export results
        """
        messagebox.showinfo("Help", help_text)
    
    def toggle_theme(self):
        """テーマ切り替え"""
        if self.app_state['dark_mode']:
            ctk.set_appearance_mode("light")
            self.app_state['dark_mode'] = False
        else:
            ctk.set_appearance_mode("dark")
            self.app_state['dark_mode'] = True
    
    def show_recent_files(self):
        messagebox.showinfo("Recent Files", "Recent files feature coming soon!")
    
    def browse_output_path(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path_var.set(directory)
    
    def export_all_thumbnails(self):
        messagebox.showinfo("Export", "Export functionality coming soon!")
    
    def minimize_window(self):
        self.root.iconify()
    
    def run(self):
        """アプリケーション実行"""
        try:
            print("🎨 Starting Rich Modern Video Thumbnail Extractor...")
            self.root.mainloop()
            print("✅ Application closed")
        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """メイン関数"""
    app = RichVideoThumbnailApp()
    app.run()

if __name__ == "__main__":
    main()
