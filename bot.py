import discord
import os
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import tasks
from holiday_fetcher import get_upcoming_holidays
from zoneinfo import ZoneInfo  # Python 3.9+

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes=1)
async def daily_feiertags_check():
    await client.wait_until_ready()
    now_berlin = datetime.now(ZoneInfo("Europe/Berlin"))

    # Nur um 08:00 Uhr Berliner Zeit ausführen
    if now_berlin.hour == 8 and now_berlin.minute == 0:
        channel = client.get_channel(CHANNEL_ID)

        # Erinnerung 2 Tage vorher
        upcoming = get_upcoming_holidays(["DE", "US"], days_ahead=2)
        if upcoming:
            msg_lines = ["📌 **Feiertags-Erinnerung in 2 Tagen:**"]
            for code, local, eng, date_str in upcoming:
                flag = ":flag_de:" if code == "DE" else ":flag_us:"
                msg_lines.append(f"{flag} **{local}** ({eng}) – am {date_str}")
            await channel.send("\n".join(msg_lines))

        # Hinweis am Feiertag selbst
        today = get_upcoming_holidays(["DE", "US"], days_ahead=0)
        if today:
            msg_lines = ["⚠️ **Bitte beachten: Heute ist ein Feiertag!**"]
            for code, local, eng, date_str in today:
                flag = ":flag_de:" if code == "DE" else ":flag_us:"
                msg_lines.append(f"{flag} **{local}** ({eng}) – heute ({date_str})")
            msg_lines.append("🏢 **Hinweis:** Heute kann es zu eingeschränktem oder gar keinem Betrieb kommen.")
            await channel.send("\n".join(msg_lines))

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
            msg_lines = ["📌 **Feiertags-Erinnerung in 2 Tagen:**"]
            for code, local, eng, date_str in holidays:
                flag = ":flag_de:" if code == "DE" else ":flag_us:"
                msg_lines.append(f"{flag} **{local}** ({eng}) – am {date_str}")
        else:
            msg_lines = ["In 2 Tagen ist kein Feiertag in Deutschland oder den USA."]
        await message.channel.send("\n".join(msg_lines))

client.run(TOKEN)
