#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание итогового JSON для дашборда с ключевыми метриками
"""

import json
from pathlib import Path

BASE_DIR = Path(r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов")
OUTPUT_DIR = BASE_DIR / "output"

def create_dashboard_data():
    """Создает структурированные данные для дашборда"""

    # Читаем исходные данные
    with open(OUTPUT_DIR / "dashboard_data_clean.json", 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Читаем анализ
    with open(OUTPUT_DIR / "analysis_report.json", 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    # Формируем итоговую структуру
    dashboard_data = {
        "report_info": {
            "title": "Отчет по регионам KARI - Регион ННВ",
            "date": raw_data.get('extraction_date'),
            "period": "12.01.2026 - 18.01.2026"
        },

        "key_metrics": {
            "total_stores": raw_data['accessories']['total_stores'],
            "nnv_stores": analysis['structure_analysis']['nnv_entries'],
            "total_regions": raw_data['regions']['total_regions'],
            "turnover_sheets": len(raw_data['turnover']['sheets'])
        },

        "regions": {
            "total": raw_data['regions']['total_regions'],
            "nnv_data": raw_data['regions']['nnv_data'],
            "columns_sample": raw_data['regions']['columns_sample']
        },

        "accessories": {
            "total_stores": raw_data['accessories']['total_stores'],
            "nnv_stores_count": raw_data['accessories']['nnv_stores_count'],
            "columns": raw_data['accessories']['columns'][:30],  # Первые 30 колонок
            "sample_data": raw_data['accessories']['sample_stores'][:20]  # Первые 20 магазинов
        },

        "turnover": {
            "sheets": {}
        },

        "structure": {
            "nnv_stores": analysis['structure_analysis']['nnv_stores_list'],
            "total_stores": analysis['structure_analysis']['nnv_entries']
        },

        "problems": []
    }

    # Добавляем данные оборачиваемости (только первые 20 строк каждого листа)
    for sheet_name, sheet_data in raw_data['turnover']['sheets'].items():
        dashboard_data["turnover"]["sheets"][sheet_name] = {
            "rows_count": sheet_data['rows_count'],
            "columns": sheet_data['columns'][:20],  # Первые 20 колонок
            "data": sheet_data['data_sample']  # Уже есть 15 строк
        }

    # Сохраняем компактный JSON
    output_file = OUTPUT_DIR / "dashboard_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("DASHBOARD DATA CREATED")
    print("=" * 80)
    print(f"\nOutput file: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")

    print("\nKEY METRICS:")
    print(f"  Total stores: {dashboard_data['key_metrics']['total_stores']}")
    print(f"  NNV stores: {dashboard_data['key_metrics']['nnv_stores']}")
    print(f"  Total regions: {dashboard_data['key_metrics']['total_regions']}")

    print("\nSTRUCTURE:")
    print(f"  NNV stores list: {len(dashboard_data['structure']['nnv_stores'])} entries")

    print("\nTURNOVER:")
    for sheet_name in dashboard_data['turnover']['sheets']:
        print(f"  {sheet_name}: {dashboard_data['turnover']['sheets'][sheet_name]['rows_count']} rows")

    return dashboard_data

if __name__ == "__main__":
    data = create_dashboard_data()
