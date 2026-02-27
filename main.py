from telethon import TelegramClient, events
import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ----------------- CONFIG BOT -----------------
api_id = 36767235
api_hash = "6a36bf6c4b15e7eecdb20885a13fc2d7"
bot_token = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

client = TelegramClient("bot", api_id, api_hash)

# ----------------- OWNER / PERMISSIONS -----------------
OWNER_ID = 7844678082  # Owner principal
owners = set([OWNER_ID])  # Owner secondaire possible via .owner
whitelist = {}  # {chat_id: set(user_id)}
clear_whitelist = {}  # {chat_id: set(user_id)}

BOT_LOGS = {}  # {chat_id: group_id}
MESSAGE_LOGS = {}  # {chat_id: group_id}

pending_config = {}  # {user_id: action}
bot_status = {}  # {chat_id: True/False} -> ON/OFF par groupe
sniped = {}  # {chat_id: {"sender_id": , "text": }} 

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

# ----------------- UTILS LOG -----------------
async def log_bot(event, text):
    gid = BOT_LOGS.get(str(event.chat_id))
    if gid:
        try:
            await client.send_message(gid, text)
        except:
            pass

async def log_message(event, text):
    gid = MESSAGE_LOGS.get(str(event.chat_id))
    if gid:
        try:
            await client.send_message(gid, text)
        except:
            pass

# ----------------- EVENT MESSAGE DELETE -----------------
@client.on(events.MessageDeleted)
async def handler(event):
    for msg in event.deleted:
        if msg.text:
            sniped[event.chat_id] = {"sender_id": msg.sender_id, "text": msg.text}
            await log_message(event, f"💬 Dernier message supprimé\nDe : {msg.sender_id}\nMessage : {msg.text}")

# ----------------- COMMANDES -----------------
@client.on(events.NewMessage(pattern=r"\.help"))
async def help_cmd(event):
    user_id = event.sender_id
    chat_id = str(event.chat_id)
    text = "**Commandes disponibles :**\n\n"

    if user_id in owners:
        text += (
            ".admin\n.owner @/id\n.unowner @/id\n"
            ".wl @/id\n.wl clear @/id\n.unwl @/id\n.wl list\n"
            ".perm\n.dashboard\n.config logs\n.config offlogs\n.config message\n.config offmessage\n.logs\n.bot on\n.bot off\n"
            ".say texte\n.pic @/id\n.info @/id\n.wakeup @/id\n.ban @/id\n.unban @/id\n.snipe\n.clear\n"
        )
    elif user_id in clear_whitelist.get(chat_id, set()):
        text += (
            ".say texte\n.pic @/id\n.info @/id\n.wakeup @/id\n.ban @/id\n.unban @/id\n.snipe\n.clear\n"
        )
    elif user_id in whitelist.get(chat_id, set()):
        text += (
            ".say texte\n.pic @/id\n.info @/id\n.wakeup @/id\n.ban @/id\n.unban @/id\n.snipe\n.clear\n"
        )
    else:
        text += "❌ Vous n’avez pas accès aux commandes du bot."
    await event.reply(text)

# ----------------- CONFIG INTERACTIF -----------------
@client.on(events.NewMessage(pattern=r"\.config (logs|offlogs|message|offmessage)"))
async def start_config(event):
    if event.sender_id not in owners:
        return
    action = event.pattern_match.group(1)
    pending_config[event.sender_id] = action
    await event.reply("📌 Envoie maintenant l'ID du groupe pour cette configuration :")

@client.on(events.NewMessage())
async def receive_config_id(event):
    if event.sender_id not in pending_config:
        return
    action = pending_config[event.sender_id]
    try:
        gid = int(event.raw_text)
    except:
        await event.reply("❌ ID invalide, envoie un nombre correct.")
        return

    if action == "logs":
        BOT_LOGS[str(event.chat_id)] = gid
        await event.reply(f"✅ Logs BOT configurés vers {gid}")
    elif action == "offlogs":
        BOT_LOGS.pop(str(event.chat_id), None)
        await event.reply("❌ Logs BOT désactivés pour ce groupe")
    elif action == "message":
        MESSAGE_LOGS[str(event.chat_id)] = gid
        await event.reply(f"✅ Logs MESSAGE configurés vers {gid}")
    elif action == "offmessage":
        MESSAGE_LOGS.pop(str(event.chat_id), None)
        await event.reply("❌ Logs MESSAGE désactivés pour ce groupe")
    pending_config.pop(event.sender_id, None)

# ----------------- DASHBOARD -----------------
@client.on(events.NewMessage(pattern=r"\.dashboard"))
async def dashboard(event):
    user_id = event.sender_id
    if user_id not in owners:
        return
    chat_id = str(event.chat_id)
    wl_count = len(whitelist.get(chat_id, set()))
    clear_count = len(clear_whitelist.get(chat_id, set()))
    logs_count = len(BOT_LOGS)
    msg_logs_count = len(MESSAGE_LOGS)
    text = (
        "📊 **ADMIN DASHBOARD**\n\n"
        f"👑 Owner ID : `{OWNER_ID}`\n"
        f"👤 Owners secondaires : {', '.join(str(o) for o in owners if o != OWNER_ID) or 'Aucun'}\n\n"
        f"👥 WL Users : **{wl_count}**\n"
        f"🧹 Clear WL : **{clear_count}**\n\n"
        f"📌 Logs Groups : **{logs_count}**\n"
        f"💬 Message Logs : **{msg_logs_count}**\n\n"
        f"⚡ Bot Status : ✅ ONLINE"
    )
    await event.reply(text)

# ----------------- BOT ON / OFF -----------------
@client.on(events.NewMessage(pattern=r"\.bot (on|off)"))
async def bot_switch(event):
    user_id = event.sender_id
    if user_id not in owners:
        return
    chat_id = str(event.chat_id)
    action = event.pattern_match.group(1)
    if action == "on":
        bot_status[chat_id] = True
        await event.reply("✅ Le bot est maintenant actif pour ce groupe.")
    else:
        bot_status[chat_id] = False
        await event.reply("❌ Le bot est maintenant désactivé pour ce groupe.")

# ----------------- OWNER / OWNER SECONDARY -----------------
@client.on(events.NewMessage(pattern=r"\.owner (.+)"))
async def add_owner(event):
    user_id = event.sender_id
    if user_id != OWNER_ID:
        return
    try:
        target = await client.get_entity(event.pattern_match.group(1))
        owners.add(target.id)
        await event.reply(f"✅ {target.first_name} est maintenant Owner secondaire.")
    except:
        await event.reply("❌ Utilisateur introuvable.")

@client.on(events.NewMessage(pattern=r"\.unowner (.+)"))
async def remove_owner(event):
    user_id = event.sender_id
    if user_id != OWNER_ID:
        return
    try:
        target = await client.get_entity(event.pattern_match.group(1))
        owners.discard(target.id)
        await event.reply(f"❌ {target.first_name} n'est plus Owner secondaire.")
    except:
        await event.reply("❌ Utilisateur introuvable.")

# ----------------- WL / WL CLEAR -----------------
@client.on(events.NewMessage(pattern=r"\.wl (clear )?(.+)"))
async def add_wl(event):
    if event.sender_id not in owners:
        return
    chat_id = str(event.chat_id)
    is_clear = event.pattern_match.group(1) is not None
    try:
        target = await client.get_entity(event.pattern_match.group(2))
        if is_clear:
            clear_whitelist.setdefault(chat_id, set()).add(target.id)
            await event.reply(f"✅ {target.first_name} ajouté à WL clear")
        else:
            whitelist.setdefault(chat_id, set()).add(target.id)
            await event.reply(f"✅ {target.first_name} ajouté à WL normal")
    except:
        await event.reply("❌ Utilisateur introuvable.")

@client.on(events.NewMessage(pattern=r"\.unwl (.+)"))
async def remove_wl(event):
    if event.sender_id not in owners:
        return
    chat_id = str(event.chat_id)
    try:
        target = await client.get_entity(event.pattern_match.group(1))
        whitelist.get(chat_id, set()).discard(target.id)
        clear_whitelist.get(chat_id, set()).discard(target.id)
        await event.reply(f"❌ {target.first_name} retiré de toutes les WL")
    except:
        await event.reply("❌ Utilisateur introuvable.")

@client.on(events.NewMessage(pattern=r"\.wl list"))
async def list_wl(event):
    if event.sender_id not in owners:
        return
    chat_id = str(event.chat_id)
    wl_users = whitelist.get(chat_id, set())
    clear_users = clear_whitelist.get(chat_id, set())
    text = "**Liste WL :**\n"
    text += "\n".join(str(uid) for uid in wl_users) or "Aucun"
    text += "\n\n**Liste WL clear :**\n"
    text += "\n".join(str(uid) for uid in clear_users) or "Aucun"
    await event.reply(text)

# ----------------- SAY -----------------
@client.on(events.NewMessage(pattern=r"\.say (.+)"))
async def say(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    text = event.pattern_match.group(1)
    await event.delete()
    await event.reply(text)
    await log_message(event, f"💬 SAY utilisé par {user_id} : {text}")

# ----------------- PIC -----------------
@client.on(events.NewMessage(pattern=r"\.pic (.+)"))
async def pic(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    try:
        user = await client.get_entity(event.pattern_match.group(1))
        photos = await client.get_profile_photos(user)
        if photos:
            await client.send_file(event.chat_id, photos[0])
    except:
        await event.reply("❌ Impossible de récupérer la photo")

# ----------------- INFO -----------------
@client.on(events.NewMessage(pattern=r"\.info (.+)"))
async def info(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    try:
        user = await client.get_entity(event.pattern_match.group(1))
        await event.reply(
            f"Nom: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"ID: {user.id}\n"
            f"Bot: {user.bot}"
        )
    except:
        await event.reply("❌ Utilisateur introuvable")

# ----------------- WAKEUP -----------------
@client.on(events.NewMessage(pattern=r"\.wakeup (.+)"))
async def wakeup(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    try:
        user = await client.get_entity(event.pattern_match.group(1))
        for _ in range(10):
            await event.reply(f"@{user.username}" if user.username else f"{user.first_name}")
    except:
        await event.reply("❌ Impossible de ping cette personne")

# ----------------- BAN / UNBAN -----------------
@client.on(events.NewMessage(pattern=r"\.ban (.+)"))
async def ban(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    try:
        user = await client.get_entity(event.pattern_match.group(1))
        await client.kick_participant(event.chat_id, user.id)
    except:
        await event.reply("❌ Impossible de ban")

@client.on(events.NewMessage(pattern=r"\.unban (.+)"))
async def unban(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    try:
        user = await client.get_entity(event.pattern_match.group(1))
        await client.unban_participant(event.chat_id, user.id)
    except:
        await event.reply("❌ Impossible de unban")

# ----------------- SNIPE -----------------
@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    data = sniped.get(event.chat_id)
    if data:
        await event.reply(f"Dernier message supprimé\nDe : {data['sender_id']}\nMessage : {data['text']}")
    else:
        await event.reply("💬 Aucun message supprimé récemment.")

# ----------------- CLEAR -----------------
@client.on(events.NewMessage(pattern=r"\.clear (.+)"))
async def clear(event):
    if not bot_status.get(str(event.chat_id), True):
        return
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    arg = event.pattern_match.group(1)

    if user_id != OWNER_ID and user_id not in clear_whitelist.get(chat_id, set()):
        await event.reply("❌ Vous n'êtes pas WL clear")
        await log_bot(event, f"⛔ Tentative CLEAR refusée\n👤 {user_id}\n💬 {event.raw_text}")
        return

    # Vérifier si arg est un nombre
    try:
        n = int(arg)
        if n > 100:
            await event.reply("❌ Nombre maximum = 100")
            n = 100
        msgs = await client.get_messages(event.chat_id, limit=n)
        await client.delete_messages(event.chat_id, msgs)
        await event.reply(f"✅ {len(msgs)} messages supprimés")
    except:
        # sinon considérer comme @id ou username
        try:
            user = await client.get_entity(arg)
            msgs = await client.get_messages(event.chat_id, limit=100)
            to_delete = [m for m in msgs if m.sender_id == user.id]
            await client.delete_messages(event.chat_id, to_delete)
            await event.reply(f"✅ {len(to_delete)} messages de {user.first_name} supprimés")
        except:
            await event.reply("❌ Utilisateur introuvable")

# ----------------- MAIN BOT LOOP -----------------
async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()

asyncio.run(main())
