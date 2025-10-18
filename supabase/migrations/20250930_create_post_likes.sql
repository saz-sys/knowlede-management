-- 投稿いいねテーブルを作成
CREATE TABLE IF NOT EXISTS public.post_likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID NOT NULL REFERENCES public.posts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(post_id, user_id)
);

-- RLSを有効化
ALTER TABLE public.post_likes ENABLE ROW LEVEL SECURITY;

-- ポリシーを作成
CREATE POLICY "Users can view all post likes" ON public.post_likes
  FOR SELECT USING (true);

CREATE POLICY "Users can insert their own post likes" ON public.post_likes
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own post likes" ON public.post_likes
  FOR DELETE USING (auth.uid() = user_id);

-- インデックスを作成
CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON public.post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON public.post_likes(user_id);
