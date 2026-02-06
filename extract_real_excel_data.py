# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import numpy as np

base_path = r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов\input"

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
    }
}

print("="*80)
print("ИЗВЛЕЧЕНИЕ РЕАЛЬНЫХ ДАННЫХ ИЗ EXCEL ФАЙЛОВ")
print("="*80)

# ========== 1. РЕГИОНЫ ==========
print("\n[1/3] ФАЙЛ: По регионам.xlsx")
print("-"*80)

regions_file = os.path.join(base_path, "Отчет по приросту регионы", "По регионам.xlsx")

try:
    # Читаем Excel без заголовков
    df_regions = pd.read_excel(regions_file, header=None)

    print(f"Размер таблицы: {df_regions.shape[0]} строк x {df_regions.shape[1]} колонок")

    # Поиск регионов в данных
    regions_map = {}
    region_codes = ['БЕЛ', 'ВРН', 'ИРК', 'КЗ', 'МСК', 'ННВ', 'САМ', 'СИБ', 'СПБ', 'УРЛ', 'ЮГ']

    # Ищем строку с регионами (обычно строка 2-4)
    for row_idx in range(min(10, len(df_regions))):
        row = df_regions.iloc[row_idx]
        for col_idx, val in enumerate(row):
            if pd.notna(val) and str(val).strip() in region_codes:
                region_code = str(val).strip()
                if region_code not in regions_map:
                    regions_map[region_code] = col_idx
                    print(f"Найден регион {region_code} в колонке {col_idx}")

    print(f"\nВсего найдено регионов: {len(regions_map)}")

    # Теперь ищем строку с данными прироста
    # Обычно это строка с меткой "Понедельник-Воскресенье" или похожей
    growth_row_idx = None

    for row_idx in range(min(20, len(df_regions))):
        row_text = ' '.join([str(x) for x in df_regions.iloc[row_idx] if pd.notna(x)])
        if 'Понедельник' in row_text and 'Воскресенье' in row_text:
            # Данные прироста обычно на 1-2 строки ниже
            growth_row_idx = row_idx + 1
            print(f"\nСтрока с приростом найдена: {growth_row_idx}")
            break

    if growth_row_idx and regions_map:
        # Извлекаем данные прироста
        for region, col_idx in regions_map.items():
            growth_val = df_regions.iloc[growth_row_idx, col_idx]

            if pd.notna(growth_val):
                try:
                    growth_num = float(growth_val)
                    # Конвертируем в проценты если нужно
                    if growth_num < 1:
                        growth_num = growth_num * 100

                    # Ищем количество магазинов (обычно целое число в следующих строках)
                    shops_count = 0
                    for offset in range(1, 10):
                        if growth_row_idx + offset < len(df_regions):
                            shop_val = df_regions.iloc[growth_row_idx + offset, col_idx]
                            if pd.notna(shop_val):
                                try:
                                    shop_num = float(shop_val)
                                    if shop_num > 10 and shop_num == int(shop_num):
                                        shops_count = int(shop_num)
                                        break
                                except:
                                    pass

                    dashboard_data["regions"]["all_regions"].append({
                        "region": region,
                        "growth": round(growth_num, 1),
                        "shops": shops_count
                    })

                    print(f"  {region}: прирост {round(growth_num, 1)}%, магазинов {shops_count}")

                except Exception as e:
                    print(f"  {region}: ошибка парсинга - {e}")

    print(f"\n✓ Извлечено данных по {len(dashboard_data['regions']['all_regions'])} регионам")

    # Поиск подразделений ННВ
    print("\nПоиск подразделений ННВ...")
    nnv_divisions_keywords = ['Ярославск', 'Ижевск', 'Север', 'Казань', 'ННВ 1', 'Владимир', 'Челны']

    found_divisions = {}

    for row_idx in range(len(df_regions)):
        for col_idx in range(min(5, df_regions.shape[1])):  # Проверяем первые 5 колонок
            val = df_regions.iloc[row_idx, col_idx]
            if pd.notna(val):
                val_str = str(val).strip()
                for keyword in nnv_divisions_keywords:
                    if keyword in val_str and val_str not in found_divisions:
                        # Ищем числовое значение прироста справа
                        for offset in range(1, 10):
                            if col_idx + offset < df_regions.shape[1]:
                                num_val = df_regions.iloc[row_idx, col_idx + offset]
                                if pd.notna(num_val):
                                    try:
                                        growth = float(num_val)
                                        if -50 < growth < 200:  # Разумный диапазон для прироста
                                            if growth < 1 and growth > -1:
                                                growth = growth * 100
                                            found_divisions[val_str] = round(growth, 1)
                                            print(f"  {val_str}: {round(growth, 1)}%")
                                            break
                                    except:
                                        pass
                        break

    # Берем уникальные подразделения
    for division, growth in list(found_divisions.items())[:7]:
        dashboard_data["regions"]["nnv_divisions"].append({
            "division": division,
            "growth": growth
        })

    print(f"\n✓ Найдено подразделений: {len(dashboard_data['regions']['nnv_divisions'])}")

    # Поиск категорий для ННВ
    print("\nПоиск категорий товаров...")

    if 'ННВ' in regions_map:
        nnv_col = regions_map['ННВ']
        categories = []

        # Проверяем все строки
        for row_idx in range(len(df_regions)):
            # Категория обычно в первой колонке
            category = df_regions.iloc[row_idx, 0]
            nnv_value = df_regions.iloc[row_idx, nnv_col]

            if pd.notna(category) and pd.notna(nnv_value):
                category_str = str(category).strip()
                # Пропускаем служебные строки
                if len(category_str) > 3 and category_str not in region_codes:
                    try:
                        growth = float(nnv_value)
                        # Фильтруем разумные значения прироста
                        if -100 < growth < 500:
                            if growth < 5 and growth > -5:
                                growth = growth * 100

                            categories.append({
                                "category": category_str[:50],
                                "growth": round(growth, 1)
                            })
                    except:
                        pass

        # Сортируем и берем ТОП-5 и ХУДШИЕ-5
        if len(categories) > 10:
            categories_sorted = sorted(categories, key=lambda x: x['growth'], reverse=True)

            dashboard_data["regions"]["nnv_categories_top5"] = categories_sorted[:5]
            dashboard_data["regions"]["nnv_categories_worst5"] = categories_sorted[-5:][::-1]

            print(f"\n✓ Найдено категорий: {len(categories)}")
            print("\nТОП-5 категорий:")
            for cat in dashboard_data["regions"]["nnv_categories_top5"]:
                print(f"  {cat['category']}: +{cat['growth']}%")

            print("\nХУДШИЕ-5 категорий:")
            for cat in dashboard_data["regions"]["nnv_categories_worst5"]:
                print(f"  {cat['category']}: {cat['growth']}%")

except Exception as e:
    print(f"✗ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

# ========== 2. АКСЕССУАРЫ ==========
print("\n" + "="*80)
print("[2/3] ФАЙЛ: Рассылка аксессуары магазины.xlsx")
print("-"*80)

accessories_file = os.path.join(base_path, "Отчет по приросту аксессуаров по магазинам", "Рассылка аксессуары магазины.xlsx")

try:
    # Пробуем разные варианты чтения
    for skip_rows in [0, 1, 2, 3]:
        try:
            df_acc = pd.read_excel(accessories_file, skiprows=skip_rows)

            print(f"\nПопытка чтения с пропуском {skip_rows} строк...")
            print(f"Размер: {df_acc.shape[0]} строк x {df_acc.shape[1]} колонок")
            print(f"Колонки: {df_acc.columns.tolist()[:5]}...")

            # Ищем нужные колонки
            region_col = None
            shop_col = None
            growth_col = None

            for col in df_acc.columns:
                col_lower = str(col).lower()
                if not region_col and ('регион' in col_lower or 'подразд' in col_lower):
                    region_col = col
                if not shop_col and ('магазин' in col_lower or 'пункт' in col_lower or 'торговая' in col_lower):
                    shop_col = col
                if not growth_col and ('неделе к' in col_lower or 'прирост' in col_lower or 'пн-вс' in col_lower):
                    growth_col = col

            print(f"Найденные колонки: регион='{region_col}', магазин='{shop_col}', прирост='{growth_col}'")

            if shop_col and growth_col:
                # Проверяем первые несколько строк
                print(f"\nПервые 5 строк данных:")
                for idx in range(min(5, len(df_acc))):
                    shop_val = df_acc.iloc[idx][shop_col] if shop_col else "N/A"
                    growth_val = df_acc.iloc[idx][growth_col] if growth_col else "N/A"
                    region_val = df_acc.iloc[idx][region_col] if region_col else "N/A"
                    print(f"  Строка {idx}: регион={region_val}, магазин={shop_val}, прирост={growth_val}")

                # Фильтруем ННВ магазины
                if region_col:
                    df_nnv = df_acc[df_acc[region_col].astype(str).str.contains('ННВ|Нижн|Н.Н', case=False, na=False)].copy()
                else:
                    df_nnv = df_acc.copy()

                print(f"\nНайдено магазинов ННВ: {len(df_nnv)}")

                # Конвертируем прирост в числа
                df_nnv[growth_col] = pd.to_numeric(df_nnv[growth_col], errors='coerce')
                df_nnv = df_nnv.dropna(subset=[growth_col])

                # Сортируем
                df_nnv_sorted = df_nnv.sort_values(by=growth_col, ascending=False)

                print(f"Магазинов с валидными данными: {len(df_nnv_sorted)}")

                # ТОП-10
                for idx, (_, row) in enumerate(df_nnv_sorted.head(10).iterrows()):
                    growth_val = float(row[growth_col])
                    if abs(growth_val) < 5:
                        growth_val = growth_val * 100

                    shop_name = str(row[shop_col])
                    dashboard_data["accessories"]["nnv_top10"].append({
                        "shop": shop_name[:30],
                        "growth": round(growth_val, 1)
                    })
                    print(f"  ТОП-{idx+1}: {shop_name[:30]} = +{round(growth_val, 1)}%")

                # ХУДШИЕ-10
                print("\nХудшие магазины:")
                for idx, (_, row) in enumerate(df_nnv_sorted.tail(10).iloc[::-1].iterrows()):
                    growth_val = float(row[growth_col])
                    if abs(growth_val) < 5:
                        growth_val = growth_val * 100

                    shop_name = str(row[shop_col])
                    dashboard_data["accessories"]["nnv_worst10"].append({
                        "shop": shop_name[:30],
                        "growth": round(growth_val, 1)
                    })
                    print(f"  ХУДШ-{idx+1}: {shop_name[:30]} = {round(growth_val, 1)}%")

                print(f"\n✓ Извлечено: ТОП-10 и ХУДШИЕ-10")
                break

        except Exception as e:
            print(f"  Ошибка при skiprows={skip_rows}: {e}")
            continue

except Exception as e:
    print(f"✗ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

# ========== 3. ОБОРАЧИВАЕМОСТЬ ==========
print("\n" + "="*80)
print("[3/3] ФАЙЛ: Отчет по оборачиваемости ТЗ регион ННВ.xlsx")
print("-"*80)

turnover_file = os.path.join(base_path, "Обувь остатки и оборачиваемость по группам товара", "Отчет по оборачиваемости ТЗ регион ННВ.xlsx")

try:
    # Пробуем разные варианты чтения
    for skip_rows in [0, 1, 2, 3, 4]:
        try:
            df_turn = pd.read_excel(turnover_file, skiprows=skip_rows)

            print(f"\nПопытка чтения с пропуском {skip_rows} строк...")
            print(f"Размер: {df_turn.shape[0]} строк x {df_turn.shape[1]} колонок")
            print(f"Колонки: {df_turn.columns.tolist()[:8]}...")

            # Ищем колонки
            group_col = None
            turnover_col = None
            stock_col = None

            for col in df_turn.columns:
                col_lower = str(col).lower()
                if not group_col and ('артикул' in col_lower or 'группа' in col_lower or 'товар' in col_lower or 'наименование' in col_lower):
                    group_col = col
                if not turnover_col and ('оборачиваемость' in col_lower or 'оборач' in col_lower):
                    turnover_col = col
                if not stock_col and ('остаток' in col_lower or 'остатки' in col_lower):
                    stock_col = col

            print(f"Найденные колонки: группа='{group_col}', оборачиваемость='{turnover_col}', остатки='{stock_col}'")

            if turnover_col:
                # Показываем первые строки
                print(f"\nПервые 5 строк:")
                for idx in range(min(5, len(df_turn))):
                    group_val = df_turn.iloc[idx][group_col] if group_col else "N/A"
                    turn_val = df_turn.iloc[idx][turnover_col] if turnover_col else "N/A"
                    stock_val = df_turn.iloc[idx][stock_col] if stock_col else "N/A"
                    print(f"  {group_val} | Оборач: {turn_val} | Остатки: {stock_val}")

                # Конвертируем оборачиваемость
                df_turn[turnover_col] = pd.to_numeric(df_turn[turnover_col], errors='coerce')

                # Фильтруем > 10 недель
                df_slow = df_turn[df_turn[turnover_col] > 10].copy()
                df_slow = df_slow.dropna(subset=[turnover_col])

                # Сортируем по убыванию
                df_slow_sorted = df_slow.sort_values(by=turnover_col, ascending=False)

                print(f"\nНайдено групп с оборачиваемостью > 10 недель: {len(df_slow_sorted)}")

                # Извлекаем данные
                for idx, (_, row) in enumerate(df_slow_sorted.head(30).iterrows()):
                    group_name = str(row[group_col]) if group_col and pd.notna(row[group_col]) else "Без названия"
                    turnover_val = float(row[turnover_col])
                    stock_val = int(float(row[stock_col])) if stock_col and pd.notna(row[stock_col]) else 0

                    dashboard_data["turnover"]["slow_groups"].append({
                        "group": group_name[:80],
                        "turnover_weeks": round(turnover_val, 1),
                        "stock": stock_val
                    })

                    if idx < 10:
                        print(f"  {idx+1}. {group_name[:50]} - {round(turnover_val, 1)} нед, {stock_val} шт")

                print(f"\n✓ Извлечено: {len(dashboard_data['turnover']['slow_groups'])} медленных групп")
                break

        except Exception as e:
            print(f"  Ошибка при skiprows={skip_rows}: {e}")
            continue

except Exception as e:
    print(f"✗ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

# ========== СОХРАНЕНИЕ ==========
print("\n" + "="*80)
print("СОХРАНЕНИЕ РЕЗУЛЬТАТА")
print("="*80)

output_file = "dashboard_data_real.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

print(f"\n✓ Данные сохранены в: {output_file}")

print("\n" + "="*80)
print("ИТОГОВАЯ СТАТИСТИКА")
print("="*80)
print(f"Регионов: {len(dashboard_data['regions']['all_regions'])}")
print(f"Подразделений ННВ: {len(dashboard_data['regions']['nnv_divisions'])}")
print(f"ТОП категорий: {len(dashboard_data['regions']['nnv_categories_top5'])}")
print(f"ХУДШИХ категорий: {len(dashboard_data['regions']['nnv_categories_worst5'])}")
print(f"ТОП-10 магазинов: {len(dashboard_data['accessories']['nnv_top10'])}")
print(f"ХУДШИЕ-10 магазинов: {len(dashboard_data['accessories']['nnv_worst10'])}")
print(f"Медленных групп: {len(dashboard_data['turnover']['slow_groups'])}")
print("="*80)
