-- Ensure posts, comments, and knowledge_cards reference auth.users for PostgREST relationships
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'posts_author_id_fkey'
      AND conrelid = 'public.posts'::regclass
  ) THEN
    ALTER TABLE public.posts
      ADD CONSTRAINT posts_author_id_fkey
      FOREIGN KEY (author_id)
      REFERENCES auth.users (id)
      ON DELETE CASCADE;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'comments_author_id_fkey'
      AND conrelid = 'public.comments'::regclass
  ) THEN
    ALTER TABLE public.comments
      ADD CONSTRAINT comments_author_id_fkey
      FOREIGN KEY (author_id)
      REFERENCES auth.users (id)
      ON DELETE CASCADE;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'knowledge_cards_created_by_fkey'
      AND conrelid = 'public.knowledge_cards'::regclass
  ) THEN
    ALTER TABLE public.knowledge_cards
      ADD CONSTRAINT knowledge_cards_created_by_fkey
      FOREIGN KEY (created_by)
      REFERENCES auth.users (id)
      ON DELETE CASCADE;
  END IF;
END
$$;

-- Align knowledge_cards schema with application expectations
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'knowledge_cards'
      AND column_name = 'summary'
  ) THEN
    ALTER TABLE public.knowledge_cards
      RENAME COLUMN summary TO content;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'knowledge_cards'
      AND column_name = 'title'
  ) THEN
    ALTER TABLE public.knowledge_cards
      ADD COLUMN title text;
  END IF;
END
$$;

UPDATE public.knowledge_cards
   SET title = 'Untitled Card'
 WHERE (title IS NULL OR title = '');

ALTER TABLE public.knowledge_cards
  ALTER COLUMN title SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'knowledge_cards'
      AND column_name = 'related_comment_ids'
  ) THEN
    ALTER TABLE public.knowledge_cards
      ADD COLUMN related_comment_ids uuid[] DEFAULT '{}'::uuid[];
  END IF;
END
$$;

-- migration revision timestamp 20250927-02

