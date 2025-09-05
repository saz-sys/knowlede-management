#!/usr/bin/env python3
"""
Mac GUI表示問題の最終解決策
- 強制描画更新
- 異なる描画方法の組み合わせ
"""
import tkinter as tk
import sys
import time

def main():
    print("=== Mac GUI 最終修正版 ===")
    
    try:
        # Macの警告を抑制
        import os
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        # ルートウィンドウ作成
        root = tk.Tk()
        root.withdraw()  # 最初は隠す
        
        # 基本設定
        root.title("Mac GUI 修正版")
        root.geometry("600x500+200+200")
        root.configure(bg="lightgray")
        
        print("✅ ウィンドウ基本設定完了")
        
        # フレーム作成（これが重要）
        main_frame = tk.Frame(root, bg="white", relief="raised", bd=5)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        print("✅ メインフレーム作成")
        
        # 大きな見出し
        title = tk.Label(main_frame, 
                        text="🎬 動画サムネイル抽出アプリ", 
                        font=("Helvetica", 28, "bold"),
                        bg="navy", 
                        fg="white",
                        pady=15)
        title.pack(fill=tk.X, padx=5, pady=5)
        
        print("✅ タイトル作成")
        
        # 状態表示
        status_text = tk.StringVar()
        status_text.set("✅ アプリケーション正常起動")
        
        status_label = tk.Label(main_frame,
                               textvariable=status_text,
                               font=("Helvetica", 16),
                               bg="lightgreen",
                               fg="darkgreen",
                               pady=10)
        status_label.pack(fill=tk.X, padx=5, pady=5)
        
        print("✅ ステータス表示作成")
        
        # 機能ボタン群
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=20)
        
        def test_function():
            print("🔥 テスト機能実行！")
            status_text.set("🔥 テスト機能が実行されました！")
            root.update()
        
        test_btn = tk.Button(button_frame,
                            text="🧪 テスト実行",
                            command=test_function,
                            font=("Helvetica", 16, "bold"),
                            bg="orange",
                            fg="white",
                            padx=20,
                            pady=10)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        def file_select():
            print("📁 ファイル選択実行！")
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="動画ファイルを選択",
                filetypes=[("動画ファイル", "*.mp4 *.avi *.mov"), ("全て", "*.*")]
            )
            if filename:
                status_text.set(f"📁 選択: {filename}")
                print(f"📁 ファイル選択: {filename}")
            root.update()
        
        file_btn = tk.Button(button_frame,
                            text="📁 ファイル選択",
                            command=file_select,
                            font=("Helvetica", 16, "bold"),
                            bg="blue",
                            fg="white",
                            padx=20,
                            pady=10)
        file_btn.pack(side=tk.LEFT, padx=10)
        
        def close_app():
            print("🚪 アプリケーション終了")
            status_text.set("🚪 終了中...")
            root.update()
            time.sleep(0.5)
            root.destroy()
        
        close_btn = tk.Button(button_frame,
                             text="🚪 終了",
                             command=close_app,
                             font=("Helvetica", 16, "bold"),
                             bg="red",
                             fg="white",
                             padx=20,
                             pady=10)
        close_btn.pack(side=tk.LEFT, padx=10)
        
        print("✅ ボタン群作成完了")
        
        # 説明テキスト
        info_text = """
🎯 このアプリケーションの機能:
• 動画ファイルからサムネイル抽出
• AI顔検出による最適化
• 複数サイズでの出力対応

📋 操作方法:
1. 「ファイル選択」で動画を選択
2. 「テスト実行」で動作確認
3. 「終了」でアプリを閉じる
        """
        
        info_label = tk.Label(main_frame,
                             text=info_text,
                             font=("Helvetica", 12),
                             bg="lightyellow",
                             fg="black",
                             justify=tk.LEFT,
                             padx=20,
                             pady=15)
        info_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        print("✅ 説明テキスト作成")
        
        # 終了処理
        root.protocol("WM_DELETE_WINDOW", close_app)
        
        # 強制更新と表示
        print("🔄 強制更新開始...")
        
        root.update_idletasks()
        root.update()
        
        print("🔄 ウィンドウ表示...")
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # 追加の強制更新
        for i in range(3):
            root.update()
            time.sleep(0.1)
        
        print("✅ 表示処理完了")
        print("")
        print("🎬 動画サムネイル抽出アプリが起動しました！")
        print("📺 以下が表示されているはずです:")
        print("   • 紺色の大きなタイトル")
        print("   • 緑色のステータス表示")
        print("   • オレンジ・青・赤のボタン")
        print("   • 黄色い説明エリア")
        print("")
        
        # メインループ
        root.mainloop()
        
        print("✅ アプリケーション正常終了")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
