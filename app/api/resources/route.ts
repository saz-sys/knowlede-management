import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";

const SUPPORTED_SERVICES = new Set(["zenn", "qiita", "note", "github", "x", "other"]);

interface ResourceLinkPayload {
  user_id: string;
  links: {
    service: string;
    url: string;
  }[];
}

const formatLink = (row: any) => ({
  id: row.id,
  user_id: row.user_id,
  user_name: row.profiles?.name || '',
  user_email: row.profiles?.email || '',
  service: row.label,
  url: row.url,
  created_at: row.created_at,
  updated_at: row.updated_at
});

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

  const { data, error } = await supabase
    .from("resource_links")
    .select(`
      id, 
      user_id, 
      label, 
      url, 
      created_at, 
      updated_at,
      profiles!inner(name, email)
    `)
    .order("updated_at", { ascending: false });

  if (error) {
    console.error("Failed to fetch resource links", error);
    return NextResponse.json({ error: "Failed to fetch resource links" }, { status: 500 });
  }

  return NextResponse.json({ links: (data ?? []).map(formatLink) });
}

export async function POST(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let body: ResourceLinkPayload;
  try {
    body = await request.json();
  } catch (error) {
    console.error("Invalid JSON", error);
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.user_id) {
    return NextResponse.json({ error: "user_id is required" }, { status: 400 });
  }

  const links = (body.links ?? []).filter((link) => link.url?.trim().length);
  if (!links.length) {
    return NextResponse.json({ error: "links are required" }, { status: 400 });
  }

  const { data: userRecord, error: userError } = await supabase
    .from("profiles")
    .select("id, name, email")
    .eq("id", body.user_id)
    .maybeSingle();

  if (userError || !userRecord) {
    console.error("Failed to fetch user", userError);
    return NextResponse.json({ error: "user not found" }, { status: 404 });
  }

  const insertRows = links.map((link) => {
    const service = link.service.trim().toLowerCase();
    if (!SUPPORTED_SERVICES.has(service)) {
      throw new Error(`Unsupported service: ${service}`);
    }
    return {
      user_id: body.user_id,
      label: service,
      url: link.url.trim()
    };
  });

  try {
    const { data, error } = await supabase
      .from("resource_links")
      .insert(insertRows)
      .select(`
        id, 
        user_id, 
        label, 
        url, 
        created_at, 
        updated_at,
        profiles!inner(name, email)
      `);

    if (error) {
      console.error("Failed to insert resource links", error);
      return NextResponse.json({ error: "Failed to create resource links" }, { status: 500 });
    }

    return NextResponse.json({ links: (data ?? []).map(formatLink) }, { status: 201 });
  } catch (error) {
    if (error instanceof Error) {
      return NextResponse.json({ error: error.message }, { status: 400 });
    }
    return NextResponse.json({ error: "Failed to create resource links" }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let body: ResourceLinkPayload;
  try {
    body = await request.json();
  } catch (error) {
    console.error("Invalid JSON", error);
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const links = (body.links ?? []).filter((link) => link.url?.trim().length);
  if (!body.user_id || !links.length) {
    return NextResponse.json({ error: "user_id and links are required" }, { status: 400 });
  }

  const { data: userRecord, error: userError } = await supabase
    .from("profiles")
    .select("id, name, email")
    .eq("id", body.user_id)
    .maybeSingle();

  if (userError || !userRecord) {
    console.error("Failed to fetch user", userError);
    return NextResponse.json({ error: "user not found" }, { status: 404 });
  }

  const { error: deleteError } = await supabase
    .from("resource_links")
    .delete()
    .eq("user_id", body.user_id);

  if (deleteError) {
    console.error("Failed to reset resource links", deleteError);
    return NextResponse.json({ error: "Failed to update resource links" }, { status: 500 });
  }

  try {
    const prepared = links.map((link) => {
      const service = link.service.trim().toLowerCase();
      if (!SUPPORTED_SERVICES.has(service)) {
        throw new Error(`Unsupported service: ${service}`);
      }
      return {
        user_id: body.user_id,
        label: service,
        url: link.url.trim()
      };
    });

    const { data: updated, error: insertError } = await supabase
      .from("resource_links")
      .insert(prepared)
      .select(`
        id, 
        user_id, 
        label, 
        url, 
        created_at, 
        updated_at,
        profiles!inner(name, email)
      `);

    if (insertError) {
      console.error("Failed to insert updated resource links", insertError);
      return NextResponse.json({ error: "Failed to update resource links" }, { status: 500 });
    }

    return NextResponse.json({ links: (updated ?? []).map(formatLink) });
  } catch (error) {
    if (error instanceof Error) {
      return NextResponse.json({ error: error.message }, { status: 400 });
    }
    return NextResponse.json({ error: "Failed to update resource links" }, { status: 500 });
  }
}
