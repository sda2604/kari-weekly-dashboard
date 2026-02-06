#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Глубокий анализ Excel файлов с выявлением проблем и причин
"""

import pandas as pd
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов")
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

def analyze_regions_deep():
    """Глубокий анализ файла По регионам.xlsx"""
    file_path = INPUT_DIR / "Отчет по приросту регионы" / "По регионам.xlsx"
    print(f"\n[DEEP ANALYSIS] Regions file")

    try:
        # Читаем с пропуском первых строк для правильного чтения заголовков
        df = pd.read_excel(file_path, sheet_name="Лист1", header=None)

        # Находим строку с заголовками
        header_row = None
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str).str.lower()
            if any('регион' in str(val) for val in row_values):
                header_row = i
                break

        if header_row is not None:
            # Читаем заново с правильным заголовком
            df = pd.read_excel(file_path, sheet_name="Лист1", header=header_row)
            print(f"  Header found at row {header_row}")
            print(f"  Columns: {list(df.columns)[:10]}")

        # Ищем данные по ННВ
        nnv_mask = df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)
        nnv_data = df[nnv_mask]

        print(f"  NNV rows found: {len(nnv_data)}")

        result = {
            "total_rows": len(df),
            "nnv_rows": len(nnv_data),
            "columns": list(df.columns),
            "nnv_data": nnv_data.to_dict(orient='records') if not nnv_data.empty else [],
            "all_data_sample": df.head(20).to_dict(orient='records'),
            "summary": {
                "regions_count": len(df),
                "nnv_found": not nnv_data.empty
            }
        }

        # Ищем колонки с приростом/продажами
        growth_cols = [col for col in df.columns if any(keyword in str(col).lower()
                      for keyword in ['прирост', 'продаж', 'шт', 'руб'])]
        if growth_cols:
            print(f"  Growth columns found: {len(growth_cols)}")
            result["growth_columns"] = growth_cols

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def analyze_accessories_deep():
    """Глубокий анализ файла аксессуаров"""
    file_path = INPUT_DIR / "Отчет по приросту аксессуаров по магазинам" / "Рассылка аксессуары магазины.xlsx"
    print(f"\n[DEEP ANALYSIS] Accessories file")

    try:
        # Читаем первый лист
        df = pd.read_excel(file_path, sheet_name="Лист1", header=None)

        # Находим заголовок
        header_row = None
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str).str.lower()
            if any('магазин' in str(val) or 'подразделение' in str(val) for val in row_values):
                header_row = i
                break

        if header_row is not None:
            df = pd.read_excel(file_path, sheet_name="Лист1", header=header_row)
            print(f"  Header found at row {header_row}")

        # Ищем магазины ННВ
        nnv_mask = df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)
        nnv_stores = df[nnv_mask]

        print(f"  Total stores: {len(df)}")
        print(f"  NNV stores: {len(nnv_stores)}")

        result = {
            "total_stores": len(df),
            "nnv_stores_count": len(nnv_stores),
            "columns": list(df.columns),
            "nnv_stores": nnv_stores.to_dict(orient='records') if not nnv_stores.empty else [],
            "all_stores_sample": df.head(20).to_dict(orient='records')
        }

        # Ищем колонки с продажами и приростом
        sales_cols = [col for col in df.columns if any(keyword in str(col).lower()
                     for keyword in ['продаж', 'прирост', 'шт', 'руб', '%'])]
        if sales_cols:
            print(f"  Sales columns: {len(sales_cols)}")
            result["sales_columns"] = sales_cols

            # Анализируем прирост по ННВ магазинам
            if not nnv_stores.empty and sales_cols:
                for col in sales_cols:
                    if 'прирост' in str(col).lower() or '%' in str(col):
                        try:
                            # Пытаемся найти числовые значения прироста
                            numeric_col = pd.to_numeric(nnv_stores[col], errors='coerce')
                            if numeric_col.notna().any():
                                avg_growth = numeric_col.mean()
                                print(f"    {col}: avg growth = {avg_growth:.2f}")
                        except:
                            pass

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def analyze_turnover_deep():
    """Глубокий анализ оборачиваемости"""
    file_path = INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара" / "Отчет по оборачиваемости ТЗ регион ННВ.xlsx"
    print(f"\n[DEEP ANALYSIS] Turnover file")

    try:
        xls = pd.ExcelFile(file_path)
        result = {"sheets": {}}

        for sheet_name in xls.sheet_names:
            print(f"  Sheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

            # Ищем заголовок
            header_row = None
            for i in range(min(10, len(df))):
                row_values = df.iloc[i].astype(str).str.lower()
                if any('оборачиваемост' in str(val) or 'остатки' in str(val) or 'группа' in str(val) for val in row_values):
                    header_row = i
                    break

            if header_row is not None:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                print(f"    Header at row {header_row}")
                print(f"    Rows: {len(df)}")

                # Конвертируем datetime колонки в строки
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].astype(str)

                result["sheets"][sheet_name] = {
                    "columns": [str(col) for col in df.columns],
                    "rows_count": len(df),
                    "data_sample": df.head(20).to_dict(orient='records'),
                    "full_data": df.to_dict(orient='records')
                }

                # Ищем колонки оборачиваемости
                turnover_cols = [col for col in df.columns if 'оборачиваемост' in str(col).lower()]
                if turnover_cols:
                    print(f"    Turnover columns: {turnover_cols}")

                    for col in turnover_cols:
                        try:
                            numeric_col = pd.to_numeric(df[col], errors='coerce')
                            if numeric_col.notna().any():
                                avg_turn = numeric_col.mean()
                                max_turn = numeric_col.max()
                                min_turn = numeric_col.min()
                                print(f"      {col}: avg={avg_turn:.1f}, max={max_turn:.1f}, min={min_turn:.1f}")

                                # Находим проблемные товары (высокая оборачиваемость = долго лежит)
                                slow_movers = df[numeric_col > avg_turn * 1.5]
                                if not slow_movers.empty:
                                    print(f"      Slow movers (>1.5x avg): {len(slow_movers)} items")
                        except:
                            pass

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def analyze_structure_deep():
    """Глубокий анализ структуры розницы"""
    file_path = INPUT_DIR / "Структура розница 21.01.2026.xlsx"
    print(f"\n[DEEP ANALYSIS] Structure file")

    try:
        # Читаем первый лист без указания имени
        xls = pd.ExcelFile(file_path)
        print(f"  Available sheets: {xls.sheet_names}")
        df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0], header=None)

        # Ищем заголовок
        header_row = None
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str).str.lower()
            if any('подразделение' in str(val) or 'магазин' in str(val) or 'ркц' in str(val) for val in row_values):
                header_row = i
                break

        if header_row is not None:
            df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0], header=header_row)
            print(f"  Header at row {header_row}")

        # Ищем ННВ
        nnv_mask = df.apply(lambda row: any('ннв' in str(val).lower() for val in row if pd.notna(val)), axis=1)
        nnv_structure = df[nnv_mask]

        print(f"  Total entries: {len(df)}")
        print(f"  NNV entries: {len(nnv_structure)}")

        result = {
            "total_entries": len(df),
            "nnv_entries": len(nnv_structure),
            "columns": list(df.columns),
            "nnv_structure": nnv_structure.to_dict(orient='records') if not nnv_structure.empty else [],
            "all_data": df.to_dict(orient='records')
        }

        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("DEEP ANALYSIS WITH PROBLEM DETECTION")
    print("=" * 80)

    results = {
        "analysis_date": "2026-01-21",
        "regions": analyze_regions_deep(),
        "accessories": analyze_accessories_deep(),
        "turnover": analyze_turnover_deep(),
        "structure": analyze_structure_deep()
    }

    # Сохраняем детальные результаты
    output_file = OUTPUT_DIR / "dashboard_data_detailed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "=" * 80)
    print(f"DEEP ANALYSIS COMPLETED")
    print(f"Output: {output_file}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    results = main()
