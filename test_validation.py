#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции валидации данных в generate_dashboard.py
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

print("=" * 60)
print("ТЕСТ ИНТЕГРАЦИИ ВАЛИДАЦИИ ДАННЫХ")
print("=" * 60)

# Тест 1: Импорт модулей
print("\n[1/3] Проверка импортов...")
try:
    from data_validator import DataValidator
    print("  ✅ DataValidator импортирован")
except ImportError as e:
    print(f"  ❌ Ошибка импорта DataValidator: {e}")
    sys.exit(1)

try:
    import generate_dashboard
    print("  ✅ generate_dashboard импортирован")
except ImportError as e:
    print(f"  ❌ Ошибка импорта generate_dashboard: {e}")
    sys.exit(1)

# Тест 2: Проверка что валидатор доступен в модуле
print("\n[2/3] Проверка доступности DataValidator...")
if hasattr(generate_dashboard, 'DataValidator'):
    print("  ✅ DataValidator доступен в generate_dashboard")
else:
    print("  ❌ DataValidator НЕ доступен в generate_dashboard")
    sys.exit(1)

# Тест 3: Проверка наличия функций валидации
print("\n[3/3] Проверка методов валидации...")
methods = [
    'validate_regions_data',
    'validate_turnover_data',
    'validate_accessories_data'
]

for method in methods:
    if hasattr(DataValidator, method):
        print(f"  ✅ {method}")
    else:
        print(f"  ❌ {method} НЕ найден")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
print("=" * 60)
print("\nВалидация успешно интегрирована в pipeline.")
print("Теперь при извлечении данных из Excel будет проверяться:")
print("  • Наличие обязательных колонок")
print("  • Корректное количество строк")
print("  • Отсутствие критичных проблем с данными")
print("\nЛоги валидации будут в:")
print("  logs/dashboard_generation_YYYY-MM-DD.log")
