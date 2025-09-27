-- RLS policy for RSS feeds
drop policy if exists "Allow moderators to manage RSS feeds" on public.rss_feeds;

create policy "Allow authenticated read rss feeds"
  on public.rss_feeds
  for select
  using ( auth.role() = 'authenticated' );

create policy "Allow moderators manage rss feeds"
  on public.rss_feeds
  for all
  using (
    auth.role() = 'authenticated'
  )
  with check (
    auth.role() = 'authenticated'
  );
