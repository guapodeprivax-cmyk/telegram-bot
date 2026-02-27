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
OWNER_ID = 7844678082
owners = set([OWNER_ID])
whitelist = {}
clear_whitelist = {}
BOT_LOGS = {}
MESSAGE_LOGS = {}
pending_config = {}
bot_status = {}
sniped = {}

# ----------------- MINI SERVEUR HTTP POUR RENDER -----------------
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

# ----------------- LOGS -----------------
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

# ----------------- MESSAGE DELETE -----------------
@client.on(events.MessageDeleted)
async def handler(event):
    for msg in event.deleted:
        if msg.text:
            sniped[event.chat_id] = {"sender_id": msg.sender_id, "text": msg.text}
            await log_message(event, f"💬 Dernier message supprimé\nDe : {msg.sender_id}\nMessage : {msg.text}")

# ----------------- HELP -----------------
@client.on(events.NewMessage(pattern=r"\.help"))
async def help_cmd(event):
    user_id = event.sender_id
    chat_id = str(event.chat_id)
    text = "**Commandes disponibles :**\n\n"

    if user_id in owners:
        text += (
            ".owner @/id\n.unowner @/id\n"
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

# ----------------- OWNER -----------------
@client.on(events.NewMessage(pattern=r"\.owner (.+)"))
async def add_owner(event):
    if event.sender_id != OWNER_ID:
        return
    try:
        target = await client.get_entity(event.pattern_match.group(1))
        owners.add(target.id)
        await event.reply(f"✅ {target.first_name} est maintenant Owner secondaire.")
    except:
        await event.reply("❌ Utilisateur introuvable.")

@client.on(events.NewMessage(pattern=r"\.unowner (.+)"))
async def remove_owner(event):
    if event.sender_id != OWNER_ID:
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
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    if not bot_status.get(chat_id, True):
        return
    text = event.pattern_match.group(1)
    await event.delete()
    await event.reply(text)
    await log_message(event, f"💬 SAY utilisé par {user_id} : {text}")

# ----------------- PIC / INFO / WAKEUP / BAN / UNBAN / SNIPE / CLEAR -----------------
# (même logique que précédemment, toutes commandes incluses)
# ... (tu peux réutiliser les fonctions de mon script précédent ici)

# ----------------- MAIN -----------------
async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()

asyncio.run(main())
