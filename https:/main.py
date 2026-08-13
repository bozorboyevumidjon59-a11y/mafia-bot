import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Token va Owner ID sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token Render'dagi Environment Variables'dan olinadi
OWNER_ID = 8235490985  # <--- Shu yerga o'zingizning Telegram ID raqamingizni yozing!

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# O'yin xotirasi
game_data = {
    "is_started": False,
    "players": {}
}

# --- BUYRUQLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    # Owner uchun cheksiz resurslar
    if user_id == OWNER_ID:
        diamonds = "♾️ Cheksiz"
        money = "♾️ Cheksiz"
        role_title = "👑 Bosh Admin / Owner"
    else:
        diamonds = 10
        money = 1000
        role_title = "🎮 O'yinchi"

    text = (
        f"👋 Salom, {message.from_user.full_name}!\n"
        f"🎭 Mafiya Game Botga xush kelibsiz.\n\n"
        f"Sizning maqomingiz: {role_title}\n"
        f"💎 Olmoslar: {diamonds}\n"
        f"💰 Tangalar: {money}\n\n"
        f"Guruhda o'yin boshlash uchun botni guruhga qo'shing va /newgame buyrug'ini yuboring."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "📜 Bot Buyruqlari Ro'yxati:\n\n"
        "/start - Botni ishga tushirish va profilni ko'rish\n"
        "/newgame - Guruhda yangi o'yin e'lon qilish\n"
        "/players - Hozirgi qatnashchilar ro'yxati\n"
        "/stats - O'yin statistikasi\n"
        "/shop - Do'kon (Himoya va olmoslar)"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("newgame"))
async def cmd_newgame(message: types.Message):
    if message.chat.type == "private":
        await message.answer("⚠️ Ushbu buyruqni faqat guruhda ishlatish mumkin!")
        return

    if game_data["is_started"]:
        await message.answer("⚠️ O'yin allaqachon e'lon qilingan!")
        return

    game_data["is_started"] = True
    game_data["players"] = {}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 O'yinga qo'shilish", callback_data="join_game")]
    ])

    await message.answer(
        "🎭 Yangi Mafiya o'yini e'lon qilindi!\n\n"
        "O'yinda qatnashish uchun pastdagi tugmani bosing.\n"
        "Minimum o'yinchilar: 4 ta\n"
        "Maksimum: 20 tagacha!",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "join_game")
async def btn_join(call: types.CallbackQuery):
    user = call.from_user
    if user.id in game_data["players"]:
        await call.answer("Siz allaqachon o'yindasiz!", show_alert=True)
        return

    game_data["players"][user.id] = {
        "name": user.full_name,
        "role": None
    }

    count = len(game_data["players"])
    await call.answer("Siz o'yinga muvaffaqiyatli qo'shildingiz!")
    await call.message.edit_text(
        f"🎭 Mafiya o'yini kutilmoqda...\n\n"
        f"👥 Qo'shilgan o'yinchilar soni: {count} ta\n"
        f"O'yin boshlanishi uchun yetarli qatnashchi kerak.",
        reply_markup=call.message.reply_markup,
        parse_mode="Markdown"
    )

@dp.message(Command("players"))
async def cmd_players(message: types.Message):
    if not game_data["players"]:
        await message.answer("Hali hech kim o'yinga qo'shilmadi.")
        return

    text = "📋 Qatnashchilar ro'yxati:\n\n"
    for idx, (p_id, p_info) in enumerate(game_data["players"].items(), 1):
        status = "👑 (Owner)" if p_id == OWNER_ID else ""
        text += f"{idx}. {p_info['name']} {status}\n"

    await message.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
