"""
Централизованная обработка ошибок для KARI Dashboard
Обеспечивает graceful degradation и детальное логирование
"""

import sys
import traceback
from typing import Optional, Callable, Any
from pathlib import Path
from logging_config import get_logger

logger = get_logger('error_handler')


class DashboardError(Exception):
    """Базовый класс для ошибок дашборда"""
    pass


class DataExtractionError(DashboardError):
    """Ошибка при извлечении данных из Excel"""
    pass


class DataValidationError(DashboardError):
    """Ошибка валидации данных"""
    pass


class HTMLGenerationError(DashboardError):
    """Ошибка генерации HTML"""
    pass


def handle_error(
    error: Exception,
    context: str,
    critical: bool = False,
    extra_data: Optional[dict] = None
) -> None:
    """
    Централизованная обработка ошибок
    
    Args:
        error: Исключение
        context: Контекст где произошла ошибка
        critical: Критичная ли ошибка (остановить выполнение?)
        extra_data: Дополнительные данные для логирования
    """
    error_info = {
        'context': context,
        'error_type': type(error).__name__,
        'error_message': str(error),
    }
    
    if extra_data:
        error_info.update(extra_data)
    
    # Логируем с полным stack trace
    if critical:
        logger.error(
            f"КРИТИЧНАЯ ОШИБКА в {context}",
            exc_info=True,
            extra={'extra_data': error_info}
        )
    else:
        logger.warning(
            f"Ошибка в {context} (продолжаем работу)",
            exc_info=True,
            extra={'extra_data': error_info}
        )


def safe_execute(
    func: Callable,
    context: str,
    default_return: Any = None,
    critical: bool = False,
    **kwargs
) -> Any:
    """
    Безопасное выполнение функции с обработкой ошибок
    
    Args:
        func: Функция для выполнения
        context: Описание контекста
        default_return: Значение по умолчанию при ошибке
        critical: Критичная ли операция
        **kwargs: Аргументы для функции
        
    Returns:
        Результат функции или default_return при ошибке
        
    Raises:
        Exception: Если critical=True и произошла ошибка
    """
    try:
        result = func(**kwargs)
        logger.debug(f"Успешное выполнение: {context}")
        return result
        
    except Exception as e:
        handle_error(
            error=e,
            context=context,
            critical=critical,
            extra_data={'function': func.__name__}
        )
        
        if critical:
            raise
        
        return default_return


def validate_file_exists(file_path: Path, file_description: str) -> bool:
    """
    Проверка существования файла с логированием
    
    Args:
        file_path: Путь к файлу
        file_description: Описание файла для логов
        
    Returns:
        bool: True если файл существует
    """
    if not file_path:
        logger.error(
            f"{file_description}: путь не указан",
            extra={'extra_data': {'file_path': None}}
        )
        return False
    
    if not file_path.exists():
        logger.error(
            f"{file_description}: файл не найден",
            extra={'extra_data': {
                'file_path': str(file_path),
                'absolute_path': str(file_path.absolute())
            }}
        )
        return False
    
    logger.debug(
        f"{file_description}: файл найден",
        extra={'extra_data': {
            'file_path': str(file_path),
            'size_kb': round(file_path.stat().st_size / 1024, 2)
        }}
    )
    return True


def validate_dataframe(df, required_columns: list, df_name: str) -> bool:
    """
    Валидация DataFrame
    
    Args:
        df: pandas DataFrame
        required_columns: Список обязательных колонок
        df_name: Название DataFrame для логов
        
    Returns:
        bool: True если валидация прошла успешно
    """
    if df is None:
        logger.error(f"{df_name}: DataFrame is None")
        return False
    
    if df.empty:
        logger.warning(f"{df_name}: DataFrame пустой")
        return False
    
    # Проверка обязательных колонок
    missing_columns = []
    for col in required_columns:
        # Проверяем точное совпадение или частичное (для гибкости)
        col_found = False
        for df_col in df.columns:
            if col.lower() in str(df_col).lower():
                col_found = True
                break
        
        if not col_found:
            missing_columns.append(col)
    
    if missing_columns:
        logger.error(
            f"{df_name}: отсутствуют обязательные колонки",
            extra={'extra_data': {
                'missing': missing_columns,
                'available': list(df.columns)
            }}
        )
        return False
    
    logger.debug(
        f"{df_name}: валидация пройдена",
        extra={'extra_data': {
            'rows': len(df),
            'columns': len(df.columns)
        }}
    )
    return True


class ErrorContext:
    """
    Context manager для обработки ошибок в блоках кода
    
    Usage:
        with ErrorContext("Извлечение данных регионов"):
            data = extract_regions_data()
    """
    
    def __init__(
        self,
        context: str,
        critical: bool = False,
        default_return: Any = None
    ):
        self.context = context
        self.critical = critical
        self.default_return = default_return
        self.result = None
    
    def __enter__(self):
        logger.debug(f"Начало: {self.context}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            handle_error(
                error=exc_val,
                context=self.context,
                critical=self.critical
            )
            
            if self.critical:
                return False  # Пробросить исключение
            else:
                return True  # Подавить исключение
        
        logger.debug(f"Завершено: {self.context}")
        return True


def log_function_call(func):
    """
    Декоратор для логирования вызовов функций
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(
            f"Вызов функции: {func_name}",
            extra={'extra_data': {
                'args_count': len(args),
                'kwargs': list(kwargs.keys())
            }}
        )
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Функция {func_name} выполнена успешно")
            return result
            
        except Exception as e:
            logger.error(
                f"Ошибка в функции {func_name}",
                exc_info=True,
                extra={'extra_data': {
                    'function': func_name,
                    'error': str(e)
                }}
            )
            raise
    
    return wrapper


# Пример использования
if __name__ == '__main__':
    # Тест обработки ошибок
    print("=== Тест обработки ошибок ===\n")
    
    # Тест 1: ErrorContext
    print("Тест 1: ErrorContext (не критичная ошибка)")
    with ErrorContext("Тестовая операция", critical=False):
        raise ValueError("Тестовая ошибка")
    print("Продолжаем работу после ошибки\n")
    
    # Тест 2: safe_execute
    print("Тест 2: safe_execute")
    def failing_function():
        raise RuntimeError("Ошибка в функции")
    
    result = safe_execute(
        failing_function,
        context="Тестовый вызов функции",
        default_return="Запасное значение"
    )
    print(f"Результат: {result}\n")
    
    # Тест 3: validate_file_exists
    print("Тест 3: validate_file_exists")
    from pathlib import Path
    validate_file_exists(Path("несуществующий_файл.txt"), "Тестовый файл")
    print("\nТесты завершены!")
