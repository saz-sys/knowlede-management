import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { Metadata } from "next";
import CommentThread from "@/components/comments/CommentThread";
import LikeButton from "@/components/posts/LikeButton";
import BookmarkButton from "@/components/bookmarks/BookmarkButton";
import ShareButton from "@/components/ShareButton";
import { Comment } from "@/lib/types/comments";

interface PostDetailPageProps {
  params: {
    id: string;
  };
}

function createExcerpt(text: string, maxLength = 200) {
  const normalized = text.replace(/\r\n/g, "\n").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }

  const slice = normalized.slice(0, maxLength);
  const lastBreak = slice.lastIndexOf("\n");
  const lastSpace = slice.lastIndexOf(" ");
  const cutIndex = Math.max(lastBreak, lastSpace);
  const truncated = cutIndex > maxLength * 0.5 ? slice.slice(0, cutIndex) : slice;

  return `${truncated.trimEnd()}…`;
}

export async function generateMetadata({ params }: PostDetailPageProps): Promise<Metadata> {
  const supabase = createServerComponentClient({ cookies });
  
  const { data: post } = await supabase
    .from("posts")
    .select("title, author_email, created_at, url, metadata")
    .eq("id", params.id)
    .single();

  if (!post) {
    return {
      title: "投稿が見つかりません | Tech Reef",
    };
  }

  const description = "Tech Reefで共有された記事です。";
  const truncatedDescription = description.length > 160 
    ? description.substring(0, 160) + "..." 
    : description;

  return {
    title: `${post.title} | Tech Reef`,
    description: truncatedDescription,
    openGraph: {
      title: post.title,
      description: truncatedDescription,
      type: "article",
      url: `https://tech-reef.vercel.app/posts/${params.id}`,
      publishedTime: post.created_at,
      authors: [post.author_email || "Tech Reef"],
      siteName: "Tech Reef",
      locale: "ja_JP",
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: truncatedDescription,
    },
  };
}

export default async function PostDetailPage({ params }: PostDetailPageProps) {
  const supabase = createServerComponentClient({ cookies });
  
  // 認証チェック - 未認証の場合は公開ページにリダイレクト
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) {
    redirect(`/posts/${params.id}/public`);
  }


  const { data: post, error: postError } = await supabase
    .from("posts")
    .select(`
      id,
      title,
      url,
      content,
      summary,
      metadata,
      created_at,
      updated_at,
      author_email,
      post_likes(count),
      bookmarks(count)
    `)
    .eq("id", params.id)
    .single();

  if (postError || !post) {
    notFound();
  }

  // 現在のユーザーのブックマーク状態を取得
  const { data: userBookmark, error: bookmarkError } = await supabase
    .from("bookmarks")
    .select("id")
    .eq("post_id", params.id)
    .eq("user_id", session.user.id)
    .single();

  if (bookmarkError && bookmarkError.code !== "PGRST116") {
    console.error("Bookmark fetch error:", bookmarkError);
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

  // プロフィール情報を取得
  const authorIds = Array.from(new Set(comments?.map(c => c.author_id) || []));
  const { data: profiles, error: profilesError } = await supabase
    .from("profiles")
    .select("id, name, email")
    .in("id", authorIds);

  if (profilesError) {
    console.error("Profiles fetch error:", profilesError);
  }

  // プロフィール情報をマップに変換
  const profileMap = new Map();
  profiles?.forEach(profile => {
    profileMap.set(profile.id, profile);
  });

  // コメントにプロフィール情報を追加
  const commentsWithProfiles = comments?.map(comment => ({
    ...comment,
    author: profileMap.get(comment.author_id) || null
  })) || [];

  const commentMap = new Map();
  const rootComments: Comment[] = [];

  commentsWithProfiles.forEach(comment => {
    (comment as any).replies = [];
    (comment as any).reply_count = 0;
    commentMap.set(comment.id, comment);
  });

  commentsWithProfiles.forEach(comment => {
    if (comment.parent_id) {
      const parent = commentMap.get(comment.parent_id);
      if (parent) {
        (parent as any).replies.push(comment);
        (parent as any).reply_count = ((parent as any).reply_count || 0) + 1;
      }
    } else {
      rootComments.push(comment);
    }
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("ja-JP");
  };

  const isRssPost = post.metadata?.source === "rss";
  const summaryText = null;
  const contentText = !post.content
    ? null
    : isRssPost
    ? createExcerpt(post.content)
    : post.content;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <article className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <header className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{post.title}</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>投稿者: {post.author_email ?? "不明"}</span>
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

        <div className="mb-4 flex items-center justify-end gap-4">
          <LikeButton
            postId={post.id}
            initialLikeCount={post.post_likes?.[0]?.count || 0}
          />
          <BookmarkButton
            postId={post.id}
            isBookmarked={!!userBookmark}
            skipInitialCheck={true}
          />
          <ShareButton postId={post.id} postTitle={post.title} />
        </div>

        {summaryText && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">要約</h3>
            <p className="text-gray-700 whitespace-pre-line">{summaryText}</p>
          </div>
        )}

        {contentText && (
          <div className="prose max-w-none">
            <h3 className="font-semibold text-gray-900 mb-2">{isRssPost ? "本文ダイジェスト" : "本文"}</h3>
            <div className="whitespace-pre-line text-gray-700">{contentText}</div>
          </div>
        )}
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
