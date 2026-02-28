import asyncio
import threading
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from flask import Flask

# --- CONFIGURATION ---
API_ID = 36767235
API_HASH = "6a36bf6c4b15e7eecdb20885a13fc2d7"
BOT_TOKEN = "8694942735:AAHmc0JEcKN6F1oANOtQkp5YNGpYzalLhf4"
OWNER_ID = 7844678082  # Ton ID

# --- LISTES ---
whitelist = {OWNER_ID}
owners = {OWNER_ID}

# --- INIT BOT ---
client = TelegramClient('bot', API_ID, API_HASH)

# --- UTILITAIRES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

async def get_user_info(username_or_mention):
    username_or_mention = username_or_mention.lstrip("@")
    try:
        user = await client.get_entity(username_or_mention)
        full = await client(GetFullUserRequest(user.id))
        return {
            "name": user.first_name,
            "username": f"@{user.username}" if user.username else "None",
            "id": user.id,
            "is_bot": user.bot
        }
    except:
        return None

# --- COMMANDES ---
@client.on(events.NewMessage(pattern=r'\.info(?: @?(\w+))?'))
async def info(event):
    if not check_whitelist(event.sender_id):
        return
    arg = event.pattern_match.group(1)
    if arg:
        info_user = await get_user_info(arg)
    else:
        info_user = await get_user_info(event.sender.username)
    if info_user:
        msg = f"Nom: {info_user['name']}\nUsername: {info_user['username']}\nID: {info_user['id']}\nBot: {info_user['is_bot']}"
        await event.reply(msg)
    else:
        await event.reply("Utilisateur introuvable")

@client.on(events.NewMessage(pattern=r'\.say (.+)'))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    message = event.text[len(".say "):]
    await event.delete()
    await event.reply(message)

@client.on(events.NewMessage(pattern=r'\.pic @?(\w+)'))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    if user.photo:
        await event.reply(file=await client.download_profile_photo(user))
    else:
        await event.reply("Pas de photo de profil")

@client.on(events.NewMessage(pattern=r'\.wakeup @?(\w+)'))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    mention = f"@{user.username}" if user.username else user.first_name
    for _ in range(10):
        await event.reply(f"⏰ Lève-toi {mention} !")
        await asyncio.sleep(2)

@client.on(events.NewMessage(pattern=r'\.ping'))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")

# --- WHITELIST / OWNER ---
@client.on(events.NewMessage(pattern=r'\.wl @?(\w+)'))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    whitelist.add(user.id)
    await event.reply(f"✅ {user.first_name} ({f'@{user.username}' if user.username else 'NoUsername'}) ajouté à la whitelist")

@client.on(events.NewMessage(pattern=r'\.unwl @?(\w+)'))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    whitelist.discard(user.id)
    await event.reply(f"❌ {user.first_name} ({f'@{user.username}' if user.username else 'NoUsername'}) retiré de la whitelist")

@client.on(events.NewMessage(pattern=r'\.clear wl'))
async def clear_wl(event):
    if not check_owner(event.sender_id):
        return
    whitelist.clear()
    whitelist.add(OWNER_ID)
    await event.reply("✅ La whitelist est vide")

@client.on(events.NewMessage(pattern=r'\.owner @?(\w+)'))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    owners.add(user.id)
    whitelist.add(user.id)
    await event.reply(f"✅ {user.first_name} ajouté aux owners et whitelist")

@client.on(events.NewMessage(pattern=r'\.unowner @?(\w+)'))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    username = event.pattern_match.group(1)
    user = await client.get_entity(username)
    owners.discard(user.id)
    whitelist.discard(user.id)
    await event.reply(f"❌ {user.first_name} retiré des owners et whitelist")

@client.on(events.NewMessage(pattern=r'\.whitelist'))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return
    msg = "Owners:\n" + "\n".join(
        [f"{await client.get_entity(uid).first_name} (@{(await client.get_entity(uid)).username if (await client.get_entity(uid)).username else 'NoUsername'})" for uid in owners]
    )
    msg += "\n\nWhitelist:\n" + "\n".join(
        [f"{await client.get_entity(uid).first_name} (@{(await client.get_entity(uid)).username if (await client.get_entity(uid)).username else 'NoUsername'})" for uid in whitelist if uid not in owners]
    )
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
    threading.Thread(target=run_flask).start()
    client.start(bot_token=BOT_TOKEN)
    print("Bot démarré…")
    client.run_until_disconnected()
