from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from random import randint
from config import *
from functions import *
import asyncio
import db

bot = Bot(token=API_TOKEN, parse_mode="markdown")
dp = Dispatcher(bot=bot, storage=MemoryStorage())

class UC(StatesGroup):
    id = State()
    amount = State()

@dp.message_handler(text="⬅️Bekor qilish", state="*")
async def cancelFunc(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("✅Bekor qilindi", reply_markup=menu)

bekor_qilish = ReplyKeyboardMarkup(resize_keyboard=True)
bekor_qilish.add("⬅️Bekor qilish")

kanallar_list = InlineKeyboardMarkup(row_width=1)
count = 1
for kanal in KANALLAR:
    kanallar_list.add(InlineKeyboardButton(text=f"{count} - homiy kanal", url=kanal))
    count += 1
kanallar_list.add(InlineKeyboardButton(text="✅Tasdiqlash", callback_data="tasdiqlash"))

menu_buttons = [
    [
        KeyboardButton("🔗Referal havola"),
        KeyboardButton("💰Balans")
    ],
    [
        KeyboardButton("🥶UC chiqarib olish")
    ]
]
menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=menu_buttons)

admin_buttons = [
    [
        KeyboardButton("🎲RANDOM"),
        KeyboardButton("⬅️Orqaga")
    ]
]
admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_buttons)

@dp.message_handler(commands=['start'])
async def welcome_function(message: types.Message):
    start_info = message.text.split()
    # AGAR USER REFERALDAN KIRGAN BO'LSA UNI MALUMOTLARINI ref TABLESIGA SAQLAB TURAMIZ
    if len(start_info) > 1:
        db.set_ref(message.from_user.id, start_info[-1])
    #-.-.-.-.-.-.-.-.-.-.-.-.-.-.
    
    await message.answer(text=ERRFOLLOW, reply_markup=kanallar_list)

@dp.callback_query_handler(text="tasdiqlash")
async def tasdiqlash_func(call: types.CallbackQuery):
    user_id = call.from_user.id
    users = db.get_users()

    if await check_follow(user_id):
        await bot.delete_message(user_id, call.message.message_id)
        await bot.send_message(user_id, text=STARTTEXT, reply_markup=menu)

        try:
            reffer = db.get_ref(user_id)
            db.del_ref(user_id)
            if user_id not in users and reffer != user_id:
                db.add_ref(reffer)
                await bot.send_message(reffer, f"*🎉Tabriklaymiz, {call.from_user.full_name} sizning havolangiz orqali ro'yhatdan o'tdi*")
                db.add_user(user_id)
            try:
                db.del_ref(user_id)
            except:
                pass
        except:
            if user_id not in users:
                db.add_user(user_id)

    else:
        await call.answer("❌Siz hali kanallarga a'zo bo'lmadingiz")

@dp.message_handler(text="💰Balans")
async def getBalance(message: types.Message):
    if await check_follow(message.from_user.id):
        balans = db.get_balans(message.from_user.id)
        await message.answer(f"*🖇Sizning referallaringiz: {balans}\n💳Jami UC laringiz: {balans * REFERAL_NARXI}*")
    else:
        await message.answer(ERRFOLLOW, reply_markup=kanallar_list)

@dp.message_handler(text="🔗Referal havola")
async def getShareLink(message: types.Message):
    if await check_follow(message.from_user.id):
        await message.answer(f"*Sizning referal havolangiz: \n{BOT}?start={message.from_user.id}\n\n🚫Siz o'zingizga referal bo'la olmaysiz, halol bo'ling*")
    else:
        await message.answer(ERRFOLLOW, reply_markup=kanallar_list)

@dp.message_handler(text="🥶UC chiqarib olish")
async def withdrawUC(message: types.Message, state: FSMContext):
    if await check_follow(message.from_user.id):
        amount = db.get_balans(message.from_user.id) * REFERAL_NARXI
        if amount < 60:
            await message.answer("*Eng kam UC yechib olish miqdori - 60 UC*")
        else:
            await message.answer("*O'zingizni PUBG MOBILE o'yinidagi ID raqamingizni yuboring:*", reply_markup=bekor_qilish)
            await UC.id.set()
    else:
        await message.answer(ERRFOLLOW, reply_markup=kanallar_list)

@dp.message_handler(state=UC.id)
async def getAmountOfUc(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(
            {
                'id': message.text
            }
        )
        await message.answer("*Yaxshi, qancha UC yechib olmoqchisiz? *", reply_markup=bekor_qilish)
        await UC.amount.set()
    else:
        await message.answer("*Iltimos, ID yuborishda faqat raqamladan foydalaning!*", reply_markup=bekor_qilish)

@dp.message_handler(state=UC.amount)
async def finishUCState(message: types.Message, state: FSMContext):
    amount = message.text
    balans = db.get_balans(message.from_user.id)
    if amount.isdigit():
        if int(amount) <= (balans * 5):
            await state.update_data(
                {
                    'amount': amount
                }
            )
            data = await state.get_data()
            await state.finish()
            db.minus_balans(message.from_user.id, int(amount)//5)
            await message.answer("*✅Qabul qilindi , barcha ma'lumotlar to'g'ri bo'lsa 24 soat ichida UC sizga o'tkazib beriladi!*", reply_markup=menu)
            await bot.send_message(ADMIN_ID, f"🆕Yangi buyurtma!\nFoydalanuvchi: {message.from_user.full_name}\nPUBG ID: {data['id']}\nMiqdor: {data['amount']}UC\nBuyurtma bajarilgandan so'ng quyidagi habarni botga yuboring:\n`/send {message.from_user.id} ✅UC TUSHDI!`")
        else:
            await message.answer("*Hisobingizda yetarli UC mavjud emas!*")
    else:
        await message.answer("*Iltimos faqat raqamlardan foydalaning!*", reply_markup=bekor_qilish)

@dp.message_handler(commands=['send'])
async def UCWifthdrawCompleted(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        data = message.text.split()
        id = data.pop(1)
        data.pop(0)
        txt = " ".join(data)
        try:
            await bot.send_message(id, text=txt)
            await bot.send_message(ADMIN_ID, "UC tushganligi haqidagi habar yuborildi!")
        except Exception as e:
            await bot.send_message(ADMIN_ID, f"Nimadir xato ketdi: {e}")

@dp.message_handler(commands=['admin'])
async def openADMINmenu(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("*KEYZO admin panelga xush kelibsiz!*", reply_markup=admin_menu)
@dp.message_handler(text="⬅️Orqaga")
async def backADMIN(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Bosh menyuga qaytdingiz!", reply_markup=menu)
@dp.message_handler(text="🎲RANDOM")
async def generateRandomUser(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        users = db.get_users()
        idx = randint(0,len(users)-1)
        await message.answer(f"💫Tasodifiy foydalanuvchi telegram ID'si: {users[idx]}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)