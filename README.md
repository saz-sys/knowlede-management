# 動画サムネイル抽出アプリケーション

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

AI顔検出技術を活用した動画サムネイル自動抽出デスクトップアプリケーション。MP4動画から多様で高品質なサムネイル画像を自動生成します。

## 🌟 主な機能

- **AI顔検出**: MediaPipeを使用した高精度な顔検出
- **多様性抽出**: 類似度分析による多様なシーン選択
- **直感的GUI**: tkinterベースの使いやすいインターフェース
- **非同期処理**: UIブロッキングなしの快適な操作
- **完全ローカル**: インターネット接続不要でプライバシー保護
- **設定可能**: サムネイル枚数・サイズの自由調整

## 📸 スクリーンショット

```
┌─────────────────────────────────────┐
│ 動画サムネイル抽出                     │
├─────────────────────────────────────┤
│ 📁 動画ファイルを選択                  │
│ ⚙️  設定                              │
├─────────────────────────────────────┤
│ ▓▓▓▓▓▓▓▓▓▓ 80% 処理中...             │
├─────────────────────────────────────┤
│ [🖼️] [🖼️] [🖼️] [🖼️] [🖼️]           │
│ [🖼️] [🖼️] [🖼️] [🖼️] [🖼️]           │
└─────────────────────────────────────┘
```

## 🚀 クイックスタート

### 前提条件

- **Python 3.11以降**
- **macOS 10.15以降** / **Windows 10以降**
- **RAM 4GB以上推奨**
- **ストレージ 500MB以上**

### インストール

```bash
# 1. リポジトリをクローン
git clone [リポジトリURL]
cd extract_thumbnail_from_video

# 2. 仮想環境作成・アクティベート
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows

# 3. 依存関係インストール
pip install -r requirements.txt
```

### 基本的な使用方法

```bash
# GUIアプリケーション起動
python run_app.py

# コンポーネントテスト実行
python run_app.py --test

# ヘルプ表示
python run_app.py --help
```

## 🎯 使用手順

1. **アプリケーション起動**
   ```bash
   python run_app.py
   ```

2. **動画ファイル選択**
   - 「動画ファイルを選択」ボタンをクリック
   - MP4ファイルを選択

3. **設定調整**（オプション）
   - サムネイル枚数: 1-20枚（デフォルト: 5枚）
   - 出力サイズ: 240x240 - 4096x4096（デフォルト: 1920x1080）

4. **サムネイル生成**
   - 「サムネイル抽出開始」ボタンをクリック
   - 処理進捗をリアルタイム表示

5. **結果確認・保存**
   - 生成されたサムネイルを一覧表示
   - 必要なサムネイルを選択して保存

## ⚙️ 設定オプション

### サムネイル設定

| 項目 | デフォルト | 範囲 | 説明 |
|------|------------|------|------|
| 枚数 | 5枚 | 1-20枚 | 生成するサムネイル数 |
| 幅 | 1920px | 240-4096px | 出力画像の幅 |
| 高さ | 1080px | 240-4096px | 出力画像の高さ |

### 顔検出設定

| 項目 | デフォルト | 説明 |
|------|------------|------|
| 信頼度閾値 | 0.5 | 顔検出の信頼度（0.0-1.0） |
| 最小顔サイズ | 0.01 | 画像サイズに対する最小顔比率 |

## 🔧 トラブルシューティング

### よくある問題

**Q: アプリケーションが起動しない**
```bash
# 依存関係の再インストール
pip install --upgrade -r requirements.txt

# コンポーネントテスト実行
python run_app.py --test
```

**Q: 「No module named 'cv2'」エラー**
```bash
# OpenCVの再インストール
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

**Q: 顔が検出されない**
- 人物が明確に映っている動画を使用
- 顔検出信頼度設定を下げる（0.3程度）
- 動画の解像度・品質を確認

**Q: 処理が遅い**
- 動画ファイルサイズを確認（推奨: 100MB以下）
- 出力サイズを下げる（720p等）
- 他のアプリケーションを終了してメモリを確保

### ログファイル確認

```bash
# ログファイル場所
# macOS: ~/.config/video_thumbnail_extractor/
# Windows: %APPDATA%\video_thumbnail_extractor\
```

## 📋 システム要件

### 最小要件
- Python 3.11+
- RAM 4GB
- ストレージ 500MB
- tkinter（通常Pythonに含まれる）

### 推奨要件
- Python 3.11+
- RAM 8GB以上
- ストレージ 1GB以上
- GPU対応（処理高速化）

### サポートフォーマット
- **入力**: MP4動画ファイル
- **出力**: PNG画像ファイル

## 🚚 配布用実行ファイル作成

### PyInstallerを使用

```bash
# 1. PyInstallerインストール
pip install pyinstaller

# 2. 単一実行ファイル作成
pyinstaller --onefile --windowed run_app.py

# 3. 生成された実行ファイル
# Windows: dist/run_app.exe
# macOS: dist/run_app
```

### 詳細な配布手順

詳しくは [DISTRIBUTION.md](DISTRIBUTION.md) をご覧ください。

## 🔬 開発者情報

### アーキテクチャ

```
src/
├── models/          # データモデル
├── services/        # ビジネスロジック
├── gui/            # ユーザーインターフェース
├── lib/            # 共通ユーティリティ
└── main.py         # アプリケーションエントリーポイント
```

### 技術スタック

- **GUI**: tkinter
- **動画処理**: OpenCV
- **顔検出**: MediaPipe
- **画像処理**: Pillow
- **機械学習**: scikit-learn
- **数値計算**: NumPy

## 🧪 テスト

```bash
# 全テスト実行
pytest

# カバレッジレポート生成
pytest --cov=src --cov-report=html

# コンポーネントテスト
python run_app.py --test
```

## 📚 ドキュメント

- [開発者ガイド](DEVELOPMENT.md) - 技術仕様・開発環境
- [配布ガイド](DISTRIBUTION.md) - 配布方法・ビルド手順
- [ユーザーガイド](USER_GUIDE.md) - 詳細な操作説明

## 🤝 コントリビューション

1. フォークしてフィーチャーブランチを作成
2. 変更をコミット
3. テストを実行して通過確認
4. プルリクエストを作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🙏 謝辞

- **MediaPipe** - 高精度な顔検出ライブラリ
- **OpenCV** - 強力な動画・画像処理ライブラリ
- **tkinter** - Python標準GUIライブラリ

## 📞 サポート

問題が発生した場合：

1. [Issues](../../issues) で既存の問題を確認
2. 新しいIssueを作成
3. ログファイルとエラーメッセージを添付

---

**バージョン**: 1.0.0  
**最終更新**: 2025年9月5日  
**作者**: s-anzai
