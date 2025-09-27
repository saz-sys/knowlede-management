-- RLS policy for RSS feeds
create policy "Allow moderators to manage RSS feeds"
  on public.rss_feeds
  for all
  using ( auth.role() = 'authenticated' )
  with check ( auth.role() = 'authenticated' );

-- RLS policy for RSS items
create policy "Allow moderators to manage RSS items"
  on public.rss_items
  for all
  using ( auth.role() = 'authenticated' )
  with check ( auth.role() = 'authenticated' );
