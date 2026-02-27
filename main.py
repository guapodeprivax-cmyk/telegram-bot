from telethon import TelegramClient, events
import asyncio

api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8575952878:AAGRVJ6a7kBoQbVyJM7Oy3OLV7zB2XYox7M"

client = TelegramClient("bot", api_id, api_hash)

sniped = {}

@client.on(events.NewMessage)
async def save(event):
    sniped[event.chat_id] = event.raw_text


@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    if event.chat_id in sniped:
        await event.reply(sniped[event.chat_id])


@client.on(events.NewMessage(pattern=r"\.clear (\d+)"))
async def clear(event):
    n = int(event.pattern_match.group(1))
    msgs = await client.get_messages(event.chat_id, limit=n+1)
    await client.delete_messages(event.chat_id, msgs)


async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()


asyncio.run(main())
