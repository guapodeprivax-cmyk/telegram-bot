import asyncio
from telethon import TelegramClient, events

# --- CONFIGURATION ---
API_ID = 36767235
API_HASH = "6a36bf6c4b15e7eecdb20885a13fc2d7"
BOT_TOKEN = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"
OWNER_ID = 7844678082  # ton ID Telegram, seul owner

# --- LISTES ---
whitelist = {OWNER_ID}  # seuls les membres de la whitelist peuvent utiliser le bot
owners = {OWNER_ID}

# --- TELETHON CLIENT ---
client = TelegramClient('bot', API_ID, API_HASH)

# --- UTILITAIRES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

# --- COMMANDES ---
@client.on(events.NewMessage(pattern=r'/info'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("/ping, /wakeup, /say, /pic, /wl, /unwl, /owner, /unowner, /whitelist")

@client.on(events.NewMessage(pattern=r'/ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

@client.on(events.NewMessage(pattern=r'/say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    msg = event.pattern_match.group(1)
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'/pic'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("📸")

@client.on(events.NewMessage(pattern=r'/wakeup'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    user_mention = f"@{event.sender.username}" if event.sender.username else event.sender.first_name
    for _ in range(10):  # 10 pings
        await event.reply(f"⏰ Lève-toi {user_mention} !")
        await asyncio.sleep(2)

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
    msg = "Whitelist :\n" + "\n".join(str(u) for u in whitelist)
    msg += "\n\nOwners :\n" + "\n".join(str(u) for u in owners)
    await event.reply(msg)

# --- DÉMARRAGE DU BOT ---
print("Bot démarré…")
asyncio.run(client.start(bot_token=BOT_TOKEN))
client.run_until_disconnected()
