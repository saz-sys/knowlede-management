"""
ThumbnailGrid（サムネイル表示グリッド）実装

生成されたサムネイル候補をグリッド形式で表示し、
ユーザーが選択・保存できる機能を提供します。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import List, Optional, Set, Callable
import logging
from PIL import Image, ImageTk
import io
import numpy as np

from ..models import Thumbnail
from ..lib import get_logger, get_config
from . import get_gui_font, get_color, get_config as get_gui_config


class ThumbnailItem:
    """サムネイル表示アイテム"""
    
    def __init__(self, parent_canvas: tk.Canvas, thumbnail: Thumbnail, 
                 x: int, y: int, width: int, height: int,
                 on_click: Optional[Callable] = None):
        """
        サムネイルアイテムを初期化
        
        Args:
            parent_canvas: 親キャンバス
            thumbnail: サムネイルデータ
            x, y: 表示位置
            width, height: 表示サイズ
            on_click: クリック時のコールバック
        """
        self.canvas = parent_canvas
        self.thumbnail = thumbnail
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click = on_click
        
        self.is_selected = False
        self.canvas_items = []  # キャンバスアイテムのID保持
        
        # 画像を準備
        self.photo = self._prepare_image()
        
        # キャンバスに描画
        self._draw()
        
        # クリックイベント（描画後に設定）
        self._setup_events()
    
    def _prepare_image(self) -> ImageTk.PhotoImage:
        """PIL画像をtkinter用に準備"""
        try:
            # numpy配列からPIL Imageに変換
            if isinstance(self.thumbnail.image_data, np.ndarray):
                # RGBからBGRに変換（OpenCVの場合）
                if self.thumbnail.image_data.shape[2] == 3:
                    rgb_image = self.thumbnail.image_data[:, :, ::-1]  # BGR -> RGB
                else:
                    rgb_image = self.thumbnail.image_data
                
                pil_image = Image.fromarray(rgb_image.astype('uint8'))
            else:
                # バイトデータの場合
                pil_image = Image.open(io.BytesIO(self.thumbnail.image_data))
            
            # リサイズ（アスペクト比維持）
            pil_image.thumbnail((self.width - 10, self.height - 30), Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(pil_image)
            
        except Exception as e:
            logging.error(f"画像準備エラー: {e}")
            # エラー時はプレースホルダー画像を作成
            placeholder = Image.new('RGB', (self.width - 10, self.height - 30), color='lightgray')
            return ImageTk.PhotoImage(placeholder)
    
    def _draw(self):
        """キャンバスに描画"""
        # 背景矩形
        border_color = get_color("primary") if self.is_selected else get_color("border")
        bg_color = get_color("surface")
        
        # タグを作成（フレーム番号ベース）
        tag_name = f"thumbnail_{self.thumbnail.frame_number}"
        
        bg_rect = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=bg_color, outline=border_color, width=2, tags=tag_name
        )
        self.canvas_items.append(bg_rect)
        
        # 画像
        img_x = self.x + self.width // 2
        img_y = self.y + 5 + (self.height - 30) // 2
        
        image_item = self.canvas.create_image(
            img_x, img_y, image=self.photo, anchor="center", tags=tag_name
        )
        self.canvas_items.append(image_item)
        
        # 情報テキスト
        info_text = f"フレーム: {self.thumbnail.frame_number}"
        if hasattr(self.thumbnail, 'quality_score'):
            info_text += f" | 品質: {self.thumbnail.quality_score:.2f}"
        
        text_item = self.canvas.create_text(
            img_x, self.y + self.height - 15,
            text=info_text, font=get_gui_font(-1),
            fill=get_color("text_secondary"), anchor="center", tags=tag_name
        )
        self.canvas_items.append(text_item)
        
        # 選択チェックマーク
        if self.is_selected:
            check_item = self.canvas.create_text(
                self.x + self.width - 15, self.y + 15,
                text="✓", font=get_gui_font(2), fill=get_color("success"),
                anchor="center", tags=tag_name
            )
            self.canvas_items.append(check_item)
        
        # タグベースのイベントバインディング
        self.canvas.tag_bind(tag_name, "<Button-1>", self._on_click)
        self.canvas.tag_bind(tag_name, "<Enter>", self._on_enter)
        self.canvas.tag_bind(tag_name, "<Leave>", self._on_leave)
        
        # デバッグ用：タグが正しく設定されているか確認
        print(f"DEBUG: Created tag '{tag_name}' for frame {self.thumbnail.frame_number}")
    
    def _setup_events(self):
        """イベントハンドリング設定（タグベースで既に設定済み）"""
        print(f"DEBUG: Events already bound via tags for {len(self.canvas_items)} canvas items")
    
    def _on_click(self, event):
        """クリック処理"""
        print(f"DEBUG: ThumbnailItem clicked - frame {self.thumbnail.frame_number}")
        messagebox.showinfo("ThumbnailItemクリック", f"ThumbnailItemがクリックされました！\nフレーム番号: {self.thumbnail.frame_number}")
        self.toggle_selection()
        if self.on_click:
            self.on_click(self)
    
    def _on_enter(self, event):
        """マウスオーバー処理"""
        if not self.is_selected:
            self.canvas.itemconfig(self.canvas_items[0], outline=get_color("secondary"))
    
    def _on_leave(self, event):
        """マウスアウト処理"""
        if not self.is_selected:
            self.canvas.itemconfig(self.canvas_items[0], outline=get_color("border"))
    
    def toggle_selection(self):
        """選択状態を切り替え"""
        old_state = self.is_selected
        self.is_selected = not self.is_selected
        print(f"DEBUG: Toggle selection - frame {self.thumbnail.frame_number}: {old_state} -> {self.is_selected}")
        self.redraw()
    
    def set_selection(self, selected: bool):
        """選択状態を設定"""
        if self.is_selected != selected:
            self.is_selected = selected
            self.redraw()
    
    def redraw(self):
        """再描画"""
        # 既存アイテムを削除
        for item_id in self.canvas_items:
            self.canvas.delete(item_id)
        self.canvas_items.clear()
        
        # 再描画（イベントバインディングも含む）
        self._draw()
    
    def cleanup(self):
        """リソースを解放"""
        for item_id in self.canvas_items:
            self.canvas.delete(item_id)
        self.canvas_items.clear()


class ThumbnailGrid:
    """サムネイル表示グリッドクラス"""
    
    def __init__(self, parent: tk.Widget):
        """
        サムネイルグリッドを初期化
        
        Args:
            parent: 親ウィジェット
        """
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.parent = parent
        
        # 状態管理
        self.thumbnails: List[Thumbnail] = []
        self.thumbnail_items: List[ThumbnailItem] = []
        self.selected_indices: Set[int] = set()
        
        # 表示設定
        self.item_width = get_gui_config("thumbnail_size", (150, 150))[0]
        self.item_height = get_gui_config("thumbnail_size", (150, 150))[1]
        self.padding = get_gui_config("grid_padding", 10)
        self.columns = 4  # 1行あたりの列数
        
        # コールバック
        self.on_selection_changed: Optional[Callable[[Set[int]], None]] = None
        
        # GUI構築
        self._setup_ui()
        
        self.logger.info("サムネイルグリッド初期化完了")
        print("DEBUG: ThumbnailGrid initialization completed")
    
    def _setup_ui(self):
        """UIを構築"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True)
        print("DEBUG: Main frame packed")
        
        # ツールバー
        self._setup_toolbar()
        
        # スクロール可能なキャンバス
        self._setup_canvas()
        
        # 初期状態の表示
        self._show_empty_state()
    
    def _setup_toolbar(self):
        """ツールバーを設定"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill="x", pady=(0, 5))
        
        # 左側：選択関連ボタン
        left_frame = ttk.Frame(toolbar)
        left_frame.pack(side="left")
        
        ttk.Button(left_frame, text="すべて選択",
                  command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(left_frame, text="選択解除",
                  command=self.deselect_all).pack(side="left", padx=(0, 5))
        ttk.Button(left_frame, text="選択を反転",
                  command=self.invert_selection).pack(side="left")
        
        # 中央：選択状況表示
        self.selection_label = ttk.Label(toolbar, text="0個のサムネイルが選択されています",
                                       font=get_gui_font(-1))
        self.selection_label.pack(side="left", padx=(20, 0))
        
        # 右側：保存ボタン
        right_frame = ttk.Frame(toolbar)
        right_frame.pack(side="right")
        
        self.save_button = ttk.Button(right_frame, text="選択したサムネイルを保存",
                                    command=self.save_selected, state="disabled")
        self.save_button.pack(side="right")
    
    def _setup_canvas(self):
        """スクロール可能なキャンバスを設定"""
        # キャンバスフレーム
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(fill="both", expand=True)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # キャンバスとスクロールバー
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        print("DEBUG: Canvas and scrollbars created")
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set,
                            xscrollcommand=self.h_scrollbar.set)
        
        # 配置
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # キャンバスにフォーカスを設定
        self.canvas.focus_set()
        
        # デバッグ用：キャンバスの状態を確認
        print(f"DEBUG: Canvas focus: {self.canvas.focus_get()}")
        print(f"DEBUG: Canvas size: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
        print(f"DEBUG: Canvas visible: {self.canvas.winfo_viewable()}")
        
        # マウスホイールスクロール
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        print("DEBUG: Mousewheel events bound")
        
        # キャンバス全体のクリックイベント（座標ベースで判定）
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        print("DEBUG: Click events bound")
        
        # リサイズイベント
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _show_empty_state(self):
        """空状態の表示"""
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300
        
        self.canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text="サムネイル候補がありません\\n\\n「サムネイル抽出開始」ボタンで\\nサムネイルを生成してください",
            font=get_gui_font(), fill=get_color("text_secondary"),
            justify="center", anchor="center"
        )
    
    def _on_mousewheel(self, event):
        """マウスホイールスクロール処理"""
        print(f"DEBUG: Mousewheel event detected - delta: {event.delta}, num: {event.num}")
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def _on_canvas_click(self, event):
        """キャンバスクリック処理（座標ベースで判定）"""
        print(f"DEBUG: Canvas clicked at ({event.x}, {event.y})")
        
        # まずはクリックイベントが動作しているか確認するためポップアップを表示
        messagebox.showinfo("クリック確認", f"キャンバスがクリックされました！\n座標: ({event.x}, {event.y})")
        
        # クリックされたサムネイルアイテムを特定
        clicked_item = None
        for i, item in enumerate(self.thumbnail_items):
            # アイテムの境界内かチェック
            if (item.x <= event.x <= item.x + item.width and 
                item.y <= event.y <= item.y + item.height):
                clicked_item = item
                print(f"DEBUG: Clicked on thumbnail item {i} (frame {item.thumbnail.frame_number})")
                messagebox.showinfo("サムネイルクリック", f"サムネイルがクリックされました！\nフレーム番号: {item.thumbnail.frame_number}")
                break
        
        if clicked_item:
            # 選択状態を切り替え
            clicked_item.toggle_selection()
            
            # グリッドの選択状態を更新
            item_index = self.thumbnail_items.index(clicked_item)
            if clicked_item.is_selected:
                self.selected_indices.add(item_index)
            else:
                self.selected_indices.discard(item_index)
            
            print(f"DEBUG: Selected indices: {self.selected_indices}")
            
            # UI更新
            self._update_selection_ui()
            
            # コールバック実行
            if self.on_selection_changed:
                self.on_selection_changed(self.selected_indices.copy())
        else:
            print("DEBUG: No thumbnail item found at click position")
            messagebox.showinfo("クリック確認", "サムネイル以外の場所がクリックされました")
    
    def _on_canvas_configure(self, event):
        """キャンバスリサイズ処理"""
        # スクロール領域を更新
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 列数を再計算（必要に応じて）
        new_columns = max(1, (event.width - self.padding) // (self.item_width + self.padding))
        if new_columns != self.columns:
            self.columns = new_columns
            self._relayout_thumbnails()
    
    def _relayout_thumbnails(self):
        """サムネイルを再レイアウト"""
        if not self.thumbnail_items:
            return
        
        # 既存アイテムをクリア
        self._clear_items()
        
        # 新しいレイアウトで再描画
        self._layout_thumbnails()
    
    def _layout_thumbnails(self):
        """サムネイルをレイアウト"""
        if not self.thumbnails:
            return
        
        current_x = self.padding
        current_y = self.padding
        
        for i, thumbnail in enumerate(self.thumbnails):
            # 行が満杯の場合は次の行へ
            if i > 0 and i % self.columns == 0:
                current_x = self.padding
                current_y += self.item_height + self.padding
            
            # ThumbnailItemを作成
            item = ThumbnailItem(
                self.canvas, thumbnail,
                current_x, current_y,
                self.item_width, self.item_height,
                on_click=self._on_item_click
            )
            print(f"DEBUG: Created ThumbnailItem {i} for frame {thumbnail.frame_number}")
            print(f"DEBUG: Item position: x={current_x}, y={current_y}, width={self.item_width}, height={self.item_height}")
            
            # 選択状態を復元
            if i in self.selected_indices:
                item.set_selection(True)
            
            self.thumbnail_items.append(item)
            
            # 次の位置へ
            current_x += self.item_width + self.padding
        
        # スクロール領域を更新
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _clear_items(self):
        """既存アイテムをクリア"""
        for item in self.thumbnail_items:
            item.cleanup()
        self.thumbnail_items.clear()
    
    def _on_item_click(self, item: ThumbnailItem):
        """アイテムクリック処理"""
        # 選択状態を更新
        item_index = self.thumbnail_items.index(item)
        
        print(f"DEBUG: Item click - index {item_index}, selected: {item.is_selected}")
        
        if item.is_selected:
            self.selected_indices.add(item_index)
        else:
            self.selected_indices.discard(item_index)
        
        print(f"DEBUG: Selected indices: {self.selected_indices}")
        
        # UI更新
        self._update_selection_ui()
        
        # コールバック実行
        if self.on_selection_changed:
            self.on_selection_changed(self.selected_indices.copy())
    
    def _update_selection_ui(self):
        """選択状況UIを更新"""
        count = len(self.selected_indices)
        self.selection_label.config(text=f"{count}個のサムネイルが選択されています")
        self.save_button.config(state="normal" if count > 0 else "disabled")
    
    # パブリックメソッド
    
    def set_thumbnails(self, thumbnails: List[Thumbnail]):
        """サムネイルリストを設定"""
        print(f"DEBUG: Setting {len(thumbnails)} thumbnails")
        self.thumbnails = thumbnails
        self.selected_indices.clear()
        
        # 既存表示をクリア
        self._clear_items()
        self.canvas.delete("all")
        
        if thumbnails:
            # サムネイルを表示
            self._layout_thumbnails()
            self.logger.info(f"{len(thumbnails)}個のサムネイルを表示")
            print(f"DEBUG: Layout completed, {len(self.thumbnail_items)} items created")
            
            # デバッグ用：キャンバスの状態を再確認
            print(f"DEBUG: Canvas focus after layout: {self.canvas.focus_get()}")
            print(f"DEBUG: Canvas size after layout: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")
            print(f"DEBUG: Canvas visible after layout: {self.canvas.winfo_viewable()}")
        else:
            # 空状態を表示
            self._show_empty_state()
        
        # UI更新
        self._update_selection_ui()
    
    def get_selected_thumbnails(self) -> List[Thumbnail]:
        """選択されたサムネイルを取得"""
        return [self.thumbnails[i] for i in self.selected_indices]
    
    def select_all(self):
        """すべて選択"""
        self.selected_indices = set(range(len(self.thumbnails)))
        
        for i, item in enumerate(self.thumbnail_items):
            item.set_selection(True)
        
        self._update_selection_ui()
        
        if self.on_selection_changed:
            self.on_selection_changed(self.selected_indices.copy())
    
    def deselect_all(self):
        """選択解除"""
        self.selected_indices.clear()
        
        for item in self.thumbnail_items:
            item.set_selection(False)
        
        self._update_selection_ui()
        
        if self.on_selection_changed:
            self.on_selection_changed(set())
    
    def invert_selection(self):
        """選択を反転"""
        all_indices = set(range(len(self.thumbnails)))
        self.selected_indices = all_indices - self.selected_indices
        
        for i, item in enumerate(self.thumbnail_items):
            item.set_selection(i in self.selected_indices)
        
        self._update_selection_ui()
        
        if self.on_selection_changed:
            self.on_selection_changed(self.selected_indices.copy())
    
    def save_selected(self):
        """選択されたサムネイルを保存"""
        selected_thumbnails = self.get_selected_thumbnails()
        
        if not selected_thumbnails:
            messagebox.showwarning("警告", "保存するサムネイルを選択してください。")
            return
        
        # 保存先ディレクトリ選択
        save_directory = filedialog.askdirectory(
            title="保存先ディレクトリを選択",
            initialdir=self.config.get('default_output_directory') or str(Path.home() / "Downloads")
        )
        
        if not save_directory:
            return
        
        try:
            save_path = Path(save_directory)
            saved_count = 0
            
            for i, thumbnail in enumerate(selected_thumbnails):
                # ファイル名生成
                filename = f"thumbnail_{thumbnail.frame_number:04d}.png"
                file_path = save_path / filename
                
                # 画像保存
                if isinstance(thumbnail.image_data, np.ndarray):
                    # numpy配列の場合
                    rgb_image = thumbnail.image_data[:, :, ::-1]  # BGR -> RGB
                    pil_image = Image.fromarray(rgb_image.astype('uint8'))
                    pil_image.save(file_path, "PNG")
                else:
                    # バイトデータの場合
                    with open(file_path, 'wb') as f:
                        f.write(thumbnail.image_data)
                
                saved_count += 1
            
            messagebox.showinfo("完了", 
                              f"{saved_count}個のサムネイルを保存しました。\\n保存先: {save_directory}")
            
            self.logger.info(f"{saved_count}個のサムネイルを保存: {save_directory}")
            
        except Exception as e:
            self.logger.error(f"サムネイル保存エラー: {e}")
            messagebox.showerror("エラー", f"サムネイルの保存に失敗しました:\\n{e}")
    
    def clear(self):
        """表示をクリア"""
        self.set_thumbnails([])
    
    def refresh(self):
        """表示を更新"""
        if self.thumbnails:
            self._relayout_thumbnails()
        else:
            self._show_empty_state()
