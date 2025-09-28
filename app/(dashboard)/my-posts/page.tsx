import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import MyPostsList from "@/components/posts/MyPostsList";

export default async function MyPostsPage() {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    redirect("/login?redirect=/my-posts");
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">マイ投稿</h1>
        <p className="mt-2 text-sm text-gray-600">
          あなたが投稿した記事の一覧です。編集や削除ができます。
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <MyPostsList />
      </div>
    </div>
  );
}
