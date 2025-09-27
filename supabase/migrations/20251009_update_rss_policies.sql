-- Update RSS related RLS policies to separate read and manage permissions

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'rss_feeds'
      AND policyname = 'Allow moderators to manage RSS feeds'
  ) THEN
    DROP POLICY "Allow moderators to manage RSS feeds" ON public.rss_feeds;
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'rss_feeds'
      AND policyname = 'Allow authenticated read rss feeds'
  ) THEN
    CREATE POLICY "Allow authenticated read rss feeds"
      ON public.rss_feeds
      FOR SELECT
      USING ( auth.role() = 'authenticated' );
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'rss_feeds'
      AND policyname = 'Allow moderators manage rss feeds'
  ) THEN
    CREATE POLICY "Allow moderators manage rss feeds"
      ON public.rss_feeds
      FOR ALL
      USING ( auth.role() = 'authenticated' )
      WITH CHECK ( auth.role() = 'authenticated' );
  END IF;
END
$$;


