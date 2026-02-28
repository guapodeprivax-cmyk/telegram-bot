# main.py
import asyncio
from telethon import TelegramClient, events

# --- CONFIGURATION ---
api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

# --- UTILISATEURS ---
OWNER_ID = 7844678082
owners = {OWNER_ID}
whitelist = set()  # les users ajoutés via /wl pourront utiliser le bot

# --- CLIENT TELETHON ---
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# --- COMMANDES ---
# Info
@client.on(events.NewMessage(pattern='/info'))
async def info(event):
    if event.sender_id not in whitelist:
        return
    await event.respond("Ceci est un bot avec commandes : /ping, /say, /pic, /wakeup, /wl, /unwl, /owner, /unowner, /whitelist")

# Say
@client.on(events.NewMessage(pattern='/say (.+)'))
async def say(event):
    if event.sender_id not in whitelist:
        return
    message = event.pattern_match.group(1)
    await event.respond(message)

# Pic
@client.on(events.NewMessage(pattern='/pic'))
async def pic(event):
    if event.sender_id not in whitelist:
        return
    await event.respond("📸")

# Wakeup
@client.on(events.NewMessage(pattern='/wakeup'))
async def wakeup(event):
    if event.sender_id not in whitelist:
        return
    username = f"@{event.sender.username}" if event.sender.username else ""
    await event.respond(f"⏰ Lève-toi {username} !")

# --- GESTION WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern='/wl (\d+)'))
async def wl(event):
    if event.sender_id not in owners:
        return
    target = int(event.pattern_match.group(1))
    whitelist.add(target)
    await event.respond(f"✅ {target} ajouté à la whitelist")

@client.on(events.NewMessage(pattern='/unwl (\d+)'))
async def unwl(event):
    if event.sender_id not in owners:
        return
    target = int(event.pattern_match.group(1))
    whitelist.discard(target)
    await event.respond(f"❌ {target} retiré de la whitelist")

@client.on(events.NewMessage(pattern='/owner (\d+)'))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.add(target)
    await event.respond(f"✅ {target} ajouté aux owners")

@client.on(events.NewMessage(pattern='/unowner (\d+)'))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.discard(target)
    await event.respond(f"❌ {target} retiré des owners")

@client.on(events.NewMessage(pattern='/whitelist'))
async def whitelist_cmd(event):
    if event.sender_id not in owners:
        return
    msg = "Whitelist :\n"
    for uid in whitelist:
        msg += f"- {uid}\n"
    msg += "\nOwners :\n"
    for uid in owners:
        msg += f"- {uid}\n"
    await event.respond(msg)

# Ping
@client.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    if event.sender_id not in whitelist:
        return
    await event.respond("🏓 Pong !")

# --- LANCEMENT DU BOT ---
async def main():
    print("Bot prêt…")
    await client.run_until_disconnected()

asyncio.run(main())
