alter table public.posts
  add column if not exists metadata jsonb default '{}'::jsonb;

alter table public.posts
  drop constraint if exists posts_author_id_fkey;
