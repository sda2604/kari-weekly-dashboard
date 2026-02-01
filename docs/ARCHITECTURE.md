# Архитектура системы KARI Weekly Dashboard

## Схема потока данных

```
[Корпоративная почта reports@kari.com]
   │  Каждый понедельник утром отправляет 5-6 писем с отчётами
   │  Из них 3 — целевые для нашей системы
   │
   ▼
[Outlook VBA макрос v5.0]
   │  Событие: Application_NewMailEx (срабатывает на каждое входящее)
   │  Фильтр: CyrInStr (vbTextCompare — кириллико-безопасный)
   │  Критерии:
   │    1. Тема содержит "оборачиваемость" + "группам товара" → TURNOVER
   │    2. Тема содержит "приросту" + "регион" (без "аксессуар") → REGIONS  
   │    3. Тема содержит "приросту" + "аксессуар" + "магазин" → ACCESSORIES
   │  Действие: сохраняет .xlsx/.pdf вложения в input/{подпапка}/
   │  Логирование: logs/outlook_macro_YYYYMMDD.log
   │
   ▼
[input/] — 3 подпапки с Excel файлами
   ├── Отчет по приросту регионы/По регионам.xlsx
   ├── Отчет по приросту аксессуаров по магазинам/Рассылка аксессуары магазины.xlsx
   └── Обувь остатки и оборачиваемость по группам товара/Отчет по оборачиваемости ТЗ регион ННВ.xlsx
   │
   ▼
[Windows Task Scheduler]
   │  Задача: KARI_Weekly_Report
   │  Триггер: каждый понедельник в 20:00 МСК
   │  Действие: запуск run_full_pipeline.bat
   │
   ▼
[run_full_pipeline.bat]
   │
   ├─ Шаг 1: python generate_dashboard.py
   │    │  Читает Excel через pandas + openpyxl
   │    │  Извлекает:
   │    │    - Регионы: доли, рост, позиция ННВ
   │    │    - Оборачиваемость: КОП, недели, неликвиды
   │    │    - Аксессуары: по 119 магазинам
   │    │    - Структура: подразделения, кол-во магазинов
   │    │  Анализирует:
   │    │    - Ключевые категории (доля >3%)
   │    │    - Рост + дефицит (рост >50%, КОП <1.0)
   │    │    - Неликвиды (оборачиваемость >50 недель)
   │    │    - Дисбалансы между подразделениями
   │    │  Генерирует: output/dashboard_current.html (~34 KB)
   │    │  + output/dashboard_data.json
   │    │
   │    ▼
   │  [output/dashboard_current.html]
   │    Мобильный HTML дашборд
   │    Inline CSS/JS (один файл)
   │    Адаптивный: iPhone, Android, Desktop
   │    Без Chart.js (не работает в Telegram iOS)
   │
   └─ Шаг 2: cd telegram_bot && python send_dashboard.py
        │  Парсит период из Excel (period_parser.py)
        │  Формирует сообщение с периодом
        │  Отправляет HTML файл в Telegram группу
        │
        ▼
      [Telegram группа ННВ]
        Директора подразделений (7 чел) + РД
        Читают дашборд с телефонов за 5-10 мин
```

## Компоненты системы

### 1. Outlook VBA макрос (macro_v5.txt)
- **Событие:** `Application_NewMailEx`
- **Ключевая функция:** `CyrInStr()` — обёртка над `InStr(1, source, search, vbTextCompare)`
- **Проблема v4.0:** `LCase()` не конвертирует кириллицу в VBA → фильтр не работал
- **Решение v5.0:** `vbTextCompare` делает регистронезависимое сравнение без `LCase`
- **Утилиты:** `TestMacro()`, `ScanInbox()` — диагностика из VBA редактора

### 2. generate_dashboard.py
- **Версия:** 2.1
- **Зависимости:** pandas, openpyxl, json, pathlib
- **Функции:**
  - `extract_regions_data()` — парсинг По регионам.xlsx
  - `extract_turnover_data()` — парсинг оборачиваемости
  - `extract_accessories_data()` — парсинг аксессуаров
  - `analyze_data()` — бизнес-логика анализа
  - `generate_html()` — рендеринг HTML

### 3. Telegram Bot
- **send_dashboard.py** — async отправка через python-telegram-bot
- **period_parser.py** — извлечение периода из Excel содержимого
- **config.py** — токен, chat_id (не в репо!)

### 4. Test Suite
- **test_full_pipeline.py** — E2E тест: файлы → генерация → Telegram
- Цветной вывод в консоли
- Проверка актуальности файлов (не старше 7 дней)

## Ограничения и совместимость

### Telegram iOS (целевая платформа)
- ❌ Chart.js, Plotly, D3.js — не рендерятся
- ❌ Canvas элементы
- ❌ ES6 (const/let, arrow functions) — старый Safari
- ✅ HTML таблицы с цветными ячейками
- ✅ Flexbox layout
- ✅ Inline CSS/JS
- ✅ Размер <50 KB

### Кодировка
- VBA: UTF-8 логи, CyrInStr для кириллицы
- Python: utf-8 encoding, Windows stdout wrapper
- BAT: chcp 65001 для UTF-8 консоли
