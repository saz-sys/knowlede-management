import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );

    const { data: tags, error } = await supabase
      .from("tags")
      .select("name")
      .order("name");

    if (error) {
      console.error("Error fetching tags:", error);
      return NextResponse.json({ error: "Failed to fetch tags" }, { status: 500 });
    }

    return NextResponse.json(tags?.map(tag => tag.name) || []);
  } catch (error) {
    console.error("Error in tags API:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
