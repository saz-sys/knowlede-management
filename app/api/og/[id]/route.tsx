import { ImageResponse } from 'next/og';
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const runtime = 'edge';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = createRouteHandlerClient({ cookies: () => cookies() });

    const { data: post, error } = await supabase
      .from("posts")
      .select("title, author_email, metadata")
      .eq("id", params.id)
      .single();

    if (error || !post) {
      return new ImageResponse(
        (
          <div
            style={{
              height: '100%',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#1a1a1a',
              backgroundImage: 'linear-gradient(45deg, #1a1a1a 0%, #2d2d2d 100%)',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: 48,
                fontWeight: 'bold',
                textAlign: 'center',
                maxWidth: '80%',
              }}
            >
              Tech Reef
            </div>
          </div>
        ),
        {
          width: 1200,
          height: 630,
        }
      );
    }

    const isRssPost = post.metadata?.source === "rss";
    const author = post.author_email || "Tech Reef";

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            justifyContent: 'center',
            backgroundColor: '#1a1a1a',
            backgroundImage: 'linear-gradient(45deg, #1a1a1a 0%, #2d2d2d 100%)',
            padding: '60px',
            position: 'relative',
          }}
        >
          {/* 背景パターン */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundImage: 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%)',
            }}
          />
          
          {/* メインコンテンツ */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              justifyContent: 'center',
              color: 'white',
              maxWidth: '90%',
              zIndex: 1,
            }}
          >
            {/* タイトル */}
            <div
              style={{
                fontSize: 56,
                fontWeight: 'bold',
                lineHeight: 1.2,
                marginBottom: 24,
                textAlign: 'left',
                maxWidth: '100%',
                wordWrap: 'break-word',
              }}
            >
              {post.title}
            </div>
            
            {/* 投稿者情報 */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                fontSize: 24,
                color: '#a0a0a0',
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: isRssPost ? '#10b981' : '#3b82f6',
                  marginRight: 12,
                }}
              />
              {author}
              {isRssPost && (
                <span style={{ marginLeft: 12, fontSize: 18, color: '#10b981' }}>
                  RSS
                </span>
              )}
            </div>
            
            {/* Tech Reef ブランド */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                fontSize: 20,
                color: '#666',
                marginTop: 'auto',
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: '#3b82f6',
                  marginRight: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 16,
                  fontWeight: 'bold',
                }}
              >
                T
              </div>
              Tech Reef
            </div>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (error) {
    console.error('OGP generation error:', error);
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#1a1a1a',
            color: 'white',
            fontSize: 48,
            fontWeight: 'bold',
          }}
        >
          Tech Reef
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
}
