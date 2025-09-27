-- Comment RLS policies

drop policy if exists "Allow comment owners to manage" on public.comments;

create policy "Allow authenticated to insert comments"
  on public.comments
  for insert
  with check (
    auth.role() = 'authenticated'
    and auth.uid() = author_id
  );

create policy "Allow comment owners to update comments"
  on public.comments
  for update
  using (auth.uid() = author_id)
  with check (auth.uid() = author_id);

create policy "Allow comment owners to delete comments"
  on public.comments
  for delete
  using (auth.uid() = author_id);
