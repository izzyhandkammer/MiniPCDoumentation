import logging
import os

import aiohttp
import discord
from aiohttp import web
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "").strip()
CORTEX_FQDN = os.getenv("CORTEX_FQDN", "").strip()
CORTEX_API_KEY_ID = os.getenv("CORTEX_API_KEY_ID", "").strip()
CORTEX_API_KEY = os.getenv("CORTEX_API_KEY", "").strip()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("soc_bot")


def _mask_secret(s: str) -> str:
    if not s:
        return "<missing>"
    try:
        s = str(s)
    except Exception:
        return "<redacted>"
    if len(s) <= 8:
        return s[:2] + "..." + s[-2:]
    return s[:4] + "..." + s[-4:]


class SOCBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

        app = web.Application()
        app.router.add_post("/webhook", self.handle_webhook)
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", 5000)
        await site.start()
        logger.info("Webhook server is running on port 5000 (Endpoint: /webhook)")

    async def handle_webhook(self, request):
        try:
            data = await request.json(content_type=None)
            logger.info("Received webhook data: %s", data)

            alert_id = data.get("alert_id") or data.get("id") or "unknown"
            description = data.get("description") or data.get("message") or "No description provided."
            severity = str(data.get("severity", "Unknown")).strip() or "Unknown"
            title = data.get("title") or f"New Alert: {alert_id}"

            try:
                channel = await self.fetch_channel(int(DISCORD_CHANNEL_ID))
            except (ValueError, discord.NotFound, discord.Forbidden) as exc:
                logger.warning("Unable to access Discord channel %s: %s", DISCORD_CHANNEL_ID, exc)
                return web.Response(text="Discord channel not found or inaccessible", status=404)

            embed = discord.Embed(
                title=title,
                description=description,
                color=(
                    discord.Color.red()
                    if severity.lower() in {"high", "critical", "urgent"}
                    else discord.Color.orange()
                    if severity.lower() in {"medium", "low", "warning"}
                    else discord.Color.dark_gray()
                ),
            )
            embed.add_field(name="Alert ID", value=str(alert_id), inline=True)
            embed.add_field(name="Severity", value=severity, inline=True)
            embed.add_field(name="Description", value=description, inline=False)
            embed.set_footer(text="Resolve this alert by typing: /resolve <alert_id>")

            await channel.send(embed=embed)
            return web.Response(text="Discord channel notified successfully", status=200)

        except Exception as exc:
            logger.exception("Error handling webhook")
            return web.Response(text="Internal Server Error", status=500)


client = SOCBot()


@client.event
async def on_ready():
    logger.info("SOC Bot is ready! Logged in as %s", client.user)


@client.tree.command(name="resolve", description="Resolve an alert in Cortex XDR")
@app_commands.describe(alert_id="The ID of the alert to resolve")
async def resolve(interaction: discord.Interaction, alert_id: str):
    # Defer the response and give immediate feedback in logs/console for debugging
    await interaction.response.defer(ephemeral=True)

    print(f"[SOC-BOT] /resolve invoked for alert_id={alert_id}")
    logger.info("/resolve invoked for alert_id=%s", alert_id)

    # Show masked Cortex credential presence for debugging (do not reveal secrets)
    print(
        "[SOC-BOT] Cortex config: FQDN=%s, API_KEY_ID=%s, API_KEY=%s"
        % (CORTEX_FQDN or "<missing>", _mask_secret(CORTEX_API_KEY_ID), _mask_secret(CORTEX_API_KEY))
    )

    if not all([CORTEX_FQDN, CORTEX_API_KEY_ID, CORTEX_API_KEY]):
        print("[SOC-BOT] Cortex credentials missing; aborting resolve.")
        await interaction.followup.send("Cortex credentials are not configured.", ephemeral=True)
        return

    url = f"https://{CORTEX_FQDN}/public_api/v1/incidents/update_incident"
    headers = {
        "Authorization": CORTEX_API_KEY,
        "x-xdr-auth-id": CORTEX_API_KEY_ID,
        "content-type": "application/json",
    }

    payload = {
        "request_data": {
            "alert_id_list": [alert_id],
            "update_data": {
                "status": "resolved",
                "resolution_reason": "Resolved via Discord SOC Bot",
            },
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            print(f"[SOC-BOT] Sending request to Cortex XDR: {url}")
            print(f"[SOC-BOT] Payload: {payload}")
            logger.info("Sending Cortex request for alert_id=%s", alert_id)

            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                # Try to read JSON safely; fall back to text on failure
                try:
                    response_data = await response.json(content_type=None)
                except Exception:
                    response_text = await response.text()
                    response_data = {"raw": response_text}

                print(
                    f"[SOC-BOT] Cortex response status={response.status}, data={response_data}"
                )
                logger.info(
                    "Cortex response for alert_id=%s: status=%s",
                    alert_id,
                    response.status,
                )

                if response.status < 400:
                    await interaction.followup.send(
                        f"Alert {alert_id} marked as resolved.",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        f"Failed to resolve alert: {response_data}",
                        ephemeral=True,
                    )
    except Exception as exc:
        logger.exception("Failed to resolve alert")
        print(f"[SOC-BOT] Exception while resolving alert {alert_id}: {exc}")
        await interaction.followup.send(f"Failed to resolve alert: {exc}", ephemeral=True)


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN is missing. Set it in your .env file.")
        raise SystemExit(1)

    client.run(DISCORD_BOT_TOKEN)