#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расчёт трендов за 4 недели
===========================
Анализ исторических данных для выявления трендов.

Логика:
1. Загружает данные из current/ и archive/ (макс 4 недели)
2. Считает динамику роста по неделям
3. Определяет тренд: ↗ (рост), ↘ (падение), → (стабильно)

Критерии трендов:
- ↗ РОСТ: среднее изменение >+5%
- ↘ ПАДЕНИЕ: среднее изменение <-5%
- → СТАБИЛЬНО: изменение от -5% до +5%

Автор: Claude Code для KARI
Версия: 1.0
Дата: 26.01.2026
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Пути
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
CURRENT_DIR = INPUT_DIR / "current"
ARCHIVE_DIR = INPUT_DIR / "archive"

# Константы
MAX_WEEKS = 4               # Максимум недель для анализа
TREND_UP_THRESHOLD = 5.0    # Рост: >+5%
TREND_DOWN_THRESHOLD = -5.0 # Падение: <-5%


def log(msg):
    """Логирование"""
    print(f"[TRENDS] {msg}")


def load_week_data(week_folder):
    """
    Загружает данные за одну неделю из папки
    Возвращает dict с ключевыми метриками
    """
    data = {
        'week_name': week_folder.name,
        'categories': {}
    }

    # Ищем файл с оборачиваемостью
    turnover_folder = week_folder / "Обувь остатки и оборачиваемость по группам товара"
    if not turnover_folder.exists():
        return None

    excel_files = list(turnover_folder.glob("*.xlsx"))
    if not excel_files:
        return None

    try:
        df = pd.read_excel(excel_files[0], sheet_name=0)

        # Ищем колонку с ростом (обычно "Прирост, %" или "Рост %")
        growth_col = None
        for col in df.columns:
            if 'прирост' in str(col).lower() or 'рост' in str(col).lower():
                if '%' in str(col):
                    growth_col = col
                    break

        # Ищем колонку с категорией
        category_col = df.columns[0]  # Обычно первая колонка

        if growth_col is None:
            log(f"  ⚠ Колонка роста не найдена в {excel_files[0].name}")
            return None

        # Извлекаем данные по категориям
        for _, row in df.iterrows():
            category = row[category_col]
            growth = row[growth_col]

            if pd.notna(category) and pd.notna(growth):
                try:
                    growth_value = float(growth)
                    data['categories'][str(category)] = growth_value
                except (ValueError, TypeError):
                    continue

        return data

    except Exception as e:
        log(f"  ⚠ Ошибка чтения {excel_files[0].name}: {e}")
        return None


def load_historical_data():
    """
    Загружает данные за последние 4 недели
    Возвращает list из dict, отсортированный от старых к новым
    """
    log("Загрузка исторических данных...")

    weeks_data = []

    # 1. Загружаем архивные данные
    if ARCHIVE_DIR.exists():
        archive_folders = sorted([f for f in ARCHIVE_DIR.iterdir() if f.is_dir()])

        # Берём последние MAX_WEEKS-1 (оставляем место для current)
        for folder in archive_folders[-(MAX_WEEKS-1):]:
            log(f"  → {folder.name}")
            data = load_week_data(folder)
            if data:
                weeks_data.append(data)

    # 2. Загружаем текущую неделю
    if CURRENT_DIR.exists():
        log(f"  → current/")
        data = load_week_data(CURRENT_DIR)
        if data:
            data['week_name'] = 'current'
            weeks_data.append(data)

    log(f"✓ Загружено недель: {len(weeks_data)}")
    return weeks_data


def calculate_trend(category, weeks_data):
    """
    Рассчитывает тренд для категории за доступные недели
    Возвращает: {'trend': '↗'/'↘'/'→', 'avg_change': 5.2, 'weeks_count': 3}
    """
    if len(weeks_data) < 2:
        return None

    # Собираем значения роста по неделям
    growth_values = []

    for week in weeks_data:
        if category in week['categories']:
            growth_values.append(week['categories'][category])

    if len(growth_values) < 2:
        return None

    # Считаем среднее изменение
    avg_change = sum(growth_values) / len(growth_values)

    # Определяем тренд
    if avg_change >= TREND_UP_THRESHOLD:
        trend_icon = '↗'
        trend_label = 'рост'
    elif avg_change <= TREND_DOWN_THRESHOLD:
        trend_icon = '↘'
        trend_label = 'падение'
    else:
        trend_icon = '→'
        trend_label = 'стабильно'

    return {
        'trend': trend_icon,
        'trend_label': trend_label,
        'avg_change': round(avg_change, 1),
        'weeks_count': len(growth_values),
        'growth_values': growth_values
    }


def get_trends_for_categories(categories_list):
    """
    Возвращает тренды для списка категорий
    categories_list: ['257 Ботинки жен зим', '261 Ботинки муж зим', ...]
    Возвращает: dict {category: trend_data}
    """
    weeks_data = load_historical_data()

    if len(weeks_data) < 2:
        log("⚠ Недостаточно данных для расчёта трендов (нужно 2+ недель)")
        return {}

    trends = {}

    for category in categories_list:
        trend_data = calculate_trend(category, weeks_data)
        if trend_data:
            trends[category] = trend_data

    log(f"✓ Рассчитано трендов: {len(trends)}")
    return trends


def format_trend_html(trend_data):
    """
    Форматирует тренд в HTML для вставки в дашборд
    Возвращает: '<span class="trend-up">↗ +5.2%</span>'
    """
    if not trend_data:
        return ''

    trend = trend_data['trend']
    avg_change = trend_data['avg_change']

    # Определяем класс CSS
    if trend == '↗':
        css_class = 'trend-up'
        color = '#10b981'  # зелёный
    elif trend == '↘':
        css_class = 'trend-down'
        color = '#ef4444'  # красный
    else:
        css_class = 'trend-stable'
        color = '#6b7280'  # серый

    # Форматируем число
    sign = '+' if avg_change >= 0 else ''

    return f'<span class="{css_class}" style="color: {color}; font-weight: 600;">{trend} {sign}{avg_change}%</span>'


# CSS для трендов (добавить в дашборд)
TRENDS_CSS = """
<style>
.trend-up {
    color: #10b981;
    font-weight: 600;
}
.trend-down {
    color: #ef4444;
    font-weight: 600;
}
.trend-stable {
    color: #6b7280;
    font-weight: 600;
}
.trend-tooltip {
    position: relative;
    cursor: help;
}
.trend-tooltip:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #1f2937;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    z-index: 1000;
}
</style>
"""


def test_trends():
    """Тестовая функция для проверки"""
    log("="*60)
    log("ТЕСТ РАСЧЁТА ТРЕНДОВ")
    log("="*60)

    # Пример категорий
    test_categories = [
        '257 Ботинки жен зим',
        '261 Ботинки муж зим',
        '797 Ботинки муж акт',
        '011 Тапочки жен'
    ]

    trends = get_trends_for_categories(test_categories)

    log("\n" + "="*60)
    log("РЕЗУЛЬТАТЫ:")
    log("="*60)

    for category, trend_data in trends.items():
        html = format_trend_html(trend_data)
        log(f"\n{category}:")
        log(f"  Тренд: {trend_data['trend']} ({trend_data['trend_label']})")
        log(f"  Среднее изменение: {trend_data['avg_change']}%")
        log(f"  Недель данных: {trend_data['weeks_count']}")
        log(f"  HTML: {html}")

    log("\n" + "="*60)


if __name__ == '__main__':
    test_trends()
