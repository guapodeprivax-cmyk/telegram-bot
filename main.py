import asyncio
import threading
from telethon import TelegramClient, events
from flask import Flask

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

# --- FONCTIONS UTILES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

# --- COMMANDES ---
@client.on(events.NewMessage(pattern=r'\.info'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply(
        ".info\n.say texte\n.pic\n.wakeup\n.ping\n.wl ID\n.unwl ID\n.owner ID\n.unowner ID\n.whitelist"
    )

@client.on(events.NewMessage(pattern=r'\.say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    message = event.text[len(".say "):]  # texte après .say
    await event.delete()                 # supprime le message original
    await event.reply(message)           # renvoie le texte

@client.on(events.NewMessage(pattern=r'\.pic'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("📸")  # tu peux mettre un lien ou une image ici

@client.on(events.NewMessage(pattern=r'\.wakeup'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    user_mention = f"@{event.sender.username}" if event.sender.username else event.sender.first_name
    for _ in range(10):  # 10 pings
        await event.reply(f"⏰ Lève-toi {user_mention} !")
        await asyncio.sleep(2)

@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

# --- GESTION WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern=r'\.wl (\d+)'))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.add(target)
    await event.reply(f"✅ {target} ajouté à la whitelist")

@client.on(events.NewMessage(pattern=r'\.unwl (\d+)'))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    target = int(event.pattern_match.group(1))
    whitelist.discard(target)
    await event.reply(f"❌ {target} retiré de la whitelist")

@client.on(events.NewMessage(pattern=r'\.owner (\d+)'))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.add(target)
    await event.reply(f"✅ {target} ajouté aux owners")

@client.on(events.NewMessage(pattern=r'\.unowner (\d+)'))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    target = int(event.pattern_match.group(1))
    owners.discard(target)
    await event.reply(f"❌ {target} retiré des owners")

@client.on(events.NewMessage(pattern=r'\.whitelist'))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return
    msg = "Whitelist :\n" + "\n".join(str(uid) for uid in whitelist)
    msg += "\n\nOwners :\n" + "\n".join(str(uid) for uid in owners)
    await event.reply(msg)

# --- FLASK POUR GARDER LE BOT EN LIGNE ---
app = Flask("")

@app.route("/")
def home():
    return "Bot en ligne !"

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# --- LANCEMENT ---
if __name__ == "__main__":
    # Flask dans un thread séparé
    threading.Thread(target=run_flask).start()
    
    # Lancer le bot Telethon
    client.start(bot_token=BOT_TOKEN)
    print("Bot démarré…")
    client.run_until_disconnected()
