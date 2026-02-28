import asyncio
from telethon import TelegramClient, events

# --- CONFIG ---
API_ID = 36767235
API_HASH = "6a36bf6c4b15e7eecdb20885a13fc2d7"
BOT_TOKEN = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"

OWNER_ID = 7844678082

whitelist = {OWNER_ID}
owners = {OWNER_ID}

# ✅ SESSION MEMORY (IMPORTANT POUR RAILWAY)
client = TelegramClient(
    None,
    API_ID,
    API_HASH
).start(bot_token=BOT_TOKEN)


# ---------------- CHECKS ----------------
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners


# ---------------- COMMANDES ----------------
@client.on(events.NewMessage(pattern="/ping"))
async def ping(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("🏓 Pong !")


@client.on(events.NewMessage(pattern="/info"))
async def info(event):
    if not check_whitelist(event.sender_id):
        return

    await event.reply(
        "/info\n"
        "/say texte\n"
        "/pic\n"
        "/wakeup\n"
        "/ping\n"
        "/wl id\n"
        "/unwl id\n"
        "/owner id\n"
        "/unowner id\n"
        "/whitelist"
    )


@client.on(events.NewMessage(pattern=r"/say (.+)"))
async def say(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply(event.pattern_match.group(1))


@client.on(events.NewMessage(pattern="/pic"))
async def pic(event):
    if not check_whitelist(event.sender_id):
        return
    await event.reply("📸")


@client.on(events.NewMessage(pattern="/wakeup"))
async def wakeup(event):
    if not check_whitelist(event.sender_id):
        return

    user = await event.get_sender()
    name = f"@{user.username}" if user.username else user.first_name

    for _ in range(10):
        await event.reply(f"⏰ Lève-toi {name} !")
        await asyncio.sleep(2)


# -------- WL / OWNER --------
@client.on(events.NewMessage(pattern=r"/wl (\d+)"))
async def wl(event):
    if not check_owner(event.sender_id):
        return
    uid = int(event.pattern_match.group(1))
    whitelist.add(uid)
    await event.reply("✅ Ajouté WL")


@client.on(events.NewMessage(pattern=r"/unwl (\d+)"))
async def unwl(event):
    if not check_owner(event.sender_id):
        return
    uid = int(event.pattern_match.group(1))
    whitelist.discard(uid)
    await event.reply("❌ Retiré WL")


@client.on(events.NewMessage(pattern=r"/owner (\d+)"))
async def owner(event):
    if event.sender_id != OWNER_ID:
        return
    uid = int(event.pattern_match.group(1))
    owners.add(uid)
    await event.reply("✅ Owner ajouté")


@client.on(events.NewMessage(pattern=r"/unowner (\d+)"))
async def unowner(event):
    if event.sender_id != OWNER_ID:
        return
    uid = int(event.pattern_match.group(1))
    owners.discard(uid)
    await event.reply("❌ Owner retiré")


@client.on(events.NewMessage(pattern="/whitelist"))
async def whitelist_cmd(event):
    if not check_owner(event.sender_id):
        return

    msg = "Whitelist:\n"
    for u in whitelist:
        msg += f"{u}\n"

    msg += "\nOwners:\n"
    for o in owners:
        msg += f"{o}\n"

    await event.reply(msg)


print("✅ Bot connecté et prêt")

client.run_until_disconnected()
