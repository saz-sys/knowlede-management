create table if not exists public.resource_links (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  user_name text not null,
  user_email text not null,
  service text not null,
  url text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.resource_links enable row level security;