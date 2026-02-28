import time
import random
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# --- CONFIGURATION ---
BOT_TOKEN = "8688863959:AAGwttSOxsdJcO1gSCsr8NgTJ6kxPXW50L8"
GIPHY_API_KEY = "YLLksuIyKHZcaMKuAOYR1s27dz2uy8Xr"

OWNER_ID = 7844678082  # Ton ID, seul vrai owner

# Cooldowns en secondes
HENTAI_COOLDOWN = 6
KISS_COOLDOWN = 5
SLAP_COOLDOWN = 5

# --- LISTES ---
whitelist = set()
owners = {OWNER_ID}

# Pour stocker le timestamp des dernières commandes
last_used = {}

# --- GIFS HENTAI ---
HENTAI_GIFS = [
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd459eaf877.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd459f14394.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd459f6d267.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd459fc75eb.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a02bca8.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a084d62.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a0ddb2f.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a1423d8.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a19b1cb.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a1f3e10.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a258610.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a2b141b.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a3168ea.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a36f3fd.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a3c845d.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a42b35a.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a484425.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a4dcad1.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a5415e3.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a598901.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a5f1ec8.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a656046.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a6af1aa.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a712990.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a769d40.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a7c1a1c.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a825a91.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a87d47b.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a938976.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a9903a5.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45a9e8c1f.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45aa4d0de.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45aaa711e.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ab0b8ee.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ab635cf.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45abbc4c0.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ac20f25.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ac786a5.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45acd0644.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ad346c7.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ad8c3fd.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ade45d4.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ae47e32.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45ae9f066.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45af02a47.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45af5b435.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45afb3c6c.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45b017ac6.gif",
    "https://s2.pictoa.com/media/galleries/296/760/2967605ffd459cac8ec/38322265ffd45b070efd.gif",
    "https://www.cougarillo.com/wp-content/uploads/2023/12/porno-hentai.gif",
    "https://www.cougarillo.com/wp-content/uploads/2023/12/levrette-gif-hentai.gif",
    "https://www.cougarillo.com/wp-content/uploads/2023/12/gif-hentai-gros-seins.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai145.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai125.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai143.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai129.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai119.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai127.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai122.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai120.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai141.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai139.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai140.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai114.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai123.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai115.gif",
    "https://www.cougarillo.com/wp-content/uploads/2024/04/gif-hentai142.gif",
    "https://img2.gelbooru.com//images/40/5f/405f442f0a5b6631821708238aed7d9a.gif",
    "https://img2.gelbooru.com//images/32/44/324418be5fba84ca057ce3601b944292.gif",
    "https://img2.gelbooru.com//images/70/09/7009626c5baad944ab31565e9509109a.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-41.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-40.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-39.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-38.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-37.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-36.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-35.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-34.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-32.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-30.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-29.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-28.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-27.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-25.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-24.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-23.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-22.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-21.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-20.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-19.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-18.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-17.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-16.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-15.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-14.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-13.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-12.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-11.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-10.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-9.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-7.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-6.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-5.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-4.gif",
    "https://commentseduire.net/wp-content/uploads/2017/06/hentai-gif-1.gif"
]

# --- FONCTIONS UTILITAIRES ---
def check_whitelist(user_id):
    return user_id in whitelist

def check_owner(user_id):
    return user_id in owners

def check_cooldown(user_id, command, cooldown):
    now = time.time()
    key = f"{user_id}:{command}"
    if key not in last_used or now - last_used[key] >= cooldown:
        last_used[key] = now
        return True, 0
    remaining = int(cooldown - (now - last_used[key]))
    return False, remaining

def get_giphy_gif(tag):
    url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&tag={tag}&rating=pg-13"
    resp = requests.get(url).json()
    if 'data' in resp and resp['data']:
        return resp['data']['images']['original']['url']
    return None

# --- COMMANDES ---
def info(update: Update, context: CallbackContext):
    if not check_whitelist(update.message.from_user.id):
        return
    update.message.reply_text("Ceci est un bot avec commandes .hentai, .kiss, .slap, etc.")

def say(update: Update, context: CallbackContext):
    if not check_whitelist(update.message.from_user.id):
        return
    update.message.reply_text(" ".join(context.args))

def pic(update: Update, context: CallbackContext):
    if not check_whitelist(update.message.from_user.id):
        return
    update.message.reply_text("📸")

def wakeup(update: Update, context: CallbackContext):
    if not check_whitelist(update.message.from_user.id):
        return
    update.message.reply_text("⏰ Réveille-toi !")

def ping(update: Update, context: CallbackContext):
    if not check_whitelist(update.message.from_user.id):
        return
    update.message.reply_text("🏓 Pong !")

def hentai(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_whitelist(user_id):
        return
    allowed, remaining = check_cooldown(user_id, "hentai", HENTAI_COOLDOWN)
    if not allowed:
        update.message.reply_text(f"❌ attends encore {remaining}s fils de pute")
        return
    gif_url = random.choice(HENTAI_GIFS)
    msg = update.message.reply_animation(gif_url)
    # Supprimer après 10s
    context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id), 10)

def kiss(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_whitelist(user_id):
        return
    if not context.args:
        update.message.reply_text("❌ mentionne quelqu’un fils de pute")
        return
    allowed, remaining = check_cooldown(user_id, "kiss", KISS_COOLDOWN)
    if not allowed:
        update.message.reply_text(f"❌ attends encore {remaining}s fils de pute")
        return
    mention = context.args[0]
    gif_url = get_giphy_gif("anime kiss")
    if gif_url:
        update.message.reply_animation(gif_url, caption=f"{update.message.from_user.mention_html()} kiss {mention} 💋", parse_mode="HTML")

def slap(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_whitelist(user_id):
        return
    if not context.args:
        update.message.reply_text("❌ mentionne quelqu’un fils de pute")
        return
    allowed, remaining = check_cooldown(user_id, "slap", SLAP_COOLDOWN)
    if not allowed:
        update.message.reply_text(f"❌ attends encore {remaining}s fils de pute")
        return
    mention = context.args[0]
    gif_url = get_giphy_gif("anime slap")
    if gif_url:
        update.message.reply_animation(gif_url, caption=f"{update.message.from_user.mention_html()} slap {mention} 👊", parse_mode="HTML")

# --- GESTION WHITELIST / OWNER ---
def wl(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_owner(user_id):
        return
    if not context.args:
        return
    target = int(context.args[0])
    whitelist.add(target)
    update.message.reply_text(f"✅ {target} ajouté à la whitelist")

def unwl(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_owner(user_id):
        return
    if not context.args:
        return
    target = int(context.args[0])
    whitelist.discard(target)
    update.message.reply_text(f"❌ {target} retiré de la whitelist")

def owner(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        return
    if not context.args:
        return
    target = int(context.args[0])
    owners.add(target)
    update.message.reply_text(f"✅ {target} ajouté aux owners")

def unowner(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != OWNER_ID:
        return
    if not context.args:
        return
    target = int(context.args[0])
    owners.discard(target)
    update.message.reply_text(f"❌ {target} retiré des owners")

def whitelist_cmd(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_owner(user_id):
        return
    msg = "Whitelist :\n"
    for uid in whitelist:
        msg += f"- {uid}\n"
    msg += "\nOwners :\n"
    for uid in owners:
        msg += f"- {uid}\n"
    update.message.reply_text(msg)

# --- INITIALISATION DU BOT ---
updater = Updater(BOT_TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("info", info))
dp.add_handler(CommandHandler("say", say))
dp.add_handler(CommandHandler("pic", pic))
dp.add_handler(CommandHandler("wakeup", wakeup))
dp.add_handler(CommandHandler("ping", ping))
dp.add_handler(CommandHandler("hentai", hentai))
dp.add_handler(CommandHandler("kiss", kiss))
dp.add_handler(CommandHandler("slap", slap))
dp.add_handler(CommandHandler("wl", wl))
dp.add_handler(CommandHandler("unwl", unwl))
dp.add_handler(CommandHandler("owner", owner))
dp.add_handler(CommandHandler("unowner", unowner))
dp.add_handler(CommandHandler("whitelist", whitelist_cmd))

updater.start_polling()
updater.idle()
