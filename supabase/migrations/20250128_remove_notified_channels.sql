-- Remove notified_channels column from posts table
alter table public.posts drop column if exists notified_channels;
