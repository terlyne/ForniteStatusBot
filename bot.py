import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import config
import status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

subscribed_users = []

current_server_status = ""

async def check_server_status_periodically():
    """Функция для периодической проверки статуса серверов каждые 5 минут"""
    global current_server_status
    while True:
        status_server = await status.check_status_servers()

        if status_server != current_server_status:
            current_server_status = status_server
            if "закрыты" in status_server.lower():
                await notify_subscribed_users(status_server)

        await asyncio.sleep(300)

async def notify_subscribed_users(status_message):
    """Отправка уведомлений пользователям, подписанным на обновления"""
    if subscribed_users:
        for user_id in subscribed_users:
            try:
                await bot.send_message(user_id, f"Уведомление о статусе серверов Fortnite: {status_message}")
                logger.info(f"Уведомление отправлено пользователю {user_id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

@dp.message(Command("start"))
async def send_welcome(message: Message):
    """Обработчик команды /start"""
    button = KeyboardButton(text="Check Server Status")
    markup = ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True
    )
    await message.answer(f"""
        @{message.from_user.username}, привет✋
        Данный телеграм-бот был создан для проверки статуса серверов Fortnite.
        Нажмите кнопку ниже, чтобы проверить состояние серверов.
        Если хотите получать уведомления о статусе серверов, нажмите "Подписаться".
    """, reply_markup=markup)

@dp.message(lambda message: message.text == "Check Server Status")
async def handle_check_status(message: Message):
    """Обработчик кнопки Check Server Status"""
    status_server = await status.check_status_servers()
    await message.answer(status_server)

@dp.message(lambda message: message.text == "Подписаться")
async def handle_subscribe(message: Message):
    """Обработчик кнопки для подписки на уведомления"""
    if message.from_user.id not in subscribed_users:
        subscribed_users.append(message.from_user.id)
        await message.answer("Вы успешно подписались на уведомления о статусе серверов!")
    else:
        await message.answer("Вы уже подписаны на уведомления.")

async def main():
    """Основная функция для запуска бота"""
    asyncio.create_task(check_server_status_periodically())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
