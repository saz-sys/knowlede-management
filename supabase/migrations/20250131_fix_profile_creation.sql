-- auth.usersにINSERTトリガーを追加してprofilesテーブルにレコードを自動作成
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, name, email)
  VALUES (
    NEW.id,
    split_part(NEW.email, '@', 1),
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- auth.usersのINSERT時にトリガーを実行
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 既存のauth.usersからprofilesレコードを作成（重複チェック付き）
INSERT INTO public.profiles (id, name, email)
SELECT 
  id,
  split_part(email, '@', 1) as name,
  email
FROM auth.users
WHERE id NOT IN (SELECT id FROM public.profiles)
ON CONFLICT (id) DO NOTHING;

-- 既存のprofilesでnameがNULLのレコードを更新
UPDATE public.profiles p
SET 
  name = split_part(u.email, '@', 1),
  email = u.email,
  updated_at = now()
FROM auth.users u
WHERE p.id = u.id 
  AND (p.name IS NULL OR p.name = '');
