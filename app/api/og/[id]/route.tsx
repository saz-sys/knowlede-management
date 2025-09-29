import { ImageResponse } from 'next/og';
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const runtime = 'edge';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = createServerComponentClient({ cookies });
    
    const { data: post } = await supabase
      .from("posts")
      .select("title, author_email, metadata")
      .eq("id", params.id)
      .single();

    if (!post) {
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
              backgroundColor: '#f8fafc',
              backgroundImage: 'linear-gradient(45deg, #1e40af 0%, #3b82f6 100%)',
            }}
          >
            <div
              style={{
                fontSize: 48,
                fontWeight: 'bold',
                color: 'white',
                textAlign: 'center',
                marginBottom: 20,
              }}
            >
              Tech Reef
            </div>
            <div
              style={{
                fontSize: 24,
                color: 'white',
                opacity: 0.8,
              }}
            >
              投稿が見つかりません
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
    const authorName = post.author_email?.split('@')[0] || "Tech Reef";

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            backgroundColor: '#ffffff',
            padding: '60px',
            position: 'relative',
          }}
        >
          {/* 背景グラデーション */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              opacity: 0.1,
            }}
          />
          
          {/* ヘッダー */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '40px',
            }}
          >
            <div
              style={{
                fontSize: 32,
                fontWeight: 'bold',
                color: '#1e40af',
                marginRight: '20px',
              }}
            >
              Tech Reef
            </div>
            <div
              style={{
                fontSize: 18,
                color: '#6b7280',
                backgroundColor: isRssPost ? '#fbbf24' : '#10b981',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '20px',
                fontWeight: 'bold',
              }}
            >
              {isRssPost ? 'RSS' : 'ユーザー投稿'}
            </div>
          </div>

          {/* タイトル */}
          <div
            style={{
              fontSize: 48,
              fontWeight: 'bold',
              color: '#1f2937',
              lineHeight: 1.2,
              marginBottom: '30px',
              maxWidth: '900px',
              display: 'flex',
              flexWrap: 'wrap',
            }}
          >
            {post.title}
          </div>

          {/* フッター */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              width: '100%',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  backgroundColor: '#3b82f6',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '20px',
                  fontWeight: 'bold',
                  marginRight: '20px',
                }}
              >
                {authorName.charAt(0).toUpperCase()}
              </div>
              <div
                style={{
                  fontSize: 20,
                  color: '#6b7280',
                }}
              >
                投稿者: {authorName}
              </div>
            </div>
            
            <div
              style={{
                fontSize: 18,
                color: '#9ca3af',
              }}
            >
              tech-reef.vercel.app
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
    console.error('OGP image generation error:', error);
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
            backgroundColor: '#f8fafc',
            backgroundImage: 'linear-gradient(45deg, #1e40af 0%, #3b82f6 100%)',
          }}
        >
          <div
            style={{
              fontSize: 48,
              fontWeight: 'bold',
              color: 'white',
              textAlign: 'center',
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
}
