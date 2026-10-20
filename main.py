import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

dp = Dispatcher()

class OrderForm(StatesGroup):
    waiting_for_product = State()
    waiting_for_place = State()
    waiting_for_time = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(OrderForm.waiting_for_product)
    await message.answer(
        "👋 Привет! Сейчас я соберу твой заказ.\n\n"
        "Шаг 1: Напиши название товара (название банки из канала, если больше одной указывать все в одном сообщение).\n"
        "Я подскажу следующий шаг."
    )

@dp.message(OrderForm.waiting_for_product)
async def process_product(message: types.Message, state: FSMContext):
    product = message.text.strip()
    await state.update_data(product=product)
    await state.set_state(OrderForm.waiting_for_place)
    await message.answer(
        f"✅ Товар: {product}\n\n"
        "Шаг 2: Напиши место встречи (например, «улица Красина,8»). А следущим сообщением время (18:00)"
    )

@dp.message(OrderForm.waiting_for_place)
async def process_place(message: types.Message, state: FSMContext):
    place = message.text.strip()
    await state.update_data(place=place)
    await state.set_state(OrderForm.waiting_for_time)
    await message.answer(
        f"✅ Товар: {state.data['product']}\n"
        f"✅ Место: {place}\n\n"
        "Шаг 3: Напиши время встречи (например, «18:00»)."
    )

@dp.message(OrderForm.waiting_for_time)
async def process_time(message: types.Message, state: FSMContext):
    time = message.text.strip()
    data = await state.get_data()
    
    # Текст для покупателя
    customer_text = (
        f"📦 Твой заказ:\n"
        f"Товар: {data['product']}\n"
        f"Место встречи: {data['place']}\n"
        f"Время: {time}\n\n"
        "Заказ принят! Ожидай подтверждения."
    )
    
    # Текст для тебя (админа)
    admin_text = (
        f"🔔 Новый заказ!\n"
        f"Товар: {data['product']}\n"
        f"Место встречи: {data['place']}\n"
        f"Время: {time}\n"
        f"От пользователя: {message.from_user.full_name} (@{message.from_user.username or 'нет'})"
    )
    
    # Отправляем покупателю
    await message.answer(customer_text)
    
    # Отправляем тебе (замените CHAT_ID на свой числовой ID чата)
    await bot.send_message(chat_id=7327512347, text=admin_text)
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())