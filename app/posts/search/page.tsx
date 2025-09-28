import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import PostSearchResults from "@/components/posts/PostSearchResults";

interface SearchPageProps {
  searchParams: {
    q?: string;
    tag?: string;
    source?: string;
  };
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const supabase = createServerComponentClient({ cookies });
  const {
    data: { session },
    error
  } = await supabase.auth.getSession();

  if (error || !session) {
    redirect("/login?redirect=/posts/search");
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">投稿検索</h1>
        <p className="mt-2 text-sm text-gray-600">
          キーワードで投稿を検索できます。
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <PostSearchResults 
          initialQuery={searchParams.q || ""}
          initialTag={searchParams.tag}
          initialSource={searchParams.source}
        />
      </div>
    </div>
  );
}
