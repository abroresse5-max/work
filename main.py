import asyncio
import json
import os
import httpx
import logging
import random
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import RetryAfter, TelegramError

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ================= CONFIG =================
BOT_TOKEN = "7745667160:AAHPm_LFAAkCQnySDGjX-w51oRmnyJqLbPM"  # @BotFather dan olingan token
SUPER_ADMIN_ID = 7721170248  # Asosiy admin ID
CHECK_INTERVAL = 30  # 30 soniyada tekshirish
MAX_RETRIES = 99999  # Maksimum qayta urinishlar
DEFAULT_ERROR = "Noma'lum"
DEFAULT_UNKNOWN = "Noma'lum"

DATA_DIR = "data"
CLONES_DIR = "clones"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CLONES_DIR, exist_ok=True)

API_FILE = f"{DATA_DIR}/api.json"
ADMINS_FILE = f"{DATA_DIR}/admins.json"
GROUPS_FILE = f"{DATA_DIR}/groups.json"
ORDERS_FILE = f"{DATA_DIR}/orders.json"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"
MANUAL_LINKS_FILE = f"{DATA_DIR}/manual_links.json"
CLONES_FILE = f"{DATA_DIR}/clones.json"  # Clone botlar ma'lumotlari

# ================= PRE-DEFINED CLONE BOTS =================
# 53 ta bot token va username lari
PREDEFINED_CLONES = [
    {"username": "Social_uNest_bot", "token": "8439259537:AAGI0peQqyjXkZENimnrFSKZf_t8EvUAdUA"},
    {"username": "Social_nestBot", "token": "8458596872:AAFPhZ8fxL0FFnde4_IXoq9akIV1K4lvP9I"},
    {"username": "SocialNest_bot", "token": "8349194397:AAGwnjHrTzj7gVqh8x6lKMi-hV82h822Kcg"},
    {"username": "Social_Nest_bot", "token": "8138037287:AAFUeQ4kLaBDWpqv4EGl2QqwkHczqs_VRUM"},
    {"username": "Social_Nest1_bot", "token": "8329449737:AAElJ2BUG2QA53SPv5W16kAM2usyMLA_y0k"},
    {"username": "Social_Nes1t_bot", "token": "8260418618:AAHHtI6BzIoWJbO8ZXmCfI_I--GkjLM_DEo"},
    {"username": "Social_huNest_bot", "token": "8588751163:AAGB2RvkZqONm_YsCT_eWNwIAHl1if_ZYzM"},
    {"username": "Yobanazavrbot", "token": "8358482693:AAEtya1M9SKcSqAjaoCZdsK5n9rXiJgpumQ"},
    {"username": "jfjfiugtittififhhfhbot", "token": "8446753816:AAHKbd0dNTXQc1CzPyFj6y9gsI8yC5PzuFo"},
    {"username": "Hshsjwusbeehbot", "token": "8436087892:AAFXtpOSLDdGmDRiznIygxOtMFA44VZ2Obo"},
    {"username": "Syeyeyehdubot", "token": "7071192782:AAGHNYE2_pCK72hcMxRylofPXqRPAR2H0aU"},
    {"username": "newbotejejebot", "token": "8056906716:AAGPDIQHP_JyGhDRsDBL8LAWmPLRsUpKCgo"},
    {"username": "Jdjrjrjdnrfnjbot", "token": "8364053820:AAF-PSGdIZMhlKGjCwWdyWasOHGAh4MFJdI"},
    {"username": "Uimgimg7bf_bot", "token": "8454283421:AAEfeQpWqVi5KtVwnye3NbyHhLpQkRriNlI"},
    {"username": "Hikjyik7jbot", "token": "8509084550:AAEVXP0Fm3ffajz_9LYVW_jCHK0LLd4LfLw"},
    {"username": "Jnhgdrunhhhijhy_bot", "token": "8344265853:AAHzauydUPeEE6JO7EUOsHAqD_qH9QCkAL0"},
    {"username": "Ho9y9unyhyhobot", "token": "8556871095:AAGBHSFeqq_n3aF87IVg46d-VtGQZIMHAvl"},
    {"username": "Fudbolltvbot", "token": "8439271297:AAFrDIEpgW3tVoySt6ZKNBYq2mAa9it4lNc"},
    {"username": "Ysheheheuubot", "token": "8191838733:AAEc6OO8drPRDLjZ3GQfFEghMYWQwhUaCTc"},
    {"username": "Hsjssuwususubot", "token": "8202875113:AAF4R7yEgWufyhzT--tnSN1Yy6DCLP0s3tc"},
    {"username": "SocialsjNestbot", "token": "8530222942:AAEPTA4CUAy9NOojGxI4uzdNSaI9gwbnGWA"},
    {"username": "shehheheuubot", "token": "8530998986:AAGER1UTAkMTF6LutfMGNTxC7K5XqYKE_G8"},
    {"username": "Hrjdjenrnrnrnrbrbfbdbrbrnrbot", "token": "8324182580:AAGj6n0yBLx0u0t7b3fryq0Kpsba9jSTHiw"},
    {"username": "DhnsusekbitBot", "token": "8472308556:AAHCslLfAKvrRdF6TCF6otlfy8CRtk-K3JE"},
    {"username": "rnrnrnrbrbfbbdbrbrnrbot", "token": "8310978154:AAH4Fc4_J_IddsHS4USyjvmbAA6pd2l49KA"},
    {"username": "Ywhwheehehehhebot", "token": "8535541914:AAFzMHZJLf5QxSyUCcRlEQQ9iBqpKY0xVOE"},
    {"username": "Hshdjdudsjsjbot", "token": "8505755981:AAEmTWfe1A7YXhpvYLFgKxC75I9zHhMPCtM"},
    {"username": "snhdjdudsjsjbot", "token": "8522266987:AAGbxWdzSGvSbR79D4i9WOiI9DYonhldwcA"},
    {"username": "Euuedueudjbot", "token": "7950751796:AAGU-wMt15FAM8WBjb0THIulZWzW3DllJAE"},
    {"username": "Dhhshehebebot", "token": "8515271652:AAFFwmavrSjUnf3YV4dh-bBzuK7RectTgK4"},
    {"username": "httphhshehebebot", "token": "8445779908:AAFyTQe8n7w4hiTuG_rBGDzuMAoHR986FFE"},
    {"username": "httpDhhshehebebot", "token": "8327089843:AAFhGfvBtHx12Pd2jkN99PczTlB2YG5M5k8"},
    {"username": "Hdjtrotkfjtjffbpybot", "token": "7970093334:AAGBpiWev8WJpvAwrw_itujjaNHGhZAX4sQ"},
    {"username": "meDjHshdjdudsjsjbot", "token": "8279198263:AAFL1oQEI-kso7_jEudejdeM2KrWM3Bg1Es"},
    {"username": "DjHshdjdudsjsjbot", "token": "8328229456:AAGjMH-ZvaHiOKSgtYWG_Mjjimrqy18ZVOE"},
    {"username": "httpDhhrrjrjrbbtpbot", "token": "7922598682:AAF2McWgB-h3F3qiwSz8K0LTO5FV5lexRs0"},
    {"username": "Dhhrrjrjrbbtpbot", "token": "8467698412:AAHtjAPbXXc0lISAHAEpmVYQw8RF74l1ZcM"},
    {"username": "httpHdjtrotkfjtjffbpybot", "token": "8273499563:AAH6dT_q3eTDbhq6ea4Dclp4R8VcUWV6WGk"},
    {"username": "Dndjrirjrbdbdbbot", "token": "6920934493:AAHKw29f4iR9pdXiOfOtFHF5XBY-n-uKPnQ"},
    {"username": "Rjdbrjtbtbot", "token": "7663977222:AAG-j_tjkmobRaZ076i4mcaocAPsG87YmgQ"},
    {"username": "Jdjdjdjrdjrjrbot", "token": "7684758850:AAEn4K4iXVRIHcKEebajYPUNO7yHhcvvmIk"},
    {"username": "Dhhrrjrjrbbtpbptbot", "token": "6624569779:AAGJsq-ltdeT3ETMfJeqeB-aTUZv1DPE_qo"},
    {"username": "Jdjdjdjrjrjr_bot", "token": "6344669351:AAGpx2JIBwxX7ulV2QvVuQalnOcmOf5OUIc"},
    {"username": "httpJdjdjdjrdjrjrbot", "token": "6891672326:AAFnRwJe_O79NYJC7PfhOlKsMulY9pY-5N4"},
    {"username": "Hrhrhrrbbotdhbpbot", "token": "6479810503:AAGYD6tNwFMczq9XFlVp_IP6wHnQeRaUhq0"},
    {"username": "TURFAphotoftoBot", "token": "6535506141:AAEEmuG2wH1AY9upiPqhJBCqo1kmQeKWtN4"},
    {"username": "Quva_ToshkentRoBot", "token": "8439259537:AAGI0peQqyjXkZENimnrFSKZf_t8EvUAdUA"},
    {"username": "OpenBudgetXalolBot", "token": "8458596872:AAFPhZ8fxL0FFnde4_IXoq9akIV1K4lvP9I"},
    {"username": "qitmiriybot", "token": "8349194397:AAGwnjHrTzj7gVqh8x6lKMi-hV82h822Kcg"},
    {"username": "Devushakaxon_bot", "token": "8138037287:AAFUeQ4kLaBDWpqv4EGl2QqwkHczqs_VRUM"},
    {"username": "QoruvuI_bot", "token": "8329449737:AAElJ2BUG2QA53SPv5W16kAM2usyMLA_y0k"},
    {"username": "Aloqa_iBot", "token": "8260418618:AAHHtI6BzIoWJbO8ZXmCfI_I--GkjLM_DEo"},
    {"username": "CosmoMaker_Bot", "token": "8588751163:AAGB2RvkZqONm_YsCT_eWNwIAHl1if_ZYzM"},
]

# ================= LOAD/SAVE DATA =================
def load_json(filename: str, default: Any) -> Any:
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error("Xato: %s", e)
    return default


def save_json(filename: str, data: Any) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Xato: %s", e)


# ================= GLOBAL DATA =================
API_DATA = load_json(API_FILE, None)
ADMINS = load_json(ADMINS_FILE, [SUPER_ADMIN_ID])
GROUPS = load_json(GROUPS_FILE, {})
ORDERS = load_json(ORDERS_FILE, [])
SETTINGS = load_json(
    SETTINGS_FILE,
    {
        "global_auto_reorder": True,
        "global_auto_cancel": False,
        "auto_reorder_interval": 60,
        "auto_cancel_minutes": 10,
    },
)
MANUAL_LINKS = load_json(MANUAL_LINKS_FILE, {})
CLONES = load_json(CLONES_FILE, {})  # Clone botlar: {clone_id: {token, api_url, api_key, status, groups}}

print("=" * 70)
print("🤖 VASYA SMM BOT - TO'LIQ VERSIYA (53 TA CLONE BOT QO'SHILGAN)")
print(f"👥 Guruhlar: {len(GROUPS)} ta")
print(f"📦 Orderlar: {len(ORDERS)} ta")
print(f"🤖 Clone botlar: {len(CLONES)} ta")
print(f"⚙️ Global Auto-reorder: {'✅ ON' if SETTINGS['global_auto_reorder'] else '❌ OFF'}")
print(f"⚠️ Global Auto-cancel: {'✅ ON' if SETTINGS['global_auto_cancel'] else '❌ OFF'}")
print("=" * 70)

# ================= UTILITY FUNCTIONS =================
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS


def is_super_admin(user_id: int) -> bool:
    return user_id == SUPER_ADMIN_ID


def get_main_menu(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📦 ORDER", callback_data="order")],
        [InlineKeyboardButton("👥 GROUPS", callback_data="groups")],
        [InlineKeyboardButton("📊 ORDERS", callback_data="orders")],
        [InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings")],
    ]

    if is_super_admin(user_id):
        buttons.append([InlineKeyboardButton("👤 ADMINS", callback_data="admins")])
        buttons.append([InlineKeyboardButton("🔐 SET API", callback_data="set_api")])
        buttons.append([InlineKeyboardButton("💰 BALANCE", callback_data="balance")])
        buttons.append([InlineKeyboardButton("🤖 CLONE BOTS", callback_data="clone_bots")])
        buttons.append([InlineKeyboardButton("🚀 CREATE ALL CLONES", callback_data="create_all_clones")])

    return InlineKeyboardMarkup(buttons)


async def smm_api_request(action: str, **kwargs: Any) -> Dict[str, Any]:
    if not API_DATA or "url" not in API_DATA or "key" not in API_DATA:
        return {"error": "API not configured"}

    try:
        data = {"key": API_DATA["key"], "action": action}
        data.update(kwargs)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_DATA["url"], data=data)
            return response.json()
    except Exception as e:
        return {"error": str(e)}


async def create_invite_link_safe(bot, group_id: str) -> str | None:
    try:
        chat = await bot.get_chat(group_id)
        if chat.username:
            return f"https://t.me/{chat.username}"

        invite = await bot.create_chat_invite_link(
            chat_id=chat.id,
            name=f"Order_{datetime.now().strftime('%H%M%S')}",
            expire_date=None,
            member_limit=None,
            creates_join_request=True,
        )
        return invite.invite_link
    except Exception as e:
        logger.error("Link yaratish xatosi: %s", e)
        return None


# ================= CLONE BOT FUNCTIONS =================
def initialize_predefined_clones() -> int:
    """53 ta predefinned clone botlarni yaratish va saqlash"""
    if not CLONES:
        logger.info("🤖 53 ta predefinned clone botlar yaratilmoqda...")

        for idx, bot_info in enumerate(PREDEFINED_CLONES, 1):
            username = bot_info["username"]
            token = bot_info["token"]

            # Clone ID yaratish
            clone_id = f"predefined_{idx:03d}_{username}"

            # Agar bu clone allaqachon mavjud bo'lsa, o'tkazib yuborish
            if clone_id in CLONES:
                continue

            # Clone bot ma'lumotlari
            clone_data = {
                "token": token,
                "username": username,
                "admin_id": SUPER_ADMIN_ID,
                "admin_ids": [SUPER_ADMIN_ID],
                "api_url": API_DATA["url"] if API_DATA else "",
                "api_key": API_DATA["key"] if API_DATA else "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "stopped",
                "type": "predefined",
                "auto_start": True,
                "groups": {},
                "orders": [],
                "settings": {
                    "auto_reorder": True,
                    "auto_cancel": False,
                    "auto_cancel_minutes": 10,
                },
            }

            CLONES[clone_id] = clone_data

        save_json(CLONES_FILE, CLONES)
        logger.info("✅ %s ta clone bot yaratildi va saqlandi", len(CLONES))

    return len(CLONES)


def create_clone_bot(
    clone_id: str,
    token: str,
    admin_id: int,
    api_url: str | None = None,
    api_key: str | None = None,
    username: str | None = None,
    auto_start: bool = True,
) -> str:
    """Yangi clone bot yaratish"""
    clone_data = {
        "token": token,
        "username": username or clone_id,
        "admin_id": admin_id,
        "admin_ids": sorted({SUPER_ADMIN_ID, admin_id}),
        "api_url": api_url or (API_DATA["url"] if API_DATA else ""),
        "api_key": api_key or (API_DATA["key"] if API_DATA else ""),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "stopped",
        "type": "manual",
        "auto_start": auto_start,
        "groups": {},
        "orders": [],
        "settings": {
            "auto_reorder": True,
            "auto_cancel": False,
            "auto_cancel_minutes": 10,
        },
    }

    CLONES[clone_id] = clone_data
    save_json(CLONES_FILE, CLONES)

    # Clone bot faylini yaratish
    clone_file = create_clone_script(clone_id, clone_data)
    return clone_file


def create_clone_script(clone_id: str, clone_data: Dict[str, Any]) -> str:
    """Clone bot uchun Python skript yaratish"""
    admin_ids = clone_data.get("admin_ids") or [clone_data["admin_id"], SUPER_ADMIN_ID]
    clone_code = f'''import asyncio
import json
import os
import httpx
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Clone bot ID: {clone_id}
CLONE_ID = "{clone_id}"
BOT_TOKEN = "{clone_data['token']}"
ADMIN_IDS = {admin_ids}
USERNAME = "{clone_data.get('username', '')}"
DEFAULT_ERROR = "Noma'lum"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DATA_DIR = f"clones/{{CLONE_ID}}_data"
os.makedirs(DATA_DIR, exist_ok=True)

API_FILE = f"{{DATA_DIR}}/api.json"
GROUPS_FILE = f"{{DATA_DIR}}/groups.json"
ORDERS_FILE = f"{{DATA_DIR}}/orders.json"
SETTINGS_FILE = f"{{DATA_DIR}}/settings.json"

API_DATA = {{
    'url': '{clone_data.get('api_url', '')}',
    'key': '{clone_data.get('api_key', '')}'
}}

GROUPS = {{}}
ORDERS = []

SETTINGS = {{
    'auto_reorder': {clone_data['settings']['auto_reorder']},
    'auto_cancel': {clone_data['settings']['auto_cancel']},
    'auto_cancel_minutes': {clone_data['settings']['auto_cancel_minutes']}
}}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default

async def smm_api_request(action, **kwargs):
    if not API_DATA or 'url' not in API_DATA or 'key' not in API_DATA:
        return {{"error": "API not configured"}}

    try:
        data = {{"key": API_DATA['key'], "action": action}}
        data.update(kwargs)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_DATA['url'], data=data)
            return response.json()
    except Exception as e:
        return {{"error": str(e)}}

async def create_invite_link_safe(bot, group_id):
    try:
        chat = await bot.get_chat(group_id)
        if chat.username:
            return f"https://t.me/{{chat.username}}"

        invite = await bot.create_chat_invite_link(
            chat_id=chat.id,
            name=f"Order_{{datetime.now().strftime('%H%M%S')}}",
            expire_date=None,
            member_limit=None,
            creates_join_request=True
        )
        return invite.invite_link
    except Exception as e:
        logger.error(f"Link yaratish xatosi: {{e}}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return

    keyboard = [
        [InlineKeyboardButton("📦 ORDER", callback_data="order")],
        [InlineKeyboardButton("👥 GROUPS", callback_data="groups")],
        [InlineKeyboardButton("📊 ORDERS", callback_data="orders")],
        [InlineKeyboardButton("💰 BALANCE", callback_data="balance")],
        [InlineKeyboardButton("⚙️ SET API", callback_data="set_api")]
    ]

    await update.message.reply_text(
        f"🤖 *CLONE BOT*\n👤 @{{USERNAME}}\n🆔 {{CLONE_ID}}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ Siz admin emassiz!")
        return

    callback_data = query.data

    if callback_data == "order":
        context.user_data["awaiting_order"] = True
        await query.edit_message_text("📦 Format: <group_id> <service_id> <quantity>")
    elif callback_data == "set_api":
        context.user_data["awaiting_api"] = True
        await query.edit_message_text("🔐 API format: <api_url> <api_key>")
    elif callback_data == "groups":
        groups_text = "👥 Guruhlar:\n"
        for group_id, info in GROUPS.items():
            groups_text += f"• {{info.get('name', group_id)}} - {{info.get('total_orders', 0)}} ta order\n"
        await query.edit_message_text(groups_text or "❌ Guruhlar yo'q!")
    elif callback_data == "orders":
        active = len([o for o in ORDERS if not o.get('done', False)])
        total = len(ORDERS)
        await query.edit_message_text(f"📊 Orderlar: {{active}} ta faol, {{total}} ta jami")
    elif callback_data == "balance":
        if API_DATA.get('url') and API_DATA.get('key'):
            result = await smm_api_request("balance")
            if 'balance' in result:
                await query.edit_message_text(f"💰 Balans: {{result['balance']}}")
            else:
                await query.edit_message_text(f'❌ Xato: {{result.get("error", DEFAULT_ERROR)}}')
        else:
            await query.edit_message_text("❌ API sozlanmagan!")

async def set_api_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return

    text = update.message.text.strip().split()
    if len(text) < 3:
        await update.message.reply_text("Format: /set_api <api_url> <api_key>")
        return

    api_url = text[1]
    api_key = text[2]

    API_DATA.update({{'url': api_url, 'key': api_key}})
    save_json(API_FILE, API_DATA)

    await update.message.reply_text("✅ API sozlandi!")

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.strip()

    if text.startswith("/order "):
        try:
            parts = text[7:].split()
            if len(parts) < 3:
                await update.message.reply_text("Format: /order <group_id> <service_id> <quantity>")
                return

            group_id, service_id, quantity = parts[0], int(parts[1]), int(parts[2])

            link = await create_invite_link_safe(context.bot, group_id)
            if not link:
                await update.message.reply_text("❌ Link yaratishda xato!")
                return

            result = await smm_api_request("add", service=service_id, link=link, quantity=quantity)

            if result and 'order' in result:
                ORDERS.append({{
                    'order_id': result['order'],
                    'link': link,
                    'service': service_id,
                    'quantity': quantity,
                    'done': False,
                    'group_id': group_id,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }})
                save_json(ORDERS_FILE, ORDERS)

                if group_id not in GROUPS:
                    GROUPS[group_id] = {{'name': group_id, 'total_orders': 0}}
                GROUPS[group_id]['total_orders'] += 1
                save_json(GROUPS_FILE, GROUPS)

                await update.message.reply_text(f"✅ Order yuborildi! ID: {{result['order']}}")
            else:
                await update.message.reply_text(f'❌ Xato: {{result.get("error", DEFAULT_ERROR)}}')

        except Exception as e:
            await update.message.reply_text(f"❌ Xato: {{str(e)}}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    text = update.message.text.strip()

    if context.user_data.get("awaiting_api"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("Format: <api_url> <api_key>")
            return

        api_url, api_key = parts[0], parts[1]
        API_DATA.update({{'url': api_url, 'key': api_key}})
        save_json(API_FILE, API_DATA)
        context.user_data.pop("awaiting_api", None)
        await update.message.reply_text("✅ API sozlandi!")
        return

    if context.user_data.get("awaiting_order"):
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("Format: <group_id> <service_id> <quantity>")
            return

        group_id, service_id, quantity = parts[0], int(parts[1]), int(parts[2])
        context.user_data.pop("awaiting_order", None)

        link = await create_invite_link_safe(context.bot, group_id)
        if not link:
            await update.message.reply_text("❌ Link yaratishda xato!")
            return

        result = await smm_api_request("add", service=service_id, link=link, quantity=quantity)

        if result and 'order' in result:
            ORDERS.append({{
                'order_id': result['order'],
                'link': link,
                'service': service_id,
                'quantity': quantity,
                'done': False,
                'group_id': group_id,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }})
            save_json(ORDERS_FILE, ORDERS)

            if group_id not in GROUPS:
                GROUPS[group_id] = {{'name': group_id, 'total_orders': 0}}
            GROUPS[group_id]['total_orders'] += 1
            save_json(GROUPS_FILE, GROUPS)

            await update.message.reply_text(f"✅ Order yuborildi! ID: {{result['order']}}")
        else:
            await update.message.reply_text(f'❌ Xato: {{result.get("error", DEFAULT_ERROR)}}')
        return

async def groups_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not GROUPS:
        await update.message.reply_text("❌ Guruhlar yo'q!")
        return

    text = "👥 Clone bot guruhlari:\n"
    for group_id, info in GROUPS.items():
        text += f"\n• {{info.get('name', group_id)}} - {{info.get('total_orders', 0)}} ta order"

    await update.message.reply_text(text)

async def auto_reorder_task(app):
    logger.info(f"🔄 {{CLONE_ID}} auto-reorder task started")

    while True:
        try:
            changed = False

            for order in ORDERS[:]:
                if order.get('done', False):
                    continue

                order_id = order.get('order_id')
                if not order_id:
                    continue

                try:
                    result = await smm_api_request("status", order=order_id)
                    if not result:
                        continue

                    status = str(result.get('status', '')).lower()

                    if 'cancel' in status or 'refund' in status:
                        retry_count = order.get('retry_count', 0)
                        if retry_count < 3 and SETTINGS['auto_reorder']:
                            new_result = await smm_api_request(
                                "add",
                                service=order['service'],
                                link=order['link'],
                                quantity=order['quantity']
                            )

                            if new_result and 'order' in new_result:
                                order['order_id'] = new_result['order']
                                order['retry_count'] = retry_count + 1
                                order['status'] = 'retried'
                                order['last_retry'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                changed = True
                                logger.info(f"♻️ Order qayta yuborildi: {{order_id}} -> {{new_result['order']}}")
                            else:
                                order['done'] = True
                                changed = True
                                logger.info(f"❌ Order qayta yuborish muvaffaqiyatsiz: {{order_id}}")
                        else:
                            order['done'] = True
                            changed = True
                            logger.info(f"❌ Order yakunlandi (max retries): {{order_id}}")

                except Exception as e:
                    logger.error(f"Order status check error {{order_id}}: {{e}}")
                    continue

            if changed:
                save_json(ORDERS_FILE, ORDERS)

            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Auto task loop error: {{e}}")
            await asyncio.sleep(10)

async def post_init(app):
    asyncio.create_task(auto_reorder_task(app))

def main():
    global GROUPS, ORDERS

    GROUPS = load_json(GROUPS_FILE, {{}})
    ORDERS = load_json(ORDERS_FILE, [])

    if os.path.exists(API_FILE):
        api_data = load_json(API_FILE, {{}})
        if api_data:
            API_DATA.update(api_data)

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("set_api", set_api_command))
    application.add_handler(CommandHandler("order", order_command))
    application.add_handler(CommandHandler("groups", groups_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    print(f"🤖 Clone bot {{CLONE_ID}} (@{{USERNAME}}) ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
'''

    clone_file = f"{CLONES_DIR}/clone_{clone_id}.py"
    with open(clone_file, "w", encoding="utf-8") as f:
        f.write(clone_code)

    return clone_file


def is_process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def start_clone_bot(clone_id: str) -> bool:
    """Clone botni ishga tushirish"""
    if clone_id not in CLONES:
        return False

    clone_data = CLONES[clone_id]

    if not clone_data.get("auto_start", True):
        return False

    if clone_data.get("status") == "running":
        pid = clone_data.get("process_pid")
        if pid and is_process_alive(pid):
            return True
        clone_data["status"] = "stopped"
        clone_data.pop("process_pid", None)

    clone_file = f"{CLONES_DIR}/clone_{clone_id}.py"
    if not os.path.exists(clone_file):
        create_clone_script(clone_id, clone_data)

    try:
        process = subprocess.Popen(
            [sys.executable, clone_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        CLONES[clone_id]["process_pid"] = process.pid
        CLONES[clone_id]["status"] = "running"
        CLONES[clone_id]["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(CLONES_FILE, CLONES)

        logger.info("✅ Clone bot ishga tushirildi: %s", clone_id)
        return True
    except Exception as e:
        logger.error("Clone botni ishga tushirishda xato %s: %s", clone_id, e)
        return False


def stop_clone_bot(clone_id: str) -> bool:
    """Clone botni to'xtatish"""
    if clone_id not in CLONES:
        return False

    try:
        pid = CLONES[clone_id].get("process_pid")
        if pid:
            import signal

            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        CLONES[clone_id]["status"] = "stopped"
        CLONES[clone_id].pop("process_pid", None)
        save_json(CLONES_FILE, CLONES)

        logger.info("✅ Clone bot to'xtatildi: %s", clone_id)
        return True
    except Exception as e:
        logger.error("Clone botni to'xtatishda xato %s: %s", clone_id, e)
        return False


def start_all_clones() -> tuple[int, int]:
    """Barcha clone botlarni ishga tushirish"""
    success_count = 0
    total_count = len(CLONES)

    logger.info("🚀 Barcha clone botlar ishga tushirilmoqda... (%s ta)", total_count)

    for clone_id in list(CLONES.keys()):
        if start_clone_bot(clone_id):
            success_count += 1

    return success_count, total_count


def stop_all_clones() -> tuple[int, int]:
    """Barcha clone botlarni to'xtatish"""
    success_count = 0
    total_count = len(CLONES)

    logger.info("🛑 Barcha clone botlar to'xtatilmoqda... (%s ta)", total_count)

    for clone_id in list(CLONES.keys()):
        if stop_clone_bot(clone_id):
            success_count += 1

    return success_count, total_count


# ================= ASOSIY BOT FUNKSIYALARI =================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return

    await update.message.reply_text(
        "🤖 VASYA SMM BOT",
        reply_markup=get_main_menu(user_id),
    )


async def set_api_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
        return

    text = update.message.text.strip().split()
    if len(text) < 3:
        await update.message.reply_text("Format: /set_api <api_url> <api_key>")
        return

    api_url = text[1]
    api_key = text[2]

    API_DATA.update({"url": api_url, "key": api_key})
    save_json(API_FILE, API_DATA)

    await update.message.reply_text("✅ API sozlandi!")


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.strip()

    if text.startswith("/order "):
        try:
            parts = text[7:].split()
            if len(parts) < 3:
                await update.message.reply_text("Format: /order <group_id> <service_id> <quantity>")
                return

            group_id, service_id, quantity = parts[0], int(parts[1]), int(parts[2])
            await submit_order(group_id, service_id, quantity, context, update.message.reply_text)

        except Exception as e:
            await update.message.reply_text(f"❌ Xato: {str(e)}")


async def submit_order(
    group_id: str,
    service_id: int,
    quantity: int,
    context: ContextTypes.DEFAULT_TYPE,
    reply_func,
) -> None:
    link = await create_invite_link_safe(context.bot, group_id)
    if not link:
        await reply_func("❌ Link yaratishda xato!")
        return

    result = await smm_api_request("add", service=service_id, link=link, quantity=quantity)

    if result and "order" in result:
        ORDERS.append(
            {
                "order_id": result["order"],
                "link": link,
                "service": service_id,
                "quantity": quantity,
                "done": False,
                "group_id": group_id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        save_json(ORDERS_FILE, ORDERS)

        if group_id not in GROUPS:
            GROUPS[group_id] = {"name": group_id, "total_orders": 0}
        GROUPS[group_id]["total_orders"] += 1
        save_json(GROUPS_FILE, GROUPS)

        await reply_func(f"✅ Order yuborildi! ID: {result['order']}")
    else:
        await reply_func(f"❌ Xato: {result.get('error', DEFAULT_ERROR)}")


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.strip().split()
    if len(text) < 2:
        await update.message.reply_text("Format: /link <group_id>")
        return

    group_id = text[1]
    link = await create_invite_link_safe(context.bot, group_id)
    if not link:
        await update.message.reply_text("❌ Link yaratishda xato!")
        return

    MANUAL_LINKS[group_id] = link
    save_json(MANUAL_LINKS_FILE, MANUAL_LINKS)
    await update.message.reply_text(f"✅ Link saqlandi: {link}")


async def clear_links_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return

    MANUAL_LINKS.clear()
    save_json(MANUAL_LINKS_FILE, MANUAL_LINKS)
    await update.message.reply_text("✅ Barcha linklar tozalandi!")


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
        return

    await update.message.reply_text(
        "Clone botlar menyusi:",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🤖 CLONE BOTS", callback_data="clone_bots")]]
        ),
    )


async def start_clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
        return

    text = update.message.text.strip().split(maxsplit=1)
    if len(text) < 2:
        await update.message.reply_text("Format: /start_clone <clone_id>")
        return

    clone_id = text[1]
    if start_clone_bot(clone_id):
        await update.message.reply_text("✅ Clone bot ishga tushirildi!")
    else:
        await update.message.reply_text("❌ Clone botni ishga tushirib bo'lmadi!")


async def stop_clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
        return

    text = update.message.text.strip().split(maxsplit=1)
    if len(text) < 2:
        await update.message.reply_text("Format: /stop_clone <clone_id>")
        return

    clone_id = text[1]
    if stop_clone_bot(clone_id):
        await update.message.reply_text("✅ Clone bot to'xtatildi!")
    else:
        await update.message.reply_text("❌ Clone botni to'xtatib bo'lmadi!")


async def delete_clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_super_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
        return

    text = update.message.text.strip().split(maxsplit=1)
    if len(text) < 2:
        await update.message.reply_text("Format: /delete_clone <clone_id>")
        return

    clone_id = text[1]
    if clone_id not in CLONES:
        await update.message.reply_text("❌ Clone bot topilmadi!")
        return

    stop_clone_bot(clone_id)
    CLONES.pop(clone_id, None)
    save_json(CLONES_FILE, CLONES)
    await update.message.reply_text("✅ Clone bot o'chirildi!")


# ================= ASOSIY CALLBACK HANDLER =================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    callback_data = query.data

    if not is_admin(user_id):
        await query.edit_message_text("❌ Siz admin emassiz!")
        return

    user_data = context.user_data

    if callback_data == "main_menu":
        await query.edit_message_text("🏠 Asosiy menyu:", reply_markup=get_main_menu(user_id))
        return

    if callback_data == "order":
        user_data["awaiting_order"] = True
        await query.edit_message_text("📦 Format: <group_id> <service_id> <quantity>")
        return

    if callback_data == "groups":
        if not GROUPS:
            await query.edit_message_text("❌ Guruhlar yo'q!")
            return

        groups_text = "👥 Guruhlar:\n"
        for group_id, info in GROUPS.items():
            groups_text += f"• {info.get('name', group_id)} - {info.get('total_orders', 0)} ta order\n"
        await query.edit_message_text(groups_text)
        return

    if callback_data == "orders":
        active = len([o for o in ORDERS if not o.get("done", False)])
        total = len(ORDERS)
        await query.edit_message_text(f"📊 Orderlar: {active} ta faol, {total} ta jami")
        return

    if callback_data == "settings":
        text = (
            "⚙️ Sozlamalar:\n"
            f"• Auto-reorder: {'✅' if SETTINGS['global_auto_reorder'] else '❌'}\n"
            f"• Auto-cancel: {'✅' if SETTINGS['global_auto_cancel'] else '❌'}\n"
            f"• Auto-cancel minutes: {SETTINGS['auto_cancel_minutes']}"
        )
        await query.edit_message_text(text)
        return

    if callback_data == "set_api":
        if not is_super_admin(user_id):
            await query.edit_message_text("❌ Bu amal faqat super admin uchun!")
            return
        user_data["awaiting_api"] = True
        await query.edit_message_text("🔐 API format: <api_url> <api_key>")
        return

    if callback_data == "balance":
        if API_DATA and API_DATA.get("url") and API_DATA.get("key"):
            result = await smm_api_request("balance")
            if "balance" in result:
                await query.edit_message_text(f"💰 Balans: {result['balance']}")
            else:
                await query.edit_message_text(f'❌ Xato: {result.get("error", DEFAULT_ERROR)}')
        else:
            await query.edit_message_text("❌ API sozlanmagan!")
        return

    # Barcha clone botlarni yaratish
    if callback_data == "create_all_clones":
        if not is_super_admin(user_id):
            await query.edit_message_text("❌ Bu amal faqat super admin uchun!")
            return

        created_count = initialize_predefined_clones()
        success_count, total_count = start_all_clones()

        await query.edit_message_text(
            "✅ Barcha clone botlar yaratildi va ishga tushirildi!\n\n"
            f"📊 Natijalar:\n"
            f"• Yaratildi: {created_count} ta\n"
            f"• Ishga tushirildi: {success_count}/{total_count} ta\n"
            f"• Jami clone botlar: {len(CLONES)} ta"
        )
        return

    # Clone botlar boshqaruvi
    if callback_data == "clone_bots":
        if not is_super_admin(user_id):
            await query.edit_message_text("❌ Bu amal faqat super admin uchun!")
            return

        running_count = len([c for c in CLONES.values() if c.get("status") == "running"])
        stopped_count = len(CLONES) - running_count

        text = (
            "🤖 Clone Botlar Boshqaruvi\n\n"
            "📊 Statistikalar:\n"
            f"• 🟢 Ishlayotgan: {running_count} ta\n"
            f"• 🔴 To'xtatilgan: {stopped_count} ta\n"
            f"• 📈 Jami: {len(CLONES)} ta\n\n"
            "Tanlang:"
        )

        keyboard = [
            [InlineKeyboardButton("📋 CLONE BOTLAR RO'YXATI", callback_data="clone_list")],
            [InlineKeyboardButton("🚀 HAMMASINI ISHGA TUSHIRISH", callback_data="start_all_clones_btn")],
            [InlineKeyboardButton("🛑 HAMMASINI TO'XTATISH", callback_data="stop_all_clones_btn")],
            [InlineKeyboardButton("➕ YANGI CLONE QO'SHISH", callback_data="create_clone")],
            [InlineKeyboardButton("🔄 CLONE BOTLARNI YANGILASH", callback_data="refresh_clones")],
            [InlineKeyboardButton("◀️ ORQAGA", callback_data="main_menu")],
        ]

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if callback_data == "clone_list":
        if not CLONES:
            await query.edit_message_text("❌ Clone botlar yo'q!")
            return

        page = user_data.get("clone_page", 0)
        clones_list = list(CLONES.items())
        page_size = 10
        start_idx = page * page_size
        end_idx = start_idx + page_size

        text = f"📋 Clone Botlar Ro'yxati (Sahifa {page + 1}):\n\n"

        keyboard = []

        for idx, (clone_id, clone_data) in enumerate(clones_list[start_idx:end_idx], start=start_idx + 1):
            status = "🟢" if clone_data.get("status") == "running" else "🔴"
            username = clone_data.get("username", DEFAULT_UNKNOWN)
            bot_type = "📦" if clone_data.get("type") == "predefined" else "🔧"

            text += f"{idx}. {status} {bot_type} {clone_id[:20]}...\n"
            text += f"   👤 @{username}\n"
            text += f"   🔑 Token: {clone_data['token'][:15]}...\n"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{status} {clone_id[:15]}...",
                        callback_data=f"clone_info_{clone_id}",
                    )
                ]
            )

        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ OLDINGI", callback_data=f"clone_page_{page-1}"))
        if end_idx < len(clones_list):
            nav_buttons.append(InlineKeyboardButton("KEYINGI ➡️", callback_data=f"clone_page_{page+1}"))

        if nav_buttons:
            keyboard.append(nav_buttons)

        keyboard.append([InlineKeyboardButton("🏠 ASOSIY MENYU", callback_data="clone_bots")])

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if callback_data.startswith("clone_page_"):
        page = int(callback_data.replace("clone_page_", ""))
        user_data["clone_page"] = page
        await handle_callback(update, context)
        return

    if callback_data.startswith("clone_info_"):
        clone_id = callback_data.replace("clone_info_", "")

        if clone_id not in CLONES:
            await query.edit_message_text("❌ Clone bot topilmadi!")
            return

        clone_data = CLONES[clone_id]
        status = "🟢 Ishlayotgan" if clone_data.get("status") == "running" else "🔴 To'xtatilgan"

        text = (
            "📋 Clone Bot Ma'lumotlari:\n\n"
            f"🆔 ID: {clone_id}\n"
            f"📊 Status: {status}\n"
            f'👤 Username: @{clone_data.get("username", DEFAULT_UNKNOWN)}\n'
            f"🔑 Token: {clone_data['token']}\n"
            f"👑 Admin ID: {clone_data['admin_id']}\n"
            f"👥 Admin IDs: {', '.join(map(str, clone_data.get('admin_ids', [])))}\n"
            f"📦 Turi: {'Predefinned' if clone_data.get('type') == 'predefined' else 'Manual'}\n"
            f"🚀 Avto-start: {'✅' if clone_data.get('auto_start', True) else '❌'}\n"
            f'📅 Yaratilgan: {clone_data.get("created_at", DEFAULT_UNKNOWN)}\n'
        )

        if clone_data.get("api_url"):
            text += f"🌐 API URL: {clone_data['api_url'][:50]}...\n"

        keyboard = []

        if clone_data.get("status") == "running":
            keyboard.append([InlineKeyboardButton("🛑 TO'XTATISH", callback_data=f"stop_clone_{clone_id}")])
        else:
            keyboard.append([InlineKeyboardButton("🚀 ISHGA TUSHIRISH", callback_data=f"start_clone_{clone_id}")])

        keyboard.append([InlineKeyboardButton("📊 STATISTIKA", callback_data=f"clone_stats_{clone_id}")])
        keyboard.append([InlineKeyboardButton("◀️ ORQAGA", callback_data="clone_list")])

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if callback_data == "start_all_clones_btn":
        success_count, total_count = start_all_clones()

        await query.edit_message_text(
            "✅ Barcha clone botlar ishga tushirildi!\n\n" f"📊 Natija: {success_count}/{total_count} ta"
        )
        return

    if callback_data == "stop_all_clones_btn":
        success_count, total_count = stop_all_clones()

        await query.edit_message_text(
            "✅ Barcha clone botlar to'xtatildi!\n\n" f"📊 Natija: {success_count}/{total_count} ta"
        )
        return

    if callback_data == "refresh_clones":
        created_count = initialize_predefined_clones()

        await query.edit_message_text(
            "✅ Clone botlar yangilandi!\n\n"
            f"📊 Yangi clone botlar: {created_count} ta\n"
            f"📈 Jami clone botlar: {len(CLONES)} ta"
        )
        return

    if callback_data.startswith("start_clone_"):
        clone_id = callback_data.replace("start_clone_", "")
        if start_clone_bot(clone_id):
            await query.edit_message_text("✅ Clone bot ishga tushirildi!")
        else:
            await query.edit_message_text("❌ Clone botni ishga tushirib bo'lmadi!")
        return

    if callback_data.startswith("stop_clone_"):
        clone_id = callback_data.replace("stop_clone_", "")
        if stop_clone_bot(clone_id):
            await query.edit_message_text("✅ Clone bot to'xtatildi!")
        else:
            await query.edit_message_text("❌ Clone botni to'xtatib bo'lmadi!")
        return


# ================= ASOSIY MESSAGE HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if not is_admin(user_id):
        return

    text = update.message.text.strip()
    user_data = context.user_data

    if user_data.get("awaiting_api"):
        if not is_super_admin(user_id):
            await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
            user_data.pop("awaiting_api", None)
            return

        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("Format: <api_url> <api_key>")
            return

        api_url, api_key = parts[0], parts[1]
        API_DATA.update({"url": api_url, "key": api_key})
        save_json(API_FILE, API_DATA)
        user_data.pop("awaiting_api", None)
        await update.message.reply_text("✅ API sozlandi!")
        return

    if user_data.get("awaiting_order"):
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("Format: <group_id> <service_id> <quantity>")
            return

        group_id, service_id, quantity = parts[0], int(parts[1]), int(parts[2])
        user_data.pop("awaiting_order", None)
        await submit_order(group_id, service_id, quantity, context, update.message.reply_text)
        return

    if text == "/cancel":
        user_data.clear()
        await update.message.reply_text("❌ Amal bekor qilindi", reply_markup=get_main_menu(user_id))
        return

    if text == "/start_all_clones":
        if not is_super_admin(user_id):
            await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
            return

        success_count, total_count = start_all_clones()
        await update.message.reply_text(
            "✅ Barcha clone botlar ishga tushirildi!\n\n" f"📊 Natija: {success_count}/{total_count} ta"
        )
        return

    if text == "/stop_all_clones":
        if not is_super_admin(user_id):
            await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
            return

        success_count, total_count = stop_all_clones()
        await update.message.reply_text(
            "✅ Barcha clone botlar to'xtatildi!\n\n" f"📊 Natija: {success_count}/{total_count} ta"
        )
        return

    if text == "/create_all_clones":
        if not is_super_admin(user_id):
            await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
            return

        created_count = initialize_predefined_clones()
        success_count, total_count = start_all_clones()

        await update.message.reply_text(
            "✅ Barcha clone botlar yaratildi va ishga tushirildi!\n\n"
            "📊 Natijalar:\n"
            f"• Yaratildi: {created_count} ta\n"
            f"• Ishga tushirildi: {success_count}/{total_count} ta\n"
            f"• Jami clone botlar: {len(CLONES)} ta"
        )
        return

    if text.startswith("/clone_status"):
        if not is_super_admin(user_id):
            await update.message.reply_text("❌ Bu amal faqat super admin uchun!")
            return

        running_count = len([c for c in CLONES.values() if c.get("status") == "running"])
        stopped_count = len(CLONES) - running_count

        text_response = (
            "📊 Clone Botlar Statusi:\n\n"
            f"🟢 Ishlayotgan: {running_count} ta\n"
            f"🔴 To'xtatilgan: {stopped_count} ta\n"
            f"📈 Jami: {len(CLONES)} ta\n\n"
            "🚀 Ishga tushirish: /start_all_clones\n"
            "🛑 To'xtatish: /stop_all_clones\n"
            "🔄 Yangilash: /create_all_clones"
        )

        await update.message.reply_text(text_response)
        return


# ================= ASOSIY FUNKSIYA =================
def main() -> None:
    logger.info("🤖 Asosiy bot ishga tushmoqda...")

    initialize_predefined_clones()

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("set_api", set_api_command))
    application.add_handler(CommandHandler("order", order_command))
    application.add_handler(CommandHandler("clone", clone_command))
    application.add_handler(CommandHandler("start_clone", start_clone_command))
    application.add_handler(CommandHandler("stop_clone", stop_clone_command))
    application.add_handler(CommandHandler("delete_clone", delete_clone_command))
    application.add_handler(CommandHandler("start_all_clones", handle_message))
    application.add_handler(CommandHandler("stop_all_clones", handle_message))
    application.add_handler(CommandHandler("create_all_clones", handle_message))
    application.add_handler(CommandHandler("clone_status", handle_message))
    application.add_handler(CommandHandler("link", link_command))
    application.add_handler(CommandHandler("clear_links", clear_links_command))
    application.add_handler(CommandHandler("cancel", handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("=" * 70)
    print("✅ VASYA SMM BOT ISHGA TUSHDI! (53 TA CLONE BOT QO'SHILGAN)")
    print(f"🤖 Jami clone botlar: {len(CLONES)} ta")
    print("👑 Asosiy admin ID: 7721170248")
    print("")
    print("🚀 TEZKOR BUYRUQLAR:")
    print("• /start_all_clones - Barcha clone botlarni ishga tushirish")
    print("• /stop_all_clones - Barcha clone botlarni to'xtatish")
    print("• /create_all_clones - 53 ta clone botni yaratish")
    print("• /clone_status - Clone botlar statusi")
    print("")
    print("🎮 INTERFACE ORQALI:")
    print("1. Asosiy menyudan '🤖 CLONE BOTS' tugmasini bosing")
    print("2. '🚀 CREATE ALL CLONES' - 53 ta clone bot yaratish")
    print("3. '📋 CLONE BOTLAR RO'YXATI' - Barcha botlarni ko'rish")
    print("=" * 70)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


# ================= POST INITIALIZE =================
async def post_init(app: Application) -> None:
    asyncio.create_task(auto_reorder_cancel_task(app))

    logger.info("🚀 Clone botlar avtomatik ishga tushirilmoqda...")
    success_count = 0

    for clone_id, clone_data in CLONES.items():
        if clone_data.get("auto_start", True) and clone_data.get("status") != "running":
            if start_clone_bot(clone_id):
                success_count += 1

    logger.info("✅ %s/%s ta clone bot ishga tushirildi", success_count, len(CLONES))


# ================= ASOSIY BOT TASK =================
async def auto_reorder_cancel_task(app: Application) -> None:
    logger.info("🔄 Asosiy bot auto-reorder task started")

    while True:
        try:
            if SETTINGS.get("global_auto_reorder"):
                for order in ORDERS[:]:
                    if order.get("done", False):
                        continue

                    order_id = order.get("order_id")
                    if not order_id:
                        continue

                    result = await smm_api_request("status", order=order_id)
                    if not result:
                        continue

                    status = str(result.get("status", "")).lower()
                    if "cancel" in status or "refund" in status:
                        retry_count = order.get("retry_count", 0)
                        if retry_count < 3:
                            new_result = await smm_api_request(
                                "add",
                                service=order["service"],
                                link=order["link"],
                                quantity=order["quantity"],
                            )
                            if new_result and "order" in new_result:
                                order["order_id"] = new_result["order"]
                                order["retry_count"] = retry_count + 1
                                order["status"] = "retried"
                                order["last_retry"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                save_json(ORDERS_FILE, ORDERS)
                            else:
                                order["done"] = True
                                save_json(ORDERS_FILE, ORDERS)
                        else:
                            order["done"] = True
                            save_json(ORDERS_FILE, ORDERS)

            if SETTINGS.get("global_auto_cancel"):
                cancel_minutes = SETTINGS.get("auto_cancel_minutes", 10)
                now = datetime.now()
                changed = False
                for order in ORDERS[:]:
                    if order.get("done", False):
                        continue
                    created_at = datetime.strptime(order["created_at"], "%Y-%m-%d %H:%M:%S")
                    if now - created_at > timedelta(minutes=cancel_minutes):
                        order["done"] = True
                        order["status"] = "auto_cancelled"
                        changed = True

                if changed:
                    save_json(ORDERS_FILE, ORDERS)

            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error("Auto task loop error: %s", e)
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖 Bot to'xtatildi!")

        success_count, total_count = stop_all_clones()
        print(f"✅ {success_count}/{total_count} ta clone bot to'xtatildi")

    except Exception as e:
        logger.error("Bot xatosi: %s", e)
