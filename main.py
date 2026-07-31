import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN", "8666007737:AAF7vJPcViQKNFMAMq0maTYX9IFRfAuRnbY")
OWNER_ID = int(os.getenv("OWNER_ID", "7993731515"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("mafia_bot.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    diamonds INTEGER DEFAULT 0,
    has_pro INTEGER DEFAULT 0,
    partner_id INTEGER DEFAULT NULL
)
''')
conn.commit()

def get_user(user_id, full_name=""):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        is_owner = (user_id == OWNER_ID)
        diamonds = 999999 if is_owner else 0
        has_pro = 1 if is_owner else 0
        
        cursor.execute(
            "INSERT INTO users (user_id, full_name, diamonds, has_pro) VALUES (?, ?, ?, ?)",
            (user_id, full_name, diamonds, has_pro)
        )
        conn.commit()
        return get_user(user_id, full_name)
    return user

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    get_user(message.from_user.id, message.from_user.full_name)
    await message.answer("👋 Xush kelibsiz! Mafiya botiga tayyormisiz?\n\nBuyruqlar: /me, /buy_pro, /pair")

@dp.message(Command("me"))
async def profile_cmd(message: types.Message):
    user = get_user(message.from_user.id, message.from_user.full_name)
    pro_status = "✅ PRO" if user[3] == 1 else "❌ Yo'q"
    partner_info = "Yo'q"
    
    if user[4]:
        cursor.execute("SELECT full_name FROM users WHERE user_id = ?", (user[4],))
        partner = cursor.fetchone()
        if partner:
            partner_info = partner[0]

    text = (
        f"👤 **Sizning profilingiz:**\n\n"
        f"🔹 Ism: {user[1]}\n"
        f"💎 Almoslar: {user[2]} ta\n"
        f"⭐ Pro Galochka: {pro_status}\n"
        f"❤️ Juftingiz: {partner_info}"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("buy_pro"))
async def buy_pro_cmd(message: types.Message):
    user = get_user(message.from_user.id, message.from_user.full_name)
    if user[3] == 1:
        await message.answer("Sizda allaqachon ✅ PRO status bor!")
        return
        
    if user[2] < 50:
        await message.answer("❌ Sizda yetarli almos yo'q! Pro galochka narxi: 50 💎 almos.")
        return

    cursor.execute("UPDATE users SET diamonds = diamonds - 50, has_pro = 1 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    await message.answer("Tashakkur! Siz muvaffaqiyatli ✅ PRO status sotib oldingiz!")

@dp.message(Command("pair"))
async def pair_cmd(message: types.Message):
    if not message.reply_to_message:
        await message.answer("Juft bo'lish uchun biror foydalanuvchining xabariga reply qilib /pair deb yozing!")
        return

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:
        await message.answer("O'zingiz bilan juft bo'la olmaysiz!")
        return

    get_user(sender.id, sender.full_name)
    get_user(target.id, target.full_name)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Rozi bo'lish", callback_data=f"accept_pair_{sender.id}_{target.id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"deny_pair_{sender.id}_{target.id}")
        ]
    ])

    await message.answer(
        f"❤️ [{target.full_name}](tg://user?id={target.id}), [{sender.full_name}](tg://user?id={sender.id}) sizga juft bo'lish taklifini yubordi!",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("accept_pair_"))
async def accept_pair(callback: types.CallbackQuery):
    data = callback.data.split("_")
    sender_id = int(data[2])
    target_id = int(data[3])

    if callback.from_user.id != target_id:
        await callback.answer("Bu taklif sizga yuborilmagan!", show_alert=True)
        return

    cursor.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (target_id, sender_id))
    cursor.execute("UPDATE users SET partner_id = ? WHERE user_id = ?", (sender_id, target_id))
    conn.commit()

    await callback.message.edit_text("🎉 Tabriklaymiz! Siz endi juftliksiz!")

@dp.callback_query(F.data.startswith("deny_pair_"))
async def deny_pair(callback: types.CallbackQuery):
    data = callback.data.split("_")
    target_id = int(data[3])

    if callback.from_user.id != target_id:
        await callback.answer("Bu taklif sizga yuborilmagan!", show_alert=True)
        return

    await callback.message.edit_text("❌ Taklif rad etildi.")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
