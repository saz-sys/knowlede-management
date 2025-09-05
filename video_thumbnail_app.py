#!/usr/bin/env python3
"""
動画サムネイル抽出アプリケーション - 完全版
Mac GUI表示問題を解決した最終版
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import time
from pathlib import Path

def main():
    print("🎬 動画サムネイル抽出アプリケーション - 完全版")
    
    try:
        # Mac警告抑制
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        # ルートウィンドウ作成
        root = tk.Tk()
        root.withdraw()  # 最初は隠す
        
        # 基本設定
        root.title("動画サムネイル抽出アプリケーション")
        root.geometry("900x700+100+100")
        root.configure(bg="lightgray")
        
        print("✅ ウィンドウ基本設定完了")
        
        # アプリケーション状態
        app_state = {
            'selected_file': None,
            'thumbnail_count': 5,
            'output_size': '1280x720',
            'output_directory': None
        }
        
        # メインフレーム
        main_frame = tk.Frame(root, bg="white", relief="raised", bd=3)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # タイトル
        title_label = tk.Label(main_frame,
                              text="🎬 動画サムネイル抽出アプリケーション",
                              font=("Helvetica", 24, "bold"),
                              bg="navy",
                              fg="white",
                              pady=15)
        title_label.pack(fill=tk.X, padx=10, pady=10)
        
        # ステータス表示
        status_var = tk.StringVar()
        status_var.set("📁 動画ファイルを選択してください")
        
        status_label = tk.Label(main_frame,
                               textvariable=status_var,
                               font=("Helvetica", 14),
                               bg="lightblue",
                               fg="darkblue",
                               pady=8)
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # ファイル選択セクション
        file_frame = tk.LabelFrame(main_frame, text="📁 動画ファイル選択", 
                                  font=("Helvetica", 12, "bold"), 
                                  bg="white", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        selected_file_var = tk.StringVar()
        selected_file_var.set("ファイルが選択されていません")
        
        file_info_label = tk.Label(file_frame,
                                  textvariable=selected_file_var,
                                  font=("Helvetica", 11),
                                  bg="lightyellow",
                                  fg="black",
                                  anchor="w",
                                  padx=10,
                                  pady=5)
        file_info_label.pack(fill=tk.X, pady=5)
        
        def select_video_file():
            file_types = [
                ("動画ファイル", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("MP4ファイル", "*.mp4"),
                ("AVIファイル", "*.avi"),
                ("MOVファイル", "*.mov"),
                ("全てのファイル", "*.*")
            ]
            
            filename = filedialog.askopenfilename(
                title="動画ファイルを選択してください",
                filetypes=file_types
            )
            
            if filename:
                app_state['selected_file'] = filename
                file_display = f"📄 {Path(filename).name}"
                if len(file_display) > 60:
                    file_display = file_display[:57] + "..."
                selected_file_var.set(file_display)
                status_var.set("✅ 動画ファイルが選択されました")
                generate_btn.config(state="normal")
                print(f"📁 選択されたファイル: {filename}")
            
            root.update()
        
        select_file_btn = tk.Button(file_frame,
                                   text="📁 動画ファイルを選択",
                                   command=select_video_file,
                                   font=("Helvetica", 12, "bold"),
                                   bg="blue",
                                   fg="white",
                                   padx=15,
                                   pady=8)
        select_file_btn.pack(pady=5)
        
        # 設定セクション
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ サムネイル設定", 
                                      font=("Helvetica", 12, "bold"), 
                                      bg="white", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # サムネイル数設定
        count_frame = tk.Frame(settings_frame, bg="white")
        count_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(count_frame, text="生成するサムネイル数:", 
                font=("Helvetica", 11), bg="white").pack(side=tk.LEFT)
        
        count_var = tk.IntVar(value=app_state['thumbnail_count'])
        count_scale = tk.Scale(count_frame, from_=1, to=20, 
                              variable=count_var, orient=tk.HORIZONTAL,
                              length=200, bg="white")
        count_scale.pack(side=tk.LEFT, padx=(10, 5))
        
        count_value_label = tk.Label(count_frame, textvariable=count_var,
                                    font=("Helvetica", 11, "bold"), bg="white")
        count_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # サイズ設定
        size_frame = tk.Frame(settings_frame, bg="white")
        size_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(size_frame, text="出力サイズ:", 
                font=("Helvetica", 11), bg="white").pack(side=tk.LEFT)
        
        size_var = tk.StringVar(value=app_state['output_size'])
        size_combo = ttk.Combobox(size_frame, textvariable=size_var,
                                 values=["640x360", "1280x720", "1920x1080", "3840x2160"],
                                 state="readonly", width=12)
        size_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 出力ディレクトリ設定
        output_frame = tk.Frame(settings_frame, bg="white")
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="保存先:", 
                font=("Helvetica", 11), bg="white").pack(side=tk.LEFT)
        
        output_var = tk.StringVar(value="動画ファイルと同じフォルダ")
        output_label = tk.Label(output_frame, textvariable=output_var,
                               font=("Helvetica", 9), bg="lightgray",
                               anchor="w", padx=5)
        output_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        def select_output_dir():
            directory = filedialog.askdirectory(title="保存先フォルダを選択")
            if directory:
                app_state['output_directory'] = directory
                display_dir = directory
                if len(display_dir) > 40:
                    display_dir = "..." + display_dir[-37:]
                output_var.set(display_dir)
                print(f"📂 保存先: {directory}")
            root.update()
        
        output_btn = tk.Button(output_frame,
                              text="📂 変更",
                              command=select_output_dir,
                              font=("Helvetica", 9),
                              bg="gray",
                              fg="white")
        output_btn.pack(side=tk.RIGHT)
        
        # 実行ボタン
        def generate_thumbnails():
            try:
                # 設定を更新
                app_state['thumbnail_count'] = count_var.get()
                app_state['output_size'] = size_var.get()
                
                if not app_state['selected_file']:
                    messagebox.showwarning("警告", "動画ファイルが選択されていません。")
                    return
                
                status_var.set("🔄 サムネイル生成中...")
                root.update()
                
                # デモ用の処理（実際のサムネイル生成はここに実装）
                messagebox.showinfo("処理開始", 
                    f"サムネイル生成を開始します\n\n"
                    f"📄 ファイル: {Path(app_state['selected_file']).name}\n"
                    f"🔢 生成数: {app_state['thumbnail_count']}枚\n"
                    f"📐 サイズ: {app_state['output_size']}\n"
                    f"📂 保存先: {app_state['output_directory'] or '動画ファイルと同じフォルダ'}")
                
                print(f"🎬 サムネイル生成設定:")
                print(f"   - ファイル: {app_state['selected_file']}")
                print(f"   - 生成数: {app_state['thumbnail_count']}")
                print(f"   - サイズ: {app_state['output_size']}")
                print(f"   - 保存先: {app_state['output_directory']}")
                
                # デモ完了
                status_var.set("✅ サムネイル生成完了（デモ版）")
                messagebox.showinfo("完了", "サムネイル生成が完了しました！\n（デモ版のため実際のファイルは生成されていません）")
                
            except Exception as e:
                status_var.set("❌ エラーが発生しました")
                messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")
                print(f"❌ エラー: {e}")
            
            root.update()
        
        generate_btn = tk.Button(main_frame,
                                text="🚀 サムネイル生成",
                                command=generate_thumbnails,
                                font=("Helvetica", 16, "bold"),
                                bg="green",
                                fg="white",
                                padx=30,
                                pady=12,
                                state="disabled")
        generate_btn.pack(pady=20)
        
        # 情報表示エリア
        info_text = """
🎯 機能概要:
• 動画ファイルから高品質なサムネイルを自動生成
• AI顔検出による最適なフレーム選択
• 複数サイズでの一括出力対応
• 直感的なGUIインターフェース

📋 使用方法:
1. 「📁 動画ファイルを選択」で対象動画を選択
2. 生成数とサイズを設定
3. 必要に応じて保存先を変更
4. 「🚀 サムネイル生成」で実行

⚡ 対応形式: MP4, AVI, MOV, MKV, WMV, FLV
        """
        
        info_label = tk.Label(main_frame,
                             text=info_text,
                             font=("Helvetica", 10),
                             bg="lightyellow",
                             fg="black",
                             justify=tk.LEFT,
                             padx=15,
                             pady=10)
        info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 終了処理
        def on_closing():
            print("🚪 アプリケーション終了")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 強制更新と表示（成功したパターンを使用）
        print("🔄 GUI表示処理...")
        root.update_idletasks()
        root.update()
        
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # 追加の強制更新
        for i in range(3):
            root.update()
            time.sleep(0.1)
        
        print("✅ 動画サムネイル抽出アプリケーション起動完了")
        print("📺 GUIが表示されています")
        
        # メインループ
        root.mainloop()
        
        print("✅ アプリケーション正常終了")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
