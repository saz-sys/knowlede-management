-- RLS policy for posts
create policy "Allow post owners to manage"
  on public.posts
  for all
  using ( auth.uid() = author_id )
  with check ( auth.uid() = author_id );

create policy "Allow moderators to insert"
  on public.posts
  for insert
  with check ( auth.uid() = author_id );
