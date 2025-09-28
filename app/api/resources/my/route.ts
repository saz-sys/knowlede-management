import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const {
      data: { session },
      error: authError
    } = await supabase.auth.getSession();

    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 自分のリソースリンクを取得
    const { data: links, error: fetchError } = await supabase
      .from("resource_links")
      .select(`
        id,
        label,
        url,
        user_id,
        created_at,
        updated_at
      `)
      .eq("user_id", session.user.id)
      .order("created_at", { ascending: true });

    if (fetchError) {
      console.error("Failed to fetch my resources:", fetchError);
      return NextResponse.json({ error: "Failed to fetch resources" }, { status: 500 });
    }

    return NextResponse.json({ links: links || [] });
  } catch (error) {
    console.error("Unexpected error while fetching my resources:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const {
      data: { session },
      error: authError
    } = await supabase.auth.getSession();

    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { links } = body;

    if (!Array.isArray(links)) {
      return NextResponse.json({ error: "Links must be an array" }, { status: 400 });
    }

    // 既存のリンクを削除
    const { error: deleteError } = await supabase
      .from("resource_links")
      .delete()
      .eq("user_id", session.user.id);

    if (deleteError) {
      console.error("Failed to delete existing links:", deleteError);
      return NextResponse.json({ error: "Failed to update resources" }, { status: 500 });
    }

    // 新しいリンクを追加
    if (links.length > 0) {
      const linkPayload = links.map((link: { service: string; url: string }) => ({
        user_id: session.user.id,
        label: link.service.trim(),
        url: link.url.trim()
      }));

      const { error: insertError } = await supabase
        .from("resource_links")
        .insert(linkPayload);

      if (insertError) {
        console.error("Failed to insert new links:", insertError);
        return NextResponse.json({ error: "Failed to save resources" }, { status: 500 });
      }
    }

    return NextResponse.json({ message: "Resources updated successfully" });
  } catch (error) {
    console.error("Unexpected error while updating resources:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
