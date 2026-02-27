from telethon import TelegramClient, events
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import time

# ----------------- CONFIG BOT -----------------
api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

client = TelegramClient("bot", api_id, api_hash)

# ----------------- DATA -----------------
sniped = {}
messages_cache = {}
banned_users = {}

# ----------------- CACHE MESSAGES -----------------
@client.on(events.NewMessage)
async def cache_messages(event):
    chat_id = event.chat_id
    if chat_id not in messages_cache:
        messages_cache[chat_id] = []
    messages_cache[chat_id].append(event.message)
    if len(messages_cache[chat_id]) > 100:
        messages_cache[chat_id].pop(0)

# ----------------- MESSAGE DELETED SNIPE -----------------
@client.on(events.MessageDeleted)
async def handler(event):
    chat_id = event.chat_id
    if chat_id not in messages_cache:
        return
    for msg in event.deleted:
        cached = next((m for m in messages_cache[chat_id] if m.id == msg.id), None)
        if cached:
            author = cached.sender.username if cached.sender and cached.sender.username else (cached.sender.first_name if cached.sender else "Inconnu")
            content = cached.text if cached.text else "[Media supprimé]"
            sniped[chat_id] = f"{author} : {content}"

# ----------------- COMMANDES -----------------
# SNIPE
@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    if event.chat_id in sniped:
        await event.reply(f"(dernier message supprimé) @ : {sniped[event.chat_id]}")
    else:
        await event.reply("💬 Aucun message supprimé récemment.")

# PIC
@client.on(events.NewMessage(pattern=r"\.pic (.+)"))
async def pic(event):
    target = event.pattern_match.group(1)
    try:
        entity = int(target) if target.isdigit() else target
        user = await client.get_entity(entity)
        photos = await client.get_profile_photos(user)
        if photos:
            await client.send_file(event.chat_id, photos[0])
        else:
            await event.reply("❌ Pas de photo de profil trouvée.")
    except Exception as e:
        await event.reply(f"❌ Impossible de récupérer la photo : {e}")

# INFO
@client.on(events.NewMessage(pattern=r"\.info (.+)"))
async def info(event):
    target = event.pattern_match.group(1)
    try:
        entity = int(target) if target.isdigit() else target
        user = await client.get_entity(entity)
        await event.reply(
            f"Nom: {user.first_name}\n"
            f"Username: @{user.username if user.username else 'N/A'}\n"
            f"ID: {user.id}\n"
            f"Bot: {user.bot}"
        )
    except Exception as e:
        await event.reply(f"❌ Impossible de récupérer les infos : {e}")

# WAKEUP
@client.on(events.NewMessage(pattern=r"\.wakeup (.+)"))
async def wakeup(event):
    target = event.pattern_match.group(1)
    try:
        entity = int(target) if target.isdigit() else target
        user = await client.get_entity(entity)
        for i in range(10):
            await event.reply(f"{user.first_name} ⏰ Wake up! ({i+1}/10)")
            await asyncio.sleep(0.5)
    except Exception as e:
        await event.reply(f"❌ Impossible de wakeup : {e}")

# BAN
@client.on(events.NewMessage(pattern=r"\.ban (.+)"))
async def ban(event):
    target = event.pattern_match.group(1)
    try:
        entity = int(target) if target.isdigit() else target
        user = await client.get_entity(entity)
        rights = ChatBannedRights(until_date=None, send_messages=True, view_messages=True)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        if event.chat_id not in banned_users:
            banned_users[event.chat_id] = set()
        banned_users[event.chat_id].add(user.id)
        await event.reply(f"⛔ {user.first_name} a été banni du chat")
    except Exception as e:
        await event.reply(f"❌ Impossible de ban : {e}")

# UNBAN
@client.on(events.NewMessage(pattern=r"\.unban (.+)"))
async def unban(event):
    target = event.pattern_match.group(1)
    try:
        entity = int(target) if target.isdigit() else target
        user = await client.get_entity(entity)
        rights = ChatBannedRights(until_date=None, send_messages=False, view_messages=False)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        if event.chat_id in banned_users and user.id in banned_users[event.chat_id]:
            banned_users[event.chat_id].remove(user.id)
        await event.reply(f"✅ {user.first_name} a été débanni")
    except Exception as e:
        await event.reply(f"❌ Impossible de unban : {e}")

# SAY
@client.on(events.NewMessage(pattern=r"\.say (.+)"))
async def say(event):
    try:
        text = event.pattern_match.group(1)
        await event.delete()
        await event.respond(text)
    except Exception as e:
        await event.reply(f"❌ Impossible de répéter le message : {e}")

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

threading.Thread(target=run_web, daemon=True).start()

# ----------------- MAIN BOT LOOP -----------------
async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()

asyncio.run(main())
