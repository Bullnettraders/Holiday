import discord
import os
import asyncio
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from holiday_fetcher import get_upcoming_holidays

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def daily_feiertags_check():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    
    while not client.is_closed():
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(hour=8))  # 8 Uhr morgens
        if now > target_time:
            target_time += timedelta(days=1)
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)

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

client.loop.create_task(daily_feiertags_check())
client.run(TOKEN)
