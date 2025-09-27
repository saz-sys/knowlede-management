import PostEditor from "@/components/PostEditor";
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function NewPostPage() {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    redirect("/login?redirect=/posts/new");
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">新規投稿</h1>
        <p className="mt-2 text-sm text-gray-600">
          社内で共有したい記事や知見を投稿しましょう。コメントにはMarkdownが利用できます。
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <PostEditor />
      </div>
    </div>
  );
}

