import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { env } from '@/lib/config/env';

interface DailyPost {
  id: string;
  title: string;
  url: string;
  author_id: string;
  created_at: string;
  profiles: {
    name: string;
    email: string;
  };
}

export async function GET(request: NextRequest) {
  try {
    const supabase = createClient(env.supabaseUrl, env.supabaseAnonKey);
    
    // 過去24時間の新規投稿を取得
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const { data: posts, error } = await supabase
      .from('posts')
      .select(`
        id,
        title,
        url,
        author_id,
        created_at,
        profiles!posts_author_id_fkey (
          name,
          email
        )
      `)
      .gte('created_at', yesterday.toISOString())
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching daily posts:', error);
      return NextResponse.json({ error: 'Failed to fetch posts' }, { status: 500 });
    }

    // ユーザー投稿のみをフィルタリング（RSS投稿を除外）
    const userPosts = posts?.filter(post => 
      post.profiles && 
      post.profiles.email !== 'rss@autogen'
    ) || [];

    return NextResponse.json({
      posts: userPosts,
      count: userPosts.length,
      period: '24 hours'
    });

  } catch (error) {
    console.error('Daily summary API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
