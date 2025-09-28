-- 既存のauth.usersからprofilesレコードを作成
INSERT INTO public.profiles (id, name, email)
SELECT 
  id,
  split_part(email, '@', 1) as name,
  email
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.profiles)
ON CONFLICT (id) DO NOTHING;
