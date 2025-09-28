create policy "allow authenticated read resource links"
  on public.resource_links
  for select
  using (auth.role() = 'authenticated');

create policy "allow moderators manage resource links"
  on public.resource_links
  for all
  using (auth.role() = 'authenticated')
  with check (auth.role() = 'authenticated');
