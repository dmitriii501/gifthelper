import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Укажи здесь токен своего бота от @BotFather
BOT_TOKEN = "8529162750:AAGFcFk2Hx6ApglXdz5Mmt2FL5xCHq34Xmo"

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Состояния для FSM
class GiftState(StatesGroup):
    age = State()
    interests = State()
    budget = State()
    style = State()
    final = State()

# Клавиатуры
def make_keyboard(options):
    buttons = [KeyboardButton(text=opt) for opt in options]
    return ReplyKeyboardMarkup(
        keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🎄 Привет! Я помогу тебе выбрать идеальный подарок для девушки на Новый год!\n\n"
        "Сколько ей лет?",
        reply_markup=make_keyboard(["<20", "20–25", "26–30", "31–35", ">35"])
    )
    await state.set_state(GiftState.age)

@router.message(GiftState.age)
async def handle_age(message: Message, state: FSMContext):
    age = message.text
    if age not in ["<20", "20–25", "26–30", "31–35", ">35"]:
        await message.answer("Пожалуйста, выбери вариант из кнопок.")
        return
    await state.update_data(age=age)
    await message.answer(
        "Какие у неё основные интересы?",
        reply_markup=make_keyboard([
            "Красота и уход", "Мода и стиль",
            "Технологии", "Книги и творчество",
            "Путешествия", "Спорт и активность"
        ])
    )
    await state.set_state(GiftState.interests)

@router.message(GiftState.interests)
async def handle_interests(message: Message, state: FSMContext):
    interests = message.text
    valid = ["Красота и уход", "Мода и стиль", "Технологии", "Книги и творчество", "Путешествия", "Спорт и активность"]
    if interests not in valid:
        await message.answer("Выбери интерес из предложенных вариантов.")
        return
    await state.update_data(interests=interests)
    await message.answer(
        "Какой у тебя бюджет?",
        reply_markup=make_keyboard(["<3000 ₽", "3000–7000 ₽", "7000–15000 ₽", ">15000 ₽"])
    )
    await state.set_state(GiftState.budget)

@router.message(GiftState.budget)
async def handle_budget(message: Message, state: FSMContext):
    budget = message.text
    if budget not in ["<3000 ₽", "3000–7000 ₽", "7000–15000 ₽", ">15000 ₽"]:
        await message.answer("Пожалуйста, выбери из кнопок.")
        return
    await state.update_data(budget=budget)
    await message.answer(
        "Какой у неё стиль?",
        reply_markup=make_keyboard(["Минимализм", "Гламур", "Бохо", "Спортивный", "Романтичный", "Не знаю"])
    )
    await state.set_state(GiftState.style)

@router.message(GiftState.style)
async def handle_style(message: Message, state: FSMContext):
    style = message.text
    valid = ["Минимализм", "Гламур", "Бохо", "Спортивный", "Романтичный", "Не знаю"]
    if style not in valid:
        await message.answer("Выбери стиль из кнопок.")
        return
    await state.update_data(style=style)
    await state.set_state(GiftState.final)
    await generate_gift(message, state)

async def generate_gift(message: Message, state: FSMContext):
    data = await state.get_data()
    age, interests, budget, style = data["age"], data["interests"], data["budget"], data["style"]

    # Логика подарков — много ветвлений
    gift = None

    # Пример: девушка моложе 25, любит технологии и бюджет до 7к → подарок
    if age in ["<20", "20–25"] and interests == "Технологии" and budget in ["<3000 ₽", "3000–7000 ₽"]:
        gift = "Беспроводные наушники с кейсом (например, Redmi Buds или AirPods 2)"

    elif interests == "Красота и уход" and budget in ["3000–7000 ₽", "7000–15000 ₽"]:
        gift = "Подарочный набор от Sephora или набор люксовой косметики (Chanel, Dior)"

    elif interests == "Мода и стиль" and style == "Гламур":
        gift = "Элегантный клатч или стильные солнцезащитные очки (Ray-Ban, Gucci)"

    elif interests == "Путешествия" and budget == ">15000 ₽":
        gift = "Персонализированный чемодан с GPS-трекером или сертификат на выходные в Париж"

    elif interests == "Спорт и активность" and age in ["20–25", "26–30"]:
        gift = "Фитнес-браслет (Huawei Band или Xiaomi Smart Band) + подписка на Fitstar"

    elif interests == "Книги и творчество" and style in ["Романтичный", "Минимализм"]:
        gift = "Кожаный ежедневник Moleskine + набор качественных ручек или ароматическая свеча с цитатой из книги"

    elif budget == "<3000 ₽":
        gift = "Персонализированная кружка с фото + набор какао и маршмеллоу + открытка с тёплым пожеланием"

    elif style == "Не знаю":
        gift = "Сертификат на выбор в популярном магазине (Летуаль, Lamoda, Ozon) — она сама выберет то, что хочет!"

    else:
        gift = "Подарочный сертификат на мастер-класс (керамика, парфюмерия, кулинария) — трендовый и запоминающийся подарок!"

    await message.answer(f"✨ Отлично! Вот мой совет:\n\n🎁 {gift}\n\nУдачи и с Новым годом! 🎄")
    await message.answer("Хочешь попробовать ещё? Напиши /start")

# Подключаем роутер
dp.include_router(router)

# Запуск
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
