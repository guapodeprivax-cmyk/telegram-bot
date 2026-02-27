from telethon import TelegramClient, events
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
from datetime import datetime, timedelta

# ----------------- CONFIG BOT -----------------
api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

client = TelegramClient("bot", api_id, api_hash)

sniped = {}  # dernier message supprimé par chat

# ----------------- EVENT MESSAGES -----------------
# Sauvegarde les messages supprimés pour .snipe
@client.on(events.MessageDeleted)
async def handler(event):
    for msg in event.deleted:
        if msg:  # On s'assure que le message existe
            author = msg.sender.username if msg.sender and msg.sender.username else (msg.sender.first_name if msg.sender else "Inconnu")
            content = ""
            if msg.text:
                content = msg.text
            elif msg.media:
                content = "[Media supprimé]"
            else:
                content = "[Message non textuel supprimé]"
            sniped[event.chat_id] = f"{author} : {content}"

# ----------------- COMMANDES -----------------
@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    if event.chat_id in sniped:
        await event.reply(f"(dernier message supprimé) @ : {sniped[event.chat_id]}")
    else:
        await event.reply("💬 Aucun message supprimé récemment.")

# ----------------- MUTE COMMAND -----------------
@client.on(events.NewMessage(pattern=r"\.mute (@\w+) (\d+)([smhd])"))
async def mute(event):
    target_username = event.pattern_match.group(1)
    amount = int(event.pattern_match.group(2))
    unit = event.pattern_match.group(3)

    # Convertir en secondes
    multiplier = {"s":1, "m":60, "h":3600, "d":86400}
    duration = amount * multiplier.get(unit, 0)
    until = datetime.utcnow() + timedelta(seconds=duration)

    try:
        user = await client.get_entity(target_username)
        rights = ChatBannedRights(
            until_date=until,
            send_messages=True  # interdit d'envoyer des messages
        )
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        await event.reply(f"✅ {target_username} mute pour {amount}{unit}")
    except Exception as e:
        await event.reply(f"❌ Impossible de mute : {e}")

# ----------------- AUTRES COMMANDES -----------------
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
        f"ID: {user.id}\n"
        f"Bot: {user.bot}"
    )

# ----------------- MINI SERVEUR POUR RENDER -----------------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web).start()

# ----------------- MAIN BOT LOOP -----------------
async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()

asyncio.run(main())
