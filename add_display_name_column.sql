-- profiles テーブルに display_name カラムを追加
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS display_name text;

-- 既存のレコードに対して display_name を name から設定
UPDATE public.profiles 
SET display_name = COALESCE(name, '')
WHERE display_name IS NULL;

-- display_name が NULL の場合のデフォルト値を設定
UPDATE public.profiles 
SET display_name = COALESCE(display_name, '')
WHERE display_name IS NULL;
