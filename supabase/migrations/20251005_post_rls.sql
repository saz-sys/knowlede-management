-- Ensure authenticated users can manage their own posts
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename = 'posts'
       AND policyname = 'Allow authenticated insert posts'
  ) THEN
    CREATE POLICY "Allow authenticated insert posts"
      ON public.posts
      FOR INSERT
      WITH CHECK ( auth.uid() = author_id );
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename = 'posts'
       AND policyname = 'Allow post owners to update/delete posts'
  ) THEN
    CREATE POLICY "Allow post owners to update/delete posts"
      ON public.posts
      FOR UPDATE
      USING ( auth.uid() = author_id )
      WITH CHECK ( auth.uid() = author_id );

    CREATE POLICY "Allow post owners to delete posts"
      ON public.posts
      FOR DELETE
      USING ( auth.uid() = author_id );
  END IF;
END
$$;
