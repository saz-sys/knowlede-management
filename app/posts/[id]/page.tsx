import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import CommentThread from "@/components/comments/CommentThread";
import { Comment } from "@/lib/types/comments";

interface PostDetailPageProps {
  params: {
    id: string;
  };
}

export default async function PostDetailPage({ params }: PostDetailPageProps) {
  const supabase = createServerComponentClient({ cookies });

  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();
  if (authError || !session) {
    redirect("/login?redirect=/posts/" + params.id);
  }

  const { data: post, error: postError } = await supabase
    .from("posts")
    .select(`
      id,
      title,
      url,
      content,
      summary,
      created_at,
      updated_at,
      author_id
    `)
    .eq("id", params.id)
    .single();

  if (postError || !post) {
    notFound();
  }

  const { data: comments, error: commentsError } = await supabase
    .from("comments")
    .select(`
      id,
      post_id,
      author_id,
      parent_id,
      content,
      reactions,
      created_at,
      updated_at
    `)
    .eq("post_id", params.id)
    .order("created_at", { ascending: true });

  if (commentsError) {
    console.error("Comments fetch error:", commentsError);
  }

  const commentMap = new Map();
  const rootComments: Comment[] = [];

  comments?.forEach(comment => {
    comment.replies = [];
    comment.reply_count = 0;
    commentMap.set(comment.id, comment);
  });

  comments?.forEach(comment => {
    if (comment.parent_id) {
      const parent = commentMap.get(comment.parent_id);
      if (parent) {
        parent.replies.push(comment);
        parent.reply_count = (parent.reply_count || 0) + 1;
      }
    } else {
      rootComments.push(comment);
    }
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("ja-JP");
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <article className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <header className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{post.title}</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>投稿者ID: {post.author_id}</span>
            <span>投稿日: {formatDate(post.created_at)}</span>
            {post.updated_at !== post.created_at && (
              <span>更新日: {formatDate(post.updated_at)}</span>
            )}
          </div>
        </header>

        {post.url && (
          <div className="mb-4">
            <a
              href={post.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              元記事を開く →
            </a>
          </div>
        )}

        {post.summary && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">要約</h3>
            <p className="text-gray-700">{post.summary}</p>
          </div>
        )}

        <div className="prose max-w-none">
          <h3 className="font-semibold text-gray-900 mb-2">コメント</h3>
          <div className="whitespace-pre-wrap text-gray-700">{post.content}</div>
        </div>
      </article>

      <section className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <CommentThread
          postId={post.id}
          initialComments={(rootComments as Comment[]) || []}
        />
      </section>
    </div>
  );
}
