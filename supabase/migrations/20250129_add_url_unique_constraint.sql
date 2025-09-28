-- postsテーブルにURLユニーク制約を追加
-- 既存の重複データを確認
DO $$
DECLARE
    duplicate_count INTEGER;
    rec RECORD;
BEGIN
    -- 重複URLの数を確認
    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT url, COUNT(*) as count
        FROM posts
        WHERE url IS NOT NULL AND url != ''
        GROUP BY url
        HAVING COUNT(*) > 1
    ) duplicates;
    
    -- 重複がある場合は警告
    IF duplicate_count > 0 THEN
        RAISE NOTICE 'Found % duplicate URLs. Please resolve duplicates before adding unique constraint.', duplicate_count;
        -- 重複データの詳細を表示
        FOR rec IN (
            SELECT url, COUNT(*) as count, array_agg(id) as post_ids
            FROM posts
            WHERE url IS NOT NULL AND url != ''
            GROUP BY url
            HAVING COUNT(*) > 1
        ) LOOP
            RAISE NOTICE 'URL: %, Count: %, Post IDs: %', rec.url, rec.count, rec.post_ids;
        END LOOP;
    END IF;
END $$;

-- まず、NULLと空文字列のURLをNULLに統一
UPDATE posts 
SET url = NULL 
WHERE url IS NULL OR url = '';

-- URLユニーク制約を追加
ALTER TABLE posts 
ADD CONSTRAINT posts_url_unique UNIQUE (url);
