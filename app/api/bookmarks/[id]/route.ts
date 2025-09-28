import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { is_read, notes } = body;

    // ブックマークの存在確認と権限チェック
    const { data: bookmark, error: fetchError } = await supabase
      .from("bookmarks")
      .select("id, user_id")
      .eq("id", params.id)
      .eq("user_id", session.user.id)
      .single();

    if (fetchError || !bookmark) {
      return NextResponse.json({ error: "Bookmark not found" }, { status: 404 });
    }

    // 更新データの準備
    const updateData: any = {};
    if (typeof is_read === "boolean") {
      updateData.is_read = is_read;
    }
    if (notes !== undefined) {
      updateData.notes = notes;
    }

    // ブックマーク更新
    const { data: updatedBookmark, error: updateError } = await supabase
      .from("bookmarks")
      .update(updateData)
      .eq("id", params.id)
      .select(`
        id,
        created_at,
        is_read,
        notes,
        posts (
          id,
          title,
          url,
          summary
        )
      `)
      .single();

    if (updateError) {
      console.error("Bookmark update error:", updateError);
      return NextResponse.json({ error: "Failed to update bookmark" }, { status: 500 });
    }

    return NextResponse.json({ bookmark: updatedBookmark });
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

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // ブックマークの存在確認と権限チェック
    const { data: bookmark, error: fetchError } = await supabase
      .from("bookmarks")
      .select("id, user_id")
      .eq("id", params.id)
      .eq("user_id", session.user.id)
      .single();

    if (fetchError || !bookmark) {
      return NextResponse.json({ error: "Bookmark not found" }, { status: 404 });
    }

    // ブックマーク削除
    const { error: deleteError } = await supabase
      .from("bookmarks")
      .delete()
      .eq("id", params.id);

    if (deleteError) {
      console.error("Bookmark deletion error:", deleteError);
      return NextResponse.json({ error: "Failed to delete bookmark" }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
