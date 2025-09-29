import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import dynamic from "next/dynamic";
import { notFound } from "next/navigation";

const AutoRedirect = dynamic(() => import("@/components/AutoRedirect"), { ssr: false });

interface PublicPostPageProps {
  params: { id: string };
}

export async function generateMetadata({ params }: PublicPostPageProps) {
  const supabase = createServerComponentClient({ cookies });

  const { data: post, error } = await supabase
    .from("posts")
    .select("title, summary, author_email, created_at, url, metadata")
    .eq("id", params.id)
    .single();

  if (error || !post) {
    return {
      title: "投稿が見つかりません | Tech Reef",
      description: "エンジニアの知識共有プラットフォーム",
    };
  }

  const description = post.summary || "Tech Reefで共有された記事です。";
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
      url: `https://tech-reef.vercel.app/posts/${params.id}/public`,
      publishedTime: post.created_at,
      authors: [post.author_email || "Tech Reef"],
      siteName: "Tech Reef",
      locale: "ja_JP",
      images: [
        {
          url: "https://tech-reef.vercel.app/branding/og-image.png",
          width: 1200,
          height: 630,
          alt: post.title,
        }
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: truncatedDescription,
      images: ["https://tech-reef.vercel.app/branding/og-image.png"],
    },
  };
}

export default async function PublicPostPage({ params }: PublicPostPageProps) {
  const supabase = createServerComponentClient({ cookies });

  const { data: post, error } = await supabase
    .from("posts")
    .select("id")
    .eq("id", params.id)
    .single();

  if (error || !post) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <AutoRedirect to={`/posts/${params.id}`} delay={200} />
      <div className="text-center px-4">
        <h1 className="text-xl font-semibold text-gray-900 mb-3">記事を表示しています...</h1>
        <p className="text-gray-600 text-sm">ページが自動的に移動しない場合は
          <a href={`/posts/${params.id}`} className="text-blue-600 hover:underline ml-1">こちら</a>
          をクリックしてください。
        </p>
      </div>
    </div>
  );
}
