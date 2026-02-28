import asyncio
from telethon import TelegramClient, events
from flask import Flask
import threading

# --- CONFIGURATION ---
API_ID = 36767235
API_HASH = "6a36bf6c4b15e7eecdb20885a13fc2d7"
BOT_TOKEN = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"
OWNER_ID = 7844678082  # Seul vrai owner

# --- LISTES ---
whitelist = {OWNER_ID}  # Seuls les membres de la whitelist peuvent utiliser le bot
owners = {OWNER_ID}

# --- INITIALISATION DU BOT ---
client = TelegramClient('bot', API_ID, API_HASH)

# --- FLASK SERVER (pour Render) ---
app = Flask("")

@app.route("/")
def home():
    return "Bot en ligne !"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# Flask dans un thread séparé
threading.Thread(target=run_flask).start()

# --- FONCTIONS UTILES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

# --- COMMANDES ---
@client.on(events.NewMessage(pattern=r'\.start'))
async def start(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply(
        "👋 Salut ! Commandes disponibles :\n"
        ".info @\n"
        ".say (texte)\n"
        ".pic @\n"
        ".wakeup @\n"
        ".ping\n"
        ".wl @\n"
        ".unwl @\n"
        ".clear wl\n"
        ".owner @\n"
        ".unowner @\n"
        ".whitelist"
    )

@client.on(events.NewMessage(pattern=r'\.say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    message = event.pattern_match.group(1)
    await event.delete()
    await event.respond(message)

@client.on(events.NewMessage(pattern=r'\.pic @(\w+)'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    if user.photo:
        await event.reply(file=user.photo)

@client.on(events.NewMessage(pattern=r'\.info @(\w+)'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    bot_status = "Oui" if user.bot else "Non"
    await event.reply(f"Nom: {user.first_name}\nUsername: @{username}\nID: {user.id}\nBot: {bot_status}")

@client.on(events.NewMessage(pattern=r'\.wakeup @(\w+)'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    username = event.pattern_match.group(1)
    for _ in range(10):  # 10 pings
        await event.reply(f"⏰ Réveille-toi sale pute @{username} !")
        await asyncio.sleep(2)

@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

# --- WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern=r'\.wl @(\w+)'))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    whitelist.add(user.id)
    await event.reply(f"✅ @{username} ajouté à la whitelist")

@client.on(events.NewMessage(pattern=r'\.unwl @(\w+)'))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    whitelist.discard(user.id)
    await event.reply(f"❌ @{username} retiré de la whitelist")

@client.on(events.NewMessage(pattern=r'\.clear wl'))
async def clear_wl(event):
    if not check_owner(event.sender_id):
        return
    whitelist.clear()
    whitelist.add(OWNER_ID)
    await event.reply("✅ Tous les utilisateurs ont été retirés de la whitelist")

@client.on(events.NewMessage(pattern=r'\.owner @(\w+)'))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    owners.add(user.id)
    whitelist.add(user.id)
    await event.reply(f"✅ @{username} ajouté aux owners")

@client.on(events.NewMessage(pattern=r'\.unowner @(\w+)'))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    owners.discard(user.id)
    whitelist.discard(user.id)
    await event.reply(f"❌ @{username} retiré des owners et whitelist")

@client.on(events.NewMessage(pattern=r'\.whitelist'))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return
    msg = "Owners :\n"
    for uid in owners:
        user = await client.get_entity(uid)
        msg += f"- @{user.username} ({user.first_name})\n"
    msg += "\nWhitelist :\n"
    for uid in whitelist:
        if uid in owners:
            continue
        user = await client.get_entity(uid)
        msg += f"- @{user.username} ({user.first_name})\n"
    await event.reply(msg)

# --- DÉMARRAGE DU BOT ---
async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("Bot démarré…")
    await client.run_until_disconnected()

asyncio.run(main())
