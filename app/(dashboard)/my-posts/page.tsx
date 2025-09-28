import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import MyPostsList from "@/components/posts/MyPostsList";
import MyProfile from "@/components/profile/MyProfile";

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
        <h1 className="text-2xl font-bold text-gray-900">マイページ</h1>
        <p className="mt-2 text-sm text-gray-600">
          あなたの投稿とプロフィールを管理できます。
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* SNS */}
        <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">SNS</h2>
            <MyProfile />
          </div>
        </div>

        {/* 投稿一覧 */}
        <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">マイ投稿</h2>
            <MyPostsList />
          </div>
        </div>
      </div>
    </div>
  );
}
