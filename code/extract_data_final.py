#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный скрипт извлечения данных для дашборда
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

def convert_to_serializable(obj):
    """Конвертирует объект в JSON-сериализуемый формат"""
    if pd.isna(obj):
        return None
    if isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.strftime('%Y-%m-%d') if not pd.isna(obj) else None
    if isinstance(obj, (pd.Int64Dtype, pd.Int32Dtype)):
        return int(obj)
    if isinstance(obj, (pd.Float64Dtype, pd.Float32Dtype)):
        return float(obj)
    return obj

def clean_dataframe(df):
    """Очищает DataFrame для JSON сериализации"""
    df_clean = df.copy()

    # Конвертируем все datetime колонки
    for col in df_clean.columns:
        if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)

    # Заменяем NaN на None
    df_clean = df_clean.where(pd.notnull(df_clean), None)

    return df_clean

def extract_regions():
    """Извлечение данных по регионам"""
    file_path = INPUT_DIR / "Отчет по приросту регионы" / "По регионам.xlsx"
    print("\n[1/4] REGIONS FILE")

    try:
        df = pd.read_excel(file_path, sheet_name="Лист1", header=3)
        df_clean = clean_dataframe(df)

        print(f"  Rows: {len(df_clean)}")
        print(f"  Columns: {len(df_clean.columns)}")

        # Ищем ННВ
        nnv_mask = df_clean.apply(lambda row: any('ннв' in str(val).lower() for val in row if val is not None), axis=1)
        nnv_data = df_clean[nnv_mask]

        print(f"  NNV rows: {len(nnv_data)}")

        # Получаем первую строку ННВ как пример
        nnv_dict = {}
        if not nnv_data.empty:
            nnv_row = nnv_data.iloc[0].to_dict()
            # Конвертируем все ключи в строки
            nnv_dict = {str(k): v for k, v in nnv_row.items()}

        return {
            "total_regions": len(df_clean),
            "nnv_found": len(nnv_data),
            "column_count": len(df_clean.columns),
            "columns_sample": [str(col) for col in list(df_clean.columns)[:20]],
            "nnv_data": nnv_dict,
            "first_10_rows": [{str(k): v for k, v in row.items()} for row in df_clean.head(10).to_dict(orient='records')]
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"error": str(e)}

def extract_accessories():
    """Извлечение данных по аксессуарам"""
    file_path = INPUT_DIR / "Отчет по приросту аксессуаров по магазинам" / "Рассылка аксессуары магазины.xlsx"
    print("\n[2/4] ACCESSORIES FILE")

    try:
        df = pd.read_excel(file_path, sheet_name="Лист1", header=4)
        df_clean = clean_dataframe(df)

        print(f"  Total stores: {len(df_clean)}")

        # Ищем ННВ магазины
        nnv_mask = df_clean.apply(lambda row: any('ннв' in str(val).lower() for val in row if val is not None), axis=1)
        nnv_stores = df_clean[nnv_mask]

        print(f"  NNV stores: {len(nnv_stores)}")

        # Собираем данные по ННВ
        nnv_list = []
        if not nnv_stores.empty:
            for idx, row in nnv_stores.head(10).iterrows():
                nnv_list.append({str(k): v for k, v in row.to_dict().items()})

        return {
            "total_stores": len(df_clean),
            "nnv_stores_count": len(nnv_stores),
            "columns": [str(col) for col in df_clean.columns],
            "nnv_stores": nnv_list,
            "sample_stores": [{str(k): v for k, v in row.items()} for row in df_clean.head(10).to_dict(orient='records')]
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"error": str(e)}

def extract_turnover():
    """Извлечение данных оборачиваемости"""
    file_path = INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара" / "Отчет по оборачиваемости ТЗ регион ННВ.xlsx"
    print("\n[3/4] TURNOVER FILE")

    try:
        xls = pd.ExcelFile(file_path)
        result = {"sheets": {}}

        for sheet_name in xls.sheet_names:
            print(f"  Sheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
            df_clean = clean_dataframe(df)

            print(f"    Rows: {len(df_clean)}")

            # Сохраняем данные
            result["sheets"][str(sheet_name)] = {
                "rows_count": len(df_clean),
                "columns": [str(col) for col in df_clean.columns],
                "data_sample": [{str(k): v for k, v in row.items()} for row in df_clean.head(15).to_dict(orient='records')],
                "all_data": [{str(k): v for k, v in row.items()} for row in df_clean.to_dict(orient='records')]
            }

        return result

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"error": str(e)}

def extract_structure():
    """Извлечение структуры розницы"""
    file_path = INPUT_DIR / "Структура розница 21.01.2026.xlsx"
    print("\n[4/4] STRUCTURE FILE")

    try:
        xls = pd.ExcelFile(file_path)
        sheet_name = xls.sheet_names[0]
        print(f"  Sheet: {sheet_name}")

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
        df_clean = clean_dataframe(df)

        print(f"  Total rows: {len(df_clean)}")

        # Ищем ННВ
        nnv_mask = df_clean.apply(lambda row: any('ннв' in str(val).lower() for val in row if val is not None), axis=1)
        nnv_structure = df_clean[nnv_mask]

        print(f"  NNV entries: {len(nnv_structure)}")

        return {
            "total_entries": len(df_clean),
            "nnv_entries_count": len(nnv_structure),
            "columns": [str(col) for col in df_clean.columns],
            "nnv_structure": [{str(k): v for k, v in row.items()} for row in nnv_structure.to_dict(orient='records')],
            "all_entries": [{str(k): v for k, v in row.items()} for row in df_clean.to_dict(orient='records')]
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("FINAL DATA EXTRACTION FOR DASHBOARD")
    print("=" * 80)

    results = {
        "extraction_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "regions": extract_regions(),
        "accessories": extract_accessories(),
        "turnover": extract_turnover(),
        "structure": extract_structure()
    }

    # Сохраняем
    output_file = OUTPUT_DIR / "dashboard_data_clean.json"
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"SUCCESS! Data extracted to: {output_file}")
    print("=" * 80)

    # Статистика
    print("\nSTATISTICS:")
    print(f"  Regions: {results['regions'].get('total_regions', 0)} total")
    print(f"  Accessories: {results['accessories'].get('total_stores', 0)} stores")
    print(f"  Turnover: {len(results['turnover'].get('sheets', {}))} sheets")
    print(f"  Structure: {results['structure'].get('nnv_entries_count', 0)} NNV entries")

    return results

if __name__ == "__main__":
    results = main()
