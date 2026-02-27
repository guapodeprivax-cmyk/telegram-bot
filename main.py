from telethon import TelegramClient, events
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

# ----------------- CONFIG BOT -----------------
api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8575952878:AAGRVJ6a7kBoQbVyJM7Oy3OLV7zB2XYox7M"

client = TelegramClient("bot", api_id, api_hash)

sniped = {}  # dernier message supprimé par chat

# ----------------- EVENT MESSAGES -----------------
# Sauvegarde les messages supprimés pour .snipe
@client.on(events.MessageDeleted)
async def handler(event):
    for msg in event.deleted:
        if msg.text:
            sniped[event.chat_id] = msg.text

# ----------------- COMMANDES -----------------
@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    # Ignore le message .snipe lui-même
    if event.chat_id in sniped:
        await event.reply(sniped[event.chat_id])
    else:
        await event.reply("💬 Aucun message supprimé récemment.")

@client.on(events.NewMessage(pattern=r"\.clear (.+)"))
async def clear(event):
    target = event.pattern_match.group(1)
    deleted = 0

    if target.startswith("@"):
        # Supprime tous les messages envoyés par l'utilisateur (@username)
        try:
            user = await client.get_entity(target)
            msgs = await client.get_messages(event.chat_id, limit=100)  # max 100 derniers messages
            for msg in msgs:
                if msg.sender_id == user.id:
                    try:
                        await client.delete_messages(event.chat_id, msg)
                        deleted += 1
                    except:
                        pass
            await event.reply(f"✅ Supprimé {deleted} messages de {target}")
        except:
            await event.reply("❌ Utilisateur introuvable.")
    else:
        # Supprime les n derniers messages
        try:
            n = int(target)
            # ignore le message .clear lui-même
            msgs = await client.get_messages(event.chat_id, limit=n+1)
            msgs_to_delete = [msg for msg in msgs if msg.id != event.id]
            for msg in msgs_to_delete:
                try:
                    await client.delete_messages(event.chat_id, msg)
                    deleted += 1
                except:
                    pass
            await event.reply(f"✅ Supprimé {deleted} messages")
        except:
            await event.reply("❌ Nombre invalide.")

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
