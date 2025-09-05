#!/usr/bin/env python3
"""
CustomTkinter デバッグ版
段階的に問題を特定・解決
"""
import customtkinter as ctk
import tkinter as tk
import time

def test_basic_customtkinter():
    """基本的なCustomTkinterテスト"""
    print("=== CustomTkinter 基本テスト ===")
    
    try:
        # 設定
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # ウィンドウ作成
        root = ctk.CTk()
        root.title("CustomTkinter テスト")
        root.geometry("600x400+200+200")
        
        print("✅ ウィンドウ作成成功")
        
        # 背景色を明確に設定
        root.configure(fg_color="#f0f0f0")
        
        # シンプルなラベル
        label = ctk.CTkLabel(
            root,
            text="これが見えていますか？",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#000000",  # 黒文字
            fg_color="#ffffff",    # 白背景
            corner_radius=10,
            width=300,
            height=50
        )
        label.pack(pady=50)
        print("✅ ラベル作成成功")
        
        # ボタン
        def button_click():
            print("🔴 ボタンがクリックされました！")
            label.configure(text="ボタンがクリックされました！")
        
        button = ctk.CTkButton(
            root,
            text="このボタンをクリック",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#ff0000",    # 赤背景
            text_color="#ffffff",  # 白文字
            width=200,
            height=40,
            command=button_click
        )
        button.pack(pady=20)
        print("✅ ボタン作成成功")
        
        # 入力フィールド
        entry = ctk.CTkEntry(
            root,
            placeholder_text="ここに文字を入力",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="#ffffff",
            text_color="#000000",
            border_color="#000000",
            border_width=2
        )
        entry.pack(pady=20)
        print("✅ エントリー作成成功")
        
        # フレーム
        frame = ctk.CTkFrame(
            root,
            fg_color="#e0e0e0",
            border_color="#000000",
            border_width=3,
            corner_radius=10,
            width=400,
            height=100
        )
        frame.pack(pady=20)
        
        frame_label = ctk.CTkLabel(
            frame,
            text="これはフレーム内のラベルです",
            font=ctk.CTkFont(size=14),
            text_color="#000000"
        )
        frame_label.pack(pady=30)
        print("✅ フレーム作成成功")
        
        # 自動終了
        def auto_close():
            print("⏰ 10秒経過 - 自動終了")
            root.destroy()
        
        root.after(10000, auto_close)
        
        print("🚀 CustomTkinter テスト開始")
        print("📺 以下が見えているはずです:")
        print("   1. 白背景の大きなテキスト")
        print("   2. 赤いボタン")
        print("   3. 入力フィールド")
        print("   4. グレーのフレーム")
        
        # 強制表示（Mac対応）
        root.update_idletasks()
        root.update()
        root.deiconify()
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        # 複数回更新
        for i in range(5):
            root.update()
            time.sleep(0.1)
        
        print("✅ 強制表示処理完了")
        
        root.mainloop()
        print("✅ テスト完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def test_fallback_tkinter():
    """フォールバック: 標準tkinter"""
    print("\n=== 標準tkinter フォールバック ===")
    
    try:
        root = tk.Tk()
        root.title("標準tkinter テスト")
        root.geometry("600x400+250+250")
        root.configure(bg="#f0f0f0")
        
        # ラベル
        label = tk.Label(
            root,
            text="標準tkinterでの表示",
            font=("Arial", 20, "bold"),
            bg="#ffffff",
            fg="#000000",
            width=20,
            height=2
        )
        label.pack(pady=30)
        
        # ボタン
        def click():
            print("🔴 標準tkinterボタンクリック")
            label.config(text="ボタンがクリックされました")
        
        button = tk.Button(
            root,
            text="標準tkinterボタン",
            font=("Arial", 14, "bold"),
            bg="#ff0000",
            fg="#ffffff",
            width=20,
            height=2,
            command=click
        )
        button.pack(pady=20)
        
        # 自動終了
        root.after(8000, root.destroy)
        
        print("🚀 標準tkinter テスト開始")
        
        # Mac対応表示
        root.update()
        root.deiconify()
        root.lift()
        
        root.mainloop()
        print("✅ 標準tkinter テスト完了")
        
    except Exception as e:
        print(f"❌ 標準tkinter エラー: {e}")

if __name__ == "__main__":
    print("🔍 CustomTkinter 問題診断開始")
    
    # Step 1: CustomTkinter テスト
    test_basic_customtkinter()
    
    # Step 2: 標準tkinter フォールバック
    test_fallback_tkinter()
    
    print("\n🔍 診断完了")
