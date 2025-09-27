# engineering-knowledge-sharing 設計書

## 1. 概要
PdEエンジニア向けナレッジ共有Webサービスの技術設計。ミニマムかつ無料枠を優先し、Next.js（Vercel Hobbyプラン）とSupabase Free Tierを基盤として、コメント付き投稿、ディスカッション、RSS取り込み、Slack通知を実現する。

## 2. コンテキスト
- 利用ステークホルダー: PdEエンジニア、PdEマネージャー/EM、PdEナレッジマネジメント担当
- 既存システムとの関係: Google WorkspaceによるSSO、Slackワークスペース連携
- 技術的制約: 招待制＋ドメイン制限で社内エンジニアのみアクセス可。VPN不要、ゼロトラスト前提。

## 3. 要件対応表
| 要件ID | 設計要素 | 実装概要 |
|--------|----------|----------|
| REQ-001 | コメント付き投稿作成 | Next.js App Router + Supabase Auth、Rich Textエディタ、Slack通知設定モーダル |
| REQ-002 | ディスカッションとナレッジ蓄積 | Supabase RLS付きコメントテーブル、階層コメントUI、ナレッジカード生成機能 |
| REQ-003 | RSS取り込み | Supabase Edge Functions + Scheduler、RSS解析、承認キュー |
| REQ-004 | Slack通知 | Slack Incoming Webhook/ボット、週次ダイジェスト生成Edge Function |
| REQ-005 | ナレッジ検索 | Supabase Postgres Full Text Search、タグ・期間フィルタUI |

## 4. システムアーキテクチャ
- フロントエンド: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- ホスティング: Vercel Hobbyプラン（無料）
- 認証/バックエンド: Supabase (Postgres, Auth, Edge Functions, Storage)
- 通知: Slack Web API / Incoming Webhook
- ビルド/インフラ: GitHub → Vercelデプロイ連携

```
利用者 -> (ブラウザ) -> Vercel上のNext.js -> Supabase Auth/DB
                               |-> Slack API
                               |-> Supabase Edge Functions (RSS/ダイジェスト)
```

### 設計方針
- App RouterでAPI Routesを最小限利用、重い処理はEdge Functionsへ委任
- Supabase Authの`allowed_email_domains`で社内ドメイン制限、招待制でさらに限定
- Row Level Security (RLS) を用いたユーザー毎のアクセス制御
- 無料枠内で収まるようCronは15分〜1時間間隔に調整

## 5. ドメインモデル
- User: Supabase Authユーザー情報（role: engineer, manager, moderator）
- Post: 記事リンク、本文コメント、タグ、Slack通知設定
- Comment: Postとのリレーション、階層構造、メンション
- KnowledgeCard: 議論要約、参照投稿、作成者
- Tag: タグ名、説明、利用回数
- RSSFeed: フィード設定、タグプリセット、最終取得日時
- RSSItem: 取得済み記事、承認ステータス、提案タグ
- SlackNotificationSetting: 通知チャンネル、サプレッション設定

## 6. ユースケース / フロー
### 投稿作成フロー
1. ユーザーがSSOでログイン（Supabase Auth）
2. 投稿ページでURL/コメント/タグを入力
3. Supabase APIで投稿を保存、サマリー生成（Edge Function or 前段ライブラリ）
4. Slack通知設定モーダルでチャンネルを選択
5. Slack Webhookに通知送信

### RSS承認フロー
1. ナレッジ担当がRSSフィードを登録
2. Supabase Scheduler → Edge Functionが定期実行
3. 新着記事を解析し、サマリー・タグ候補生成
4. `rss_items`テーブルの`status = pending`として保存
5. 管理UIで承認→`posts`に変換し公開

### 週次ダイジェストフロー
1. Schedulerが週1でEdge Functionを起動
2. 直近投稿を集計し、ランキングと未読数を生成
3. Slack Webhookにまとめを送信

## 7. UI/UX ラフ案
- ダッシュボード: 投稿一覧カード、タグフィルタ、未読バッジ
- 投稿詳細: 記事プレビュー、コメントツリー、関連タグ
- 投稿作成: リッチエディタ（Blocknote等）、タグピッカー、Slack通知設定
- 管理画面: RSS承認キュー、タグ管理、Slack設定

## 8. データ設計
### テーブル概要
- `profiles`: Supabase Authの拡張（role, team, invited_at）
- `posts`: 投稿本体（title, url, content, author_id, notified_channels）
- `post_tags`: 投稿とタグの多対多
- `comments`: 階層コメント（parent_id）
- `knowledge_cards`: 要約カード（post_id, summary, created_by）
- `rss_feeds`: RSS設定（name, url, tags, is_active, last_fetched_at）
- `rss_items`: 取得記事（feed_id, title, summary, status）
- `slack_channels`: 利用可能な通知先（name, webhook_url, suppressed_hours）

Row Level Securityポリシー例:
```sql
create policy "profiles can view own" on profiles
  for select using (auth.uid() = id);

create policy "posts readable by authenticated" on posts
  for select using (auth.role() = 'authenticated');
```

## 9. インテグレーション/外部サービス
- Supabase Auth: Google Workspace OAuth、ドメイン制限、メール招待
- Supabase Storage: 画像等の添付（無料枠1GB）
- Supabase Edge Functions: RSS取得、サマリー生成、Slackダイジェスト
- Slack: Incoming Webhookで通知、必要に応じてBot Tokenでリッチメッセージ
- Vercel: GitHub連携によるCI/CD、環境変数でAPIキー管理

## 10. セキュリティ・運用
- SSO必須、MFAはWorkspaceポリシーで強制
- 招待メール送付後に初回ログインを許可
- Supabase RLSでロールベースアクセス制御
- HTTPS (Vercel / Supabase標準)
- Edge Functionの失敗時はSlack #infra にエラーログ送信
- バックアップ: Supabaseの自動バックアップ（7日） + 必要に応じて`pg_dump`

## 11. 非機能要件対応
- パフォーマンス: ISR/SSGで初期表示を高速化、Full Text Searchで検索1秒以内
- 可用性: 無料枠内のSLA。重大障害時は復旧手順をNotionで共有
- スケーラビリティ: アクセス増加時はSupabase有償プラン/Vercel Pro移行を検討
- コスト管理: 無料枠モニタリング、上限逼迫時に通知

## 12. テスト戦略
- 単体テスト: Next.jsコンポーネント（Vitest/Testing Library）、Supabase RPC
- 統合テスト: 投稿→コメント→通知の一連のフロー（Playwright）
- Edge Functionテスト: RSS取得・Slack送信をモックで検証
- スモークテスト: デプロイ後に主要画面表示と通知APIをチェック

## 13. オープンな課題
- Supabase Auth招待フローのUX改善（リマインドメール）
- 無料枠での監視強化（サードパーティモニタリング検討）
- 将来的な全文検索強化（有償Elastic導入タイミング）
- モバイルファーストのUI最適化範囲
