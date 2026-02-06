"""
Скрипт для обновления generate_dashboard.py с новым логированием
Запуск: python update_to_logging.py
"""

import re
from pathlib import Path

# Путь к файлу
file_path = Path(__file__).parent / 'generate_dashboard.py'

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем старый import блок
old_import = """import pandas as pd
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Импорт парсера периода из telegram_bot
sys.path.insert(0, str(Path(__file__).parent / 'telegram_bot'))
from period_parser import get_report_period as parse_period_from_excel"""

new_import = """import pandas as pd
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Импорт логирования
from logging_config import setup_logging

# Импорт парсера периода из telegram_bot
sys.path.insert(0, str(Path(__file__).parent / 'telegram_bot'))
from period_parser import get_report_period as parse_period_from_excel

# Настройка логгера
logger = setup_logging(
    name='dashboard_generator',
    log_file='dashboard_generation'
)"""

content = content.replace(old_import, new_import)

# Заменяем функцию log
old_log = '''def log(msg):
    """Логирование с временем"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")'''

new_log = '''# DEPRECATED: Используй logger вместо log()
# Оставлено для обратной совместимости
def log(msg):
    """Устаревшая функция логирования (используй logger.info вместо неё)"""
    logger.info(msg)'''

content = content.replace(old_log, new_log)

# Сохраняем
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл generate_dashboard.py обновлён!")
print("✅ Старая функция log() теперь использует logger.info()")
print("✅ Добавлен импорт logging_config")
