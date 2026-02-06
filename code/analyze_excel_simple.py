#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ всех Excel файлов для создания дашборда
"""

import pandas as pd
import json
import sys
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
        value = value.replace(' ', '').replace(',', '.').replace('%', '')
        try:
            return float(value)
        except:
            return None
    return None

def analyze_regions(file_path):
    """Анализ файла По регионам.xlsx"""
    print(f"\n[REGIONS] Analyzing: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Sheets: {len(xls.sheet_names)}")

        result = {
            "file": "По регионам.xlsx",
            "sheets": {},
            "nnv_data": {},
            "key_metrics": {},
            "problems": [],
            "top_regions": [],
            "worst_regions": []
        }

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  Sheet: {sheet_name}, Size: {df.shape}")

            # Ищем регион ННВ
            nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
            if not nnv_rows.empty:
                print(f"  Found {len(nnv_rows)} rows with NNV")
                result["nnv_data"][sheet_name] = nnv_rows.to_dict(orient='records')

            # Сохраняем структуру
            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": list(df.shape),
                "sample": df.head(15).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"ERROR analyzing regions: {e}")
        return {"error": str(e), "file": "По регионам.xlsx"}

def analyze_accessories(file_path):
    """Анализ файла Рассылка аксессуары магазины.xlsx"""
    print(f"\n[ACCESSORIES] Analyzing: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Sheets: {len(xls.sheet_names)}")

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
            print(f"  Sheet: {sheet_name}, Size: {df.shape}")

            # Ищем магазины ННВ
            nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
            if not nnv_rows.empty:
                print(f"  Found {len(nnv_rows)} NNV stores")
                result["nnv_stores"][sheet_name] = nnv_rows.to_dict(orient='records')

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": list(df.shape),
                "sample": df.head(15).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"ERROR analyzing accessories: {e}")
        return {"error": str(e), "file": "Рассылка аксессуары магазины.xlsx"}

def analyze_turnover(file_path):
    """Анализ файла Отчет по оборачиваемости ТЗ регион ННВ.xlsx"""
    print(f"\n[TURNOVER] Analyzing: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Sheets: {len(xls.sheet_names)}")

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
            print(f"  Sheet: {sheet_name}, Size: {df.shape}")

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": list(df.shape),
                "sample": df.head(15).to_dict(orient='records')
            }

            # Ищем колонки с оборачиваемостью
            turnover_cols = [col for col in df.columns if 'оборачиваемост' in str(col).lower()]
            if turnover_cols:
                print(f"  Found turnover columns: {len(turnover_cols)}")
                result["turnover_data"][sheet_name] = {
                    "turnover_columns": turnover_cols,
                    "data": df.to_dict(orient='records')[:50]
                }

        return result

    except Exception as e:
        print(f"ERROR analyzing turnover: {e}")
        return {"error": str(e), "file": "Отчет по оборачиваемости ТЗ регион ННВ.xlsx"}

def analyze_structure(file_path):
    """Анализ файла Структура розница 21.01.2026.xlsx"""
    print(f"\n[STRUCTURE] Analyzing: {file_path.name}")

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Sheets: {len(xls.sheet_names)}")

        result = {
            "file": "Структура розница 21.01.2026.xlsx",
            "sheets": {},
            "nnv_structure": {},
            "total_stores": 0
        }

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  Sheet: {sheet_name}, Size: {df.shape}")

            # Ищем структуру ННВ
            nnv_rows = df[df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)]
            if not nnv_rows.empty:
                print(f"  Found {len(nnv_rows)} NNV entries")
                result["nnv_structure"][sheet_name] = nnv_rows.to_dict(orient='records')
                result["total_stores"] += len(nnv_rows)

            result["sheets"][sheet_name] = {
                "columns": list(df.columns),
                "shape": list(df.shape),
                "sample": df.head(15).to_dict(orient='records')
            }

        return result

    except Exception as e:
        print(f"ERROR analyzing structure: {e}")
        return {"error": str(e), "file": "Структура розница 21.01.2026.xlsx"}

def main():
    print("=" * 80)
    print("EXCEL FILES ANALYSIS STARTING")
    print("=" * 80)

    # Проверяем файлы
    for name, path in FILES.items():
        status = "OK" if path.exists() else "NOT FOUND"
        print(f"{name}: {status} - {path.name}")

    # Собираем результаты
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
    print(f"ANALYSIS COMPLETED")
    print(f"Output: {output_file}")
    print(f"Files analyzed: {len(all_results['files_analyzed'])}")
    print("=" * 80)

    for file_name in all_results['files_analyzed']:
        print(f"  - {file_name}")

    return all_results

if __name__ == "__main__":
    results = main()
