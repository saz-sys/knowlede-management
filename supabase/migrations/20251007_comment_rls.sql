-- Update comment RLS policies to allow authenticated users to create and manage their own comments

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'comments'
      AND policyname = 'Allow comment owners to manage'
  ) THEN
    DROP POLICY "Allow comment owners to manage" ON public.comments;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'comments'
      AND policyname = 'Allow authenticated to insert comments'
  ) THEN
    CREATE POLICY "Allow authenticated to insert comments"
      ON public.comments
      FOR INSERT
      WITH CHECK (
        auth.uid() = author_id
        AND auth.role() = 'authenticated'
      );
  ELSE
    ALTER POLICY "Allow authenticated to insert comments"
      ON public.comments
      WITH CHECK (
        auth.uid() = author_id
        AND auth.role() = 'authenticated'
      );
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'comments'
      AND policyname = 'Allow comment owners to update comments'
  ) THEN
    CREATE POLICY "Allow comment owners to update comments"
      ON public.comments
      FOR UPDATE
      USING (auth.uid() = author_id)
      WITH CHECK (auth.uid() = author_id);
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'comments'
      AND policyname = 'Allow comment owners to delete comments'
  ) THEN
    CREATE POLICY "Allow comment owners to delete comments"
      ON public.comments
      FOR DELETE
      USING (auth.uid() = author_id);
  END IF;
END
$$;

