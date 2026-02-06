# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import sys

# Fix encoding для Windows консоли
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

base_path = r"C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов\input"

dashboard_data = {
    "regions": {"all_regions": [], "nnv_divisions": [], "nnv_categories_top5": [], "nnv_categories_worst5": []},
    "accessories": {"nnv_top10": [], "nnv_worst10": []},
    "turnover": {"slow_groups": []}
}

print("="*80)
print("EXTRACTION OF REAL DATA FROM EXCEL")
print("="*80)

# ========== 1. REGIONS ==========
print("\n[1/3] FILE: Po regionam.xlsx")
print("-"*80)

regions_file = os.path.join(base_path, "Отчет по приросту регионы", "По регионам.xlsx")

try:
    df_regions = pd.read_excel(regions_file, header=None)
    print(f"Table size: {df_regions.shape[0]} rows x {df_regions.shape[1]} cols")

    # Find regions
    regions_map = {}
    region_codes = ['БЕЛ', 'ВРН', 'ИРК', 'КЗ', 'МСК', 'ННВ', 'САМ', 'СИБ', 'СПБ', 'УРЛ', 'ЮГ']

    for row_idx in range(min(10, len(df_regions))):
        row = df_regions.iloc[row_idx]
        for col_idx, val in enumerate(row):
            if pd.notna(val) and str(val).strip() in region_codes:
                region_code = str(val).strip()
                if region_code not in regions_map:
                    regions_map[region_code] = col_idx
                    print(f"Found region {region_code} at col {col_idx}")

    print(f"Total regions found: {len(regions_map)}")

    # Find row with growth data - looking for "Всего сеть" or similar
    growth_row_idx = None
    for row_idx in range(min(30, len(df_regions))):
        first_col = str(df_regions.iloc[row_idx, 0]) if pd.notna(df_regions.iloc[row_idx, 0]) else ""
        if 'Всего сеть' in first_col or 'ВСЕГО СЕТЬ' in first_col:
            growth_row_idx = row_idx
            print(f"Growth data row found: {growth_row_idx} ('{first_col}')")
            break

    if growth_row_idx and regions_map:
        for region, col_idx in regions_map.items():
            # Get value from the row
            val = df_regions.iloc[growth_row_idx, col_idx]

            if pd.notna(val):
                try:
                    growth_num = float(val)
                    # Convert to percent if needed (value < 1 means decimal format)
                    if -1 < growth_num < 1:
                        growth_num = growth_num * 100

                    # Find shop count - usually a few rows below
                    shops_count = 0
                    for offset in range(2, 15):
                        if growth_row_idx + offset < len(df_regions):
                            shop_val = df_regions.iloc[growth_row_idx + offset, col_idx]
                            if pd.notna(shop_val):
                                try:
                                    shop_num = float(shop_val)
                                    # Shop count is typically 20-150
                                    if 15 < shop_num < 200 and shop_num == int(shop_num):
                                        shops_count = int(shop_num)
                                        break
                                except:
                                    pass

                    dashboard_data["regions"]["all_regions"].append({
                        "region": region,
                        "growth": round(growth_num, 1),
                        "shops": shops_count
                    })

                    print(f"  {region}: growth {round(growth_num, 1)}%, shops {shops_count}")

                except Exception as e:
                    print(f"  {region}: parse error - {e}")

    print(f"\nOK: Extracted {len(dashboard_data['regions']['all_regions'])} regions")

    # Find NNV divisions - search in first column
    print("\nSearching NNV divisions...")
    division_keywords = {
        'Ярослав': 'Ярославское',
        'Ижевск': 'Ижевское',
        'Север': 'ННВ Север',
        'Казань 1': 'Казань 1',
        'ННВ 1': 'ННВ 1',
        'Владимир': 'Владимир',
        'Челны': 'Наб.Челны'
    }

    found_divs = {}

    for row_idx in range(len(df_regions)):
        first_val = str(df_regions.iloc[row_idx, 0]) if pd.notna(df_regions.iloc[row_idx, 0]) else ""

        for keyword, full_name in division_keywords.items():
            if keyword in first_val and full_name not in found_divs:
                # Look for numeric value in nearby cells
                for col_offset in range(1, 5):
                    cell_val = df_regions.iloc[row_idx, col_offset]
                    if pd.notna(cell_val):
                        try:
                            growth = float(cell_val)
                            if -50 < growth < 200 and growth != 0:
                                if -1 < growth < 1:
                                    growth = growth * 100
                                found_divs[full_name] = round(growth, 1)
                                print(f"  {full_name}: {round(growth, 1)}%")
                                break
                        except:
                            pass
                break

    for div, growth in list(found_divs.items())[:7]:
        dashboard_data["regions"]["nnv_divisions"].append({"division": div, "growth": growth})

    print(f"\nOK: Found {len(dashboard_data['regions']['nnv_divisions'])} divisions")

    # Categories for NNV
    print("\nSearching product categories...")

    if 'ННВ' in regions_map:
        nnv_col = regions_map['ННВ']
        categories = []

        for row_idx in range(len(df_regions)):
            category = df_regions.iloc[row_idx, 0]
            nnv_value = df_regions.iloc[row_idx, nnv_col]

            if pd.notna(category) and pd.notna(nnv_value):
                cat_str = str(category).strip()
                if len(cat_str) > 3 and cat_str not in region_codes and 'ВСЕГО' not in cat_str.upper():
                    try:
                        growth = float(nnv_value)
                        if -100 < growth < 500:
                            if -1 < growth < 5:
                                growth = growth * 100
                            categories.append({"category": cat_str[:50], "growth": round(growth, 1)})
                    except:
                        pass

        if len(categories) > 10:
            categories_sorted = sorted(categories, key=lambda x: x['growth'], reverse=True)
            dashboard_data["regions"]["nnv_categories_top5"] = categories_sorted[:5]
            dashboard_data["regions"]["nnv_categories_worst5"] = categories_sorted[-5:][::-1]

            print(f"\nOK: Found {len(categories)} categories")
            print("TOP-5:")
            for cat in dashboard_data["regions"]["nnv_categories_top5"]:
                print(f"  {cat['category']}: +{cat['growth']}%")
            print("WORST-5:")
            for cat in dashboard_data["regions"]["nnv_categories_worst5"]:
                print(f"  {cat['category']}: {cat['growth']}%")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# ========== 2. ACCESSORIES ==========
print("\n" + "="*80)
print("[2/3] FILE: Accessories by shops.xlsx")
print("-"*80)

accessories_file = os.path.join(base_path, "Отчет по приросту аксессуаров по магазинам", "Рассылка аксессуары магазины.xlsx")

try:
    success = False
    for skip in [2, 3, 4, 1, 0]:
        try:
            df_acc = pd.read_excel(accessories_file, skiprows=skip)
            print(f"\nReading with skiprows={skip}")
            print(f"Size: {df_acc.shape[0]} rows x {df_acc.shape[1]} cols")

            region_col = shop_col = growth_col = None

            for col in df_acc.columns:
                col_str = str(col).lower()
                if not region_col and ('регион' in col_str or 'подразд' in col_str):
                    region_col = col
                if not shop_col and ('магазин' in col_str or 'пункт' in col_str or 'торговая' in col_str):
                    shop_col = col
                if not growth_col and ('неделе к' in col_str or 'пн-вс' in col_str):
                    growth_col = col

            print(f"Columns: region='{region_col}', shop='{shop_col}', growth='{growth_col}'")

            if shop_col and growth_col:
                if region_col:
                    df_nnv = df_acc[df_acc[region_col].astype(str).str.contains('ННВ|Нижн', case=False, na=False)].copy()
                else:
                    df_nnv = df_acc.copy()

                df_nnv[growth_col] = pd.to_numeric(df_nnv[growth_col], errors='coerce')
                df_nnv = df_nnv.dropna(subset=[growth_col])

                df_nnv_sorted = df_nnv.sort_values(by=growth_col, ascending=False)

                print(f"NNV shops found: {len(df_nnv_sorted)}")

                # TOP-10
                for _, row in df_nnv_sorted.head(10).iterrows():
                    g = float(row[growth_col])
                    if abs(g) < 5:
                        g = g * 100
                    shop = str(row[shop_col])[:30]
                    dashboard_data["accessories"]["nnv_top10"].append({"shop": shop, "growth": round(g, 1)})
                    print(f"  TOP: {shop} = +{round(g, 1)}%")

                # WORST-10
                for _, row in df_nnv_sorted.tail(10).iloc[::-1].iterrows():
                    g = float(row[growth_col])
                    if abs(g) < 5:
                        g = g * 100
                    shop = str(row[shop_col])[:30]
                    dashboard_data["accessories"]["nnv_worst10"].append({"shop": shop, "growth": round(g, 1)})
                    print(f"  WORST: {shop} = {round(g, 1)}%")

                print(f"\nOK: Extracted TOP-10 and WORST-10")
                success = True
                break

        except Exception as e:
            print(f"  Failed with skiprows={skip}: {e}")

    if not success:
        print("WARNING: Could not extract accessories data")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# ========== 3. TURNOVER ==========
print("\n" + "="*80)
print("[3/3] FILE: Turnover report.xlsx")
print("-"*80)

turnover_file = os.path.join(base_path, "Обувь остатки и оборачиваемость по группам товара", "Отчет по оборачиваемости ТЗ регион ННВ.xlsx")

try:
    success = False
    for skip in [2, 3, 4, 1, 0]:
        try:
            df_turn = pd.read_excel(turnover_file, skiprows=skip)
            print(f"\nReading with skiprows={skip}")
            print(f"Size: {df_turn.shape[0]} rows x {df_turn.shape[1]} cols")

            group_col = turnover_col = stock_col = None

            for col in df_turn.columns:
                col_str = str(col).lower()
                if not group_col and ('артикул' in col_str or 'группа' in col_str or 'товар' in col_str):
                    group_col = col
                if not turnover_col and ('оборач' in col_str):
                    turnover_col = col
                if not stock_col and ('остаток' in col_str):
                    stock_col = col

            print(f"Columns: group='{group_col}', turnover='{turnover_col}', stock='{stock_col}'")

            if turnover_col:
                df_turn[turnover_col] = pd.to_numeric(df_turn[turnover_col], errors='coerce')
                df_slow = df_turn[df_turn[turnover_col] > 10].copy()
                df_slow = df_slow.dropna(subset=[turnover_col])
                df_slow_sorted = df_slow.sort_values(by=turnover_col, ascending=False)

                print(f"Groups with turnover > 10 weeks: {len(df_slow_sorted)}")

                for _, row in df_slow_sorted.head(30).iterrows():
                    grp = str(row[group_col])[:80] if group_col and pd.notna(row[group_col]) else "No name"
                    turn = round(float(row[turnover_col]), 1)
                    stock = int(float(row[stock_col])) if stock_col and pd.notna(row[stock_col]) else 0

                    dashboard_data["turnover"]["slow_groups"].append({
                        "group": grp, "turnover_weeks": turn, "stock": stock
                    })

                print(f"\nOK: Extracted {len(dashboard_data['turnover']['slow_groups'])} slow groups")
                success = True
                break

        except Exception as e:
            print(f"  Failed with skiprows={skip}: {e}")

    if not success:
        print("WARNING: Could not extract turnover data")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# ========== SAVE ==========
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

output_file = "dashboard_data_real.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: {output_file}")
print(f"\nSTATS:")
print(f"  Regions: {len(dashboard_data['regions']['all_regions'])}")
print(f"  NNV divisions: {len(dashboard_data['regions']['nnv_divisions'])}")
print(f"  TOP categories: {len(dashboard_data['regions']['nnv_categories_top5'])}")
print(f"  WORST categories: {len(dashboard_data['regions']['nnv_categories_worst5'])}")
print(f"  TOP-10 shops: {len(dashboard_data['accessories']['nnv_top10'])}")
print(f"  WORST-10 shops: {len(dashboard_data['accessories']['nnv_worst10'])}")
print(f"  Slow groups: {len(dashboard_data['turnover']['slow_groups'])}")
print("="*80)
