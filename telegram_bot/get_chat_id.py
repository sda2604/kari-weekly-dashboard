"""
Скрипт для получения chat_id пользователей Telegram
Запускай этот скрипт, затем попроси пользователей отправить /start боту
"""

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN

# Словарь для хранения chat_id
users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Unknown"
    first_name = update.effective_user.first_name or "Unknown"
    
    print(f"\n{'='*60}")
    print(f"Новый пользователь!")
    print(f"chat_id: {chat_id}")
    print(f"Username: @{username}")
    print(f"Имя: {first_name}")
    print(f"{'='*60}\n")
    
    users[chat_id] = {
        'username': username,
        'first_name': first_name
    }
    
    await update.message.reply_text(
        f"✅ Привет, {first_name}!\n\n"
        f"Твой chat_id: <code>{chat_id}</code>\n\n"
        f"Добавь этот chat_id в config.py для получения рассылки дашбордов.",
        parse_mode='HTML'
    )


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список всех зарегистрированных пользователей"""
    if not users:
        await update.message.reply_text("Пока никто не отправил /start")
        return
    
    message = "👥 <b>Зарегистрированные пользователи:</b>\n\n"
    for chat_id, info in users.items():
        message += f"• {info['first_name']} (@{info['username']})\n"
        message += f"  chat_id: <code>{chat_id}</code>\n\n"
    
    await update.message.reply_text(message, parse_mode='HTML')


def main():
    """Запуск бота"""
    print("\n" + "="*60)
    print("🤖 БОТ ДЛЯ ПОЛУЧЕНИЯ CHAT_ID ЗАПУЩЕН")
    print("="*60)
    print("\nИнструкция:")
    print("1. Открой бота в Telegram")
    print("2. Отправь команду /start")
    print("3. Бот покажет твой chat_id")
    print("4. Добавь chat_id в config.py")
    print("\nДля просмотра всех пользователей отправь /list")
    print("\nДля остановки бота нажми Ctrl+C")
    print("="*60 + "\n")
    
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_users))
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Бот остановлен")
        print("\n📋 Собранные chat_id:")
        for chat_id, info in users.items():
            print(f"  {chat_id},  # {info['first_name']} (@{info['username']})")
        print("\nДобавь их в config.py в список RECIPIENTS\n")
