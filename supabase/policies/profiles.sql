create policy "allow authenticated read profiles"
  on public.profiles
  for select
  using (auth.role() = 'authenticated');
