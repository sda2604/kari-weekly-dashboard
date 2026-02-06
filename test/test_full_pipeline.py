#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТИРОВАНИЕ ПОЛНОЙ ЦЕПОЧКИ KARI DASHBOARD
==========================================

Этот скрипт проверяет ВСЮ цепочку обработки:
1. Проверка входных файлов (актуальность, наличие)
2. Генерация дашборда
3. Тестовая отправка в Telegram

Автор: Claude для синхронизации с Claude Code
Дата: 27.01.2026
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Константы
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TELEGRAM_BOT_DIR = BASE_DIR / "telegram_bot"

# Цвета для консоли (Windows)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Красивый заголовок"""
    print("\n" + "=" * 70)
    print(Colors.BOLD + Colors.BLUE + text.center(70) + Colors.RESET)
    print("=" * 70 + "\n")

def print_success(text):
    """Зелёный текст (успех)"""
    print(Colors.GREEN + "✅ " + text + Colors.RESET)

def print_warning(text):
    """Жёлтый текст (предупреждение)"""
    print(Colors.YELLOW + "⚠️  " + text + Colors.RESET)

def print_error(text):
    """Красный текст (ошибка)"""
    print(Colors.RED + "❌ " + text + Colors.RESET)

def print_info(text):
    """Синий текст (инфо)"""
    print(Colors.BLUE + "ℹ️  " + text + Colors.RESET)

def check_file_freshness(file_path, max_age_days=7):
    """Проверка актуальности файла"""
    if not file_path.exists():
        return False, f"Файл не найден: {file_path.name}"
    
    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mod_time
    age_days = age.days
    
    if age_days > max_age_days:
        return False, f"Файл устарел ({age_days} дн.): {file_path.name} (изменён {mod_time.strftime('%d.%m.%Y %H:%M')})"
    
    return True, f"Файл актуален: {file_path.name} (изменён {mod_time.strftime('%d.%m.%Y %H:%M')})"

def step1_check_input_files():
    """ШАГ 1: Проверка входных файлов"""
    print_header("ШАГ 1: ПРОВЕРКА ВХОДНЫХ ФАЙЛОВ")
    
    required_files = [
        INPUT_DIR / "Отчет по приросту регионы" / "По регионам.xlsx",
        INPUT_DIR / "Отчет по приросту аксессуаров по магазинам" / "Рассылка аксессуары магазины.xlsx",
        INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара" / "Отчет по оборачиваемости ТЗ регион ННВ.xlsx"
    ]
    
    all_ok = True
    issues = []
    
    for file_path in required_files:
        is_fresh, message = check_file_freshness(file_path, max_age_days=7)
        
        if is_fresh:
            print_success(message)
        else:
            print_error(message)
            all_ok = False
            issues.append(message)
    
    print()
    if all_ok:
        print_success("Все файлы актуальные! Можно генерировать дашборд.")
    else:
        print_warning(f"Найдено проблем: {len(issues)}")
        print_info("Дашборд будет создан с доступными данными, но может быть неполным.")
    
    return all_ok, issues

def step2_generate_dashboard():
    """ШАГ 2: Генерация дашборда"""
    print_header("ШАГ 2: ГЕНЕРАЦИЯ ДАШБОРДА")
    
    script_path = BASE_DIR / "generate_dashboard.py"
    
    if not script_path.exists():
        print_error(f"Скрипт не найден: {script_path}")
        return False
    
    print_info(f"Запуск: {script_path.name}")
    print()
    
    try:
        # Запуск через subprocess с выводом в реальном времени
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(BASE_DIR)
        )
        
        # Читаем вывод построчно
        for line in process.stdout:
            print("  ", line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print()
            print_success("Дашборд успешно создан!")
            
            # Проверяем что файл создан
            dashboard_path = OUTPUT_DIR / "dashboard_current.html"
            if dashboard_path.exists():
                size_kb = dashboard_path.stat().st_size / 1024
                print_info(f"Файл: {dashboard_path}")
                print_info(f"Размер: {size_kb:.1f} KB")
                return True
            else:
                print_error("Файл дашборда не найден!")
                return False
        else:
            print()
            print_error(f"Ошибка при генерации дашборда (код: {process.returncode})")
            
            # Показываем stderr если есть
            stderr = process.stderr.read()
            if stderr:
                print_error("Детали ошибки:")
                print(stderr)
            
            return False
            
    except Exception as e:
        print_error(f"Ошибка запуска: {e}")
        return False

def step3_test_telegram():
    """ШАГ 3: Тестовая отправка в Telegram"""
    print_header("ШАГ 3: ТЕСТОВАЯ ОТПРАВКА В TELEGRAM")
    
    script_path = TELEGRAM_BOT_DIR / "send_dashboard.py"
    
    if not script_path.exists():
        print_error(f"Скрипт не найден: {script_path}")
        return False
    
    dashboard_path = OUTPUT_DIR / "dashboard_current.html"
    if not dashboard_path.exists():
        print_error("Дашборд не найден! Сначала нужно создать дашборд.")
        return False
    
    print_info(f"Запуск: {script_path.name}")
    print()
    
    try:
        # Запуск с выводом
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(TELEGRAM_BOT_DIR)
        )
        
        # Читаем вывод
        for line in process.stdout:
            print("  ", line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print()
            print_success("Дашборд успешно отправлен в Telegram!")
            return True
        else:
            print()
            print_error(f"Ошибка при отправке (код: {process.returncode})")
            
            stderr = process.stderr.read()
            if stderr:
                print_error("Детали ошибки:")
                print(stderr)
            
            return False
            
    except Exception as e:
        print_error(f"Ошибка запуска: {e}")
        return False

def check_outlook_macro_logs():
    """Проверка логов Outlook макроса"""
    print_header("ПРОВЕРКА ЛОГОВ OUTLOOK МАКРОСА")
    
    today = datetime.now().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"outlook_macro_{today}.log"
    
    if log_file.exists():
        print_success(f"Лог найден: {log_file.name}")
        
        # Читаем и показываем последние 30 строк
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        print_info(f"Размер лога: {len(lines)} строк")
        
        # Считаем сколько писем обработано
        email_count = lines.count('=== ПОЛУЧЕНО ПИСЬМО ===\n')
        if email_count > 0:
            print_success(f"Обработано писем: {email_count}")
        else:
            print_warning("Писем не обработано или формат лога изменился")
        
        print()
        print_info("Последние 30 строк лога:")
        print("-" * 70)
        for line in lines[-30:]:
            print(line.rstrip())
        print("-" * 70)
        
        return True
    else:
        print_warning(f"Лог не найден: {log_file.name}")
        print_info("Возможные причины:")
        print_info("  1. Outlook макрос не получал письма сегодня")
        print_info("  2. Макрос не установлен или отключён")
        print_info("  3. Логирование отключено в настройках макроса")
        return False

def check_project_structure():
    """Проверка структуры проекта"""
    print_header("ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    
    critical_paths = {
        "Входные данные": INPUT_DIR,
        "Выходные данные": OUTPUT_DIR,
        "Логи": LOGS_DIR,
        "Telegram бот": TELEGRAM_BOT_DIR,
        "Скрипт генерации": BASE_DIR / "generate_dashboard.py"
    }
    
    all_ok = True
    
    for name, path in critical_paths.items():
        if path.exists():
            print_success(f"{name}: {path}")
        else:
            print_error(f"{name} НЕ НАЙДЕН: {path}")
            all_ok = False
    
    print()
    if all_ok:
        print_success("Структура проекта в порядке!")
    else:
        print_error("Найдены отсутствующие компоненты!")
    
    return all_ok

def main():
    """Главная функция"""
    print()
    print("=" * 70)
    print(Colors.BOLD + Colors.BLUE + "ТЕСТИРОВАНИЕ СИСТЕМЫ KARI DASHBOARD".center(70) + Colors.RESET)
    print(Colors.BLUE + f"Дата и время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}".center(70) + Colors.RESET)
    print("=" * 70)
    
    # Проверка структуры
    if not check_project_structure():
        print_error("\nКритичные проблемы со структурой проекта! Остановка теста.")
        return 1
    
    # Проверка Outlook логов (информативно, не критично)
    check_outlook_macro_logs()
    
    # Проверка входных файлов
    files_ok, issues = step1_check_input_files()
    
    if not files_ok:
        print_warning("\nНайдены устаревшие файлы, но продолжаем тест...")
    
    # Генерация дашборда
    if not step2_generate_dashboard():
        print_error("\nТест прерван: не удалось создать дашборд")
        return 1
    
    # Отправка в Telegram
    input("\nНажми ENTER для отправки тестового дашборда в Telegram (или Ctrl+C для отмены)...")
    
    if not step3_test_telegram():
        print_error("\nТест прерван: не удалось отправить дашборд")
        return 1
    
    # Финальный отчёт
    print_header("ИТОГИ ТЕСТИРОВАНИЯ")
    
    print_success("✅ Проверка структуры проекта")
    
    if files_ok:
        print_success("✅ Входные файлы актуальные")
    else:
        print_warning("⚠️  Входные файлы частично устаревшие")
    
    print_success("✅ Генерация дашборда")
    print_success("✅ Отправка в Telegram")
    
    print()
    print(Colors.GREEN + Colors.BOLD + "🎉 СИСТЕМА РАБОТАЕТ ПОЛНОСТЬЮ!" + Colors.RESET)
    print()
    print_info("Следующий автоматический запуск:")
    print_info("  Понедельник в 20:00 МСК через Task Scheduler")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n" + Colors.YELLOW + "Тест прерван пользователем" + Colors.RESET)
        sys.exit(1)
    except Exception as e:
        print("\n\n" + Colors.RED + f"Непредвиденная ошибка: {e}" + Colors.RESET)
        import traceback
        traceback.print_exc()
        sys.exit(1)
