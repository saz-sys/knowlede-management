import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

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

interface SlackMessage {
  channel: string;
  text: string;
  blocks?: any[];
}

serve(async (req) => {
  try {
    // 平日かどうかをチェック（月曜日=1, 金曜日=5）
    const today = new Date();
    const dayOfWeek = today.getDay();
    
    // 土曜日(6)と日曜日(0)の場合はスキップ
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      console.log("Today is weekend, skipping daily summary");
      return new Response(JSON.stringify({ message: "Weekend - no notification sent" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // 環境変数の取得
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    const slackBotToken = Deno.env.get("SLACK_BOT_TOKEN");
    const slackChannel = Deno.env.get("SLACK_NOTIFICATION_CHANNEL");

    if (!supabaseUrl || !supabaseServiceKey || !slackBotToken || !slackChannel) {
      throw new Error("Missing required environment variables");
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

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
      throw new Error(`Failed to fetch posts: ${error.message}`);
    }

    // ユーザー投稿のみをフィルタリング（RSS投稿を除外）
    const userPosts = posts?.filter(post => 
      post.profiles && 
      post.profiles.email !== 'rss@autogen'
    ) || [];

    console.log(`Found ${userPosts.length} user posts in the last 24 hours`);

    // 投稿がない場合は通知を送信しない
    if (userPosts.length === 0) {
      console.log("No posts to notify about");
      return new Response(JSON.stringify({ message: "No posts to notify about" }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Slack通知を送信
    const todayFormatted = today.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });

    // シンプルなメッセージ形式
    const postList = userPosts.map(post => 
      `• [${post.title}](${post.url})`
    ).join('\n');

    const message: SlackMessage = {
      channel: slackChannel,
      text: `📰 新規投稿 ${userPosts.length}件\n\n${postList}`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `📰 *新規投稿 ${userPosts.length}件*\n\n${postList}`
          }
        }
      ]
    };

    const slackResponse = await fetch("https://slack.com/api/chat.postMessage", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${slackBotToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    const slackResult = await slackResponse.json();
    
    if (!slackResult.ok) {
      throw new Error(`Failed to send Slack notification: ${slackResult.error}`);
    }

    console.log("Daily summary notification sent successfully");

    return new Response(JSON.stringify({ 
      message: "Daily summary notification sent successfully",
      postsCount: userPosts.length,
      channel: slackChannel
    }), {
      headers: { "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("Error in daily summary function:", error);
    return new Response(JSON.stringify({ 
      error: error.message 
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
