"""
Централизованная конфигурация логирования для KARI Dashboard
Поддерживает JSON формат и различные уровни логирования
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
import os
from typing import Optional


class JsonFormatter(logging.Formatter):
    """
    Форматтер для структурированных JSON логов
    Соответствует стандартам ИТ-департамента
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Форматирует лог-запись в JSON
        
        Args:
            record: Объект лог-записи
            
        Returns:
            JSON строка с структурированными данными
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Добавляем correlation_id если есть
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        
        # Добавляем user_id если есть
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Добавляем дополнительные поля если есть
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Добавляем exception если есть
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """
    Форматтер для человеко-читаемых текстовых логов
    Используется для консольного вывода в режиме разработки
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Форматирует лог-запись в читаемый текст
        
        Args:
            record: Объект лог-записи
            
        Returns:
            Форматированная строка
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname.ljust(8)
        message = record.getMessage()
        
        # Базовый формат
        log_line = f"[{timestamp}] {level} {message}"
        
        # Добавляем модуль и функцию для DEBUG
        if record.levelno == logging.DEBUG:
            log_line += f" ({record.module}.{record.funcName}:{record.lineno})"
        
        # Добавляем exception если есть
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line


def setup_logging(
    name: str = 'kari_dashboard',
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Настраивает логгер с заданными параметрами
    
    Args:
        name: Имя логгера
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Формат логов ('json' или 'text')
        log_dir: Директория для файлов логов
        log_file: Имя файла лога (без расширения)
        
    Returns:
        Настроенный логгер
    """
    # Загружаем настройки из .env если не указаны явно
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    if log_format is None:
        log_format = os.getenv('LOG_FORMAT', 'json')
    
    if log_dir is None:
        log_dir = os.getenv('LOG_DIR', '../logs')
    
    # Создаём логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Очищаем существующие handlers
    logger.handlers.clear()
    
    # Выбираем форматтер
    if log_format.lower() == 'json':
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter()
    
    # Console handler (всегда есть)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Консоль показывает INFO+
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (если указана директория)
    if log_dir and log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Создаём имя файла с датой
        date_suffix = datetime.now().strftime('%Y%m%d')
        file_name = f"{log_file}_{date_suffix}.log"
        file_path = log_path / file_name
        
        file_handler = logging.FileHandler(
            file_path,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Файл записывает всё
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'kari_dashboard') -> logging.Logger:
    """
    Получает существующий логгер или создаёт новый
    
    Args:
        name: Имя логгера
        
    Returns:
        Логгер
    """
    logger = logging.getLogger(name)
    
    # Если логгер ещё не настроен - настраиваем
    if not logger.handlers:
        logger = setup_logging(name)
    
    return logger


# Utility функции для быстрого логирования
def log_info(message: str, **kwargs):
    """Быстрое INFO логирование"""
    logger = get_logger()
    logger.info(message, extra={'extra_data': kwargs} if kwargs else {})


def log_warning(message: str, **kwargs):
    """Быстрое WARNING логирование"""
    logger = get_logger()
    logger.warning(message, extra={'extra_data': kwargs} if kwargs else {})


def log_error(message: str, exc_info=None, **kwargs):
    """Быстрое ERROR логирование"""
    logger = get_logger()
    logger.error(
        message,
        exc_info=exc_info,
        extra={'extra_data': kwargs} if kwargs else {}
    )


def log_debug(message: str, **kwargs):
    """Быстрое DEBUG логирование"""
    logger = get_logger()
    logger.debug(message, extra={'extra_data': kwargs} if kwargs else {})


# Пример использования
if __name__ == '__main__':
    # Тестирование JSON формата
    print("=== Тест JSON формата ===")
    logger = setup_logging(
        name='test_json',
        log_level='DEBUG',
        log_format='json'
    )
    
    logger.debug("Это DEBUG сообщение")
    logger.info("Это INFO сообщение", extra={'extra_data': {'user': 'test'}})
    logger.warning("Это WARNING сообщение")
    logger.error("Это ERROR сообщение")
    
    try:
        1 / 0
    except Exception as e:
        logger.error("Поймали ошибку", exc_info=True)
    
    print("\n=== Тест TEXT формата ===")
    logger = setup_logging(
        name='test_text',
        log_level='DEBUG',
        log_format='text'
    )
    
    logger.debug("Это DEBUG сообщение")
    logger.info("Это INFO сообщение")
    logger.warning("Это WARNING сообщение")
    logger.error("Это ERROR сообщение")
    
    try:
        1 / 0
    except Exception as e:
        logger.error("Поймали ошибку", exc_info=True)
