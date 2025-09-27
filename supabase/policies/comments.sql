-- RLS policy for comments
create policy "Allow comment owners to manage"
  on public.comments
  for all
  using ( auth.uid() = author_id )
  with check ( auth.uid() = author_id );

create policy "Allow authenticated to insert comments"
  on public.comments
  for insert
  with check ( auth.role() = 'authenticated' );
