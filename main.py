import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8973302507:AAHoAmYP3g0bPdR46HJ7sVRCXpTEz69yDII"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Привязываем ваш канал напрямую
target_channel_id = "@RustZEROo"
target_message_id = None


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Включен", callback_data="status_on")
    builder.button(text="🔴 Выключен", callback_data="status_off")
    builder.button(text="🛠 На тех. работах", callback_data="status_maint")
    builder.adjust(1)
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 **Привет!** Я бот управления статусом для канала `{target_channel_id}`.\n\n"
        "Выберите статус ниже, чтобы запустить анимацию в канале:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("status_"))
async def process_status_change(callback: types.CallbackQuery):
    global target_message_id, target_channel_id

    status_code = callback.data.split("_")[1]
    await callback.answer("⏳ Обновляем статус в канале...")

    if status_code == "on":
        frames = [
            "🔄 **Запуск сервера...** [▱▱▱▱▱▱▱▱▱▱] 0%",
            "🔄 **Запуск сервера...** [████▱▱▱▱▱▱] 40%",
            "🔄 **Запуск сервера...** [████████▱▱] 80%",
            "✨ **Сервер почти готов!** [██████████] 100%",
        ]
        final_text = (
            "🟢 **СТАТУС СЕРВЕРА: ВKЛЮЧЕН**\n\n"
            "Сервер работает в штатном режиме. Добро пожаловать в игру!"
        )

    elif status_code == "off":
        frames = [
            "⚠️ **Инициализация остановки...** ⏳",
            "🔴 **Сохранение данных и выключение...** 💾",
        ]
        final_text = (
            "🔴 **СТАТУС СЕРВЕРА: ВЫКЛЮЧЕН**\n\n"
            "Сервер остановлен. Следите за новостями о запуске!"
        )

    elif status_code == "maint":
        frames = [
            "🛠 **Подготовка к техническим работам...** ⚙️",
            "🛠 **Установка обновлений и проверка систем...** 🔧",
        ]
        final_text = (
            "🛠 **СТАТУС СЕРВЕРА: ТЕХ. РАБОТЫ**\n\n"
            "На сервере ведутся профилактические работы. Доступ временно ограничен."
        )

    try:
        # Если пост в канале ещё не создавался
        if target_message_id is None:
            msg = await bot.send_message(
                chat_id=target_channel_id, 
                text=frames[0], 
                parse_mode="Markdown"
            )
            target_message_id = msg.message_id
            await asyncio.sleep(1)

            for frame in frames[1:]:
                await bot.edit_message_text(
                    chat_id=target_channel_id,
                    message_id=target_message_id,
                    text=frame,
                    parse_mode="Markdown"
                )
                await asyncio.sleep(1)
        else:
            # Если пост уже есть — проигрываем анимацию редактирования
            for frame in frames:
                await bot.edit_message_text(
                    chat_id=target_channel_id,
                    message_id=target_message_id,
                    text=frame,
                    parse_mode="Markdown"
                )
                await asyncio.sleep(1)

        # Выводим финальный текст
        await bot.edit_message_text(
            chat_id=target_channel_id,
            message_id=target_message_id,
            text=final_text,
            parse_mode="Markdown"
        )
        await callback.message.answer("✅ Статус сервера успешно обновлен в канале!")

    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при изменении сообщения: `{e}`\n\n"
            "Убедитесь, что бот добавлен в администраторы канала @RustZEROo с правом публикаций.",
            parse_mode="Markdown"
        )


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
