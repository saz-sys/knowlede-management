# 配布ガイド

動画サムネイル抽出アプリケーションの配布用実行ファイル作成・配布方法の詳細ガイド。

## 📋 目次

- [配布形式](#配布形式)
- [PyInstaller配布](#pyinstaller配布)
- [プラットフォーム別対応](#プラットフォーム別対応)
- [自動ビルド](#自動ビルド)
- [配布前チェック](#配布前チェック)
- [トラブルシューティング](#トラブルシューティング)

## 📦 配布形式

### オプション1: 単一実行ファイル（推奨）

**メリット**
- 1つのファイルで完結
- 依存関係を内包
- ユーザーの手間が最小

**デメリット**
- ファイルサイズが大きい（150-250MB）
- 起動時間がやや長い

### オプション2: フォルダ配布

**メリット**
- 起動が高速
- デバッグが容易

**デメリット**
- 複数ファイルの管理が必要
- 誤削除のリスク

### オプション3: インストーラー

**メリット**
- プロフェッショナルな配布
- アンインストール対応
- ショートカット自動作成

**デメリット**
- 作成が複雑
- プラットフォーム依存

## 🚀 PyInstaller配布

### 1. 基本セットアップ

```bash
# PyInstallerインストール
pip install pyinstaller

# 基本的な実行ファイル作成
pyinstaller run_app.py

# 単一ファイル作成（推奨）
pyinstaller --onefile run_app.py

# GUI用設定（コンソールなし）
pyinstaller --onefile --windowed run_app.py
```

### 2. 詳細設定

```bash
# 完全設定版
pyinstaller \
    --onefile \
    --windowed \
    --name "VideoThumbnailExtractor" \
    --icon assets/app.ico \
    --add-data "assets:assets" \
    --hidden-import cv2 \
    --hidden-import mediapipe \
    --exclude-module _tkinter_finder \
    run_app.py
```

### 3. specファイル使用

```python
# create_executable.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'cv2',
        'mediapipe',
        'PIL._tkinter_finder',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoThumbnailExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico'
)
```

実行:
```bash
pyinstaller create_executable.spec
```

### 4. ビルドスクリプト

```bash
#!/bin/bash
# scripts/build_distribution.sh

set -e

echo "🚀 配布用実行ファイル作成開始..."

# 1. 環境確認
python --version
pip list | grep pyinstaller

# 2. クリーンアップ
rm -rf build/ dist/ *.spec

# 3. アイコンファイル確認
if [ ! -f "assets/app.ico" ]; then
    echo "⚠️ アイコンファイルが見つかりません。デフォルトアイコンを使用します。"
    ICON_OPTION=""
else
    ICON_OPTION="--icon assets/app.ico"
fi

# 4. 実行ファイル作成
echo "📦 実行ファイル作成中..."
pyinstaller \
    --onefile \
    --windowed \
    --name "VideoThumbnailExtractor" \
    $ICON_OPTION \
    --hidden-import cv2 \
    --hidden-import mediapipe \
    --exclude-module matplotlib \
    --exclude-module scipy \
    run_app.py

# 5. 動作確認
echo "🧪 動作確認テスト..."
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    ./dist/VideoThumbnailExtractor --test || exit 1
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    ./dist/VideoThumbnailExtractor --test || exit 1
else
    # Windows (Git Bash)
    ./dist/VideoThumbnailExtractor.exe --test || exit 1
fi

# 6. ファイルサイズ確認
echo "📊 生成ファイル情報:"
ls -lh dist/

echo "✅ 配布用実行ファイル作成完了!"
echo "📁 出力場所: dist/"
```

## 🖥️ プラットフォーム別対応

### macOS

#### 基本ビルド
```bash
# .app形式作成
pyinstaller --onedir --windowed run_app.py

# 単一実行ファイル
pyinstaller --onefile --windowed run_app.py

# コード署名（開発者向け）
codesign --force --verify --verbose --sign "Developer ID Application: Your Name" dist/VideoThumbnailExtractor
```

#### DMGファイル作成
```bash
# 1. create-dmg インストール
brew install create-dmg

# 2. DMG作成
create-dmg \
    --volname "Video Thumbnail Extractor" \
    --window-pos 200 120 \
    --window-size 600 300 \
    --icon-size 100 \
    --icon "VideoThumbnailExtractor.app" 175 120 \
    --hide-extension "VideoThumbnailExtractor.app" \
    --app-drop-link 425 120 \
    "VideoThumbnailExtractor.dmg" \
    "dist/"
```

### Windows

#### 基本ビルド
```bash
# 実行ファイル作成
pyinstaller --onefile --windowed --icon app.ico run_app.py

# UPX圧縮（ファイルサイズ削減）
pyinstaller --onefile --windowed --upx-dir upx run_app.py
```

#### インストーラー作成（Inno Setup）
```pascal
; installer.iss
[Setup]
AppName=Video Thumbnail Extractor
AppVersion=1.0.0
DefaultDirName={autopf}\VideoThumbnailExtractor
DefaultGroupName=Video Thumbnail Extractor
OutputBaseFilename=VideoThumbnailExtractor-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\VideoThumbnailExtractor.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Video Thumbnail Extractor"; Filename: "{app}\VideoThumbnailExtractor.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
```

### Linux

#### AppImage作成
```bash
# 1. AppImage用ディレクトリ構造
mkdir -p VideoThumbnailExtractor.AppDir/usr/bin
cp dist/VideoThumbnailExtractor VideoThumbnailExtractor.AppDir/usr/bin/

# 2. .desktop ファイル作成
cat > VideoThumbnailExtractor.AppDir/VideoThumbnailExtractor.desktop << EOF
[Desktop Entry]
Type=Application
Name=Video Thumbnail Extractor
Exec=VideoThumbnailExtractor
Icon=VideoThumbnailExtractor
Categories=Multimedia;Video;
EOF

# 3. AppImage生成
appimagetool VideoThumbnailExtractor.AppDir
```

## 🤖 自動ビルド

### GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build Distribution

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed run_app.py
    
    - name: Test executable
      run: |
        ./dist/run_app --test  # Linux/macOS
        # .\dist\run_app.exe --test  # Windows
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: VideoThumbnailExtractor-${{ matrix.os }}
        path: dist/
```

### ローカル自動ビルド

```bash
#!/bin/bash
# scripts/auto_build.sh

# 全プラットフォーム用ビルド
for platform in "windows" "macos" "linux"; do
    echo "🔨 $platform 用ビルド開始..."
    
    # Docker使用（クロスプラットフォームビルド）
    docker run --rm -v $(pwd):/app -w /app \
        python-build-$platform \
        bash scripts/build_for_$platform.sh
        
    echo "✅ $platform 用ビルド完了"
done
```

## ✅ 配布前チェック

### 1. 動作確認チェックリスト

```bash
# 基本動作テスト
./dist/VideoThumbnailExtractor --test

# GUI起動テスト
./dist/VideoThumbnailExtractor

# 実際のファイル処理テスト
# - MP4ファイル読み込み
# - サムネイル生成
# - 設定変更
# - エラーハンドリング
```

### 2. ファイルサイズ確認

```bash
# ファイルサイズ目標
# - Windows: < 200MB
# - macOS: < 250MB
# - Linux: < 180MB

ls -lh dist/
```

### 3. 依存関係確認

```bash
# Windows
dumpbin /dependents VideoThumbnailExtractor.exe

# macOS
otool -L VideoThumbnailExtractor

# Linux
ldd VideoThumbnailExtractor
```

### 4. ウイルススキャン

```bash
# Windows Defender
MpCmdRun.exe -Scan -ScanType 3 -File dist/VideoThumbnailExtractor.exe

# VirusTotal API（オプション）
curl -X POST 'https://www.virustotal.com/vtapi/v2/file/scan' \
     -F 'key=YOUR_API_KEY' \
     -F 'file=@dist/VideoThumbnailExtractor.exe'
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. ImportError: No module named 'cv2'

**解決方法:**
```bash
# hidden-import オプション追加
pyinstaller --hidden-import cv2 --onefile run_app.py

# または specファイルに追加
hiddenimports=['cv2', 'cv2.data']
```

#### 2. tkinter関連エラー

**解決方法:**
```bash
# tkinter明示的インクルード
pyinstaller --hidden-import tkinter.filedialog --onefile run_app.py
```

#### 3. MediaPipeモデルファイル不足

**解決方法:**
```bash
# データファイル追加
pyinstaller --add-data "site-packages/mediapipe/modules:mediapipe/modules" --onefile run_app.py
```

#### 4. ファイルサイズが大きすぎる

**解決方法:**
```bash
# 不要モジュール除外
pyinstaller --exclude-module matplotlib --exclude-module scipy --onefile run_app.py

# UPX圧縮使用
pyinstaller --upx-dir /path/to/upx --onefile run_app.py
```

#### 5. 起動が遅い

**解決方法:**
```bash
# フォルダ形式で配布
pyinstaller --onedir --windowed run_app.py

# または起動画面追加
pyinstaller --splash splash.png --onefile run_app.py
```

### デバッグ方法

```bash
# 1. デバッグモードでビルド
pyinstaller --debug=all --onefile run_app.py

# 2. コンソール付きで実行（Windows）
pyinstaller --onefile run_app.py  # --windowed を除く

# 3. 詳細ログ出力
./dist/VideoThumbnailExtractor 2>&1 | tee debug.log
```

## 📋 配布チェックリスト

配布前の最終確認項目：

- [ ] 全プラットフォームでビルド成功
- [ ] 基本動作テスト完了
- [ ] ファイルサイズが目標値以内
- [ ] ウイルススキャン実行
- [ ] ライセンス情報確認
- [ ] README.md更新
- [ ] リリースノート作成
- [ ] バージョンタグ作成
- [ ] 配布サイトアップロード

---

**最終更新**: 2025年9月5日  
**対応PyInstallerバージョン**: 5.13+
