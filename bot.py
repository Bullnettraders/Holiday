import discord
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord.ext import tasks
from holiday_fetcher import get_upcoming_holidays
from zoneinfo import ZoneInfo  # Nur ab Python 3.9+

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes=1)
async def daily_feiertags_check():
    await client.wait_until_ready()
    now_berlin = datetime.now(ZoneInfo("Europe/Berlin"))
    if now_berlin.hour == 8 and now_berlin.minute == 0:
        channel = client.get_channel(CHANNEL_ID)
        holidays = get_upcoming_holidays(["DE", "US"], days_ahead=2)
        if holidays:
            msg_lines = ["**Feiertags-Erinnerung in 2 Tagen:**"]
            for code, local, eng, date_str in holidays:
                flag = ":flag_de:" if code == "DE" else ":flag_us:"
                msg_lines.append(f"{flag} **{local}** ({eng}) – am {date_str}")
            msg = "\n".join(msg_lines)
        else:
            msg = "In 2 Tagen ist kein Feiertag in Deutschland oder den USA."

        await channel.send(msg)

@client.event
async def on_ready():
    print(f'{client.user} ist online!')
    if not daily_feiertags_check.is_running():
        daily_feiertags_check.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "!feiertag":
        holidays = get_upcoming_holidays(["DE", "US"], days_ahead=2)
        if holidays:
            msg_lines = ["**Feiertags-Erinnerung in 2 Tagen:**"]
            for code, local, eng, date_str in holidays:
                flag = ":flag_de:" if code == "DE" else ":flag_us:"
                msg_lines.append(f"{flag} **{local}** ({eng}) – am {date_str}")
            msg = "\n".join(msg_lines)
        else:
            msg = "In 2 Tagen ist kein Feiertag in Deutschland oder den USA."
        await message.channel.send(msg)

client.run(TOKEN)
