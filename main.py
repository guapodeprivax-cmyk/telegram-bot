from telethon import TelegramClient, events

# ✅ Token BotFather
bot_token = "8575952878:AAGRVJ6a7kBoQbVyJM7Oy3OLV7zB2XYox7M"

# Crée le client en mode bot
client = TelegramClient('bot', api_id=0, api_hash='', bot_token=bot_token)

# Pour stocker le dernier message supprimé (snipe)
sniped = {}

# Sauvegarde tous les nouveaux messages pour le snipe
@client.on(events.NewMessage)
async def save_messages(event):
    sniped[event.chat_id] = event.raw_text

# Commande .clear : supprime les derniers n messages du chat
@client.on(events.NewMessage(pattern=r"\.clear (\d+)"))
async def clear(event):
    n = int(event.pattern_match.group(1))
    msgs = await client.get_messages(event.chat_id, limit=n+1)
    await client.delete_messages(event.chat_id, msgs, revoke=True)

# Commande .snipe : renvoie le dernier message supprimé
@client.on(events.NewMessage(pattern=r"\.snipe"))
async def snipe(event):
    msg = sniped.get(event.chat_id)
    if msg:
        await event.reply(msg)

# Commande .pic : envoie la photo de profil d’un utilisateur
@client.on(events.NewMessage(pattern=r"\.pic (.+)"))
async def pic(event):
    user = await client.get_entity(event.pattern_match.group(1))
    photos = await client.get_profile_photos(user)
    if photos.total:
        await client.send_file(event.chat_id, photos[0], caption=f"Photo de {user.first_name}")

# Commande .info : affiche les infos d’un utilisateur
@client.on(events.NewMessage(pattern=r"\.info (.+)"))
async def info(event):
    user = await client.get_entity(event.pattern_match.group(1))
    text = f"""
Nom : {user.first_name}
Username : @{user.username if user.username else 'Aucun'}
ID : {user.id}
Bot : {user.bot}
"""
    await event.reply(text)

# Lancer le bot
client.start(bot_token=bot_token)
client.run_until_disconnected()
