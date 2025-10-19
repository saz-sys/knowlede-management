interface SlackMessage {
  channel: string;
  text: string;
  blocks?: any[];
}

interface CommentNotificationData {
  postTitle: string;
  postUrl: string;
  commentAuthor: string;
  commentContent: string;
  postAuthorEmail: string;
  postAuthorName?: string;
  isReply?: boolean;
  parentCommentAuthor?: string;
  parentCommentAuthorEmail?: string;
}

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

interface PostNotificationData {
  postId: string;
  title: string;
  url: string;
  authorName: string;
  authorEmail: string;
  content?: string;
}

export async function sendCommentNotification(data: CommentNotificationData): Promise<boolean> {
  const botToken = process.env.SLACK_BOT_TOKEN;
  const channel = process.env.SLACK_NOTIFICATION_CHANNEL
  
  if (!botToken) {
    console.error("SLACK_BOT_TOKEN is not configured");
    return false;
  }

  if (!channel) {
    console.error("SLACK_NOTIFICATION_CHANNEL is not configured");
    return false;
  }

  // メンション用のテキストを生成
  // 返信コメントの場合は元のコメント投稿者にメンション、そうでなければ投稿者にメンション
  let mentionText: string;
  if (data.isReply && data.parentCommentAuthor) {
    mentionText = `@${data.parentCommentAuthor}`;
  } else {
    mentionText = data.postAuthorName ? `@${data.postAuthorName}` : data.postAuthorEmail;
  }
  
  const message: SlackMessage = {
    channel: channel as string,
    text: data.isReply ? `💬 返信コメントが投稿されました: ${data.postTitle}` : `💬 新しいコメントが投稿されました: ${data.postTitle}`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: data.isReply ? "💬 返信コメントが投稿されました" : "💬 新しいコメントが投稿されました"
        }
      },
      {
        type: "section",
        fields: [
          {
            type: "mrkdwn",
            text: `*記事:*\n${data.postTitle}`
          },
          {
            type: "mrkdwn",
            text: `*投稿者:*\n${mentionText}`
          }
        ]
      },
      {
        type: "section",
        fields: [
          {
            type: "mrkdwn",
            text: `*コメント投稿者:*\n${data.commentAuthor}`
          },
          {
            type: "mrkdwn",
            text: `*コメント:*\n${data.commentContent.length > 200 ? data.commentContent.substring(0, 200) + "..." : data.commentContent}`
          }
        ]
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: {
              type: "plain_text",
              text: "記事を確認する"
            },
            url: data.postUrl,
            style: "primary"
          }
        ]
      }
    ]
  };

  try {
    const response = await fetch("https://slack.com/api/chat.postMessage", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${botToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    const result = await response.json();
    
    if (!result.ok) {
      console.error("Failed to send Slack notification:", result.error);
      return false;
    }

    console.log("Slack notification sent successfully");
    return true;
  } catch (error) {
    console.error("Error sending Slack notification:", error);
    return false;
  }
}

export async function sendDailySummaryNotification(posts: DailyPost[]): Promise<boolean> {
  const botToken = process.env.SLACK_BOT_TOKEN;
  const channel = process.env.SLACK_NOTIFICATION_CHANNEL;
  
  if (!botToken) {
    console.error("SLACK_BOT_TOKEN is not configured");
    return false;
  }

  if (!channel) {
    console.error("SLACK_NOTIFICATION_CHANNEL is not configured");
    return false;
  }

  if (posts.length === 0) {
    console.log("No posts to notify about");
    return true;
  }

  const today = new Date().toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });

  // 投稿詳細ページのURLを生成
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;
  
  // シンプルなメッセージ形式
  const postList = posts.map(post => 
    `• [${post.title}](${baseUrl}/posts/${post.id})`
  ).join('\n');

  const message: SlackMessage = {
    channel: channel as string,
    text: `📰 新規投稿 ${posts.length}件\n\n${postList}`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `📰 *新規投稿 ${posts.length}件*\n\n${postList}`
        }
      }
    ]
  };

  try {
    const response = await fetch("https://slack.com/api/chat.postMessage", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${botToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    const result = await response.json();
    
    if (!result.ok) {
      console.error("Failed to send daily summary notification:", result.error);
      return false;
    }

    console.log("Daily summary notification sent successfully");
    return true;
  } catch (error) {
    console.error("Error sending daily summary notification:", error);
    return false;
  }
}

export async function sendPostNotification(data: PostNotificationData): Promise<boolean> {
  const botToken = process.env.SLACK_BOT_TOKEN;
  const channel = process.env.SLACK_NOTIFICATION_CHANNEL;
  
  if (!botToken) {
    console.error("SLACK_BOT_TOKEN is not configured");
    return false;
  }

  if (!channel) {
    console.error("SLACK_NOTIFICATION_CHANNEL is not configured");
    return false;
  }

  // 投稿詳細ページのURLを生成
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || process.env.VERCEL_URL || 'http://localhost:3000';
  const postDetailUrl = `${baseUrl}/posts/${data.postId}`;

  const message: SlackMessage = {
    channel: channel as string,
    text: `📝 新しい投稿: ${data.title}`,
    blocks: [
      {
        type: "section",
          text: {
            type: "mrkdwn",
            text: `📝 *新しい投稿が作成されました*\n\n*タイトル:* ${data.title}\n*投稿者:* ${data.authorName || data.authorEmail}`
          }
      },
      ...(data.content ? [{
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*コメント:*\n${data.content.length > 300 ? data.content.substring(0, 300) + "..." : data.content}`
        }
      }] : []),
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: {
              type: "plain_text",
              text: "記事を確認する"
            },
            url: postDetailUrl,
            style: "primary"
          }
        ]
      }
    ]
  };

  try {
    const response = await fetch("https://slack.com/api/chat.postMessage", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${botToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    const result = await response.json();
    
    if (!result.ok) {
      console.error("Failed to send post notification:", result.error);
      return false;
    }

    console.log("Post notification sent successfully");
    return true;
  } catch (error) {
    console.error("Error sending post notification:", error);
    return false;
  }
}
