import os
import timeit
import asyncio
import datetime
import dataclasses

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor, exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ["BOT_TOKEN"]
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_list_full = []


@dataclasses.dataclass
class User:
    user_id: int
    is_active: bool = False


@dp.message_handler(commands=["notify"])
async def process_start_comm(message: types.Message):
    await notify_users()


@dp.message_handler(commands=["report"])
async def report(message: types.Message):
    await create_report()


async def notify_users():
    start = timeit.default_timer()

    task_list = [
        try_send_message(text=f"Hello, world {i}", user_id=u.user_id)
        for i, u in enumerate(user_list_full)
    ]
    await asyncio.gather(*task_list)

    elapsed = timeit.default_timer() - start
    print("Done in", round(elapsed, 2))


async def try_send_message(text: str, user_id: int):
    try:
        button1 = InlineKeyboardButton("Читать", callback_data="read_signal")
        kb = InlineKeyboardMarkup()
        kb.add(button1)
        await bot.send_message(user_id, text, reply_markup=kb)
    except exceptions.RetryAfter as ex:
        await asyncio.sleep(ex.timeout)
        await try_send_message(text=text, user_id=user_id)


@dp.callback_query_handler(lambda c: c.data == "read_signal")
async def precess_callback_read(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    for u in user_list_full:
        if u.user_id == user_id:
            u.is_active = True
            break


async def create_report():
    with open("reports/template.html", "r") as file:
        template = file.read()
    table_content = ""
    for u in user_list_full:
        table_content += f"""<tr><td>{u.user_id}</td><td>{u.is_active}</td></tr>
    """
    result = template.replace("{table_content}", table_content)
    idx = datetime.datetime.now()
    file_name = f"reports/{idx.strftime('%Y-%m-%d %H-%M-%S')}.html"
    with open(file_name, "w") as file:
        file.write(result)


def main():
    [user_list_full.append(User(user_id=1498994847)) for _ in range(1000)]
    print("Starting bot...")
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
