"""
Скрипт для рассылки дашборда KARI через Telegram
Отправляет dashboard_current.html всем получателям из config.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError
from config import (
    BOT_TOKEN,
    RECIPIENTS,
    USE_GROUP,
    GROUP_CHAT_ID,
    DASHBOARD_PATH,
    MESSAGE_TEMPLATE
)
from period_parser import get_report_period


def safe_print(text):
    """Безопасный вывод текста без эмодзи и юникода"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Если не удалось вывести - просто игнорируем
        pass


def get_dashboard_path():
    """Получить абсолютный путь к дашборду"""
    script_dir = Path(__file__).parent
    dashboard = script_dir / DASHBOARD_PATH
    
    if not dashboard.exists():
        raise FileNotFoundError(
            f"Дашборд не найден: {dashboard}\n"
            f"Убедись что файл существует: {dashboard.absolute()}"
        )
    
    return dashboard


def format_message():
    """Форматировать сообщение для отправки"""
    # Получаем период из Excel файлов
    period = get_report_period()
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    return MESSAGE_TEMPLATE.format(
        period=period,
        timestamp=timestamp
    )


async def send_to_user(bot: Bot, chat_id: int, dashboard_path: Path, message: str):
    """Отправить дашборд одному пользователю"""
    try:
        with open(dashboard_path, 'rb') as file:
            await bot.send_document(
                chat_id=chat_id,
                document=file,
                filename="dashboard_kari_nnv.html",
                caption=message,
                parse_mode='HTML'
            )
        safe_print(f"  [OK] Otpravleno polzovatelju {chat_id}")
        return True
    except TelegramError as e:
        safe_print(f"  [ERROR] Otpravka polzovatelju {chat_id}: {e}")
        return False


async def send_dashboard():
    """Основная функция рассылки"""
    safe_print("\n" + "="*60)
    safe_print("RASSYLKA DASHBORDA KARI")
    safe_print("="*60)
    
    # Проверяем наличие дашборда
    try:
        dashboard_path = get_dashboard_path()
        safe_print(f"\n[OK] Dashboard najden: {dashboard_path.name}")
        file_size = dashboard_path.stat().st_size / 1024  # KB
        safe_print(f"[OK] Razmer fajla: {file_size:.1f} KB")
    except FileNotFoundError as e:
        safe_print(f"\n[ERROR] {e}")
        return
    
    # Создаём бота
    bot = Bot(token=BOT_TOKEN)
    
    # Формируем сообщение
    message = format_message()
    safe_print(f"\n[OK] Soobschenie sformirovano")
    
    # Определяем получателей
    if USE_GROUP and GROUP_CHAT_ID:
        recipients = [GROUP_CHAT_ID]
        safe_print(f"\n[OK] Rassylka v gruppu: {GROUP_CHAT_ID}")
    else:
        recipients = RECIPIENTS
        safe_print(f"\n[OK] Poluchateli: {len(recipients)} chelovek")
    
    if not recipients:
        safe_print("\n[WARNING] Spisok poluchatelej pust!")
        safe_print("Dobav' chat_id v config.py")
        return
    
    # Отправка
    safe_print("\n[START] Nachinayu rassylku...\n")
    
    success_count = 0
    fail_count = 0
    
    for chat_id in recipients:
        result = await send_to_user(bot, chat_id, dashboard_path, message)
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Небольшая пауза между отправками
        await asyncio.sleep(0.5)
    
    # Итоги
    safe_print("\n" + "="*60)
    safe_print("ITOGI RASSYLKI")
    safe_print("="*60)
    safe_print(f"[OK] Uspeshno otpravleno: {success_count}")
    safe_print(f"[ERROR] Oshibki: {fail_count}")
    safe_print(f"[TOTAL] Uspeshnost': {success_count}/{len(recipients)}")
    safe_print("="*60 + "\n")


def main():
    """Точка входа"""
    try:
        # Запускаем асинхронную функцию
        asyncio.run(send_dashboard())
    except KeyboardInterrupt:
        safe_print("\n\n[STOP] Rassylka prervana pol'zovatelem\n")
    except Exception as e:
        safe_print(f"\n[CRITICAL ERROR] {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
