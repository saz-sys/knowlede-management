-- コメント数ランキングを取得する関数
CREATE OR REPLACE FUNCTION get_comment_rankings(
  period_filter TEXT DEFAULT '',
  limit_count INTEGER DEFAULT 20,
  offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
  post_id UUID,
  title TEXT,
  url TEXT,
  author_email TEXT,
  author_name TEXT,
  created_at TIMESTAMPTZ,
  comment_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id as post_id,
    p.title,
    p.url,
    p.author_email,
    COALESCE(prof.name, split_part(p.author_email, '@', 1)) as author_name,
    p.created_at,
    COUNT(c.id) as comment_count
  FROM posts p
  LEFT JOIN comments c ON p.id = c.post_id
  LEFT JOIN profiles prof ON p.author_id = prof.id
  WHERE 1=1
    AND (period_filter = '' OR period_filter IS NULL OR 
         (period_filter != '' AND p.created_at >= 
          CASE 
            WHEN period_filter LIKE '%1 day%' THEN NOW() - INTERVAL '1 day'
            WHEN period_filter LIKE '%1 week%' THEN NOW() - INTERVAL '1 week'
            WHEN period_filter LIKE '%1 month%' THEN NOW() - INTERVAL '1 month'
            ELSE p.created_at
          END))
  GROUP BY p.id, p.title, p.url, p.author_email, prof.name, p.created_at
  HAVING COUNT(c.id) > 0
  ORDER BY comment_count DESC, p.created_at DESC
  LIMIT limit_count
  OFFSET offset_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- コメント数ランキングの総件数を取得する関数
CREATE OR REPLACE FUNCTION get_comment_rankings_count(
  period_filter TEXT DEFAULT ''
)
RETURNS TABLE (total BIGINT) AS $$
BEGIN
  RETURN QUERY
  SELECT COUNT(*) as total
  FROM (
    SELECT p.id
    FROM posts p
    LEFT JOIN comments c ON p.id = c.post_id
    WHERE 1=1
      AND (period_filter = '' OR period_filter IS NULL OR 
           (period_filter != '' AND p.created_at >= 
            CASE 
              WHEN period_filter LIKE '%1 day%' THEN NOW() - INTERVAL '1 day'
              WHEN period_filter LIKE '%1 week%' THEN NOW() - INTERVAL '1 week'
              WHEN period_filter LIKE '%1 month%' THEN NOW() - INTERVAL '1 month'
              ELSE p.created_at
            END))
    GROUP BY p.id
    HAVING COUNT(c.id) > 0
  ) ranked_posts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
