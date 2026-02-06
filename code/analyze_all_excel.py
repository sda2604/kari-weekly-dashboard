#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ всех Excel файлов для создания дашборда
Извлечение ключевых показателей, проблемных зон, топ/худших магазинов
"""

import pandas as pd
import json
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Пути к файлам
BASE_DIR = Path(r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Файлы для анализа
FILES = {
    "regions": INPUT_DIR / "Отчет по приросту регионы" / "По регионам.xlsx",
    "accessories": INPUT_DIR / "Отчет по приросту аксессуаров по магазинам" / "Рассылка аксессуары магазины.xlsx",
    "turnover": INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара" / "Отчет по оборачиваемости ТЗ регион ННВ.xlsx",
    "structure": INPUT_DIR / "Структура розница 21.01.2026.xlsx"
}

def safe_float(value):
    """Безопасное преобразование в float"""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Убираем пробелы, заменяем запятую на точку
        value = value.replace(' ', '').replace(',', '.').replace('%', '')
        try:
            return float(value)
        except:
            return None
    return None

def analyze_regions(file_path):
    """Анализ файла По регионам.xlsx"""
    print(f"\n📊 Анализ: {file_path.name}")

    try:
        # Читаем все листы
        xls = pd.ExcelFile(file_path)
        print(f"Листы в файле: {xls.sheet_names}")

        result = {
            "file": "По регионам.xlsx",
            "sheets": {},
            "nnv_data": {},
            "key_metrics": {},
            "problems": [],
            "top_regions": [],
            "worst_regions": []
        }

        # Анализируем каждый лист
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n  Лист: {sheet_name}")
            print(f"  Размер: {df.shape}")
            print(f"  Колонки: {list(df.columns)[:5]}...")

            # Ищем регион ННВ
            if 'регион' in str(df.columns).lower() or any('ннв' in str(col).lower() for col in df.columns):
                # Ищем строки с ННВ
                nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
                if not nnv_rows.empty:
                    print(f"  ✅ Найдено {len(nnv_rows)} строк с ННВ")
                    result["nnv_data"][sheet_name] = nnv_rows.to_dict(orient='records')

            # Сохраняем первые 10 строк для анализа
            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": df.shape,
                "sample": df.head(10).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"❌ Ошибка при анализе regions: {e}")
        return {"error": str(e), "file": "По регионам.xlsx"}

def analyze_accessories(file_path):
    """Анализ файла Рассылка аксессуары магазины.xlsx"""
    print(f"\n📊 Анализ: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Листы в файле: {xls.sheet_names}")

        result = {
            "file": "Рассылка аксессуары магазины.xlsx",
            "sheets": {},
            "nnv_stores": {},
            "key_metrics": {},
            "problems": [],
            "top_stores": [],
            "worst_stores": []
        }

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n  Лист: {sheet_name}")
            print(f"  Размер: {df.shape}")
            print(f"  Колонки: {list(df.columns)[:5]}...")

            # Ищем магазины ННВ
            nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
            if not nnv_rows.empty:
                print(f"  ✅ Найдено {len(nnv_rows)} магазинов ННВ")
                result["nnv_stores"][sheet_name] = nnv_rows.to_dict(orient='records')

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": df.shape,
                "sample": df.head(10).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"❌ Ошибка при анализе accessories: {e}")
        return {"error": str(e), "file": "Рассылка аксессуары магазины.xlsx"}

def analyze_turnover(file_path):
    """Анализ файла Отчет по оборачиваемости ТЗ регион ННВ.xlsx"""
    print(f"\n📊 Анализ: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Листы в файле: {xls.sheet_names}")

        result = {
            "file": "Отчет по оборачиваемости ТЗ регион ННВ.xlsx",
            "sheets": {},
            "turnover_data": {},
            "key_metrics": {},
            "problems": [],
            "slow_movers": [],
            "fast_movers": []
        }

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n  Лист: {sheet_name}")
            print(f"  Размер: {df.shape}")
            print(f"  Колонки: {list(df.columns)[:5]}...")

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": df.shape,
                "sample": df.head(10).to_dict(orient='records')
            }

            # Если есть колонка с оборачиваемостью
            turnover_cols = [col for col in df.columns if 'оборачиваемост' in str(col).lower()]
            if turnover_cols:
                print(f"  ✅ Найдены колонки оборачиваемости: {turnover_cols}")
                result["turnover_data"][sheet_name] = {
                    "turnover_columns": turnover_cols,
                    "data": df.to_dict(orient='records')[:50]  # Первые 50 строк
                }

        return result

    except Exception as e:
        print(f"❌ Ошибка при анализе turnover: {e}")
        return {"error": str(e), "file": "Отчет по оборачиваемости ТЗ регион ННВ.xlsx"}

def analyze_structure(file_path):
    """Анализ файла Структура розница 21.01.2026.xlsx"""
    print(f"\n📊 Анализ: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Листы в файле: {xls.sheet_names}")

        result = {
            "file": "Структура розница 21.01.2026.xlsx",
            "sheets": {},
            "nnv_structure": {},
            "total_stores": 0
        }

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"\n  Лист: {sheet_name}")
            print(f"  Размер: {df.shape}")
            print(f"  Колонки: {list(df.columns)[:5]}...")

            # Ищем структуру ННВ
            nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
            if not nnv_rows.empty:
                print(f"  ✅ Найдено {len(nnv_rows)} записей ННВ")
                result["nnv_structure"][sheet_name] = nnv_rows.to_dict(orient='records')
                result["total_stores"] += len(nnv_rows)

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": df.shape,
                "sample": df.head(10).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"❌ Ошибка при анализе structure: {e}")
        return {"error": str(e), "file": "Структура розница 21.01.2026.xlsx"}

def main():
    print("🚀 ЗАПУСК АНАЛИЗА ВСЕХ EXCEL ФАЙЛОВ")
    print("=" * 80)

    # Проверяем существование файлов
    for name, path in FILES.items():
        if path.exists():
            print(f"✅ {name}: {path.name}")
        else:
            print(f"❌ {name}: НЕ НАЙДЕН - {path}")

    # Собираем все результаты
    all_results = {
        "analysis_date": "2026-01-21",
        "files_analyzed": [],
        "data": {}
    }

    # Анализируем каждый файл
    if FILES["regions"].exists():
        all_results["data"]["regions"] = analyze_regions(FILES["regions"])
        all_results["files_analyzed"].append("По регионам.xlsx")

    if FILES["accessories"].exists():
        all_results["data"]["accessories"] = analyze_accessories(FILES["accessories"])
        all_results["files_analyzed"].append("Рассылка аксессуары магазины.xlsx")

    if FILES["turnover"].exists():
        all_results["data"]["turnover"] = analyze_turnover(FILES["turnover"])
        all_results["files_analyzed"].append("Отчет по оборачиваемости ТЗ регион ННВ.xlsx")

    if FILES["structure"].exists():
        all_results["data"]["structure"] = analyze_structure(FILES["structure"])
        all_results["files_analyzed"].append("Структура розница 21.01.2026.xlsx")

    # Сохраняем результаты
    output_file = OUTPUT_DIR / "dashboard_data.json"
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "=" * 80)
    print(f"✅ АНАЛИЗ ЗАВЕРШЕН")
    print(f"📁 Результаты сохранены: {output_file}")
    print(f"📊 Проанализировано файлов: {len(all_results['files_analyzed'])}")

    # Выводим краткую сводку
    print("\n📋 КРАТКАЯ СВОДКА:")
    for file_name in all_results['files_analyzed']:
        print(f"  ✅ {file_name}")

    return all_results

if __name__ == "__main__":
    results = main()
