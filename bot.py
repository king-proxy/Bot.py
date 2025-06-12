from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import json
import os
import nest_asyncio
import asyncio

BOT_TOKEN = '8164823725:AAE1Cgrn1ByjmYT469XV7Jk76Pyzgv6bAqw'
OWNER_ID = 7330902444
PROXY_FILE = 'proxies.json'
USERS_FILE = 'users.json'
CHANNEL_ID = "@Proxyking_Telegram"  # آیدی کانال بدون https://t.me/


# --- بارگذاری و ذخیره پروکسی‌ها ---
def load_data():
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"mci": [], "irancell": []}


def save_data(data):
    with open(PROXY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- بارگذاری و ذخیره کاربران ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # ذخیره کاربر اگر جدید بود
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

    keyboard = [
        [InlineKeyboardButton("📡 پروکسی همراه اول", callback_data='show_mci')],
        [InlineKeyboardButton("📡 پروکسی ایرانسل", callback_data='show_irancell')]
    ]
    if user_id == OWNER_ID:
        keyboard += [
            [InlineKeyboardButton("➕ افزودن پروکسی همراه اول", callback_data='add_mci')],
            [InlineKeyboardButton("➕ افزودن پروکسی ایرانسل", callback_data='add_irancell')],
            [InlineKeyboardButton("🛠 مدیریت پروکسی‌ها", callback_data='manage')],
            [InlineKeyboardButton("👥 کاربران فعال", callback_data='show_users')]
        ]

    # چک عضویت در کانال
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            # عضو نیست
            raise Exception("Not member")
    except:
        # اگر کانال نیست، پیام با دکمه‌های عضویت و بررسی عضویت نشان بده
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.strip('@')}")],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
        ]
        text = ("سلام 👋\nبرای استفاده از ربات باید ابتدا عضو کانال شوید.")
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # اگر عضو بود منوی اصلی رو نشان بده
    text = "سلام خوش اومدی 👋\nلطفاً از منو یکی رو انتخاب کن:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()
    proxies = load_data()

    if data == "check_join":
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                await query.edit_message_text("✅ شما عضو کانال هستید.")
                await start(update, context)
            else:
                raise Exception("Not a member")
        except:
            await query.edit_message_text("❌ هنوز عضو نشدی. لطفاً ابتدا عضو شو:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.strip('@')}")],
                [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join")]
            ]))

    elif data == "show_users" and user_id == OWNER_ID:
        users = load_users()
        if not users:
            text = "👥 هنوز هیچ کاربری ثبت نشده."
        else:
            text = "👥 کاربران فعال:\n"
            lines = []
            for u_id in users:
                try:
                    user_obj = await context.bot.get_chat(u_id)
                    username = f"@{user_obj.username}" if user_obj.username else "(بدون یوزرنیم)"
                except:
                    username = "(مشخصات قابل دریافت نیست)"
                lines.append(f"• {username} — {u_id}")
            text += "\n".join(lines)
        await query.edit_message_text(text, reply_markup=back_menu())

    elif data.startswith("show_"):
        key = "mci" if "mci" in data else "irancell"
        proxy_list = proxies.get(key, [])
        if not proxy_list:
            await query.edit_message_text("❌ چیزی ثبت نشده.", reply_markup=back_menu())
            return
        keyboard = []
        for idx, proxy in enumerate(proxy_list, 1):
            keyboard.append([InlineKeyboardButton(f"Proxy {idx}", url=proxy)])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        await query.edit_message_text(
            f"🔌 لیست پروکسی‌های {'همراه اول' if key == 'mci' else 'ایرانسل'}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("add_") and user_id == OWNER_ID:
        context.user_data["add_mode"] = "mci" if "mci" in data else "irancell"
        await query.edit_message_text(
            "لطفاً لینک پروکسی رو یکی‌یکی بفرست. به‌محض ارسال، ذخیره موقت میشه و باید ذخیره نهایی کنی.",
            reply_markup=back_menu()
        )

    elif data == "final_save":
        if "confirm_proxy" not in context.user_data or "add_mode" not in context.user_data:
            await query.answer("⚠️ داده‌ای برای ذخیره وجود ندارد.", show_alert=True)
            return
        link = context.user_data["confirm_proxy"]
        key = context.user_data["add_mode"]
        data = load_data()
        data[key].append(link)
        save_data(data)
        context.user_data.pop("confirm_proxy")
        context.user_data.pop("add_mode")
        await start(update, context)

    elif data == "manage":
        keyboard = [
            [InlineKeyboardButton("🗑 حذف همراه اول", callback_data="delete_mci")],
            [InlineKeyboardButton("🗑 حذف ایرانسل", callback_data="delete_irancell")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await query.edit_message_text("مدیریت پروکسی‌ها:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("delete_") and user_id == OWNER_ID:
        key = "mci" if "mci" in data else "irancell"
        proxy_list = proxies.get(key, [])
        if not proxy_list:
            await query.edit_message_text("❌ هیچ پروکسی برای حذف وجود ندارد.", reply_markup=back_menu())
            return
        keyboard = []
        for idx, proxy in enumerate(proxy_list, 1):
            keyboard.append([InlineKeyboardButton(f"❌ حذف Proxy {idx}", callback_data=f"confirm_del_{key}_{idx-1}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage")])
        await query.edit_message_text(
            f"🗑 کدوم پروکسی {key.upper()} رو میخوای حذف کنی؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("confirm_del_"):
        _, key, index = data.split("_")
        index = int(index)
        data = load_data()
        if 0 <= index < len(data[key]):
            deleted = data[key].pop(index)
            save_data(data)
            await query.edit_message_text(f"✅ پروکسی حذف شد:\n{deleted}")
        else:
            await query.edit_message_text("⚠️ شماره پروکسی نامعتبر بود.")
        await start(update, context)

    elif data == "back":
        await start(update, context)


async def handle_proxy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return
    if "add_mode" not in context.user_data:
        await update.message.reply_text("⛔️ ابتدا گزینه افزودن پروکسی را بزن.")
        return
    link = update.message.text.strip()
    if not link.startswith("https://t.me/proxy?"):
        await update.message.reply_text("⛔️ لینک معتبر نیست.")
        return
    key = context.user_data["add_mode"]
    data = load_data()
    proxy_number = len(data[key]) + 1
    context.user_data["confirm_proxy"] = link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Proxy {proxy_number}", url=link)],
        [
            InlineKeyboardButton("💾 ذخیره نهایی", callback_data="final_save"),
            InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back")
        ]
    ])
    await update.message.reply_text(
        "✅ لینک ذخیره موقت شد.\nبرای ذخیره نهایی روی دکمه «💾 ذخیره نهایی» بزن.",
        reply_markup=keyboard
    )


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_message))
    print("🤖 Bot is running...")
    await app.run_polling()


if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
