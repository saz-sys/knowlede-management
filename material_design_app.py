#!/usr/bin/env python3
"""
Video Thumbnail Extractor - Material Design UI
マテリアルデザインに準拠したモダンUI実装
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import time
from pathlib import Path

class MaterialColors:
    """マテリアルデザインカラーパレット"""
    PRIMARY = "#1976d2"  # Blue 700
    PRIMARY_DARK = "#0d47a1"  # Blue 900
    PRIMARY_LIGHT = "#42a5f5"  # Blue 400
    SECONDARY = "#4caf50"  # Green 500
    SECONDARY_DARK = "#388e3c"  # Green 700
    BACKGROUND = "#fafafa"  # Grey 50
    SURFACE = "#ffffff"  # White
    ERROR = "#f44336"  # Red 500
    ON_PRIMARY = "#ffffff"  # White
    ON_SURFACE = "#000000"  # Black
    TEXT_PRIMARY = "#212121"  # Grey 900
    TEXT_SECONDARY = "#757575"  # Grey 600
    DIVIDER = "#bdbdbd"  # Grey 400

class MaterialStyles:
    """マテリアルデザインスタイル定義"""
    
    @staticmethod
    def create_style():
        """ttk用のマテリアルスタイルを作成"""
        style = ttk.Style()
        
        # Card風フレームスタイル
        style.configure(
            "Card.TFrame",
            background=MaterialColors.SURFACE,
            relief="flat",
            borderwidth=0
        )
        
        # プライマリボタンスタイル
        style.configure(
            "Primary.TButton",
            background=MaterialColors.PRIMARY,
            foreground=MaterialColors.ON_PRIMARY,
            font=("Roboto", 14, "bold"),
            padding=(24, 12),
            relief="flat",
            borderwidth=0
        )
        
        # セカンダリボタンスタイル
        style.configure(
            "Secondary.TButton",
            background=MaterialColors.SECONDARY,
            foreground=MaterialColors.ON_PRIMARY,
            font=("Roboto", 14, "bold"),
            padding=(24, 12),
            relief="flat",
            borderwidth=0
        )
        
        # アウトラインボタンスタイル
        style.configure(
            "Outlined.TButton",
            background=MaterialColors.SURFACE,
            foreground=MaterialColors.PRIMARY,
            font=("Roboto", 14),
            padding=(24, 12),
            relief="solid",
            borderwidth=1
        )
        
        return style

class MaterialCard(tk.Frame):
    """マテリアルデザインカード風フレーム"""
    
    def __init__(self, parent, elevation=2, **kwargs):
        # デフォルト設定
        default_config = {
            'bg': MaterialColors.SURFACE,
            'relief': 'flat',
            'bd': 0,
            'padx': 16,
            'pady': 16
        }
        default_config.update(kwargs)
        
        super().__init__(parent, **default_config)
        
        self.elevation = elevation
        self._create_shadow()
    
    def _create_shadow(self):
        """影効果をシミュレート（tkinterでは簡易実装）"""
        # 影色のフレームを背後に配置
        shadow_offset = self.elevation
        shadow_frame = tk.Frame(
            self.master,
            bg="#e0e0e0",
            height=shadow_offset,
            width=shadow_offset
        )
        shadow_frame.place(
            in_=self,
            x=shadow_offset,
            y=shadow_offset,
            relwidth=1.0,
            relheight=1.0
        )
        # カードを最前面に
        self.lift()

class MaterialButton(tk.Button):
    """マテリアルデザインボタン"""
    
    def __init__(self, parent, style="primary", **kwargs):
        if style == "primary":
            default_config = {
                'bg': MaterialColors.PRIMARY,
                'fg': MaterialColors.ON_PRIMARY,
                'font': ('Roboto', 14, 'bold'),
                'relief': 'flat',
                'bd': 0,
                'padx': 24,
                'pady': 12,
                'cursor': 'hand2'
            }
        elif style == "secondary":
            default_config = {
                'bg': MaterialColors.SECONDARY,
                'fg': MaterialColors.ON_PRIMARY,
                'font': ('Roboto', 14, 'bold'),
                'relief': 'flat',
                'bd': 0,
                'padx': 24,
                'pady': 12,
                'cursor': 'hand2'
            }
        elif style == "outlined":
            default_config = {
                'bg': MaterialColors.SURFACE,
                'fg': MaterialColors.PRIMARY,
                'font': ('Roboto', 14),
                'relief': 'solid',
                'bd': 1,
                'highlightbackground': MaterialColors.PRIMARY,
                'padx': 24,
                'pady': 12,
                'cursor': 'hand2'
            }
        
        default_config.update(kwargs)
        super().__init__(parent, **default_config)
        
        # ホバー効果
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """ホバー時の効果"""
        if self['bg'] == MaterialColors.PRIMARY:
            self.configure(bg=MaterialColors.PRIMARY_LIGHT)
        elif self['bg'] == MaterialColors.SECONDARY:
            self.configure(bg=MaterialColors.SECONDARY_DARK)
    
    def _on_leave(self, event):
        """ホバー終了時の復元"""
        if MaterialColors.PRIMARY_LIGHT in str(self['bg']):
            self.configure(bg=MaterialColors.PRIMARY)
        elif MaterialColors.SECONDARY_DARK in str(self['bg']):
            self.configure(bg=MaterialColors.SECONDARY)

class MaterialSlider(tk.Frame):
    """マテリアルデザインスライダー"""
    
    def __init__(self, parent, from_=0, to=100, value=50, **kwargs):
        super().__init__(parent, bg=MaterialColors.SURFACE, **kwargs)
        
        self.from_ = from_
        self.to = to
        self.value = tk.IntVar(value=value)
        
        # スライダー作成
        self.scale = tk.Scale(
            self,
            from_=from_,
            to=to,
            variable=self.value,
            orient=tk.HORIZONTAL,
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            activebackground=MaterialColors.PRIMARY,
            highlightbackground=MaterialColors.PRIMARY,
            troughcolor=MaterialColors.DIVIDER,
            font=('Roboto', 12),
            length=200,
            showvalue=0,  # 値表示を無効化
            relief='flat',
            bd=0
        )
        self.scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # 値表示ラベル
        self.value_label = tk.Label(
            self,
            textvariable=self.value,
            bg=MaterialColors.PRIMARY,
            fg=MaterialColors.ON_PRIMARY,
            font=('Roboto', 12, 'bold'),
            padx=8,
            pady=4,
            relief='flat'
        )
        self.value_label.pack(side=tk.LEFT)

class VideoThumbnailApp:
    """メイン アプリケーション クラス"""
    
    def __init__(self):
        self.root = None
        self.app_state = {
            'selected_file': None,
            'thumbnail_count': 5,
            'output_size': '1280x720',
            'output_directory': None
        }
        self.setup_ui()
    
    def setup_ui(self):
        """UI初期化"""
        # Mac警告抑制
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        # ルートウィンドウ
        self.root = tk.Tk()
        self.root.withdraw()  # 初期状態では隠す
        
        # ウィンドウ設定
        self.root.title("Video Thumbnail Extractor")
        self.root.geometry("1000x800+100+100")
        self.root.configure(bg=MaterialColors.BACKGROUND)
        
        # スタイル適用
        self.style = MaterialStyles.create_style()
        
        print("✅ ウィンドウ基本設定完了")
        
        # UI構築
        self.create_app_bar()
        self.create_main_content()
        self.create_fab()
        self.create_status_bar()
        
        # 表示
        self.show_window()
    
    def create_app_bar(self):
        """App Bar作成"""
        self.app_bar = tk.Frame(
            self.root,
            bg=MaterialColors.PRIMARY,
            height=64
        )
        self.app_bar.pack(fill=tk.X)
        self.app_bar.pack_propagate(False)
        
        # タイトル
        title_label = tk.Label(
            self.app_bar,
            text="🎬 Video Thumbnail Extractor",
            bg=MaterialColors.PRIMARY,
            fg=MaterialColors.ON_PRIMARY,
            font=('Roboto', 20, 'bold'),
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, padx=24, pady=16)
        
        # メニューボタン（今後実装）
        menu_btn = tk.Label(
            self.app_bar,
            text="⋮",
            bg=MaterialColors.PRIMARY,
            fg=MaterialColors.ON_PRIMARY,
            font=('Roboto', 24),
            cursor='hand2'
        )
        menu_btn.pack(side=tk.RIGHT, padx=24, pady=16)
        
        print("✅ App Bar作成完了")
    
    def create_main_content(self):
        """メインコンテンツエリア作成"""
        # スクロール可能なメインフレーム
        self.main_frame = tk.Frame(
            self.root,
            bg=MaterialColors.BACKGROUND,
            padx=24,
            pady=24
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ファイル選択カード
        self.create_file_upload_card()
        
        # 設定カード
        self.create_settings_card()
        
        # プレビューカード
        self.create_preview_card()
        
        print("✅ メインコンテンツ作成完了")
    
    def create_file_upload_card(self):
        """ファイルアップロードカード"""
        upload_card = MaterialCard(self.main_frame, elevation=2)
        upload_card.pack(fill=tk.X, pady=(0, 16))
        
        # カードタイトル
        title = tk.Label(
            upload_card,
            text="📁 Video File Selection",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 18, 'bold'),
            anchor='w'
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # ドラッグ&ドロップエリア
        self.drop_area = tk.Frame(
            upload_card,
            bg=MaterialColors.BACKGROUND,
            relief='solid',
            bd=2,
            height=120
        )
        self.drop_area.pack(fill=tk.X, pady=(0, 16))
        self.drop_area.pack_propagate(False)
        
        # ドロップエリア内容
        drop_content = tk.Frame(self.drop_area, bg=MaterialColors.BACKGROUND)
        drop_content.pack(expand=True)
        
        drop_icon = tk.Label(
            drop_content,
            text="📤",
            bg=MaterialColors.BACKGROUND,
            fg=MaterialColors.TEXT_SECONDARY,
            font=('Arial', 48)
        )
        drop_icon.pack(pady=(10, 5))
        
        drop_text = tk.Label(
            drop_content,
            text="Drag & Drop your video file here",
            bg=MaterialColors.BACKGROUND,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 16, 'bold')
        )
        drop_text.pack()
        
        drop_subtext = tk.Label(
            drop_content,
            text="or click to browse",
            bg=MaterialColors.BACKGROUND,
            fg=MaterialColors.TEXT_SECONDARY,
            font=('Roboto', 14)
        )
        drop_subtext.pack()
        
        # ファイル選択ボタン
        select_btn = MaterialButton(
            upload_card,
            text="SELECT VIDEO FILE",
            style="outlined",
            command=self.select_video_file
        )
        select_btn.pack(pady=(0, 8))
        
        # 選択ファイル表示
        self.selected_file_var = tk.StringVar(value="No file selected")
        self.file_info = tk.Label(
            upload_card,
            textvariable=self.selected_file_var,
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_SECONDARY,
            font=('Roboto', 12),
            anchor='w'
        )
        self.file_info.pack(fill=tk.X)
        
        # ドロップエリアのクリックイベント
        self.drop_area.bind("<Button-1>", lambda e: self.select_video_file())
        drop_content.bind("<Button-1>", lambda e: self.select_video_file())
        drop_icon.bind("<Button-1>", lambda e: self.select_video_file())
        drop_text.bind("<Button-1>", lambda e: self.select_video_file())
        drop_subtext.bind("<Button-1>", lambda e: self.select_video_file())
        
        print("✅ ファイルアップロードカード作成完了")
    
    def create_settings_card(self):
        """設定カード"""
        settings_card = MaterialCard(self.main_frame, elevation=2)
        settings_card.pack(fill=tk.X, pady=(0, 16))
        
        # カードタイトル
        title = tk.Label(
            settings_card,
            text="⚙️ Thumbnail Settings",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 18, 'bold'),
            anchor='w'
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 設定項目フレーム
        settings_frame = tk.Frame(settings_card, bg=MaterialColors.SURFACE)
        settings_frame.pack(fill=tk.X)
        
        # サムネイル数設定
        count_frame = tk.Frame(settings_frame, bg=MaterialColors.SURFACE)
        count_frame.pack(fill=tk.X, pady=(0, 16))
        
        count_label = tk.Label(
            count_frame,
            text="Number of Thumbnails",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 14, 'bold'),
            anchor='w'
        )
        count_label.pack(fill=tk.X, pady=(0, 8))
        
        self.count_slider = MaterialSlider(
            count_frame,
            from_=1,
            to=20,
            value=self.app_state['thumbnail_count']
        )
        self.count_slider.pack(fill=tk.X)
        
        # 出力サイズ設定
        size_frame = tk.Frame(settings_frame, bg=MaterialColors.SURFACE)
        size_frame.pack(fill=tk.X)
        
        size_label = tk.Label(
            size_frame,
            text="Output Size",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 14, 'bold'),
            anchor='w'
        )
        size_label.pack(fill=tk.X, pady=(0, 8))
        
        self.size_var = tk.StringVar(value=self.app_state['output_size'])
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["640x360", "1280x720", "1920x1080", "3840x2160"],
            state="readonly",
            font=('Roboto', 12)
        )
        size_combo.pack(fill=tk.X)
        
        print("✅ 設定カード作成完了")
    
    def create_preview_card(self):
        """プレビューカード"""
        preview_card = MaterialCard(self.main_frame, elevation=4)
        preview_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # カードタイトル
        title = tk.Label(
            preview_card,
            text="👁️ Thumbnail Preview",
            bg=MaterialColors.SURFACE,
            fg=MaterialColors.TEXT_PRIMARY,
            font=('Roboto', 18, 'bold'),
            anchor='w'
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # プレビューエリア
        self.preview_area = tk.Frame(
            preview_card,
            bg=MaterialColors.BACKGROUND,
            relief='solid',
            bd=1,
            height=200
        )
        self.preview_area.pack(fill=tk.BOTH, expand=True)
        
        # プレースホルダー
        placeholder = tk.Label(
            self.preview_area,
            text="🖼️\n\nThumbnail previews will appear here\nafter generation",
            bg=MaterialColors.BACKGROUND,
            fg=MaterialColors.TEXT_SECONDARY,
            font=('Roboto', 16),
            justify=tk.CENTER
        )
        placeholder.pack(expand=True)
        
        print("✅ プレビューカード作成完了")
    
    def create_fab(self):
        """Floating Action Button作成"""
        # FABのコンテナ
        fab_container = tk.Frame(self.root, bg=MaterialColors.BACKGROUND)
        fab_container.place(relx=1.0, rely=1.0, x=-80, y=-80, anchor='se')
        
        # FAB
        self.fab = MaterialButton(
            fab_container,
            text="▶️",
            style="secondary",
            font=('Arial', 20),
            width=3,
            height=1,
            command=self.generate_thumbnails
        )
        self.fab.pack()
        
        print("✅ FAB作成完了")
    
    def create_status_bar(self):
        """ステータスバー作成"""
        self.status_bar = tk.Frame(
            self.root,
            bg=MaterialColors.TEXT_PRIMARY,
            height=32
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready - Select a video file to begin")
        status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_var,
            bg=MaterialColors.TEXT_PRIMARY,
            fg=MaterialColors.ON_PRIMARY,
            font=('Roboto', 12),
            anchor='w'
        )
        status_label.pack(side=tk.LEFT, padx=16, pady=4)
        
        print("✅ ステータスバー作成完了")
    
    def select_video_file(self):
        """動画ファイル選択"""
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("MP4 files", "*.mp4"),
            ("AVI files", "*.avi"),
            ("MOV files", "*.mov"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=file_types
        )
        
        if filename:
            self.app_state['selected_file'] = filename
            file_display = f"📄 {Path(filename).name}"
            if len(file_display) > 60:
                file_display = file_display[:57] + "..."
            self.selected_file_var.set(file_display)
            self.status_var.set("✅ Video file selected - Ready to generate thumbnails")
            
            # ドロップエリアの見た目を更新
            self.drop_area.configure(highlightbackground=MaterialColors.PRIMARY)
            
            print(f"📁 Selected file: {filename}")
        
        self.root.update()
    
    def generate_thumbnails(self):
        """サムネイル生成"""
        try:
            if not self.app_state['selected_file']:
                messagebox.showwarning("Warning", "Please select a video file first.")
                return
            
            # 設定を更新
            self.app_state['thumbnail_count'] = self.count_slider.value.get()
            self.app_state['output_size'] = self.size_var.get()
            
            self.status_var.set("🔄 Generating thumbnails...")
            self.root.update()
            
            # デモ処理
            messagebox.showinfo("Processing", 
                f"Generating thumbnails...\n\n"
                f"📄 File: {Path(self.app_state['selected_file']).name}\n"
                f"🔢 Count: {self.app_state['thumbnail_count']}\n"
                f"📐 Size: {self.app_state['output_size']}")
            
            print(f"🎬 Thumbnail generation settings:")
            print(f"   - File: {self.app_state['selected_file']}")
            print(f"   - Count: {self.app_state['thumbnail_count']}")
            print(f"   - Size: {self.app_state['output_size']}")
            
            self.status_var.set("✅ Thumbnails generated successfully (Demo)")
            messagebox.showinfo("Complete", "Thumbnail generation completed!\n(Demo version)")
            
        except Exception as e:
            self.status_var.set("❌ Error occurred")
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            print(f"❌ Error: {e}")
        
        self.root.update()
    
    def show_window(self):
        """ウィンドウ表示"""
        print("🔄 Showing window...")
        
        # 強制更新
        self.root.update_idletasks()
        self.root.update()
        
        # 表示
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # 追加更新
        for i in range(3):
            self.root.update()
            time.sleep(0.1)
        
        print("✅ Material Design UI displayed successfully")
    
    def run(self):
        """アプリケーション実行"""
        try:
            print("🎨 Starting Material Design Video Thumbnail Extractor...")
            self.root.mainloop()
            print("✅ Application closed")
        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """メイン関数"""
    app = VideoThumbnailApp()
    app.run()

if __name__ == "__main__":
    main()
