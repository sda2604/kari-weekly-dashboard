"""
Скрипт для рассылки дашборда KARI через Telegram
Отправляет dashboard_current.html всем получателям из config.py

ИЗМЕНЕНИЯ v2.0 (05.02.2026):
- Добавлено структурированное логирование (JSON формат)
- Добавлены таймауты для Telegram API
- Добавлен retry механизм с exponential backoff
- Улучшенная обработка ошибок
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError, NetworkError, TimedOut
from telegram.request import HTTPXRequest

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_logging
from telegram_bot.config import (
    BOT_TOKEN,
    RECIPIENTS,
    USE_GROUP,
    GROUP_CHAT_ID,
    DASHBOARD_PATH,
    MESSAGE_TEMPLATE,
    TELEGRAM_TIMEOUT,
    TELEGRAM_RETRY_COUNT,
    TELEGRAM_RETRY_DELAY
)
from telegram_bot.period_parser import get_report_period

# Настройка логгера
logger = setup_logging(
    name='telegram_sender',
    log_file='telegram_send'
)


def get_dashboard_path():
    """
    Получить абсолютный путь к дашборду
    
    Returns:
        Path: Абсолютный путь к файлу дашборда
        
    Raises:
        FileNotFoundError: Если дашборд не найден
    """
    script_dir = Path(__file__).parent
    dashboard = script_dir / DASHBOARD_PATH
    
    if not dashboard.exists():
        error_msg = f"Дашборд не найден: {dashboard.absolute()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Дашборд найден", extra={'extra_data': {
        'path': str(dashboard),
        'size_kb': round(dashboard.stat().st_size / 1024, 2)
    }})
    
    return dashboard


def format_message():
    """
    Форматировать сообщение для отправки
    
    Returns:
        str: Форматированное сообщение
    """
    try:
        period = get_report_period()
        logger.debug(f"Период получен", extra={'extra_data': {'period': period}})
    except Exception as e:
        logger.warning(f"Не удалось получить период, используем дефолтное значение", 
                      exc_info=True)
        period = "Текущая неделя"
    
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    message = MESSAGE_TEMPLATE.format(
        period=period,
        timestamp=timestamp
    )
    
    logger.info("Сообщение сформировано", extra={'extra_data': {
        'period': period,
        'timestamp': timestamp
    }})
    
    return message


async def send_to_user_with_retry(
    bot: Bot, 
    chat_id: int, 
    dashboard_path: Path, 
    message: str,
    max_retries: int = TELEGRAM_RETRY_COUNT,
    retry_delay: int = TELEGRAM_RETRY_DELAY
) -> bool:
    """
    Отправить дашборд одному пользователю с retry механизмом
    
    Args:
        bot: Telegram bot instance
        chat_id: ID чата получателя
        dashboard_path: Путь к файлу дашборда
        message: Текст сообщения
        max_retries: Максимальное количество попыток
        retry_delay: Базовая задержка между попытками (секунды)
        
    Returns:
        bool: True если отправка успешна, False иначе
    """
    for attempt in range(max_retries):
        try:
            with open(dashboard_path, 'rb') as file:
                await bot.send_document(
                    chat_id=chat_id,
                    document=file,
                    filename="dashboard_kari_nnv.html",
                    caption=message,
                    parse_mode='HTML'
                )
            
            logger.info(f"Успешная отправка пользователю", extra={'extra_data': {
                'chat_id': chat_id,
                'attempt': attempt + 1
            }})
            return True
            
        except (NetworkError, TimedOut) as e:
            # Временные сетевые ошибки - retry
            if attempt < max_retries - 1:
                delay = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Сетевая ошибка при отправке, повтор через {delay}с",
                    extra={'extra_data': {
                        'chat_id': chat_id,
                        'attempt': attempt + 1,
                        'error': str(e),
                        'delay': delay
                    }}
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Не удалось отправить после {max_retries} попыток",
                    exc_info=True,
                    extra={'extra_data': {'chat_id': chat_id}}
                )
                return False
                
        except TelegramError as e:
            # Другие ошибки Telegram (неправильный chat_id, бот заблокирован и т.д.)
            logger.error(
                f"Ошибка Telegram API",
                exc_info=True,
                extra={'extra_data': {
                    'chat_id': chat_id,
                    'error': str(e),
                    'error_type': type(e).__name__
                }}
            )
            return False
            
        except Exception as e:
            # Неожиданные ошибки
            logger.error(
                f"Неожиданная ошибка при отправке",
                exc_info=True,
                extra={'extra_data': {
                    'chat_id': chat_id,
                    'error': str(e),
                    'error_type': type(e).__name__
                }}
            )
            return False
    
    return False


async def send_dashboard():
    """
    Основная функция рассылки
    
    Returns:
        dict: Статистика отправки
    """
    logger.info("=" * 60)
    logger.info("НАЧАЛО РАССЫЛКИ ДАШБОРДА KARI")
    logger.info("=" * 60)
    
    # Проверяем наличие дашборда
    try:
        dashboard_path = get_dashboard_path()
    except FileNotFoundError:
        logger.error("Дашборд не найден, рассылка отменена")
        return {'success': 0, 'failed': 0, 'total': 0}
    
    # Создаём бота с таймаутами
    try:
        request = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=TELEGRAM_TIMEOUT,
            write_timeout=TELEGRAM_TIMEOUT,
            connect_timeout=10
        )
        bot = Bot(token=BOT_TOKEN, request=request)
        logger.info("Telegram Bot создан", extra={'extra_data': {
            'timeout': TELEGRAM_TIMEOUT,
            'retry_count': TELEGRAM_RETRY_COUNT
        }})
    except Exception as e:
        logger.error("Ошибка создания Telegram Bot", exc_info=True)
        return {'success': 0, 'failed': 0, 'total': 0}
    
    # Формируем сообщение
    try:
        message = format_message()
    except Exception as e:
        logger.error("Ошибка форматирования сообщения", exc_info=True)
        return {'success': 0, 'failed': 0, 'total': 0}
    
    # Определяем получателей
    if USE_GROUP and GROUP_CHAT_ID:
        recipients = [GROUP_CHAT_ID]
        logger.info("Режим: рассылка в группу", extra={'extra_data': {
            'group_id': GROUP_CHAT_ID
        }})
    else:
        recipients = RECIPIENTS
        logger.info("Режим: личные сообщения", extra={'extra_data': {
            'recipients_count': len(recipients)
        }})
    
    if not recipients:
        logger.warning("Список получателей пуст! Проверь config.py")
        return {'success': 0, 'failed': 0, 'total': 0}
    
    # Отправка
    logger.info("Начинаю рассылку...")
    
    success_count = 0
    fail_count = 0
    
    for chat_id in recipients:
        result = await send_to_user_with_retry(bot, chat_id, dashboard_path, message)
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Небольшая пауза между отправками
        await asyncio.sleep(0.5)
    
    # Итоги
    total = len(recipients)
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    logger.info("=" * 60)
    logger.info("ИТОГИ РАССЫЛКИ", extra={'extra_data': {
        'success': success_count,
        'failed': fail_count,
        'total': total,
        'success_rate': round(success_rate, 1)
    }})
    logger.info("=" * 60)
    
    return {
        'success': success_count,
        'failed': fail_count,
        'total': total
    }


def main():
    """
    Точка входа
    
    Returns:
        int: Код возврата (0 если успех, 1 если ошибка)
    """
    try:
        logger.info("Запуск скрипта рассылки дашборда")
        
        # Запускаем асинхронную функцию
        stats = asyncio.run(send_dashboard())
        
        # Проверяем результат
        if stats['success'] > 0:
            logger.info(f"Рассылка завершена успешно: {stats['success']}/{stats['total']}")
            return 0
        else:
            logger.error(f"Рассылка провалилась: 0/{stats['total']} успешных отправок")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("Рассылка прервана пользователем")
        return 130  # Standard exit code for SIGINT
        
    except Exception as e:
        logger.error("Критическая ошибка при рассылке", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
