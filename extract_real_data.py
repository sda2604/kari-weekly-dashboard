import pandas as pd
import json
import os

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
    }
}

# ========== 1. ДАННЫЕ ПО РЕГИОНАМ ==========
print("[1/3] Читаю данные по регионам...")
regions_file = os.path.join(base_path, "Отчет по приросту регионы", "По регионам.xlsx")

try:
    # Читаем все листы файла
    xls = pd.ExcelFile(regions_file)
    print(f"Листы в файле: {xls.sheet_names}")

    # Пробуем найти данные на первом листе
    df_regions = pd.read_excel(regions_file, sheet_name=0)
    print(f"\nПервый лист - форма данных: {df_regions.shape}")
    print(f"Колонки: {list(df_regions.columns)}")
    print("\nПервые 20 строк:")
    print(df_regions.head(20))

    # Ищем регионы (БЕЛ, ВРН, ИРК, КЗ, МСК, ННВ, САМ, СИБ, СПБ, УРЛ, ЮГ)
    regions_codes = ['БЕЛ', 'ВРН', 'ИРК', 'КЗ', 'МСК', 'ННВ', 'САМ', 'СИБ', 'СПБ', 'УРЛ', 'ЮГ']

    # Пробуем разные варианты структуры
    for col_name in df_regions.columns:
        col_values = df_regions[col_name].astype(str).tolist()
        for region in regions_codes:
            if region in col_values:
                print(f"\nНашёл регион {region} в колонке '{col_name}'")
                break

    # Сохраняем сырые данные для анализа
    with open('regions_raw_data.txt', 'w', encoding='utf-8') as f:
        f.write("=== СТРУКТУРА ФАЙЛА ПО РЕГИОНАМ ===\n")
        f.write(f"Листы: {xls.sheet_names}\n\n")
        f.write(f"Форма данных: {df_regions.shape}\n")
        f.write(f"Колонки: {list(df_regions.columns)}\n\n")
        f.write("=== ПЕРВЫЕ 30 СТРОК ===\n")
        f.write(df_regions.head(30).to_string())

except Exception as e:
    print(f"ERROR при чтении регионов: {e}")

# ========== 2. ДАННЫЕ ПО АКСЕССУАРАМ ==========
print("\n[2/3] Читаю данные по аксессуарам...")
accessories_file = os.path.join(base_path, "Отчет по приросту аксессуаров по магазинам", "Рассылка аксессуары магазины.xlsx")

try:
    xls_acc = pd.ExcelFile(accessories_file)
    print(f"Листы в файле: {xls_acc.sheet_names}")

    df_accessories = pd.read_excel(accessories_file, sheet_name=0)
    print(f"\nПервый лист - форма данных: {df_accessories.shape}")
    print(f"Колонки: {list(df_accessories.columns)}")
    print("\nПервые 20 строк:")
    print(df_accessories.head(20))

    # Сохраняем сырые данные
    with open('accessories_raw_data.txt', 'w', encoding='utf-8') as f:
        f.write("=== СТРУКТУРА ФАЙЛА ПО АКСЕССУАРАМ ===\n")
        f.write(f"Листы: {xls_acc.sheet_names}\n\n")
        f.write(f"Форма данных: {df_accessories.shape}\n")
        f.write(f"Колонки: {list(df_accessories.columns)}\n\n")
        f.write("=== ПЕРВЫЕ 50 СТРОК ===\n")
        f.write(df_accessories.head(50).to_string())

except Exception as e:
    print(f"ERROR при чтении аксессуаров: {e}")

# ========== 3. ДАННЫЕ ПО ОБОРАЧИВАЕМОСТИ ==========
print("\n[3/3] Читаю данные по оборачиваемости...")
turnover_file = os.path.join(base_path, "Обувь остатки и оборачиваемость по группам товара", "Отчет по оборачиваемости ТЗ регион ННВ.xlsx")

try:
    xls_turn = pd.ExcelFile(turnover_file)
    print(f"Листы в файле: {xls_turn.sheet_names}")

    df_turnover = pd.read_excel(turnover_file, sheet_name=0)
    print(f"\nПервый лист - форма данных: {df_turnover.shape}")
    print(f"Колонки: {list(df_turnover.columns)}")
    print("\nПервые 20 строк:")
    print(df_turnover.head(20))

    # Сохраняем сырые данные
    with open('turnover_raw_data.txt', 'w', encoding='utf-8') as f:
        f.write("=== СТРУКТУРА ФАЙЛА ПО ОБОРАЧИВАЕМОСТИ ===\n")
        f.write(f"Листы: {xls_turn.sheet_names}\n\n")
        f.write(f"Форма данных: {df_turnover.shape}\n")
        f.write(f"Колонки: {list(df_turnover.columns)}\n\n")
        f.write("=== ПЕРВЫЕ 50 СТРОК ===\n")
        f.write(df_turnover.head(50).to_string())

except Exception as e:
    print(f"ERROR при чтении оборачиваемости: {e}")

print("\n=== ГОТОВО ===")
print("Сырые данные сохранены в файлы:")
print("   - regions_raw_data.txt")
print("   - accessories_raw_data.txt")
print("   - turnover_raw_data.txt")
print("\nПроанализирую структуру и извлеку нужные данные.")
