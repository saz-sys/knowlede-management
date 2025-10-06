export const env = {
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
  supabaseAnonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
  slackBotToken: process.env.SLACK_BOT_TOKEN ?? "",
  slackNotificationChannel: process.env.SLACK_NOTIFICATION_CHANNEL ?? ""
};
