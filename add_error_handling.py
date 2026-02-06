"""
Скрипт для добавления error handling в generate_dashboard.py
"""

from pathlib import Path

file_path = Path(__file__).parent / 'generate_dashboard.py'

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем импорт error_handler после logging_config
old_import = """# Импорт логирования
from logging_config import setup_logging"""

new_import = """# Импорт логирования и обработки ошибок
from logging_config import setup_logging
from error_handler import (
    ErrorContext,
    safe_execute,
    validate_file_exists,
    validate_dataframe,
    DataExtractionError,
    handle_error
)"""

content = content.replace(old_import, new_import)

# Оборачиваем extract_regions_data в try/except
old_extract_regions = """def extract_regions_data():
    \"\"\"Извлечение данных по регионам\"\"\"
    log("Извлекаю данные по регионам...")

    file_path = find_excel_file("По регионам", INPUT_DIR / "Отчет по приросту регионы")
    if not file_path:
        file_path = find_excel_file("регион")

    if not file_path or not file_path.exists():
        log("  ВНИМАНИЕ: Файл регионов не найден")
        return None

    log(f"  Файл: {file_path.name}")

    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)"""

new_extract_regions = """def extract_regions_data():
    \"\"\"
    Извлечение данных по регионам из Excel файла
    
    Returns:
        dict: Словарь с данными или None при ошибке
        
    Raises:
        DataExtractionError: При критичных ошибках чтения
    \"\"\"
    logger.info("Извлечение данных по регионам")
    
    with ErrorContext("Поиск файла регионов", critical=False):
        file_path = find_excel_file("По регионам", INPUT_DIR / "Отчет по приросту регионы")
        if not file_path:
            file_path = find_excel_file("регион")
        
        if not validate_file_exists(file_path, "Файл регионов"):
            logger.warning("Продолжаем без данных по регионам")
            return None
        
        logger.info(f"Файл найден", extra={'extra_data': {'filename': file_path.name}})
    
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)"""

content = content.replace(old_extract_regions, new_extract_regions)

# Оборачиваем extract_turnover_data
old_extract_turnover = """def extract_turnover_data():
    \"\"\"Извлечение данных оборачиваемости\"\"\"
    log("Извлекаю данные оборачиваемости...")

    file_path = find_excel_file("оборачиваемост", INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара")
    if not file_path:
        file_path = find_excel_file("оборач")

    if not file_path or not file_path.exists():
        log("  ВНИМАНИЕ: Файл оборачиваемости не найден")
        return None

    log(f"  Файл: {file_path.name}")

    try:"""

new_extract_turnover = """def extract_turnover_data():
    \"\"\"
    Извлечение данных оборачиваемости из Excel файла
    
    Returns:
        dict: Словарь с данными или None при ошибке
    \"\"\"
    logger.info("Извлечение данных оборачиваемости")
    
    with ErrorContext("Поиск файла оборачиваемости", critical=False):
        file_path = find_excel_file("оборачиваемост", INPUT_DIR / "Обувь остатки и оборачиваемость по группам товара")
        if not file_path:
            file_path = find_excel_file("оборач")
        
        if not validate_file_exists(file_path, "Файл оборачиваемости"):
            logger.warning("Продолжаем без данных оборачиваемости")
            return None
        
        logger.info(f"Файл найден", extra={'extra_data': {'filename': file_path.name}})
    
    try:"""

content = content.replace(old_extract_turnover, new_extract_turnover)

# Оборачиваем main() в try/except
old_main = """def main():
    \"\"\"Главная функция\"\"\"
    print("=" * 60)
    print("  KARI DASHBOARD GENERATOR v2.0")
    print("  Улучшенный дашборд с новой терминологией")
    print("=" * 60)
    print()

    # Извлечение данных
    regions = extract_regions_data()
    turnover = extract_turnover_data()
    accessories = extract_accessories_data()
    structure = extract_structure_data()

    # Анализ
    analysis = analyze_data(regions, turnover, accessories, structure)

    # Генерация HTML
    html = generate_html(analysis)

    # Сохранение
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "dashboard_current.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    log(f"Дашборд сохранён: {output_file}")
    log(f"Размер: {output_file.stat().st_size / 1024:.1f} KB")
    log(f"Строк HTML: {len(html.splitlines())}")

    # Сохраняем также JSON с данными
    json_file = OUTPUT_DIR / "dashboard_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        analysis_json = {k: v for k, v in analysis.items()}
        json.dump(analysis_json, f, ensure_ascii=False, indent=2, default=str)

    log(f"Данные сохранены: {json_file}")

    print()
    print("=" * 60)
    print("  ГОТОВО!")
    print(f"  Дашборд: {output_file}")
    print(f"  Период: {analysis['period']}")
    print("=" * 60)

    return output_file"""

new_main = """def main():
    \"\"\"
    Главная функция генерации дашборда
    
    Returns:
        Path: Путь к созданному дашборду или None при ошибке
    \"\"\"
    logger.info("=" * 60)
    logger.info("СТАРТ ГЕНЕРАЦИИ ДАШБОРДА KARI v2.0")
    logger.info("=" * 60)
    
    try:
        # Извлечение данных (с graceful degradation)
        with ErrorContext("Извлечение данных из Excel", critical=False):
            regions = extract_regions_data()
            turnover = extract_turnover_data()
            accessories = extract_accessories_data()
            structure = extract_structure_data()
            
            # Проверяем что хотя бы один источник данных доступен
            available_sources = sum([
                regions is not None,
                turnover is not None,
                accessories is not None,
                structure is not None
            ])
            
            logger.info(f"Доступно источников данных: {available_sources}/4")
            
            if available_sources == 0:
                logger.error("Нет доступных источников данных!")
                logger.error("Проверь наличие Excel файлов в директории input/")
                return None
        
        # Анализ данных
        with ErrorContext("Анализ данных", critical=True):
            analysis = analyze_data(regions, turnover, accessories, structure)
        
        # Генерация HTML
        with ErrorContext("Генерация HTML", critical=True):
            html = generate_html(analysis)
        
        # Сохранение
        with ErrorContext("Сохранение файлов", critical=True):
            OUTPUT_DIR.mkdir(exist_ok=True)
            output_file = OUTPUT_DIR / "dashboard_current.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(
                "Дашборд сохранён",
                extra={'extra_data': {
                    'file': str(output_file),
                    'size_kb': round(output_file.stat().st_size / 1024, 1),
                    'lines': len(html.splitlines())
                }}
            )
            
            # Сохраняем также JSON с данными
            json_file = OUTPUT_DIR / "dashboard_data.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                analysis_json = {k: v for k, v in analysis.items()}
                json.dump(analysis_json, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Данные сохранены", extra={'extra_data': {'file': str(json_file)}})
        
        logger.info("=" * 60)
        logger.info("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        logger.info(f"Дашборд: {output_file}")
        logger.info(f"Период: {analysis['period']}")
        logger.info("=" * 60)
        
        return output_file
        
    except Exception as e:
        logger.error(
            "КРИТИЧЕСКАЯ ОШИБКА при генерации дашборда",
            exc_info=True
        )
        return None"""

content = content.replace(old_main, new_main)

# Добавляем обработку в if __name__ == "__main__"
old_name_main = """if __name__ == "__main__":
    main()"""

new_name_main = """if __name__ == "__main__":
    try:
        result = main()
        if result is None:
            logger.error("Генерация дашборда завершилась с ошибкой")
            sys.exit(1)
        else:
            sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("Генерация прервана пользователем")
        sys.exit(130)
    except Exception as e:
        logger.error("Неожиданная ошибка", exc_info=True)
        sys.exit(1)"""

content = content.replace(old_name_main, new_name_main)

# Сохраняем
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ generate_dashboard.py обновлён с error handling!")
print("✅ Добавлен импорт error_handler")
print("✅ Обновлены функции extract_*")
print("✅ Добавлена обработка ошибок в main()")
print("✅ Graceful degradation для отсутствующих файлов")
