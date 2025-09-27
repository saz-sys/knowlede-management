-- Add author_email column to posts for display purposes

ALTER TABLE public.posts
  ADD COLUMN IF NOT EXISTS author_email text;

-- Backfill existing posts with current email information
UPDATE public.posts AS p
SET author_email = u.email
FROM auth.users AS u
WHERE p.author_id = u.id
  AND (p.author_email IS NULL OR p.author_email = '');


