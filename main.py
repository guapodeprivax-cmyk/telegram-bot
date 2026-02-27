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

# ----------------- DATA -----------------
sniped = {}  # dernier message supprimé par chat
messages_cache = {}  # cache messages pour snipe
muted_users = {}  # chat_id -> {user_id: unmute_time}
original_permissions = {}  # chat_id -> {user_id: can_send_messages}
banned_users = {}  # chat_id -> set(user_id)

# ----------------- EVENT MESSAGES -----------------
@client.on(events.NewMessage)
async def cache_messages(event):
    chat_id = event.chat_id
    if chat_id not in messages_cache:
        messages_cache[chat_id] = []
    messages_cache[chat_id].append(event.message)
    if len(messages_cache[chat_id]) > 100:
        messages_cache[chat_id].pop(0)

# ----------------- AUTO UNMUTE -----------------
async def auto_unmute_loop():
    while True:
        for chat_id in list(muted_users.keys()):
            to_remove = []
            for user_id, unmute_time in muted_users[chat_id].items():
                if datetime.utcnow() >= unmute_time:
                    can_send = True
                    if chat_id in original_permissions and user_id in original_permissions[chat_id]:
                        can_send = original_permissions[chat_id][user_id]
                        del original_permissions[chat_id][user_id]
                    rights = ChatBannedRights(until_date=None, send_messages=not can_send)
                    try:
                        await client(EditBannedRequest(chat_id, user_id, rights))
                    except:
                        pass
                    to_remove.append(user_id)
            for uid in to_remove:
                del muted_users[chat_id][uid]
            if not muted_users[chat_id]:
                del muted_users[chat_id]
        await asyncio.sleep(5)

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

# MUTE
@client.on(events.NewMessage(pattern=r"\.mute (@\w+) (\d+)([smhd])"))
async def mute(event):
    target_username = event.pattern_match.group(1)
    amount = int(event.pattern_match.group(2))
    unit = event.pattern_match.group(3)

    multiplier = {"s":1, "m":60, "h":3600, "d":86400}
    duration = amount * multiplier.get(unit, 0)

    if duration > 3600:
        await event.reply("❌ Temps maximal de mute : 1 heure")
        duration = 3600
        amount = 1
        unit = "h"

    until = datetime.utcnow() + timedelta(seconds=duration)

    try:
        user = await client.get_entity(target_username)
        perms = await client.get_permissions(event.chat_id, user.id)
        can_send = perms.send_messages
        if event.chat_id not in original_permissions:
            original_permissions[event.chat_id] = {}
        original_permissions[event.chat_id][user.id] = can_send

        rights = ChatBannedRights(until_date=until, send_messages=True)
        await client(EditBannedRequest(event.chat_id, user.id, rights))

        if event.chat_id not in muted_users:
            muted_users[event.chat_id] = {}
        muted_users[event.chat_id][user.id] = until

        await event.reply(f"✅ {target_username} mute pour {amount}{unit}")
    except Exception as e:
        await event.reply(f"❌ Impossible de mute : {e}")

# UNMUTE
@client.on(events.NewMessage(pattern=r"\.unmute (@\w+)"))
async def unmute(event):
    target_username = event.pattern_match.group(1)
    try:
        user = await client.get_entity(target_username)
        can_send = True
        if event.chat_id in original_permissions and user.id in original_permissions[event.chat_id]:
            can_send = original_permissions[event.chat_id][user.id]
            del original_permissions[event.chat_id][user.id]
        rights = ChatBannedRights(until_date=None, send_messages=not can_send)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        if event.chat_id in muted_users and user.id in muted_users[event.chat_id]:
            del muted_users[event.chat_id][user.id]
        await event.reply(f"✅ {target_username} unmute")
    except Exception as e:
        await event.reply(f"❌ Impossible de unmute : {e}")

# UNMUTEALL
@client.on(events.NewMessage(pattern=r"\.unmuteall"))
async def unmuteall(event):
    chat_id = event.chat_id
    if chat_id in muted_users:
        for user_id in list(muted_users[chat_id].keys()):
            can_send = True
            if chat_id in original_permissions and user_id in original_permissions[chat_id]:
                can_send = original_permissions[chat_id][user_id]
                del original_permissions[chat_id][user_id]
            rights = ChatBannedRights(until_date=None, send_messages=not can_send)
            try:
                await client(EditBannedRequest(chat_id, user_id, rights))
            except:
                pass
        del muted_users[chat_id]
        await event.reply("✅ Tous les utilisateurs ont été unmute")
    else:
        await event.reply("Aucun utilisateur mute actuellement")

# MUTELIST
@client.on(events.NewMessage(pattern=r"\.mutelist"))
async def mutelist(event):
    chat_id = event.chat_id
    if chat_id in muted_users and muted_users[chat_id]:
        msg = "🔇 Utilisateurs mute actuellement :\n"
        for uid, until in muted_users[chat_id].items():
            user = await client.get_entity(uid)
            remaining = until - datetime.utcnow()
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            msg += f"- @{user.username} pendant {minutes}m {seconds}s\n"
        await event.reply(msg)
    else:
        await event.reply("Aucun utilisateur mute actuellement.")

# WAKEUP
@client.on(events.NewMessage(pattern=r"\.wakeup (@\w+)"))
async def wakeup(event):
    target_username = event.pattern_match.group(1)
    try:
        user = await client.get_entity(target_username)
        for i in range(10):
            await event.reply(f"{target_username} ⏰ Wake up! ({i+1}/10)")
            await asyncio.sleep(0.5)
    except Exception as e:
        await event.reply(f"❌ Impossible de wakeup : {e}")

# BAN
@client.on(events.NewMessage(pattern=r"\.ban (@\w+)"))
async def ban(event):
    target_username = event.pattern_match.group(1)
    try:
        user = await client.get_entity(target_username)
        rights = ChatBannedRights(until_date=None, send_messages=True, view_messages=True)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        if event.chat_id not in banned_users:
            banned_users[event.chat_id] = set()
        banned_users[event.chat_id].add(user.id)
        await event.reply(f"⛔ {target_username} a été banni du chat")
    except Exception as e:
        await event.reply(f"❌ Impossible de ban : {e}")

# UNBAN
@client.on(events.NewMessage(pattern=r"\.unban (@\w+)"))
async def unban(event):
    target_username = event.pattern_match.group(1)
    try:
        user = await client.get_entity(target_username)
        rights = ChatBannedRights(until_date=None, send_messages=False, view_messages=False)
        await client(EditBannedRequest(event.chat_id, user.id, rights))
        if event.chat_id in banned_users and user.id in banned_users[event.chat_id]:
            banned_users[event.chat_id].remove(user.id)
        await event.reply(f"✅ {target_username} a été débanni")
    except Exception as e:
        await event.reply(f"❌ Impossible de unban : {e}")

# UNBANALL
@client.on(events.NewMessage(pattern=r"\.unbanall"))
async def unbanall(event):
    chat_id = event.chat_id
    if chat_id in banned_users and banned_users[chat_id]:
        for user_id in list(banned_users[chat_id]):
            rights = ChatBannedRights(until_date=None, send_messages=False, view_messages=False)
            try:
                await client(EditBannedRequest(chat_id, user_id, rights))
            except:
                pass
        banned_users[chat_id].clear()
        await event.reply("✅ Tous les utilisateurs bannis ont été débannis")
    else:
        await event.reply("Aucun utilisateur n’est banni actuellement")

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
    asyncio.create_task(auto_unmute_loop())
    await client.run_until_disconnected()

asyncio.run(main())
