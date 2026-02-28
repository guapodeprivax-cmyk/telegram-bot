from telethon import TelegramClient, events

# --- CONFIGURATION ---
api_id = 36767235          # ton API ID
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"  # ton API hash
bot_token = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"  # token du bot

OWNER_ID = 7844678082      # ton ID

# --- LISTES ---
whitelist = set()          # IDs autorisés à utiliser le bot
owners = {OWNER_ID}

# --- INITIALISATION DU CLIENT ---
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# --- FONCTIONS ---
def check_whitelist(user_id):
    return user_id in whitelist or user_id in owners

def check_owner(user_id):
    return user_id in owners

# --- COMMANDES ---
@client.on(events.NewMessage(pattern='/info'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("Ceci est un bot avec commandes: /info, /say, /pic, /wakeup, /ping")

@client.on(events.NewMessage(pattern='/say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    msg = event.pattern_match.group(1)
    await event.reply(msg)

@client.on(events.NewMessage(pattern='/pic'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("📸")

@client.on(events.NewMessage(pattern='/wakeup'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    # mention de la personne
    user = await event.get_sender()
    await event.reply(f"⏰ Lève-toi @{user.username if user.username else user.first_name} !")

@client.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

# --- WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern='/wl (\d+)'))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.add(target)
    await event.reply(f"✅ {target} ajouté à la whitelist")

@client.on(events.NewMessage(pattern='/unwl (\d+)'))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.discard(target)
    await event.reply(f"❌ {target} retiré de la whitelist")

@client.on(events.NewMessage(pattern='/whitelist'))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return
    msg = "Whitelist :\n" + "\n".join(str(uid) for uid in whitelist)
    msg += "\n\nOwners :\n" + "\n".join(str(uid) for uid in owners)
    await event.reply(msg)

# --- LANCEMENT DU BOT ---
print("Bot démarré...")
client.run_until_disconnected()
