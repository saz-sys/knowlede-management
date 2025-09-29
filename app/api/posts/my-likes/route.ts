import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const { data: likes, error } = await supabase
      .from("post_likes")
      .select("post_id")
      .eq("user_id", session.user.id);

    if (error) {
      console.error("Error fetching user likes:", error);
      return NextResponse.json({ error: "Failed to fetch likes" }, { status: 500 });
    }

    const likedPostIds = likes?.map((like) => like.post_id) || [];
    return NextResponse.json({ likedPostIds });
  } catch (error) {
    console.error("Unexpected error fetching user likes:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
