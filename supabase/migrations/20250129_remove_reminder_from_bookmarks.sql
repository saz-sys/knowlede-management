-- ブックマーク統計ビューを先に削除
DROP VIEW IF EXISTS bookmark_stats;

-- リマインド関連のインデックスを削除
DROP INDEX IF EXISTS bookmarks_reminder_at_idx;

-- ブックマークテーブルからリマインド関連カラムを削除
ALTER TABLE bookmarks DROP COLUMN IF EXISTS reminder_at;

-- ブックマーク統計ビューを再作成
CREATE OR REPLACE VIEW bookmark_stats AS
SELECT 
  user_id,
  COUNT(*) as total_bookmarks,
  COUNT(*) FILTER (WHERE is_read = FALSE) as unread_bookmarks
FROM bookmarks
GROUP BY user_id;
