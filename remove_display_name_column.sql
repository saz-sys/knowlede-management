-- 本番環境のprofilesテーブルからdisplay_nameカラムを削除
ALTER TABLE public.profiles DROP COLUMN IF EXISTS display_name;
