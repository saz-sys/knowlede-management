# タスク: 動画サムネイル抽出機能

**入力**: `/specs/001-feature-name-description/` からの設計ドキュメント
**前提条件**: plan.md (必須), research.md, data-model.md, contracts/

## 実行フロー (メイン)
```
1. 機能ディレクトリからplan.mdを読み込み
   → 見つからない場合: ERROR "実装計画が見つかりません"
   → 抽出: 技術スタック、ライブラリ、構造
2. オプションの設計ドキュメントを読み込み:
   → data-model.md: エンティティ抽出 → モデルタスク
   → contracts/: 各ファイル → 契約テストタスク
   → research.md: 決定抽出 → セットアップタスク
3. カテゴリ別にタスクを生成:
   → セットアップ: プロジェクト初期化、依存関係、リンティング
   → テスト: 契約テスト、統合テスト
   → コア: モデル、サービス、CLIコマンド
   → 統合: DB、ミドルウェア、ログ
   → 仕上げ: ユニットテスト、パフォーマンス、ドキュメント
4. タスクルールを適用:
   → 異なるファイル = 並列用[P]マーク
   → 同じファイル = 順次（[P]なし）
   → 実装前にテスト（TDD）
5. タスクを順次番号付け（T001、T002...）
6. 依存関係グラフを生成
7. 並列実行例を生成
8. タスク完全性を検証:
   → すべての契約にテストがあるか？
   → すべてのエンティティにモデルがあるか？
   → すべてのエンドポイントが実装されているか？
9. 戻り値: SUCCESS (タスク実行準備完了)
```

## フォーマット: `[ID] [P?] 説明`
- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- 説明に正確なファイルパスを含める

## パス規約
- **単一プロジェクト**: リポジトリルートの `src/`、`tests/`
- Python デスクトップアプリケーション構成を使用

## フェーズ 3.1: セットアップ
- [x] T001 実装計画に従ってプロジェクト構造を作成 (src/, tests/, requirements.txt, setup.py)
- [x] T002 Python 3.11+ とtkinter、OpenCV、MediaPipe依存関係でプロジェクトを初期化
- [x] T003 [P] リンティング（black、flake8）とフォーマットツールを設定
- [x] T004 [P] pytest設定とテスト環境構築
- [x] T005 [P] src/lib/logger.py でログ設定（JSON形式、ファイル出力）

## フェーズ 3.2: テストファースト（TDD）⚠️ 3.3より前に完了必須
**重要: これらのテストは実装前に書かれ、失敗しなければならない**

### 契約テスト [P]
- [ ] T006 [P] tests/contract/test_video_processor_contract.py でVideoProcessor契約テスト
- [ ] T007 [P] tests/contract/test_face_detector_contract.py でFaceDetector契約テスト  
- [ ] T008 [P] tests/contract/test_thumbnail_extractor_contract.py でThumbnailExtractor契約テスト
- [ ] T009 [P] tests/contract/test_gui_interface_contract.py でGUIインターフェース契約テスト

### 統合テスト [P]
- [ ] T010 [P] tests/integration/test_video_processing_pipeline.py で動画読み込み→フレーム抽出の統合テスト
- [ ] T011 [P] tests/integration/test_face_detection_integration.py でフレーム→顔検出の統合テスト
- [ ] T012 [P] tests/integration/test_thumbnail_extraction_e2e.py で全体フロー（動画→サムネイル）のE2Eテスト
- [ ] T013 [P] tests/integration/test_cli_workflow.py でCLIコマンドの統合テスト
- [ ] T014 [P] tests/integration/test_gui_workflow.py でGUIアプリケーションの統合テスト

## フェーズ 3.3: データモデル実装（テストが失敗している場合のみ）

### 基本モデル [P]
- [ ] T015 [P] src/models/__init__.py でモデルパッケージ初期化
- [ ] T016 [P] src/models/point_2d.py でPoint2Dクラス（座標計算メソッド含む）
- [ ] T017 [P] src/models/bounding_box.py でBoundingBoxクラス（ピクセル座標変換含む）
- [ ] T018 [P] src/models/face_detection_result.py でFaceDetectionResultクラス
- [ ] T019 [P] src/models/video_file.py でVideoFileクラス（バリデーション、状態遷移含む）
- [ ] T020 [P] src/models/frame.py でFrameクラス（計算プロパティ含む）
- [ ] T021 [P] src/models/user_settings.py でUserSettingsクラス（列挙型含む）
- [ ] T022 [P] src/models/thumbnail.py でThumbnailクラス
- [ ] T023 [P] src/models/thumbnail_extraction_job.py でThumbnailExtractionJobクラス

## フェーズ 3.4: コアサービス実装

### 動画処理サービス
- [ ] T024 src/services/__init__.py でサービスパッケージ初期化
- [ ] T025 src/services/video_processor.py でVideoProcessor実装（OpenCV、フレーム抽出、シーンチェンジ検出）
- [ ] T026 src/services/face_detector.py でFaceDetector実装（MediaPipe、バッチ処理、設定調整）
- [ ] T027 src/services/diversity_selector.py でDiversitySelector実装（ORB特徴量、K-means、多様性スコア）
- [ ] T028 src/services/thumbnail_extractor.py でThumbnailExtractor実装（リサイズ、切り抜き、PNG保存）

### ユーティリティライブラリ
- [ ] T029 [P] src/lib/__init__.py でライブラリパッケージ初期化  
- [ ] T030 [P] src/lib/config.py で設定管理（ファイル読み書き、デフォルト値）
- [ ] T031 [P] src/lib/errors.py でカスタム例外クラス定義

## フェーズ 3.5: CLI実装
- [ ] T032 src/cli/__init__.py でCLIパッケージ初期化
- [ ] T033 src/cli/main.py でCLIエントリーポイント（argparse、extract、--helpコマンド）

## フェーズ 3.6: GUI実装

### GUI基盤
- [ ] T034 src/gui/__init__.py でGUIパッケージ初期化
- [ ] T035 src/gui/main_window.py でメインウィンドウ実装（tkinter、ファイル選択、進捗表示）
- [ ] T036 src/gui/settings_dialog.py で設定ダイアログ実装（サイズ・枚数入力、バリデーション）
- [ ] T037 src/gui/thumbnail_grid.py でサムネイル表示グリッド実装（PIL表示、選択機能）

### 非同期処理
- [ ] T038 src/gui/async_worker.py で非同期ワーカー実装（threading、進捗コールバック）

## フェーズ 3.7: 統合・最適化
- [ ] T039 サービス層をCLIに統合（エラーハンドリング、進捗表示）
- [ ] T040 サービス層をGUIに統合（非同期処理、リアルタイム更新）
- [ ] T041 パフォーマンス最適化（メモリ管理、並列処理、ガベージコレクション調整）
- [ ] T042 エラーハンドリング強化（ユーザーフレンドリーメッセージ、ログ出力）

## フェーズ 3.8: 仕上げ

### ユニットテスト [P]  
- [ ] T043 [P] tests/unit/test_video_processor.py でVideoProcessorのユニットテスト
- [ ] T044 [P] tests/unit/test_face_detector.py でFaceDetectorのユニットテスト
- [ ] T045 [P] tests/unit/test_thumbnail_extractor.py でThumbnailExtractorのユニットテスト
- [ ] T046 [P] tests/unit/test_diversity_selector.py でDiversitySelectorのユニットテスト
- [ ] T047 [P] tests/unit/test_models.py で全データモデルのユニットテスト
- [ ] T048 [P] tests/unit/test_cli.py でCLIコマンドのユニットテスト

### パフォーマンス・品質テスト
- [ ] T049 tests/performance/test_processing_speed.py でパフォーマンステスト（10分動画30秒以内処理）
- [ ] T050 tests/performance/test_memory_usage.py でメモリ使用量テスト（2GB以内）
- [ ] T051 テストサンプル動画作成（30秒短尺、5分長尺、エッジケース動画）

### ドキュメント・配布準備 [P]
- [ ] T052 [P] llms.txt でAI開発者向けドキュメント作成
- [ ] T053 [P] README.md でユーザー向けドキュメント作成  
- [ ] T054 [P] requirements.txt で依存関係バージョン固定
- [ ] T055 [P] setup.py でパッケージング設定
- [ ] T056 [P] .gitignore で適切なファイル除外設定

### 検証・クリーンアップ
- [ ] T057 quickstart.md の手順実行とテストシナリオ検証
- [ ] T058 重複コード削除、コード品質向上
- [ ] T059 全テスト実行、カバレッジ確認
- [ ] T060 デバッグログ削除、本番用設定

## 依存関係

### 厳密な順序要件
- **セットアップ前提**: T001-T005 → 他のすべて
- **TDD前提**: T006-T014 → T015以降
- **モデル前提**: T015-T023 → T024以降  
- **サービス前提**: T024-T031 → T032以降
- **統合前提**: T032-T038 → T039-T042
- **実装前提**: T039-T042 → T043以降

### 並列実行可能グループ
1. **契約テスト**: T006-T009（異なるファイル）
2. **統合テスト**: T010-T014（異なるファイル）  
3. **基本モデル**: T015-T023（異なるファイル）
4. **ユーティリティ**: T029-T031（異なるファイル）
5. **ユニットテスト**: T043-T048（異なるファイル）
6. **ドキュメント**: T052-T056（異なるファイル）

## 並列実行例

### 契約テスト並列実行
```bash
# T006-T009を同時実行:
Task: "tests/contract/test_video_processor_contract.py でVideoProcessor契約テスト"
Task: "tests/contract/test_face_detector_contract.py でFaceDetector契約テスト"  
Task: "tests/contract/test_thumbnail_extractor_contract.py でThumbnailExtractor契約テスト"
Task: "tests/contract/test_gui_interface_contract.py でGUIインターフェース契約テスト"
```

### モデル実装並列実行
```bash
# T015-T023を同時実行:
Task: "src/models/point_2d.py でPoint2Dクラス（座標計算メソッド含む）"
Task: "src/models/bounding_box.py でBoundingBoxクラス（ピクセル座標変換含む）"
Task: "src/models/face_detection_result.py でFaceDetectionResultクラス"
Task: "src/models/video_file.py でVideoFileクラス（バリデーション、状態遷移含む）"
# ... 他のモデルクラス
```

### ユニットテスト並列実行
```bash  
# T043-T048を同時実行:
Task: "tests/unit/test_video_processor.py でVideoProcessorのユニットテスト"
Task: "tests/unit/test_face_detector.py でFaceDetectorのユニットテスト"
Task: "tests/unit/test_thumbnail_extractor.py でThumbnailExtractorのユニットテスト"
Task: "tests/unit/test_diversity_selector.py でDiversitySelectorのユニットテスト"
Task: "tests/unit/test_models.py で全データモデルのユニットテスト"
Task: "tests/unit/test_cli.py でCLIコマンドのユニットテスト"
```

## 注意事項
- **[P]タスク**: 異なるファイルで依存関係なし、並列実行可能
- **TDD遵守**: 実装前にテストが失敗することを確認必須  
- **コミット**: 各タスク完了後に必ずコミット
- **避けるべきこと**: 曖昧なタスク、同じファイルでの競合

## タスク生成ルール
*main()実行中に適用された*

1. **契約から**:
   - 4つの契約ファイル → 4つの契約テストタスク [P]
   - 各契約メソッド → 対応するサービス実装タスク

2. **データモデルから**:
   - 8つのエンティティ → 8つのモデル作成タスク [P]  
   - データ関係 → サービス層統合タスク

3. **ユーザーストーリーから**:
   - quickstart.mdの5つのストーリー → 5つの統合テスト [P]
   - テストシナリオ → 検証タスク

4. **技術決定から（research.md）**:
   - MediaPipe設定 → FaceDetector実装詳細
   - OpenCV最適化 → VideoProcessor実装詳細
   - tkinter設計 → GUI実装詳細

## 検証チェックリスト
*GATE: 戻る前にmain()でチェックされた*

- [x] すべての契約に対応するテストがある（T006-T009）
- [x] すべてのエンティティにモデルタスクがある（T015-T023）
- [x] すべてのテストが実装前にある（T006-T014がT015より前）
- [x] 並列タスクが真に独立している（[P]マークは異なるファイル）
- [x] 各タスクが正確なファイルパスを指定している
- [x] 他の[P]タスクと同じファイルを変更するタスクがない

## 成功基準
全60タスク完了時点で以下が達成される：
- 完全にローカル動作するデスクトップアプリケーション
- MP4動画からキャラクター顔検出による多様なサムネイル抽出
- GUIとCLI両方のインターフェース
- 高品質なテストカバレッジ（契約、統合、ユニット）
- 10分動画を30秒以内で処理するパフォーマンス
- ユーザーフレンドリーなエラーハンドリング
- 完全なドキュメント（ユーザー、開発者向け）
