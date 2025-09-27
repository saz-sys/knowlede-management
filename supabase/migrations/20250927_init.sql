-- Posts table
create table if not exists public.posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid not null,
  title text not null,
  url text not null,
  content text,
  summary text,
  notified_channels jsonb default '[]'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Comments table
create table if not exists public.comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.posts(id) on delete cascade,
  author_id uuid not null,
  parent_id uuid references public.comments(id) on delete cascade,
  content text not null,
  reactions jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Tags table
create table if not exists public.tags (
  id uuid primary key default gen_random_uuid(),
  name text unique not null,
  description text,
  usage_count integer default 0,
  created_at timestamptz default now()
);

-- Post-Tag relation
create table if not exists public.post_tags (
  post_id uuid references public.posts(id) on delete cascade,
  tag_id uuid references public.tags(id) on delete cascade,
  created_at timestamptz default now(),
  primary key (post_id, tag_id)
);

-- Knowledge cards
create table if not exists public.knowledge_cards (
  id uuid primary key default gen_random_uuid(),
  post_id uuid references public.posts(id) on delete cascade,
  summary text not null,
  created_by uuid not null,
  created_at timestamptz default now()
);

-- RSS feeds
create table if not exists public.rss_feeds (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  url text not null,
  tags text[] default '{}',
  is_active boolean default true,
  last_fetched_at timestamptz,
  created_at timestamptz default now()
);

-- RSS items queue
create table if not exists public.rss_items (
  id uuid primary key default gen_random_uuid(),
  feed_id uuid references public.rss_feeds(id) on delete cascade,
  title text not null,
  url text not null,
  summary text,
  tag_suggestions text[],
  status text default 'pending',
  created_at timestamptz default now()
);

-- Slack channels
create table if not exists public.slack_channels (
  id uuid primary key default gen_random_uuid(),
  channel_id text not null,
  name text not null,
  suppressed_hours int[] default '{}',
  created_at timestamptz default now()
);

-- Event log for analytics
create table if not exists public.event_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  event_type text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Enable Row Level Security
alter table public.posts enable row level security;
alter table public.comments enable row level security;
alter table public.knowledge_cards enable row level security;
alter table public.rss_feeds enable row level security;
alter table public.rss_items enable row level security;
alter table public.slack_channels enable row level security;
alter table public.event_logs enable row level security;

-- Basic policies (allow authenticated users to read)
create policy "Allow authenticated read posts" on public.posts
  for select using ( auth.role() = 'authenticated' );

create policy "Allow authenticated read comments" on public.comments
  for select using ( auth.role() = 'authenticated' );

-- Writing policies will be refined later
