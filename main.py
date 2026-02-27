from telethon import TelegramClient, events
import asyncio, os
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

# ----------------- MESSAGE DELETE / SNIPE -----------------
@client.on(events.MessageDeleted)
async def handler(event):
    for msg in event.deleted:
        sniped[event.chat_id] = {
            "sender_id": msg.sender_id,
            "text": msg.text if msg.text else "<non-text message>",
            "media": msg.media
        }
        await log_message(event, f"💬 Message supprimé de {msg.sender_id}: {msg.text or '<media>'}")

@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    data = sniped.get(event.chat_id)
    if data:
        text = f"Dernier message supprimé\nDe : {data['sender_id']}\nMessage : {data['text']}"
        await event.reply(text)
    else:
        await event.reply("💬 Aucun message supprimé récemment.")

# ----------------- CLEAR -----------------
@client.on(events.NewMessage(pattern=r"\.clear (.+)"))
async def clear(event):
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    arg = event.pattern_match.group(1)

    if user_id != OWNER_ID and user_id not in clear_whitelist.get(chat_id, set()):
        await event.reply("❌ Vous n'êtes pas WL clear")
        await log_bot(event, f"⛔ Tentative CLEAR refusée\n👤 {user_id}\n💬 {event.raw_text}")
        return

    try:
        n = int(arg)
        if n > 100:
            await event.reply("❌ Nombre maximum = 100")
            n = 100
        msgs = await client.get_messages(event.chat_id, limit=n)
        await client.delete_messages(event.chat_id, msgs)
        await event.reply(f"✅ {len(msgs)} messages supprimés")
    except ValueError:
        try:
            user = await client.get_entity(arg)
            msgs = await client.get_messages(event.chat_id, limit=100)
            to_delete = [m for m in msgs if m.sender_id == user.id]
            await client.delete_messages(event.chat_id, to_delete)
            await event.reply(f"✅ {len(to_delete)} messages de {user.first_name} supprimés")
        except:
            await event.reply("❌ Utilisateur introuvable")

# ----------------- LOG DE TOUS LES MESSAGES -----------------
@client.on(events.NewMessage)
async def log_all_messages(event):
    if str(event.chat_id) in MESSAGE_LOGS:
        await log_message(event, f"💬 {event.sender_id} : {event.raw_text}")

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
            ".perm\n.dashboard\n"
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

# ----------------- OWNER / WL -----------------
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

# ----------------- MAIN -----------------
async def main():
    print("BOT STARTING...")
    await client.start(bot_token=bot_token)
    print("BOT CONNECTED ✅")
    await client.run_until_disconnected()

asyncio.run(main())
