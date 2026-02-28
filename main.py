import asyncio
from telethon import TelegramClient, events

# --- CONFIGURATION ---
API_ID = 36767235
API_HASH = "6a36bf6c4b15e7eecdb20885a13fc2d7"
BOT_TOKEN = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

OWNER_ID = 7844678082  # Ton ID, seul vrai owner

# --- LISTES ---
whitelist = {OWNER_ID}  # Seuls les membres de la whitelist peuvent utiliser le bot
owners = {OWNER_ID}

# --- INITIALISATION DU BOT ---
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- FONCTIONS UTILES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

# --- COMMANDES ---
@client.on(events.NewMessage(pattern=r'/info'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("Commandes disponibles :\n/info\n/say\n/pic\n/wakeup\n/ping\n/wl\n/unwl\n/owner\n/unowner\n/whitelist")

@client.on(events.NewMessage(pattern=r'/say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    message = event.pattern_match.group(1)
    await event.reply(message)

@client.on(events.NewMessage(pattern=r'/pic'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("📸")  # Ici tu peux mettre un lien ou photo si tu veux

@client.on(events.NewMessage(pattern=r'/wakeup'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    user_mention = f"@{event.sender.username}" if event.sender.username else event.sender.first_name
    for _ in range(10):  # 10 pings
        await event.reply(f"⏰ Lève-toi {user_mention} !")
        await asyncio.sleep(2)  # pause 2s entre chaque ping

@client.on(events.NewMessage(pattern=r'/ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

# --- GESTION WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern=r'/wl (\d+)'))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.add(target)
    await event.reply(f"✅ {target} ajouté à la whitelist")

@client.on(events.NewMessage(pattern=r'/unwl (\d+)'))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.discard(target)
    await event.reply(f"❌ {target} retiré de la whitelist")

@client.on(events.NewMessage(pattern=r'/owner (\d+)'))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.add(target)
    await event.reply(f"✅ {target} ajouté aux owners")

@client.on(events.NewMessage(pattern=r'/unowner (\d+)'))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.discard(target)
    await event.reply(f"❌ {target} retiré des owners")

@client.on(events.NewMessage(pattern=r'/whitelist'))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return
    msg = "Whitelist :\n"
    for uid in whitelist:
        msg += f"- {uid}\n"
    msg += "\nOwners :\n"
    for uid in owners:
        msg += f"- {uid}\n"
    await event.reply(msg)

# --- DÉMARRAGE DU BOT ---
print("Bot démarré…")
client.run_until_disconnected()
