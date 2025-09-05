#!/usr/bin/env python3
"""
動画サムネイル抽出アプリケーション起動スクリプト

使用方法:
    python run_app.py        # GUIアプリケーションを起動
    python run_app.py --test # 基本テストのみ実行（GUI起動なし）
    python run_app.py --help # ヘルプを表示
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_components():
    """コンポーネントのテスト実行"""
    print("🧪 動画サムネイル抽出アプリケーション - コンポーネントテスト")
    print("=" * 60)
    
    try:
        # 1. ライブラリテスト
        print("1️⃣ ライブラリのテスト...")
        from src.lib import get_logger, get_config, ConfigPresets
        config = get_config()
        logger = get_logger(__name__)
        print(f"   ✅ 設定管理: {type(config).__name__}")
        print(f"   ✅ ログ機能: {type(logger).__name__}")
        print(f"   ✅ プリセット: {len(ConfigPresets.high_quality())}項目")
        
        # 2. モデルテスト
        print("\n2️⃣ データモデルのテスト...")
        from src.models import VideoFile, UserSettings, Thumbnail
        
        # テスト用の設定作成
        user_settings = UserSettings(
            thumbnail_count=5,
            output_width=1920,
            output_height=1080
        )
        print(f"   ✅ UserSettings: {user_settings.thumbnail_count}枚, {user_settings.output_width}x{user_settings.output_height}")
        
        # 3. サービステスト
        print("\n3️⃣ サービス層のテスト...")
        from src.services import VideoProcessor, FaceDetector, DiversitySelector, ThumbnailExtractor
        
        video_processor = VideoProcessor()
        face_detector = FaceDetector()
        diversity_selector = DiversitySelector()
        thumbnail_extractor = ThumbnailExtractor()
        
        print(f"   ✅ VideoProcessor: {type(video_processor).__name__}")
        print(f"   ✅ FaceDetector: {type(face_detector).__name__}")
        print(f"   ✅ DiversitySelector: {type(diversity_selector).__name__}")
        print(f"   ✅ ThumbnailExtractor: {type(thumbnail_extractor).__name__}")
        
        # 4. GUIコンポーネントテスト（起動なし）
        print("\n4️⃣ GUIコンポーネントのテスト...")
        from src.gui import get_gui_font, get_color, get_config as get_gui_config
        from src.gui.main_window import MainWindow
        from src.gui.settings_dialog import SettingsDialog
        from src.gui.thumbnail_grid import ThumbnailGrid
        from src.gui.async_worker import AsyncWorker
        
        print(f"   ✅ GUI基本関数: font={get_gui_font()}, color={get_color('primary')}")
        print(f"   ✅ MainWindow: {MainWindow.__name__}")
        print(f"   ✅ SettingsDialog: {SettingsDialog.__name__}")
        print(f"   ✅ ThumbnailGrid: {ThumbnailGrid.__name__}")
        print(f"   ✅ AsyncWorker: {AsyncWorker.__name__}")
        
        print("\n" + "=" * 60)
        print("🎉 すべてのコンポーネントテストが正常に完了しました！")
        print("\n📋 アプリケーション情報:")
        print(f"   - プロジェクトルート: {project_root}")
        print(f"   - 設定ファイル: {config.config_path}")
        print(f"   - ログレベル: {config.get('log_level', 'INFO')}")
        
        print("\n🚀 GUI起動方法:")
        print("   python run_app.py")
        print("   または")
        print("   python -m src.main")
        
        return True
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_gui():
    """GUIアプリケーションを起動"""
    print("🚀 動画サムネイル抽出アプリケーション - GUI起動中...")
    
    try:
        from src.main import main
        main()
        
    except KeyboardInterrupt:
        print("\n⏹️ ユーザーによってアプリケーションが中断されました")
    except Exception as e:
        print(f"\n❌ アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def show_help():
    """ヘルプを表示"""
    print(__doc__)
    print("\n🎯 このアプリケーションについて:")
    print("   - MP4動画から多様なサムネイルを自動抽出")
    print("   - AI顔検出による高品質な候補生成")
    print("   - ローカル処理でプライバシー保護")
    print("   - 直感的なGUIインターフェース")
    
    print("\n⚙️ システム要件:")
    print("   - Python 3.11+")
    print("   - tkinter（通常Pythonに含まれています）")
    print("   - OpenCV, MediaPipe, PIL, NumPy")
    print("   - MP4動画ファイル")

def main():
    """メイン関数"""
    # コマンドライン引数の処理
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['-h', '--help', 'help']:
            show_help()
            return
        elif arg in ['-t', '--test', 'test']:
            success = test_components()
            sys.exit(0 if success else 1)
        elif arg in ['-v', '--version', 'version']:
            try:
                from src import __version__
                print(f"動画サムネイル抽出アプリケーション v{__version__}")
            except ImportError:
                print("動画サムネイル抽出アプリケーション v1.0.0")
            return
        else:
            print(f"不明な引数: {arg}")
            print("ヘルプを表示するには: python run_app.py --help")
            return
    
    # デフォルト: GUIアプリケーション起動
    start_gui()

if __name__ == "__main__":
    main()
