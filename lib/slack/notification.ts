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

  // メンション用のテキストを生成（@ユーザー名の形式）
  const mentionText = data.postAuthorName ? `@${data.postAuthorName}` : data.postAuthorEmail;
  
  const message: SlackMessage = {
    channel: channel as string,
    text: `💬 新しいコメントが投稿されました: ${data.postTitle}`,
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: "💬 新しいコメントが投稿されました"
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
