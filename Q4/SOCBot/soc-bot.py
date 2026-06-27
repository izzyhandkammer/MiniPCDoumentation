import json
import discord
from discord import app_commands
import aiohttp
from aiohttp import web
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
CORTEX_FQDN = os.getenv("CORTEX_FQDN")
CORTEX_API_KEY_ID = os.getenv("CORTEX_API_KEY_ID")
CORTEX_API_KEY = os.getenv("CORTEX_API_KEY")

class SOCBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        # Sync the command tree with Discord
        await self.tree.sync()

        # Start the web server for handling incoming requests
        app = web.Application()
        app.router.add_post("/webhook", self.handle_webhook)
        runner = web.AppRunner(app)
        await runner.setup()

        # Listen on all interfaces on port 5000
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        print("🔒 Webhook server is running on port 5000 (Endpoint: /webhook)")
    
    async def handle_webhook(self, request):
        try:
            data = await request.json()
            print(f"Received webhook data: {data}")

            # Map data from the webhook to the expected format
            alert_id = data.get("alert_id")
            description = data.get("description", "No description provided.")
            severity = data.get("severity", "Unknown")

            # Create an embed message for Discord
            channel = self.get_channel(int(DISCORD_CHANNEL_ID))
            if channel:
                embed = discord.Embed(
                    title=f"New Alert: {alert_id}",
                    description=description,
                    color=(
                        discord.Color.red()
                        if severity == "High"
                        else discord.Color.orange()
                        if severity == "Medium"
                        else discord.Color.dark_gray()
                    )
                )
                embed.add_field(name="Alert ID", value=alert_id, inline=True)
                embed.add_field(name="Severity", value=severity, inline=True)
                embed.add_field(name="Description", value=description, inline=False)
                embed.set_footer(text="Resolve this alert by typing: /resolve <alert_id>")

                await channel.send(embed=embed)
            return web.Response(text="Discord channel notified successfully", status=200)
    
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return web.Response(text="Internal Server Error", status=500)


client = SOCBot()

@client.event
async def on_ready():
    print(f"⚡️ SOC Bot is ready! Logged in as {client.user}")

# Define the /resolve slash command
@client.tree.command(name="resolve", description="Resolve an alert in Cortex XDR")
@app_commands.describe(alert_id="The ID of the alert to resolve")
async def resolve(interaction: discord.Interaction, alert_id: str):
    await interaction.response.defer(ephemeral=True)

    url = f"https://{CORTEX_FQDN}/public_api/v1/incidents/update_incident"

    headers = {
        "Authorization": CORTEX_API_KEY,
        "x-xdr-auth-id": CORTEX_API_KEY_ID,
        "content-type": "application/json"
    }

    payload = {
        "request_data": {
            "alert_id_list": [alert_id],
            "update_data": {
                "status": "resolved",
                "resolution_reason": "Resolved via Discord SOC Bot"

            }
        }
    }