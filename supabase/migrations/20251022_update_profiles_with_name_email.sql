   -- profiles テーブルにカラムを追加
   alter table public.profiles
     add column if not exists name text,
     add column if not exists email text;

   -- 既存データに name/email をセット
   update public.profiles p
   set
     name = split_part(u.email, '@', 1),
     email = u.email,
     updated_at = now()
   from auth.users u
   where p.id = u.id;

   -- name/email が NULL の場合のフォールバック
   update public.profiles
   set name = coalesce(name, ''), email = coalesce(email, '');

   -- ビューを作成・権限付与
   create or replace view public.auth_users ("id", "email") as
     select id, email from public.profiles;

   grant select on public.auth_users to authenticated;
