#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ данных с выявлением проблем и причин
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов")
OUTPUT_DIR = BASE_DIR / "output"

def safe_float(value):
    """Безопасное преобразование в float"""
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace(' ', '').replace(',', '.').replace('%', '')
            return float(value)
    except:
        pass
    return None

def analyze_regions_data(regions_data):
    """Анализ данных по регионам"""
    print("\n=== ANALYSIS: REGIONS ===")

    problems = []
    insights = []

    total_regions = regions_data.get('total_regions', 0)
    nnv_found = regions_data.get('nnv_found', 0)
    nnv_data = regions_data.get('nnv_data', {})

    print(f"Total regions: {total_regions}")
    print(f"NNV rows: {nnv_found}")

    if nnv_data:
        print("\nNNV Region Data:")
        for key, value in list(nnv_data.items())[:20]:
            if value is not None and str(value).strip():
                print(f"  {key}: {value}")

        # Ищем колонки с числовыми показателями
        numeric_data = {}
        for key, value in nnv_data.items():
            num_val = safe_float(value)
            if num_val is not None:
                numeric_data[key] = num_val

        if numeric_data:
            print(f"\nNumeric metrics found: {len(numeric_data)}")
            for key, value in list(numeric_data.items())[:10]:
                print(f"  {key}: {value}")

    return {
        "total_regions": total_regions,
        "nnv_found": nnv_found,
        "problems": problems,
        "insights": insights,
        "key_metrics": nnv_data
    }

def analyze_accessories_data(acc_data):
    """Анализ данных по аксессуарам"""
    print("\n=== ANALYSIS: ACCESSORIES ===")

    problems = []
    insights = []
    top_stores = []
    worst_stores = []

    total_stores = acc_data.get('total_stores', 0)
    nnv_stores_count = acc_data.get('nnv_stores_count', 0)
    columns = acc_data.get('columns', [])
    nnv_stores = acc_data.get('nnv_stores', [])
    sample_stores = acc_data.get('sample_stores', [])

    print(f"Total stores: {total_stores}")
    print(f"NNV stores: {nnv_stores_count}")
    print(f"Columns count: {len(columns)}")

    # Выводим первые колонки
    print(f"\nFirst 15 columns:")
    for i, col in enumerate(columns[:15]):
        print(f"  {i+1}. {col}")

    # Анализируем образец данных
    if sample_stores:
        print(f"\nAnalyzing {len(sample_stores)} sample stores...")

        # Ищем колонки с приростом
        growth_cols = [col for col in columns if any(keyword in str(col).lower()
                      for keyword in ['прирост', '%', 'рост'])]

        if growth_cols:
            print(f"\nGrowth columns found: {growth_cols}")

            # Собираем статистику по приросту
            growth_values = []
            for store in sample_stores:
                for col in growth_cols:
                    val = safe_float(store.get(col))
                    if val is not None:
                        growth_values.append((store, col, val))

            if growth_values:
                # Сортируем
                growth_values.sort(key=lambda x: x[2])

                print(f"\nTop 5 growth:")
                for store, col, val in growth_values[-5:]:
                    store_name = store.get(columns[0] if columns else 'Store')
                    print(f"  {store_name}: {val}% ({col})")

                print(f"\nWorst 5 growth:")
                for store, col, val in growth_values[:5]:
                    store_name = store.get(columns[0] if columns else 'Store')
                    print(f"  {store_name}: {val}% ({col})")

                    if val < -10:
                        problems.append({
                            "type": "NEGATIVE_GROWTH",
                            "store": store_name,
                            "metric": col,
                            "value": val,
                            "severity": "HIGH"
                        })

    return {
        "total_stores": total_stores,
        "nnv_stores_count": nnv_stores_count,
        "problems": problems,
        "insights": insights,
        "top_stores": top_stores[:3],
        "worst_stores": worst_stores[:3]
    }

def analyze_turnover_data(turnover_data):
    """Анализ оборачиваемости"""
    print("\n=== ANALYSIS: TURNOVER ===")

    problems = []
    slow_movers = []
    fast_movers = []

    sheets = turnover_data.get('sheets', {})
    print(f"Sheets count: {len(sheets)}")

    for sheet_name, sheet_data in sheets.items():
        print(f"\nSheet: {sheet_name}")
        rows_count = sheet_data.get('rows_count', 0)
        columns = sheet_data.get('columns', [])
        all_data = sheet_data.get('all_data', [])

        print(f"  Rows: {rows_count}")
        print(f"  Columns: {len(columns)}")

        # Выводим колонки
        print(f"  First 10 columns:")
        for i, col in enumerate(columns[:10]):
            print(f"    {i+1}. {col}")

        # Ищем колонки оборачиваемости
        turnover_cols = [col for col in columns if 'оборачиваемост' in str(col).lower()]

        if turnover_cols:
            print(f"\n  Turnover columns: {turnover_cols}")

            for col in turnover_cols:
                values = []
                for row in all_data:
                    val = safe_float(row.get(col))
                    if val is not None and val > 0:
                        values.append((row, val))

                if values:
                    values.sort(key=lambda x: x[1])

                    avg_turn = sum(v[1] for v in values) / len(values)
                    print(f"\n    {col}:")
                    print(f"      Average: {avg_turn:.1f} days")
                    print(f"      Min: {values[0][1]:.1f} days")
                    print(f"      Max: {values[-1][1]:.1f} days")

                    # Медленно движущиеся (>60 дней)
                    slow = [v for v in values if v[1] > 60]
                    if slow:
                        print(f"      Slow movers (>60 days): {len(slow)} items")
                        print(f"        Top 3 slowest:")
                        for row, val in slow[-3:]:
                            group_name = row.get(columns[0] if columns else 'Group', 'Unknown')
                            print(f"          {group_name}: {val:.0f} days")

                            problems.append({
                                "type": "SLOW_TURNOVER",
                                "item": group_name,
                                "days": val,
                                "severity": "HIGH" if val > 90 else "MEDIUM"
                            })

    return {
        "sheets_analyzed": len(sheets),
        "problems": problems,
        "slow_movers": slow_movers,
        "fast_movers": fast_movers
    }

def analyze_structure_data(structure_data):
    """Анализ структуры розницы"""
    print("\n=== ANALYSIS: STRUCTURE ===")

    total_entries = structure_data.get('total_entries', 0)
    nnv_entries_count = structure_data.get('nnv_entries_count', 0)
    columns = structure_data.get('columns', [])
    nnv_structure = structure_data.get('nnv_structure', [])

    print(f"Total entries: {total_entries}")
    print(f"NNV entries: {nnv_entries_count}")
    print(f"Columns: {columns}")

    # Выводим структуру ННВ
    if nnv_structure:
        print(f"\nNNV Structure (first 10):")
        for entry in nnv_structure[:10]:
            print(f"  {entry}")

    return {
        "total_entries": total_entries,
        "nnv_entries": nnv_entries_count,
        "nnv_stores_list": nnv_structure
    }

def main():
    print("=" * 80)
    print("DEEP ANALYSIS WITH PROBLEM DETECTION")
    print("=" * 80)

    # Читаем данные
    data_file = OUTPUT_DIR / "dashboard_data_clean.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Анализируем каждый блок
    analysis_results = {
        "extraction_date": data.get('extraction_date'),
        "regions_analysis": analyze_regions_data(data['regions']),
        "accessories_analysis": analyze_accessories_data(data['accessories']),
        "turnover_analysis": analyze_turnover_data(data['turnover']),
        "structure_analysis": analyze_structure_data(data['structure'])
    }

    # Собираем все проблемы
    all_problems = []
    all_problems.extend(analysis_results['regions_analysis']['problems'])
    all_problems.extend(analysis_results['accessories_analysis']['problems'])
    all_problems.extend(analysis_results['turnover_analysis']['problems'])

    print("\n" + "=" * 80)
    print(f"TOTAL PROBLEMS FOUND: {len(all_problems)}")
    print("=" * 80)

    for i, problem in enumerate(all_problems, 1):
        print(f"\n{i}. [{problem.get('severity', 'MEDIUM')}] {problem.get('type', 'Unknown')}")
        for key, value in problem.items():
            if key not in ['type', 'severity']:
                print(f"   {key}: {value}")

    # Сохраняем анализ
    output_file = OUTPUT_DIR / "analysis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)

    print(f"\nAnalysis saved to: {output_file}")

    return analysis_results

if __name__ == "__main__":
    results = main()
