import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const period = searchParams.get("period") || "all"; // all, day, week, month
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "20");
    const offset = (page - 1) * limit;

    // 期間フィルターの条件を設定
    let dateFilter = "";
    switch (period) {
      case "day":
        dateFilter = "AND p.created_at >= NOW() - INTERVAL '1 day'";
        break;
      case "week":
        dateFilter = "AND p.created_at >= NOW() - INTERVAL '1 week'";
        break;
      case "month":
        dateFilter = "AND p.created_at >= NOW() - INTERVAL '1 month'";
        break;
      default:
        dateFilter = "";
    }

    // ブックマーク数ランキングを取得するクエリ
    const { data: rankings, error: rankingsError } = await supabase
      .rpc('get_bookmark_rankings', {
        period_filter: dateFilter,
        limit_count: limit,
        offset_count: offset
      });

    if (rankingsError) {
      console.error("Bookmark rankings query error:", rankingsError);
      return NextResponse.json({ error: "Failed to fetch bookmark rankings" }, { status: 500 });
    }

    // 総件数を取得
    const { data: totalCount, error: countError } = await supabase
      .rpc('get_bookmark_rankings_count', {
        period_filter: dateFilter
      });

    if (countError) {
      console.error("Bookmark rankings count error:", countError);
      return NextResponse.json({ error: "Failed to fetch bookmark rankings count" }, { status: 500 });
    }

    return NextResponse.json({
      rankings: rankings || [],
      pagination: {
        page,
        limit,
        total: totalCount?.[0]?.total || 0,
        totalPages: Math.ceil((totalCount?.[0]?.total || 0) / limit)
      }
    });

  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
