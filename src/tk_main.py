"""
tkinter 版 エントリーポイント（PySimpleGUI不使用）

提供機能:
- 動画ファイル選択
- サムネイル枚数/出力サイズ/向きの設定
- 抽出開始/キャンセル、進捗バー、ステータス表示
- 生成サムネイルのプレビューと保存
"""

from __future__ import annotations

import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageTk

from src.lib import get_logger
from src.models import VideoFile, UserSettings, Thumbnail, ThumbnailOrientation
from src.gui.async_worker import create_worker, thumbnail_extraction_worker

class TkThumbnailApp:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.root = tk.Tk()
        self.root.title("動画サムネイル抽出 (tkinter)")
        self.root.geometry("1200x720")

        style = ttk.Style(self.root)
        style.theme_use("clam")

        try:
            self.root.tk.call("tk", "scaling", 1.0)
        except Exception:
            pass

        # 状態
        self.current_video: Optional[VideoFile] = None
        self.thumbnails: List[Thumbnail] = []
        self._photo_images: List[ImageTk.PhotoImage] = []  # GC防止

        # ワーカー
        self.worker = create_worker("thumbnail_extraction")
        self.worker.on_progress = self._on_progress
        self.worker.on_completed = self._on_completed
        self.worker.on_error = self._on_error
        self.worker.on_cancelled = self._on_cancelled

        self._build_ui()

    # ---------- UI 構築 ----------
    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container = ttk.Frame(self.root, padding=10)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=0)

        # 左: 操作
        control = ttk.LabelFrame(container, text="操作", padding=10)
        control.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        control.columnconfigure(1, weight=1)

        ttk.Label(control, text="動画ファイル").grid(row=0, column=0, sticky="w")
        self.var_path = tk.StringVar()
        ent_path = ttk.Entry(control, textvariable=self.var_path)
        ent_path.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ttk.Button(control, text="選択", command=self._choose_file).grid(row=0, column=2, sticky="w")

        ttk.Label(control, text="サムネイル枚数").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.var_count = tk.StringVar(value="5")
        spn_count = ttk.Spinbox(control, from_=1, to=50, textvariable=self.var_count, width=6)
        spn_count.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(8, 0))

        ttk.Label(control, text="幅x高さ").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.var_w = tk.StringVar(value="1920")
        self.var_h = tk.StringVar(value="1080")
        frm_size = ttk.Frame(control)
        frm_size.grid(row=2, column=1, sticky="w", padx=(5, 0), pady=(8, 0))
        ttk.Entry(frm_size, textvariable=self.var_w, width=8).grid(row=0, column=0)
        ttk.Label(frm_size, text="x").grid(row=0, column=1, padx=(4, 4))
        ttk.Entry(frm_size, textvariable=self.var_h, width=8).grid(row=0, column=2)

        ttk.Label(control, text="向き").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.var_ori = tk.StringVar(value="横型 (Landscape)")
        cmb_ori = ttk.Combobox(control, state="readonly", textvariable=self.var_ori,
                               values=["横型 (Landscape)", "縦型 (Portrait)", "自動 (Auto)"])
        cmb_ori.grid(row=3, column=1, sticky="w", padx=(5, 0), pady=(8, 0))

        frm_btn = ttk.Frame(control)
        frm_btn.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        frm_btn.columnconfigure(0, weight=1)
        self.btn_start = ttk.Button(frm_btn, text="サムネイル抽出開始", command=self._start)
        self.btn_start.grid(row=0, column=0, sticky="ew")
        self.btn_cancel = ttk.Button(frm_btn, text="キャンセル", command=self._cancel, state="disabled")
        self.btn_cancel.grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.prog = ttk.Progressbar(control, mode="determinate", maximum=100)
        self.prog.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        self.lbl_status = ttk.Label(control, text="待機中")
        self.lbl_status.grid(row=6, column=0, columnspan=3, sticky="w", pady=(4, 0))

        frm_save = ttk.Frame(control)
        frm_save.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        self.btn_save_all = ttk.Button(frm_save, text="全て保存", command=self._save_all, state="disabled")
        self.btn_save_all.grid(row=0, column=0, sticky="w")

        # 右: プレビュー（スクロール）
        preview = ttk.LabelFrame(container, text="プレビュー・結果", padding=10)
        preview.grid(row=0, column=1, sticky="nsew")
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(preview, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(preview, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")

        self.inner = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # ステータスバー（任意）
        statusbar = ttk.Frame(container)
        statusbar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Label(statusbar, text="準備完了").pack(side="left")

    # ---------- イベント/コールバック ----------
    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # キャンバス幅に合わせて内部フレーム幅を更新
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        except Exception:
            pass

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(title="動画を選択", filetypes=[("MP4", "*.mp4"), ("All", "*.*")])
        if not path:
            return
        self.var_path.set(path)
        self.current_video = VideoFile(file_path=Path(path))

    def _orientation_enum(self) -> ThumbnailOrientation:
        label = self.var_ori.get()
        if "Portrait" in label:
            return ThumbnailOrientation.PORTRAIT
        if "Auto" in label:
            return ThumbnailOrientation.AUTO
        return ThumbnailOrientation.LANDSCAPE

    def _start(self) -> None:
        if not self.current_video and self.var_path.get():
            self.current_video = VideoFile(file_path=Path(self.var_path.get()))
        if not self.current_video:
            messagebox.showinfo("情報", "動画を選択してください")
            return
        try:
            settings = UserSettings(
                thumbnail_count=int(self.var_count.get()),
                output_width=int(self.var_w.get()),
                output_height=int(self.var_h.get()),
                orientation=self._orientation_enum(),
            )
        except Exception as e:
            messagebox.showerror("設定エラー", f"設定値が不正です: {e}")
            return

        self.btn_start.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.btn_save_all.configure(state="disabled")
        self._set_status("処理開始...")
        self._set_progress(0)

        self.worker.start(thumbnail_extraction_worker, self.current_video, settings)

    def _cancel(self) -> None:
        if self.worker.is_running():
            self.worker.cancel()
        self.btn_cancel.configure(state="disabled")
        self._set_status("キャンセル中...")

    # ワーカー -> UI（メインスレッドにディスパッチ）
    def _on_progress(self, upd) -> None:
        self.root.after(0, lambda: self._handle_progress(upd))

    def _handle_progress(self, upd) -> None:
        self._set_progress(max(0, min(100, upd.progress)))
        self._set_status(upd.status_message)

    def _on_completed(self, result) -> None:
        self.root.after(0, lambda: self._handle_completed(result))

    def _handle_completed(self, result) -> None:
        self.thumbnails = result.result or []
        self._render_thumbnails(self.thumbnails)
        self._set_status(f"完了 - {len(self.thumbnails)}個のサムネイル")
        self.btn_start.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.btn_save_all.configure(state="normal")

    def _on_error(self, error: Exception) -> None:
        self.root.after(0, lambda: self._handle_error(error))

    def _handle_error(self, error: Exception) -> None:
        messagebox.showerror("エラー", str(error))
        self.btn_start.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self._set_status("エラーが発生しました")

    def _on_cancelled(self) -> None:
        self.root.after(0, lambda: self._set_status("キャンセルされました"))
        self.root.after(0, lambda: self.btn_start.configure(state="normal"))
        self.root.after(0, lambda: self.btn_cancel.configure(state="disabled"))

    # ---------- プレビュー/保存 ----------
    def _clear_preview(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()
        self._photo_images.clear()

    def _render_thumbnails(self, thumbnails: List[Thumbnail]) -> None:
        self._clear_preview()
        if not thumbnails:
            return
        cols = 3
        thumb_max_w = 360
        for i, th in enumerate(thumbnails):
            try:
                png_bytes = th.to_png_bytes()
                img = Image.open(io.BytesIO(png_bytes))
                scale = min(1.0, float(thumb_max_w) / float(max(1, img.width)))
                if scale < 1.0:
                    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._photo_images.append(photo)
            except Exception:
                photo = None
            frame = ttk.Frame(self.inner, padding=6)
            r, c = divmod(i, cols)
            frame.grid(row=r, column=c, sticky="nw")
            meta = f"{i+1}: {th.width}x{th.height} @ {th.timestamp:.1f}s"
            ttk.Label(frame, text=meta).pack(anchor="w")
            if photo is not None:
                tk.Label(frame, image=photo).pack(anchor="w")

    def _save_all(self) -> None:
        if not self.thumbnails:
            messagebox.showinfo("情報", "サムネイルがありません")
            return
        out_dir = filedialog.askdirectory(title="保存先フォルダを選択")
        if not out_dir:
            return
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        for i, th in enumerate(self.thumbnails, 1):
            th.save_to_file(out / f"thumbnail_{i:03d}.png")
        messagebox.showinfo("完了", "保存が完了しました")

    # ---------- ユーティリティ ----------
    def _set_progress(self, value: float) -> None:
        self.prog.configure(value=value)

    def _set_status(self, text: str) -> None:
        self.lbl_status.configure(text=text)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    TkThumbnailApp().run()


if __name__ == "__main__":
    main()


