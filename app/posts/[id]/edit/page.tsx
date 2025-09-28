import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import PostEditForm from "@/components/posts/PostEditForm";

interface EditPostPageProps {
  params: {
    id: string;
  };
}

export default async function EditPostPage({ params }: EditPostPageProps) {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    redirect("/login?redirect=/posts/new");
  }

  // 投稿データを取得
  const { data: post, error: postError } = await supabase
    .from("posts")
    .select(`
      id,
      title,
      url,
      content,
      summary,
      author_id,
      post_tags(
        tag:tags(name)
      )
    `)
    .eq("id", params.id)
    .single();

  if (postError || !post) {
    redirect("/my-posts");
  }

  // 所有者チェック
  if (post.author_id !== session.user.id) {
    redirect("/my-posts");
  }

  // タグを配列に変換
  const tags = post.post_tags?.map((pt: any) => pt.tag.name).join(", ") || "";

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">投稿を編集</h1>
        <p className="mt-2 text-sm text-gray-600">
          投稿内容を編集できます。
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <PostEditForm 
          postId={post.id}
          initialData={{
            title: post.title,
            url: post.url,
            content: post.content || "",
            summary: post.summary || "",
            tags: tags
          }}
        />
      </div>
    </div>
  );
}
