-- いいね数ランキングを取得する関数
CREATE OR REPLACE FUNCTION get_like_rankings(
  period_filter TEXT DEFAULT '',
  limit_count INTEGER DEFAULT 20,
  offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
  post_id UUID,
  title TEXT,
  author_name TEXT,
  author_email TEXT,
  like_count BIGINT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id as post_id,
    p.title,
    COALESCE(pr.name, pr.email, 'ユーザー' || substring(p.author_id::text, 1, 8)) as author_name,
    pr.email as author_email,
    COALESCE(like_counts.like_count, 0) as like_count,
    p.created_at
  FROM public.posts p
  LEFT JOIN public.profiles pr ON p.author_id = pr.id
  LEFT JOIN (
    SELECT 
      pl.post_id,
      COUNT(*) as like_count
    FROM public.post_likes pl
    GROUP BY pl.post_id
  ) like_counts ON p.id = like_counts.post_id
  WHERE p.is_public = true
    AND (period_filter = '' OR period_filter IS NULL OR 
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 day' AND period_filter LIKE '%1 day%') OR
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 week' AND period_filter LIKE '%1 week%') OR
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 month' AND period_filter LIKE '%1 month%'))
  ORDER BY like_count DESC, p.created_at DESC
  LIMIT limit_count
  OFFSET offset_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- いいね数ランキングの総件数を取得する関数
CREATE OR REPLACE FUNCTION get_like_rankings_count(
  period_filter TEXT DEFAULT ''
)
RETURNS TABLE (
  total BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT COUNT(*) as total
  FROM public.posts p
  WHERE p.is_public = true
    AND (period_filter = '' OR period_filter IS NULL OR 
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 day' AND period_filter LIKE '%1 day%') OR
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 week' AND period_filter LIKE '%1 week%') OR
         (period_filter LIKE '%created_at%' AND 
          p.created_at >= NOW() - INTERVAL '1 month' AND period_filter LIKE '%1 month%'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
