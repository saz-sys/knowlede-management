import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // いいね数を取得
    const { count: likeCount, error: countError } = await supabase
      .from("post_likes")
      .select("*", { count: "exact", head: true })
      .eq("post_id", params.id);

    if (countError) {
      console.error("Failed to fetch like count:", countError);
      return NextResponse.json({ error: "Failed to fetch like count" }, { status: 500 });
    }

    // ユーザーがいいねしているかチェック
    const { data: userLike, error: userLikeError } = await supabase
      .from("post_likes")
      .select("id")
      .eq("post_id", params.id)
      .eq("user_id", session.user.id)
      .single();

    if (userLikeError && userLikeError.code !== "PGRST116") {
      console.error("Failed to check user like:", userLikeError);
      return NextResponse.json({ error: "Failed to check user like" }, { status: 500 });
    }

    return NextResponse.json({
      likeCount: likeCount || 0,
      isLiked: !!userLike
    });

  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // いいねを追加
    const { data: like, error: likeError } = await supabase
      .from("post_likes")
      .insert({
        post_id: params.id,
        user_id: session.user.id
      })
      .select("id")
      .single();

    if (likeError) {
      if (likeError.code === "23505") {
        // 重複エラー（既にいいね済み）
        return NextResponse.json({ error: "Already liked" }, { status: 409 });
      }
      console.error("Failed to add like:", likeError);
      return NextResponse.json({ error: "Failed to add like" }, { status: 500 });
    }

    return NextResponse.json({ success: true, like });

  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // いいねを削除
    const { error: deleteError } = await supabase
      .from("post_likes")
      .delete()
      .eq("post_id", params.id)
      .eq("user_id", session.user.id);

    if (deleteError) {
      console.error("Failed to remove like:", deleteError);
      return NextResponse.json({ error: "Failed to remove like" }, { status: 500 });
    }

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
