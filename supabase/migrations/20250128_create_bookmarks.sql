-- ブックマークテーブルの作成
CREATE TABLE IF NOT EXISTS bookmarks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  reminder_at TIMESTAMP WITH TIME ZONE,
  is_read BOOLEAN DEFAULT FALSE,
  notes TEXT,
  UNIQUE(user_id, post_id)
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS bookmarks_user_id_idx ON bookmarks(user_id);
CREATE INDEX IF NOT EXISTS bookmarks_post_id_idx ON bookmarks(post_id);
CREATE INDEX IF NOT EXISTS bookmarks_reminder_at_idx ON bookmarks(reminder_at) WHERE reminder_at IS NOT NULL;

-- RLS（Row Level Security）の有効化
ALTER TABLE bookmarks ENABLE ROW LEVEL SECURITY;

-- RLSポリシーの作成
CREATE POLICY "Users can view their own bookmarks" ON bookmarks
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own bookmarks" ON bookmarks
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own bookmarks" ON bookmarks
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own bookmarks" ON bookmarks
  FOR DELETE USING (auth.uid() = user_id);

-- ブックマーク統計用のビュー
CREATE OR REPLACE VIEW bookmark_stats AS
SELECT 
  user_id,
  COUNT(*) as total_bookmarks,
  COUNT(*) FILTER (WHERE is_read = FALSE) as unread_bookmarks,
  COUNT(*) FILTER (WHERE reminder_at IS NOT NULL AND reminder_at <= NOW()) as overdue_reminders
FROM bookmarks
GROUP BY user_id;
