"""
PySimpleGUIQt 版 エントリーポイント（tkinter非依存）

要件:
- 動画選択
- サムネイル枚数/出力サイズ/向き
- 開始/キャンセル、進捗表示
- サムネイルプレビューと保存
"""

import PySimpleGUIQt as sg
from pathlib import Path
from typing import List, Optional
import threading

from src.lib import get_logger
from src.models import VideoFile, UserSettings, Thumbnail, ThumbnailOrientation
from src.gui.async_worker import create_worker, thumbnail_extraction_worker


logger = get_logger(__name__)


# Qt バックエンド使用のため、tkinterワークアラウンドは不要

def create_layout():
    settings_col = [
        [sg.Text("動画ファイル"), sg.Input(key="-VID-", enable_events=True, readonly=True, expand_x=True), sg.FileBrowse("選択", file_types=(("MP4", "*.mp4"), ("All", "*.*")))],
        [sg.Text("サムネイル枚数"), sg.Spin(values=list(range(1, 21)), initial_value=5, key="-COUNT-", size=(5,1))],
        [sg.Text("幅"), sg.Input("1920", key="-W-", size=(6,1)), sg.Text("高さ"), sg.Input("1080", key="-H-", size=(6,1))],
        [sg.Text("向き"), sg.Combo(["横型 (Landscape)", "縦型 (Portrait)", "自動 (Auto)"], default_value="横型 (Landscape)", key="-ORI-", readonly=True)],
        [sg.Button("サムネイル抽出開始", key="-START-", size=(20,1)), sg.Button("キャンセル", key="-CANCEL-", disabled=True)],
        [sg.ProgressBar(100, orientation='h', size=(40,20), key='-PROG-')],
        [sg.Text("待機中", key="-STATUS-", size=(50,1))],
        [sg.HSeparator()],
        [sg.Button("選択したサムネイルを保存", key="-SAVESEL-", disabled=True), sg.Button("全て保存", key="-SAVEALL-", disabled=True)]
    ]

    preview_col = [
        [sg.Frame("プレビュー・結果", [[sg.Column([[]], key="-GRID-", scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)]], expand_x=True, expand_y=True)]
    ]

    layout = [
        [sg.Column(settings_col, vertical_alignment='top'), sg.VSeperator(), sg.Column(preview_col, expand_x=True, expand_y=True)]
    ]
    return layout


def orientation_label_to_enum(label: str) -> ThumbnailOrientation:
    if 'Portrait' in label:
        return ThumbnailOrientation.PORTRAIT
    if 'Auto' in label:
        return ThumbnailOrientation.AUTO
    return ThumbnailOrientation.LANDSCAPE


class PSGApp:
    def __init__(self):
        self.window = sg.Window("動画サムネイル抽出 (PySimpleGUIQt)", create_layout(), resizable=True, finalize=True)
        self.worker = create_worker("thumbnail_extraction")
        self.worker.on_progress = self._on_progress
        self.worker.on_completed = self._on_completed
        self.worker.on_error = self._on_error
        self.worker.on_cancelled = self._on_cancelled

        self.current_video: Optional[VideoFile] = None
        self.thumbnails: List[Thumbnail] = []

    def _on_progress(self, upd):
        self.window.write_event_value("_EVT_PROGRESS_", upd)

    def _on_completed(self, result):
        self.window.write_event_value("_EVT_DONE_", result.result)

    def _on_error(self, error: Exception):
        self.window.write_event_value("_EVT_ERROR_", error)

    def _on_cancelled(self):
        self.window.write_event_value("_EVT_CANCELLED_", None)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                if self.worker.is_running():
                    self.worker.cancel()
                break

            if event == "-VID-":
                path = values["-VID-"]
                self.current_video = VideoFile(file_path=Path(path)) if path else None

            if event == "-START-":
                if not self.current_video:
                    sg.popup("動画を選択してください")
                    continue
                try:
                    settings = UserSettings(
                        thumbnail_count=int(values["-COUNT-"]),
                        output_width=int(values["-W-"]),
                        output_height=int(values["-H-"]),
                        orientation=orientation_label_to_enum(values["-ORI-"])
                    )
                except Exception as e:
                    sg.popup_error(f"設定値が不正です: {e}")
                    continue

                self.window["-START-"].update(disabled=True)
                self.window["-CANCEL-"].update(disabled=False)
                self.window["-STATUS-"].update("処理開始...")
                self.window["-PROG-"].update(0)

                self.worker.start(thumbnail_extraction_worker, self.current_video, settings)

            if event == "-CANCEL-":
                if self.worker.is_running():
                    self.worker.cancel()
                self.window["-CANCEL-"].update(disabled=True)
                self.window["-STATUS-"].update("キャンセル中...")

            if event == "_EVT_PROGRESS_":
                upd = values[event]
                self.window["-PROG-"].update(max(0, min(100, upd.progress)))
                self.window["-STATUS-"].update(upd.status_message)

            if event == "_EVT_DONE_":
                self.thumbnails = values[event]
                self._render_thumbnails(self.thumbnails)
                self.window["-STATUS-"].update(f"完了 - {len(self.thumbnails)}個のサムネイル")
                self.window["-START-"].update(disabled=False)
                self.window["-CANCEL-"].update(disabled=True)
                self.window["-SAVESEL-"].update(disabled=False)
                self.window["-SAVEALL-"].update(disabled=False)

            if event == "_EVT_ERROR_":
                err = values[event]
                sg.popup_error(f"エラー: {err}")
                self.window["-START-"].update(disabled=False)
                self.window["-CANCEL-"].update(disabled=True)

            if event == "_EVT_CANCELLED_":
                self.window["-STATUS-"].update("キャンセルされました")
                self.window["-START-"].update(disabled=False)
                self.window["-CANCEL-"].update(disabled=True)

            if event == "-SAVEALL-":
                self._save_thumbnails(self.thumbnails)

            if event == "-SAVESEL-":
                # シンプルに全保存と同等（選択UIは今後拡張）
                self._save_thumbnails(self.thumbnails)

        self.window.close()

    def _render_thumbnails(self, thumbnails: List[Thumbnail]):
        grid = self.window["-GRID-"]
        # サムネイルを行列に並べる（3列）
        rows: List[List[sg.Element]] = []
        current_row: List[sg.Element] = []
        cols = 3
        for i, th in enumerate(thumbnails):
            meta = f"{i+1}: {th.width}x{th.height} @ {th.timestamp:.1f}s"
            try:
                img_data = th.to_png_bytes()  # QtはPNGバイトをそのまま扱える
            except Exception:
                img_data = b""
            img_elem = sg.Image(data=img_data, key=f"-IMG-{i}-")
            frame = sg.Frame(meta, [[img_elem]], expand_x=True)
            current_row.append(frame)
            if (i + 1) % cols == 0:
                rows.append(current_row)
                current_row = []
        if current_row:
            rows.append(current_row)
        grid.update(rows)

    def _save_thumbnails(self, thumbnails: List[Thumbnail]):
        if not thumbnails:
            sg.popup("サムネイルがありません")
            return
        out_dir = sg.popup_get_folder("保存先フォルダを選択")
        if not out_dir:
            return
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        for i, th in enumerate(thumbnails, 1):
            th.save_to_file(out / f"thumbnail_{i:03d}.png")
        sg.popup("保存完了")


def main():
    PSGApp().run()


if __name__ == "__main__":
    main()


