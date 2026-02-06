"""
Telegram Bot Configuration
Загружает настройки из .env файла для безопасности
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ============================================
# TELEGRAM BOT SETTINGS
# ============================================

# Токен бота (из .env)
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в .env файле!\n"
        "1. Скопируй .env.example в .env\n"
        "2. Заполни BOT_TOKEN значением от @BotFather"
    )

# Список chat_id получателей (личные сообщения)
recipients_str = os.getenv('RECIPIENTS', '')
RECIPIENTS = [int(x.strip()) for x in recipients_str.split(',') if x.strip()]

# Рассылка в группу
USE_GROUP = os.getenv('USE_GROUP', 'true').lower() == 'true'

# ID группы для рассылки
group_id_str = os.getenv('GROUP_CHAT_ID')
GROUP_CHAT_ID = int(group_id_str) if group_id_str else None

if USE_GROUP and not GROUP_CHAT_ID:
    raise ValueError(
        "USE_GROUP=true, но GROUP_CHAT_ID не указан в .env!\n"
        "Используй get_group_id.bat для получения ID группы"
    )

# ============================================
# PATHS
# ============================================

# Путь к дашборду
DASHBOARD_PATH = os.getenv('DASHBOARD_PATH', '../output/dashboard_current.html')

# ============================================
# ADVANCED SETTINGS
# ============================================

# Таймауты и retry (с дефолтными значениями)
TELEGRAM_TIMEOUT = int(os.getenv('TELEGRAM_TIMEOUT', '30'))
TELEGRAM_RETRY_COUNT = int(os.getenv('TELEGRAM_RETRY_COUNT', '3'))
TELEGRAM_RETRY_DELAY = int(os.getenv('TELEGRAM_RETRY_DELAY', '2'))

# ============================================
# MESSAGE TEMPLATE
# ============================================

MESSAGE_TEMPLATE = """
📊 <b>Недельный отчёт ННВ по товару</b>

Период: {period}
Регион: Нижний Новгород

📎 Дашборд во вложении

---
<i>Автоматическая рассылка | {timestamp}</i>
"""

# ============================================
# VALIDATION
# ============================================

def validate_config():
    """Проверка корректности конфигурации"""
    errors = []
    
    if not BOT_TOKEN or BOT_TOKEN == 'your_bot_token_here':
        errors.append("BOT_TOKEN не настроен в .env")
    
    if USE_GROUP and (not GROUP_CHAT_ID or GROUP_CHAT_ID == 'your_group_chat_id_here'):
        errors.append("GROUP_CHAT_ID не настроен в .env")
    
    if not USE_GROUP and not RECIPIENTS:
        errors.append("Не указаны получатели (RECIPIENTS в .env)")
    
    if errors:
        raise ValueError(
            "Ошибки в конфигурации:\n" + 
            "\n".join(f"  - {err}" for err in errors) +
            "\n\nПроверь .env файл!"
        )

# Проверяем конфигурацию при импорте
if __name__ != '__main__':
    validate_config()
