# Telegram Bot Configuration
# Copy this file as config.py and fill in real values
# cp config.example.py config.py

# Bot token (get from @BotFather in Telegram)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# List of recipient chat_ids (personal messages)
RECIPIENTS = [
    123456789,    # Example: your chat_id
]

# Group delivery
USE_GROUP = True
GROUP_CHAT_ID = -1001234567890  # Your Telegram group ID

# Dashboard path (relative to telegram_bot/)
DASHBOARD_PATH = "../output/dashboard_current.html"

# Message template
MESSAGE_TEMPLATE = """
📊 <b>Недельный отчёт ННВ по товару</b>

Период: {period}
Регион: Нижний Новгород

📎 Дашборд во вложении

---
<i>Автоматическая рассылка | {timestamp}</i>
"""
