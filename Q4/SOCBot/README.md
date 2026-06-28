# SOC Bot

SOC Bot is a Discord-based security operations assistant for posting Cortex XDR alerts to a Discord channel and resolving them with a `/resolve` slash command.

## Setup

1. Create a Discord application and bot in the Discord Developer Portal.
2. Enable `Message Content Intent` under the Bot settings.
3. Invite the bot to your Discord server with the following OAuth2 scopes:
   - `bot`
   - `applications.commands`
4. Ensure the bot role has permission to send messages and embed links in the target channel.

## Configuration

Create a `.env` file in the project root with:

```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_target_channel_id
CORTEX_FQDN=your_xdr_host
CORTEX_API_KEY_ID=your_xdr_api_key_id
CORTEX_API_KEY=your_xdr_api_key
```

- `DISCORD_BOT_TOKEN`: bot token from the Developer Portal.
- `DISCORD_CHANNEL_ID`: numeric Discord channel ID where alerts should be posted.
- `CORTEX_FQDN`, `CORTEX_API_KEY_ID`, and `CORTEX_API_KEY`: used by the `/resolve` command to update alerts in Cortex XDR.

## Running

Install dependencies and run the bot:

```bash
python -m pip install -r requirements.txt
python soc-bot.py
```

## XDR Webhook Payload

The bot receives alert data via HTTP POST to `/webhook` and expects JSON with these fields:

- `alert_id` or `id`
- `title`
- `description` or `message`
- `severity`

Example payload:

```json
{
  "alert_id": "12345",
  "title": "Malicious process detected",
  "description": "A suspicious process spawned network activity.",
  "severity": "High"
}
```

## Usage

- The bot posts alerts to the configured Discord channel as embedded messages.
- Use `/resolve <alert_id>` in Discord to resolve the alert in Cortex XDR.

## Notes

- The bot currently uses a text-only integration path: alerts are posted to Discord and resolved via slash commands.
- Slash command registration may take a few minutes to appear after the bot starts.
