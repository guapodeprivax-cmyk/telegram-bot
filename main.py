from telethon import TelegramClient, events

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
    msgs = await client.get_messages(event.chat_id, limit=n + 1)
    await client.delete_messages(event.chat_id, msgs)


@client.on(events.NewMessage(pattern=r"\.pic (.+)"))
async def pic(event):
    user = await client.get_entity(event.pattern_match.group(1))
    photos = await client.get_profile_photos(user)
    if photos:
        await client.send_file(event.chat_id, photos[0])


@client.on(events.NewMessage(pattern=r"\.info (.+)"))
async def info(event):
    user = await client.get_entity(event.pattern_match.group(1))
    await event.reply(
        f"Nom: {user.first_name}\n"
        f"Username: @{user.username}\n"
        f"ID: {user.id}"
    )

client.start(bot_token=bot_token)
client.run_until_disconnected()
