#!/usr/bin/env python3
"""
Video Thumbnail Extractor - Modern Tkinter UI
標準tkinterでモダンデザインを実現（確実に表示される版）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas
import os
import sys
import time
import threading
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# 実際のサービスクラスをインポート
SERVICES_AVAILABLE = False
VideoProcessor = None
ThumbnailExtractor = None
DiversitySelector = None
FaceDetector = None
UserSettings = None
ThumbnailOrientation = None
VideoFile = None

try:
    # 絶対インポートで試行
    import sys
    import os
    
    # srcディレクトリを一時的にカレントディレクトリに設定してインポート
    original_cwd = os.getcwd()
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    
    if os.path.exists(src_path):
        os.chdir(src_path)
        sys.path.insert(0, src_path)
        
        from services.video_processor import VideoProcessor
        from services.thumbnail_extractor import ThumbnailExtractor
        from services.diversity_selector import DiversitySelector
        from services.face_detector import FaceDetector
        from models.user_settings import UserSettings, ThumbnailOrientation
        from models.video_file import VideoFile
        
        os.chdir(original_cwd)  # 元のディレクトリに戻す
        print("✅ サービスクラスのインポート成功")
        SERVICES_AVAILABLE = True
    else:
        print("⚠️ srcディレクトリが見つかりません")
        
except ImportError as e:
    if 'original_cwd' in locals():
        os.chdir(original_cwd)  # エラー時も元のディレクトリに戻す
    print(f"⚠️ サービスクラスのインポートに失敗: {e}")
    print("⚠️ ダミーモードで動作します")
except Exception as e:
    if 'original_cwd' in locals():
        os.chdir(original_cwd)  # エラー時も元のディレクトリに戻す
    print(f"⚠️ 予期しないエラー: {e}")
    print("⚠️ ダミーモードで動作します")

class ModernTkinterApp:
    """標準tkinterベースのモダンアプリケーション"""
    
    def __init__(self):
        self.app_state = {
            'selected_file': None,
            'thumbnail_count': 5,
            'processing': False
        }
        
        # サービスクラスを初期化
        global SERVICES_AVAILABLE
        if SERVICES_AVAILABLE:
            try:
                self.video_processor = VideoProcessor()
                self.thumbnail_extractor = ThumbnailExtractor()
                self.diversity_selector = DiversitySelector()
                self.face_detector = FaceDetector()
                print("✅ サービス初期化成功")
            except Exception as e:
                print(f"⚠️ サービス初期化失敗: {e}")
                SERVICES_AVAILABLE = False
                self.video_processor = None
                self.thumbnail_extractor = None
                self.diversity_selector = None
                self.face_detector = None
        else:
            self.video_processor = None
            self.thumbnail_extractor = None
            self.diversity_selector = None
            self.face_detector = None
        
        # カラーパレット（UI_DESIGN.md準拠）
        self.colors = {
            'primary_start': '#667eea',
            'primary_end': '#764ba2', 
            'secondary_start': '#f093fb',
            'secondary_end': '#f5576c',
            'accent_start': '#4facfe',
            'accent_end': '#00f2fe',
            'success_start': '#43e97b',
            'success_end': '#38f9d7',
            'warning_start': '#fa709a',
            'warning_end': '#fee140',
            'info_start': '#a8edea',
            'info_end': '#fed6e3',
            'background': '#f8fafc',
            'surface': '#ffffff',
            'text_primary': '#1a202c',
            'text_secondary': '#718096',
            'border': '#e2e8f0'
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI初期化"""
        # メインウィンドウ
        self.root = tk.Tk()
        self.root.title("🎬 Video Thumbnail Extractor - Modern Edition")
        self.root.geometry("1200x800+100+100")
        self.root.configure(bg=self.colors['background'])
        
        # スタイル設定
        self.setup_styles()
        
        print("✅ モダンtkinterウィンドウ作成完了")
        
        # レイアウト構築
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # サムネイル結果表示エリア作成（main_frame作成後）
        self.create_thumbnail_results_area()
        
        print("✅ Modern Tkinter UI構築完了")
    
    def setup_styles(self):
        """ttk スタイル設定"""
        self.style = ttk.Style()
        
        # モダンボタンスタイル
        self.style.configure(
            "Modern.TButton",
            background=self.colors['primary_start'],
            foreground='white',
            font=('Arial', 12, 'bold'),
            borderwidth=0,
            focuscolor='none',
            padding=(20, 10)
        )
        
        # ホバー効果
        self.style.map(
            "Modern.TButton",
            background=[('active', self.colors['primary_end']),
                       ('pressed', self.colors['primary_end'])]
        )
        
        # 成功ボタン
        self.style.configure(
            "Success.TButton",
            background=self.colors['success_start'],
            foreground='white',
            font=('Arial', 12, 'bold'),
            borderwidth=0,
            focuscolor='none',
            padding=(20, 10)
        )
        
        # 警告ボタン
        self.style.configure(
            "Warning.TButton",
            background=self.colors['warning_start'],
            foreground='white',
            font=('Arial', 12, 'bold'),
            borderwidth=0,
            focuscolor='none',
            padding=(20, 10)
        )
    
    def create_gradient_canvas(self, parent, width, height, colors, **kwargs):
        """グラデーション描画キャンバス"""
        canvas = Canvas(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            **kwargs
        )
        
        # グラデーション描画
        r1, g1, b1 = self.hex_to_rgb(colors[0])
        r2, g2, b2 = self.hex_to_rgb(colors[1])
        
        for i in range(height):
            ratio = i / height if height > 0 else 0
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color)
        
        return canvas
    
    def hex_to_rgb(self, hex_color):
        """16進数カラーをRGBに変換"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_modern_frame(self, parent, bg_color=None, relief='flat', bd=0, **kwargs):
        """モダンなフレーム作成"""
        if bg_color is None:
            bg_color = self.colors['surface']
        
        frame = tk.Frame(
            parent,
            bg=bg_color,
            relief=relief,
            bd=bd,
            **kwargs
        )
        return frame
    
    def create_modern_button(self, parent, text, command=None, bg_color=None, **kwargs):
        """モダンなボタン作成"""
        if bg_color is None:
            bg_color = self.colors['primary_start']
        
        # 重複する引数を除去
        for key in ['font', 'padx', 'pady', 'bg', 'fg', 'relief', 'bd', 'cursor']:
            if key in kwargs:
                kwargs.pop(key)
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            **kwargs
        )
        
        # ホバー効果
        def on_enter(e):
            button.configure(bg=self.colors['primary_end'])
        
        def on_leave(e):
            button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_header(self):
        """ヘッダー作成 - グラデーション背景"""
        # ヘッダーフレーム
        header_frame = tk.Frame(self.root, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # グラデーション背景
        self.header_canvas = self.create_gradient_canvas(
            header_frame,
            1200, 80,
            [self.colors['primary_start'], self.colors['primary_end']]
        )
        self.header_canvas.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = tk.Label(
            self.header_canvas,
            text="🎬 Video Thumbnail Extractor",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg=self.colors['primary_start']
        )
        self.header_canvas.create_window(50, 40, window=title_label, anchor='w')
        
        # バージョン
        version_label = tk.Label(
            self.header_canvas,
            text="v2.0 Modern",
            font=('Arial', 12),
            fg='#cccccc',
            bg=self.colors['primary_start']
        )
        self.header_canvas.create_window(1150, 40, window=version_label, anchor='e')
        
        print("✅ ヘッダー作成完了")
    
    def create_main_content(self):
        """メインコンテンツ作成"""
        # メインコンテナ
        self.main_frame = self.create_modern_frame(
            self.root,
            bg_color=self.colors['background']
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 1. ファイル選択カード
        self.create_file_selection_card(self.main_frame)
        
        # 2. 設定カード
        self.create_settings_card(self.main_frame)
        
        # 3. アクションカード
        self.create_action_card(self.main_frame)
        
        print("✅ メインコンテンツ作成完了")
    
    def create_file_selection_card(self, parent):
        """ファイル選択カード"""
        # カードフレーム
        card_frame = self.create_modern_frame(
            parent,
            bg_color=self.colors['surface'],
            relief='solid',
            bd=1
        )
        card_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=20)
        
        # カードタイトル
        title_label = tk.Label(
            card_frame,
            text="📁 STEP 1: VIDEO FILE SELECTION",
            font=('Arial', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        title_label.pack(pady=(20, 10))
        
        # ドロップエリア
        self.drop_area = tk.Frame(
            card_frame,
            bg=self.colors['background'],
            relief='ridge',  # dashedの代わりにridgeを使用
            bd=2,
            height=120
        )
        self.drop_area.pack(fill=tk.X, padx=30, pady=10)
        self.drop_area.pack_propagate(False)
        
        # ドロップエリア内容
        drop_content = tk.Frame(self.drop_area, bg=self.colors['background'])
        drop_content.pack(expand=True)
        
        icon_label = tk.Label(
            drop_content,
            text="📤",
            font=('Arial', 48),
            bg=self.colors['background']
        )
        icon_label.pack(pady=(20, 5))
        
        main_text = tk.Label(
            drop_content,
            text="動画ファイルをドラッグ&ドロップ",
            font=('Arial', 16, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        )
        main_text.pack()
        
        sub_text = tk.Label(
            drop_content,
            text="または クリックして選択",
            font=('Arial', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        )
        sub_text.pack()
        
        # ファイル選択ボタン（インスタンス変数として保存）
        self.select_btn = self.create_modern_button(
            card_frame,
            "🎬 VIDEO FILE を選択",
            command=self.select_video_file,
            bg_color=self.colors['secondary_start']
        )
        self.select_btn.pack(pady=15)
        
        # ファイル情報表示
        self.file_info_label = tk.Label(
            card_frame,
            text="ファイルが選択されていません",
            font=('Arial', 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['surface']
        )
        self.file_info_label.pack(pady=(0, 20))
        
        # クリックイベント
        for widget in [self.drop_area, drop_content, icon_label, main_text, sub_text]:
            widget.bind("<Button-1>", lambda e: self.select_video_file())
        
        print("✅ ファイル選択カード作成完了")
    
    def create_settings_card(self, parent):
        """設定カード"""
        # カードフレーム
        card_frame = self.create_modern_frame(
            parent,
            bg_color=self.colors['surface'],
            relief='solid',
            bd=1
        )
        card_frame.pack(fill=tk.X, pady=(0, 20), padx=10, ipady=20)
        
        # カードタイトル
        title_label = tk.Label(
            card_frame,
            text="⚙️ STEP 2: GENERATION SETTINGS",
            font=('Arial', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        title_label.pack(pady=(20, 20))
        
        # 設定エリア
        settings_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        settings_frame.pack(fill=tk.X, padx=40)
        
        # サムネイル数設定
        count_frame = tk.Frame(settings_frame, bg=self.colors['surface'])
        count_frame.pack(fill=tk.X, pady=(0, 20))
        
        count_label = tk.Label(
            count_frame,
            text="生成するサムネイル数:",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        count_label.pack(anchor='w')
        
        # スライダーフレーム
        slider_frame = tk.Frame(count_frame, bg=self.colors['surface'])
        slider_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.count_var = tk.IntVar(value=5)
        self.count_scale = tk.Scale(
            slider_frame,
            from_=1,
            to=20,
            variable=self.count_var,
            orient=tk.HORIZONTAL,
            length=300,
            font=('Arial', 12),
            bg=self.colors['surface'],
            fg=self.colors['text_primary'],
            highlightthickness=0,
            command=self.update_count_display
        )
        self.count_scale.pack(side=tk.LEFT)
        
        self.count_display = tk.Label(
            slider_frame,
            text="5 枚",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg=self.colors['accent_start'],
            padx=15,
            pady=5
        )
        self.count_display.pack(side=tk.LEFT, padx=(20, 0))
        
        # 出力サイズ設定
        size_frame = tk.Frame(settings_frame, bg=self.colors['surface'])
        size_frame.pack(fill=tk.X)
        
        size_label = tk.Label(
            size_frame,
            text="出力サイズ:",
            font=('Arial', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        size_label.pack(anchor='w')
        
        self.size_var = tk.StringVar(value="1280x720 (HD)")
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["640x360 (SD)", "1280x720 (HD)", "1920x1080 (Full HD)", "3840x2160 (4K)"],
            state="readonly",
            font=('Arial', 12),
            width=30
        )
        size_combo.pack(anchor='w', pady=(5, 20))
        
        print("✅ 設定カード作成完了")
    
    def create_action_card(self, parent):
        """アクションカード"""
        # カードフレーム
        card_frame = self.create_modern_frame(
            parent,
            bg_color=self.colors['surface'],
            relief='solid',
            bd=1
        )
        card_frame.pack(fill=tk.X, padx=10, ipady=30)
        
        # カードタイトル
        title_label = tk.Label(
            card_frame,
            text="🚀 STEP 3: GENERATE THUMBNAILS",
            font=('Arial', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        title_label.pack(pady=(20, 30))
        
        # 生成ボタン
        self.generate_btn = self.create_modern_button(
            card_frame,
            "🎯 サムネイル生成を開始",
            command=self.start_generation,
            bg_color=self.colors['warning_start'],
            font=('Arial', 16, 'bold'),
            padx=40,
            pady=15
        )
        self.generate_btn.pack(pady=(0, 20))
        
        # プログレスバー
        progress_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        progress_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack()
        
        print("✅ アクションカード作成完了")
    
    def create_status_bar(self):
        """ステータスバー"""
        # ステータスフレーム
        status_frame = tk.Frame(self.root, height=40)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        # グラデーション背景
        self.status_canvas = self.create_gradient_canvas(
            status_frame,
            1200, 40,
            [self.colors['info_start'], self.colors['info_end']]
        )
        self.status_canvas.pack(fill=tk.BOTH, expand=True)
        
        # ステータステキスト
        self.status_var = tk.StringVar(value="準備完了 - 動画ファイルを選択してください")
        status_label = tk.Label(
            self.status_canvas,
            textvariable=self.status_var,
            font=('Arial', 12),
            fg=self.colors['text_primary'],
            bg=self.colors['info_start']
        )
        self.status_canvas.create_window(20, 20, window=status_label, anchor='w')
        
        print("✅ ステータスバー作成完了")
    
    def create_thumbnail_results_area(self):
        """サムネイル結果表示エリア作成"""
        # 結果表示コンテナ（初期は非表示）
        self.results_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['background']
        )
        
        # 結果タイトル
        self.results_title = tk.Label(
            self.results_frame,
            text="📸 生成されたサムネイル候補",
            font=('Arial', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        )
        self.results_title.pack(pady=(20, 10))
        
        # サムネイルグリッドエリア
        self.thumbnail_canvas = tk.Canvas(
            self.results_frame,
            bg='white',
            height=400,
            bd=1,
            relief='solid'
        )
        self.thumbnail_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # スクロールバー
        self.thumbnail_scrollbar = tk.Scrollbar(
            self.results_frame,
            orient=tk.VERTICAL,
            command=self.thumbnail_canvas.yview
        )
        self.thumbnail_canvas.configure(yscrollcommand=self.thumbnail_scrollbar.set)
        
        # グリッドフレーム
        self.thumbnail_grid_frame = tk.Frame(self.thumbnail_canvas, bg='white')
        self.thumbnail_canvas.create_window(0, 0, window=self.thumbnail_grid_frame, anchor='nw')
        
        # アクションボタンエリア
        self.results_actions = tk.Frame(
            self.results_frame,
            bg=self.colors['background']
        )
        self.results_actions.pack(fill=tk.X, padx=20, pady=10)
        
        # 保存ボタン
        self.save_selected_btn = self.create_modern_button(
            self.results_actions,
            "💾 選択したサムネイルを保存",
            command=self.save_selected_thumbnails,
            bg_color=self.colors['success_start']
        )
        self.save_selected_btn.pack(side=tk.LEFT, padx=5)
        
        # 全て保存ボタン
        self.save_all_btn = self.create_modern_button(
            self.results_actions,
            "💾 全て保存",
            command=self.save_all_thumbnails,
            bg_color=self.colors['secondary_start']
        )
        self.save_all_btn.pack(side=tk.LEFT, padx=5)
        
        # やり直しボタン
        self.retry_btn = self.create_modern_button(
            self.results_actions,
            "🔄 やり直し",
            command=self.retry_generation,
            bg_color=self.colors['warning_start']
        )
        self.retry_btn.pack(side=tk.RIGHT, padx=5)
        
        # 選択状態を管理
        self.selected_thumbnails = []
        self.thumbnail_widgets = []
        
        print("✅ サムネイル結果表示エリア作成完了")
    
    def display_thumbnail_candidates(self, thumbnails):
        """サムネイル候補をGUIに表示"""
        try:
            # 結果エリアを表示
            self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # 既存のサムネイルをクリア
            for widget in self.thumbnail_grid_frame.winfo_children():
                widget.destroy()
            self.thumbnail_widgets.clear()
            self.selected_thumbnails.clear()
            
            # グリッドレイアウトでサムネイルを表示
            columns = 3
            for i, thumbnail in enumerate(thumbnails):
                row = i // columns
                col = i % columns
                
                # サムネイルフレーム
                thumb_frame = tk.Frame(
                    self.thumbnail_grid_frame,
                    bg='white',
                    relief='solid',
                    bd=2,
                    padx=5,
                    pady=5
                )
                thumb_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                
                # サムネイル画像表示（仮）
                img_label = tk.Label(
                    thumb_frame,
                    text=f"🖼️\nサムネイル {i+1}\n{thumbnail.width}x{thumbnail.height}",
                    bg='#f0f0f0',
                    width=20,
                    height=10,
                    relief='solid',
                    bd=1
                )
                img_label.pack(pady=5)
                
                # 選択チェックボックス
                is_selected = tk.BooleanVar()
                checkbox = tk.Checkbutton(
                    thumb_frame,
                    text=f"選択",
                    variable=is_selected,
                    bg='white',
                    command=lambda idx=i, var=is_selected: self.toggle_thumbnail_selection(idx, var)
                )
                checkbox.pack(pady=2)
                
                # サムネイル情報
                info_text = f"フレーム: {thumbnail.frame_number}\n時刻: {thumbnail.timestamp:.1f}s"
                info_label = tk.Label(
                    thumb_frame,
                    text=info_text,
                    bg='white',
                    font=('Arial', 9),
                    fg='gray'
                )
                info_label.pack(pady=2)
                
                # ウィジェットを保存
                self.thumbnail_widgets.append({
                    'frame': thumb_frame,
                    'thumbnail': thumbnail,
                    'selected_var': is_selected,
                    'index': i
                })
            
            # キャンバスのスクロール領域を更新
            self.thumbnail_grid_frame.update_idletasks()
            self.thumbnail_canvas.configure(scrollregion=self.thumbnail_canvas.bbox("all"))
            
            # 処理完了
            self.app_state['processing'] = False
            self.generate_btn.configure(
                text="✅ 生成完了！",
                state=tk.NORMAL,
                bg=self.colors['success_start']
            )
            self.status_var.set("✅ サムネイル候補が表示されました。お好みの候補を選択して保存してください。")
            
            print(f"✅ サムネイル候補表示完了: {len(thumbnails)}個")
            
        except Exception as e:
            print(f"❌ サムネイル表示エラー: {e}")
            self.generation_error(f"サムネイル表示エラー: {e}")
    
    def toggle_thumbnail_selection(self, index, is_selected_var):
        """サムネイル選択状態を切り替え"""
        if is_selected_var.get():
            if index not in self.selected_thumbnails:
                self.selected_thumbnails.append(index)
                # 選択時の見た目変更
                self.thumbnail_widgets[index]['frame'].configure(bg='#e3f2fd')
        else:
            if index in self.selected_thumbnails:
                self.selected_thumbnails.remove(index)
                # 非選択時の見た目変更
                self.thumbnail_widgets[index]['frame'].configure(bg='white')
        
        # 保存ボタンの状態更新
        if self.selected_thumbnails:
            self.save_selected_btn.configure(
                text=f"💾 選択したサムネイル({len(self.selected_thumbnails)}個)を保存",
                state=tk.NORMAL
            )
        else:
            self.save_selected_btn.configure(
                text="💾 選択したサムネイルを保存",
                state=tk.DISABLED
            )
    
    def save_selected_thumbnails(self):
        """選択されたサムネイルを保存"""
        if not self.selected_thumbnails:
            messagebox.showwarning("警告", "保存するサムネイルを選択してください。")
            return
        
        try:
            output_dir = self.app_state['output_directory']
            output_dir.mkdir(exist_ok=True)
            
            saved_files = []
            for i, thumb_index in enumerate(self.selected_thumbnails):
                thumbnail = self.app_state['generated_thumbnails'][thumb_index]
                output_path = output_dir / f"selected_thumbnail_{i+1:03d}.png"
                thumbnail.save_to_file(output_path)
                saved_files.append(output_path)
            
            # 完了メッセージ
            message = f"✅ 選択されたサムネイル {len(saved_files)}個を保存しました！\n\n📁 保存先: {output_dir}"
            result = messagebox.askyesno("保存完了", f"{message}\n\nフォルダを開きますか？")
            if result:
                os.system(f"open '{output_dir}'")
                
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")
    
    def save_all_thumbnails(self):
        """全てのサムネイルを保存"""
        try:
            output_dir = self.app_state['output_directory']
            output_dir.mkdir(exist_ok=True)
            
            saved_files = []
            for i, thumbnail in enumerate(self.app_state['generated_thumbnails']):
                output_path = output_dir / f"thumbnail_{i+1:03d}.png"
                thumbnail.save_to_file(output_path)
                saved_files.append(output_path)
            
            # 完了メッセージ
            message = f"✅ 全てのサムネイル {len(saved_files)}個を保存しました！\n\n📁 保存先: {output_dir}"
            result = messagebox.askyesno("保存完了", f"{message}\n\nフォルダを開きますか？")
            if result:
                os.system(f"open '{output_dir}'")
                
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {e}")
    
    def retry_generation(self):
        """サムネイル生成をやり直し"""
        # 結果エリアを非表示
        self.results_frame.pack_forget()
        
        # 状態をリセット
        self.app_state['processing'] = False
        self.app_state['generated_thumbnails'] = []
        self.selected_thumbnails.clear()
        
        # ボタンを元に戻す
        self.generate_btn.configure(
            text="🚀 サムネイル生成開始",
            state=tk.NORMAL,
            bg=self.colors['primary_start']
        )
        
        self.status_var.set("設定を調整してサムネイル生成をやり直してください。")
        self.progress_var.set(0)
    
    def select_video_file(self):
        """動画ファイル選択"""
        # 既に選択済みの場合は再選択するかconfirm
        if self.app_state['selected_file']:
            current_file = Path(self.app_state['selected_file']).name
            result = messagebox.askyesno(
                "ファイル再選択", 
                f"現在選択されているファイル:\n{current_file}\n\n別のファイルを選択しますか？"
            )
            if not result:
                return
        
        file_types = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("MP4 files", "*.mp4"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="動画ファイルを選択",
            filetypes=file_types
        )
        
        if filename:
            self.app_state['selected_file'] = filename
            
            # ボタンの見た目を更新
            self.select_btn.configure(
                text="✅ ファイル選択済み",
                bg=self.colors['success_start']
            )
            
            # ドロップエリアの見た目を更新
            self.drop_area.configure(
                bg='#f0fff4',  # 薄い緑
                relief='solid',
                bd=2
            )
            
            # ファイル情報更新
            file_info = f"✅ 選択済み: {Path(filename).name}"
            self.file_info_label.configure(
                text=file_info,
                fg=self.colors['success_start'],
                font=('Arial', 12, 'bold')
            )
            
            self.status_var.set("✅ 動画ファイルが選択されました - 設定を確認して生成を開始してください")
            
            print(f"📁 Selected: {filename}")
    
    def update_count_display(self, value):
        """スライダー値表示更新"""
        count = int(float(value))
        self.count_display.configure(text=f"{count} 枚")
        self.app_state['thumbnail_count'] = count
    
    def start_generation(self):
        """サムネイル生成開始"""
        if not self.app_state['selected_file']:
            messagebox.showwarning("警告", "まず動画ファイルを選択してください。")
            return
        
        if self.app_state['processing']:
            return
        
        self.app_state['processing'] = True
        self.generate_btn.configure(
            text="🔄 処理中...",
            state=tk.DISABLED,
            bg='#9e9e9e'
        )
        self.status_var.set("🔄 サムネイル生成中...")
        
        # 別スレッドで処理
        threading.Thread(target=self.process_generation, daemon=True).start()
    
    def process_generation(self):
        """サムネイル生成処理"""
        try:
            video_path = Path(self.app_state['selected_file'])
            count = self.app_state['thumbnail_count']
            
            if SERVICES_AVAILABLE and self.video_processor:
                # 実際のサムネイル抽出処理
                self.real_thumbnail_extraction(video_path, count)
            else:
                # ダミー処理（開発用）
                self.dummy_thumbnail_extraction(count)
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            print(f"❌ {error_msg}")
            self.root.after(0, lambda: self.generation_error(error_msg))
    
    def real_thumbnail_extraction(self, video_path: Path, count: int):
        """実際のサムネイル抽出処理"""
        try:
            # ステップ1: 動画読み込み
            self.root.after(0, lambda: self.status_var.set("📹 動画を読み込み中..."))
            self.root.after(0, lambda: self.progress_var.set(10))
            
            video_file = self.video_processor.load_video(video_path)
            print(f"📹 動画読み込み完了: {video_file.duration}秒, {video_file.frame_count}フレーム")
            
            # ステップ2: フレーム抽出
            self.root.after(0, lambda: self.status_var.set("🎞️ フレームを抽出中..."))
            self.root.after(0, lambda: self.progress_var.set(30))
            
            frames = list(self.video_processor.extract_frames(video_file, frame_limit=count*10))
            print(f"🎞️ フレーム抽出完了: {len(frames)}フレーム")
            
            # ステップ3: 顔検出
            self.root.after(0, lambda: self.status_var.set("👤 キャラクターの顔を検出中..."))
            self.root.after(0, lambda: self.progress_var.set(40))
            
            frames_with_faces = []
            for frame in frames:
                faces = self.face_detector.detect_faces(frame)
                if faces:  # 顔が検出されたフレームのみ
                    frames_with_faces.append(frame)
            
            print(f"👤 顔検出完了: {len(frames_with_faces)}フレームに顔を検出")
            
            if not frames_with_faces:
                raise Exception("この動画からキャラクターの顔を検出できませんでした。別の動画を選択してください。")
            
            # ステップ4: 多様性選択
            self.root.after(0, lambda: self.status_var.set("🎯 最適なフレームを選択中..."))
            self.root.after(0, lambda: self.progress_var.set(50))
            
            selected_frames = self.diversity_selector.select_diverse_frames(frames_with_faces, count)
            print(f"🎯 フレーム選択完了: {len(selected_frames)}フレーム")
            
            # ステップ5: サムネイル生成
            self.root.after(0, lambda: self.status_var.set("🖼️ サムネイルを生成中..."))
            self.root.after(0, lambda: self.progress_var.set(70))
            
            settings = UserSettings(
                thumbnail_count=count,
                orientation=ThumbnailOrientation.LANDSCAPE,
                width=320,
                height=180
            )
            
            def progress_callback(progress):
                self.root.after(0, lambda p=progress: self.progress_var.set(70 + (p * 0.25)))
            
            thumbnails = self.thumbnail_extractor.extract_thumbnails(
                selected_frames, 
                settings, 
                progress_callback
            )
            print(f"🖼️ サムネイル生成完了: {len(thumbnails)}個")
            
            # 完了：サムネイル候補表示
            self.root.after(0, lambda: self.status_var.set("✅ サムネイル候補を表示中..."))
            self.root.after(0, lambda: self.progress_var.set(100))
            
            # サムネイルデータを保存
            self.app_state['generated_thumbnails'] = thumbnails
            self.app_state['output_directory'] = video_path.parent / f"{video_path.stem}_thumbnails"
            
            # UIに候補を表示
            self.root.after(0, lambda: self.display_thumbnail_candidates(thumbnails))
            
        except Exception as e:
            raise e
    
    def dummy_thumbnail_extraction(self, count: int):
        """ダミー処理（サービスが利用できない場合）"""
        for i in range(count + 1):
            progress = (i / count) * 100
            # UI更新
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda i=i, c=count: self.status_var.set(f"🔄 処理中: {i}/{c} 完了"))
            time.sleep(0.8)  # デモ用遅延
        
        # 完了処理
        self.root.after(0, self.generation_complete)
    
    def generation_complete(self):
        """生成完了"""
        self.app_state['processing'] = False
        self.generate_btn.configure(
            text="✅ 生成完了！",
            state=tk.NORMAL,
            bg=self.colors['success_start']
        )
        
        # 完了メッセージを表示
        if 'output_directory' in self.app_state:
            output_dir = self.app_state['output_directory']
            saved_count = len(self.app_state.get('saved_paths', []))
            message = f"✅ サムネイル生成完了！\n\n📁 保存先: {output_dir}\n🖼️ 生成数: {saved_count}個"
            self.status_var.set("✅ サムネイル生成が完了しました！")
            
            # 結果ダイアログを表示
            result = messagebox.askyesno(
                "生成完了", 
                f"{message}\n\nフォルダを開きますか？"
            )
            if result:
                # フォルダを開く（macOS）
                os.system(f"open '{output_dir}'")
        else:
            self.status_var.set("✅ サムネイル生成が完了しました！")
        
        self.progress_var.set(100)
        
        messagebox.showinfo(
            "完了",
            f"サムネイル生成が完了しました！\n\n"
            f"📄 ファイル: {Path(self.app_state['selected_file']).name}\n"
            f"🔢 生成数: {self.app_state['thumbnail_count']}枚\n"
            f"📐 サイズ: {self.size_var.get()}\n\n"
            f"(デモ版のため実際のファイルは生成されていません)"
        )
        
        print(f"✅ Generated {self.app_state['thumbnail_count']} thumbnails")
    
    def generation_error(self, error_msg):
        """生成エラー"""
        self.app_state['processing'] = False
        self.generate_btn.configure(
            text="❌ エラー",
            state=tk.NORMAL,
            bg='#f44336'
        )
        self.status_var.set("❌ 生成中にエラーが発生しました")
        self.progress_var.set(0)
        
        messagebox.showerror("エラー", f"生成中にエラーが発生しました:\n{error_msg}")
    
    def run(self):
        """アプリケーション実行"""
        try:
            print("🎨 Starting Modern Tkinter Video Thumbnail Extractor...")
            
            # Mac対応の強制表示
            self.root.update_idletasks()
            self.root.update()
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            # 複数回更新
            for i in range(3):
                self.root.update()
                time.sleep(0.1)
            
            print("✅ Modern Tkinter UI displayed successfully")
            
            self.root.mainloop()
            print("✅ Application closed")
            
        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """メイン関数"""
    app = ModernTkinterApp()
    app.run()

if __name__ == "__main__":
    main()
