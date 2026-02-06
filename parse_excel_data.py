# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import numpy as np

# Путь к файлам
base_path = r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов\input"

# Структура данных для дашборда
dashboard_data = {
    "regions": {
        "all_regions": [],
        "nnv_divisions": [],
        "nnv_categories_top5": [],
        "nnv_categories_worst5": []
    },
    "accessories": {
        "nnv_top10": [],
        "nnv_worst10": []
    },
    "turnover": {
        "slow_groups": []
    },
    "metadata": {
        "period": "12.01.2026 - 18.01.2026",
        "extraction_date": "21.01.2026"
    }
}

# ========== 1. ДАННЫЕ ПО РЕГИОНАМ ==========
print("[1/3] Парсинг данных по регионам...")
regions_file = os.path.join(base_path, "Отчет по приросту регионы", "По регионам.xlsx")

try:
    df = pd.read_excel(regions_file, sheet_name=0, header=None)

    # Ищем заголовок с регионами - они в Unnamed колонках
    # Регионы: БЕЛ, ВРН, ИРК, КЗ, МСК, ННВ, САМ, СИБ, СПБ, УРЛ, ЮГ

    # Находим строку с названиями регионов (обычно это вторая или третья строка)
    region_codes = ['БЕЛ', 'ВРН', 'ИРК', 'КЗ', 'МСК', 'ННВ', 'САМ', 'СИБ', 'СПБ', 'УРЛ', 'ЮГ']

    # Ищем в каких колонках находятся регионы
    region_cols = {}
    for idx, row in df.iterrows():
        for col_idx, val in enumerate(row):
            if pd.notna(val) and str(val).strip() in region_codes:
                region_code = str(val).strip()
                if region_code not in region_cols:
                    region_cols[region_code] = {'col': col_idx, 'row': idx}

    print(f"Найдено регионов: {len(region_cols)}")
    print(f"Регионы: {list(region_cols.keys())}")

    # Извлекаем данные для каждого региона
    # Обычно после названия региона идут показатели по строкам вниз

    # Ищем строку с приростом (обычно содержит "%" или "прирост")
    # Для упрощения возьмем первые 3 числовые ячейки под каждым регионом

    for region, info in region_cols.items():
        col = info['col']
        row = info['row']

        # Ищем числовые значения ниже названия региона
        values = []
        for r in range(row + 1, min(row + 20, len(df))):
            val = df.iloc[r, col]
            if pd.notna(val):
                try:
                    num_val = float(val)
                    values.append(num_val)
                except:
                    pass

        # Первое значение обычно прирост в %
        growth_pct = values[0] * 100 if len(values) > 0 and values[0] < 1 else (values[0] if len(values) > 0 else 0)

        # Количество магазинов - обычно второе или третье значение (целое число)
        shops_count = 0
        for v in values[1:]:
            if v > 10 and v == int(v):  # Целое число больше 10
                shops_count = int(v)
                break

        dashboard_data["regions"]["all_regions"].append({
            "region": region,
            "growth": round(growth_pct, 1),
            "shops": shops_count
        })

    print(f"Извлечено данных по {len(dashboard_data['regions']['all_regions'])} регионам")

    # Детализация по ННВ подразделениям
    # Ищем подразделения ННВ в той же таблице или на других листах
    # Подразделения: Ярославское, Ижевское, ННВ Север, Казань 1, ННВ 1, Владимир, Наб.Челны

    nnv_divisions = ['Ярославское', 'Ижевское', 'ННВ Север', 'Казань 1', 'ННВ 1', 'Владимир', 'Наб.Челны', 'Наб. Челны']

    for idx, row in df.iterrows():
        for col_idx, val in enumerate(row):
            if pd.notna(val):
                val_str = str(val).strip()
                for div in nnv_divisions:
                    if div in val_str or val_str in div:
                        # Извлекаем данные для этого подразделения
                        values = []
                        for r in range(idx + 1, min(idx + 10, len(df))):
                            v = df.iloc[r, col_idx]
                            if pd.notna(v):
                                try:
                                    values.append(float(v))
                                except:
                                    pass

                        if values:
                            growth_pct = values[0] * 100 if values[0] < 1 else values[0]
                            dashboard_data["regions"]["nnv_divisions"].append({
                                "division": div,
                                "growth": round(growth_pct, 1)
                            })
                        break

    print(f"Найдено подразделений ННВ: {len(dashboard_data['regions']['nnv_divisions'])}")

    # ТОП и ХУДШИЕ категории для ННВ
    # Ищем категории товаров в строках (обычно в первой колонке)
    categories_data = []

    # Находим колонку с ННВ
    nnv_col = region_cols.get('ННВ', {}).get('col', None)

    if nnv_col is not None:
        for idx, row in df.iterrows():
            category_name = str(row[0]).strip() if pd.notna(row[0]) else ""
            nnv_value = row[nnv_col] if nnv_col < len(row) else None

            # Пропускаем пустые и служебные строки
            if category_name and nnv_value is not None and category_name not in region_codes:
                try:
                    value_num = float(nnv_value)
                    # Если значение похоже на процент прироста (от -1 до 5)
                    if -1 < value_num < 5:
                        growth_pct = value_num * 100
                        categories_data.append({
                            "category": category_name[:50],  # Обрезаем длинные названия
                            "growth": round(growth_pct, 1)
                        })
                except:
                    pass

        # Сортируем и берем ТОП-5 и ХУДШИЕ-5
        categories_data = sorted(categories_data, key=lambda x: x['growth'], reverse=True)

        if len(categories_data) >= 5:
            dashboard_data["regions"]["nnv_categories_top5"] = categories_data[:5]
            dashboard_data["regions"]["nnv_categories_worst5"] = categories_data[-5:][::-1]

        print(f"Найдено категорий для ННВ: {len(categories_data)}")

except Exception as e:
    print(f"ERROR при обработке регионов: {e}")
    import traceback
    traceback.print_exc()

# ========== 2. ДАННЫЕ ПО АКСЕССУАРАМ ==========
print("\n[2/3] Парсинг данных по аксессуарам...")
accessories_file = os.path.join(base_path, "Отчет по приросту аксессуаров по магазинам", "Рассылка аксессуары магазины.xlsx")

try:
    df_acc = pd.read_excel(accessories_file, sheet_name=0, header=None)

    # Ищем колонку с регионом и номером магазина
    # Обычно структура: Регион | Номер магазина | Прирост % | ...

    # Находим заголовки
    header_row = None
    for idx, row in df_acc.iterrows():
        row_str = ' '.join([str(x) for x in row if pd.notna(x)]).lower()
        if 'регион' in row_str or 'магазин' in row_str or 'прирост' in row_str:
            header_row = idx
            break

    if header_row is not None:
        # Устанавливаем заголовки
        df_acc.columns = df_acc.iloc[header_row]
        df_acc = df_acc.iloc[header_row + 1:].reset_index(drop=True)

        # Ищем колонки
        region_col = None
        shop_col = None
        growth_col = None

        for col in df_acc.columns:
            col_str = str(col).lower()
            if 'регион' in col_str:
                region_col = col
            elif 'магазин' in col_str or 'номер' in col_str:
                shop_col = col
            elif 'прирост' in col_str or '%' in col_str:
                growth_col = col

        print(f"Колонки: регион={region_col}, магазин={shop_col}, прирост={growth_col}")

        if region_col and shop_col and growth_col:
            # Фильтруем магазины ННВ
            df_nnv = df_acc[df_acc[region_col].astype(str).str.contains('ННВ', na=False)].copy()

            # Конвертируем прирост в числа
            df_nnv[growth_col] = pd.to_numeric(df_nnv[growth_col], errors='coerce')
            df_nnv = df_nnv.dropna(subset=[growth_col])

            # Сортируем по приросту
            df_nnv = df_nnv.sort_values(by=growth_col, ascending=False)

            # ТОП-10
            top10 = df_nnv.head(10)
            for _, row in top10.iterrows():
                dashboard_data["accessories"]["nnv_top10"].append({
                    "shop": str(row[shop_col]),
                    "growth": round(float(row[growth_col]) * 100 if float(row[growth_col]) < 1 else float(row[growth_col]), 1)
                })

            # ХУДШИЕ-10
            worst10 = df_nnv.tail(10).iloc[::-1]
            for _, row in worst10.iterrows():
                dashboard_data["accessories"]["nnv_worst10"].append({
                    "shop": str(row[shop_col]),
                    "growth": round(float(row[growth_col]) * 100 if float(row[growth_col]) < 1 else float(row[growth_col]), 1)
                })

            print(f"Извлечено: ТОП-10 и ХУДШИЕ-10 магазинов ННВ")

except Exception as e:
    print(f"ERROR при обработке аксессуаров: {e}")
    import traceback
    traceback.print_exc()

# ========== 3. ДАННЫЕ ПО ОБОРАЧИВАЕМОСТИ ==========
print("\n[3/3] Парсинг данных по оборачиваемости...")
turnover_file = os.path.join(base_path, "Обувь остатки и оборачиваемость по группам товара", "Отчет по оборачиваемости ТЗ регион ННВ.xlsx")

try:
    df_turn = pd.read_excel(turnover_file, sheet_name=0, header=None)

    # Ищем заголовки таблицы
    header_row = None
    for idx, row in df_turn.iterrows():
        row_str = ' '.join([str(x) for x in row if pd.notna(x)]).lower()
        if 'группа' in row_str or 'оборачиваемость' in row_str or 'остатки' in row_str:
            header_row = idx
            break

    if header_row is not None:
        df_turn.columns = df_turn.iloc[header_row]
        df_turn = df_turn.iloc[header_row + 1:].reset_index(drop=True)

        # Ищем нужные колонки
        group_col = None
        turnover_col = None
        stock_col = None

        for col in df_turn.columns:
            col_str = str(col).lower()
            if 'группа' in col_str or 'товар' in col_str:
                group_col = col
            elif 'оборачиваемость' in col_str or 'недел' in col_str:
                turnover_col = col
            elif 'остаток' in col_str or 'остатки' in col_str:
                stock_col = col

        print(f"Колонки: группа={group_col}, оборачиваемость={turnover_col}, остатки={stock_col}")

        if group_col and turnover_col:
            # Конвертируем оборачиваемость в числа
            df_turn[turnover_col] = pd.to_numeric(df_turn[turnover_col], errors='coerce')

            # Фильтруем группы с оборачиваемостью > 10 недель
            df_slow = df_turn[df_turn[turnover_col] > 10].copy()
            df_slow = df_slow.dropna(subset=[turnover_col])

            # Сортируем по убыванию оборачиваемости
            df_slow = df_slow.sort_values(by=turnover_col, ascending=False)

            # Извлекаем данные
            for _, row in df_slow.iterrows():
                group_name = str(row[group_col]) if pd.notna(row[group_col]) else "Без названия"
                turnover_weeks = float(row[turnover_col])
                stock = float(row[stock_col]) if stock_col and pd.notna(row[stock_col]) else 0

                dashboard_data["turnover"]["slow_groups"].append({
                    "group": group_name[:80],
                    "turnover_weeks": round(turnover_weeks, 1),
                    "stock": int(stock)
                })

            print(f"Найдено медленных групп (>10 недель): {len(dashboard_data['turnover']['slow_groups'])}")

except Exception as e:
    print(f"ERROR при обработке оборачиваемости: {e}")
    import traceback
    traceback.print_exc()

# ========== СОХРАНЕНИЕ РЕЗУЛЬТАТА ==========
print("\n=== СОХРАНЕНИЕ ДАННЫХ ===")

output_file = "dashboard_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

print(f"Данные сохранены в {output_file}")

# Вывод краткой статистики
print("\n=== СТАТИСТИКА ===")
print(f"Регионов: {len(dashboard_data['regions']['all_regions'])}")
print(f"Подразделений ННВ: {len(dashboard_data['regions']['nnv_divisions'])}")
print(f"ТОП категорий ННВ: {len(dashboard_data['regions']['nnv_categories_top5'])}")
print(f"ХУДШИХ категорий ННВ: {len(dashboard_data['regions']['nnv_categories_worst5'])}")
print(f"ТОП-10 магазинов по аксессуарам: {len(dashboard_data['accessories']['nnv_top10'])}")
print(f"ХУДШИЕ-10 магазинов по аксессуарам: {len(dashboard_data['accessories']['nnv_worst10'])}")
print(f"Медленных групп товаров: {len(dashboard_data['turnover']['slow_groups'])}")

print("\n=== ГОТОВО ===")
