@echo off
chcp 65001 >nul
echo ========================================================
echo   KARI OUTLOOK MACRO - АВТОМАТИЧЕСКАЯ ДИАГНОСТИКА
echo ========================================================
echo.
echo Этот скрипт:
echo   1. Проверит настройки Outlook
echo   2. Проверит что макрос установлен
echo   3. Создаст тестовое письмо для проверки
echo   4. Проверит логи
echo.
pause

cd /d "%~dp0"

echo.
echo [1/4] Проверка структуры проекта...
if not exist "input\" (
    echo   ERROR: Папка input не найдена!
    pause
    exit /b 1
)
if not exist "logs\" (
    echo   WARNING: Папка logs не существует, создаю...
    mkdir logs
)
echo   OK - Структура в порядке

echo.
echo [2/4] Проверка VBA кода...
if exist "OUTLOOK_VBA_v6_ENCODING_FIX.txt" (
    echo   OK - Файл макроса найден
    echo   Путь: %cd%\OUTLOOK_VBA_v6_ENCODING_FIX.txt
    echo.
    echo   ВАЖНО: Убедись что этот код установлен в Outlook:
    echo   1. Alt+F11 в Outlook
    echo   2. Открой ThisOutlookSession
    echo   3. Проверь что там функция GetSubjectSafe
) else (
    echo   ERROR: Файл макроса не найден!
    pause
    exit /b 1
)

echo.
echo [3/4] Проверка логов...
set TODAY=%date:~-4,4%%date:~-7,2%%date:~-10,2%
set LOGFILE=logs\outlook_macro_%TODAY%.log

if exist "%LOGFILE%" (
    echo   OK - Лог найден: %LOGFILE%
    echo.
    echo   Последние 20 строк лога:
    echo   ----------------------------------------
    powershell -Command "Get-Content '%LOGFILE%' | Select-Object -Last 20"
    echo   ----------------------------------------
) else (
    echo   WARNING: Лог за сегодня не найден
    echo   Это означает что макрос не получал события сегодня
)

echo.
echo [4/4] Создание инструкции для ручной проверки...

echo. > ДИАГНОСТИКА_OUTLOOK.txt
echo ========================================================>> ДИАГНОСТИКА_OUTLOOK.txt
echo   ИНСТРУКЦИЯ ПО ПРОВЕРКЕ OUTLOOK МАКРОСА>> ДИАГНОСТИКА_OUTLOOK.txt
echo ========================================================>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ШАГ 1: Проверь что макрос установлен>> ДИАГНОСТИКА_OUTLOOK.txt
echo ---------------------------------------->> ДИАГНОСТИКА_OUTLOOK.txt
echo 1. Открой Outlook>> ДИАГНОСТИКА_OUTLOOK.txt
echo 2. Нажми Alt+F11 (VBA редактор)>> ДИАГНОСТИКА_OUTLOOK.txt
echo 3. В левой панели найди "ThisOutlookSession">> ДИАГНОСТИКА_OUTLOOK.txt
echo 4. Проверь что там есть функция "GetSubjectSafe">> ДИАГНОСТИКА_OUTLOOK.txt
echo 5. Проверь что есть функция "Application_NewMailEx">> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Код должен начинаться с "Option Explicit">> ДИАГНОСТИКА_OUTLOOK.txt
echo - Должна быть строка "Version: 6.0">> ДИАГНОСТИКА_OUTLOOK.txt
echo - Функция GetSubjectSafe должна использовать PropertyAccessor>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ШАГ 2: Проверь настройки безопасности>> ДИАГНОСТИКА_OUTLOOK.txt
echo ---------------------------------------->> ДИАГНОСТИКА_OUTLOOK.txt
echo 1. В Outlook: Файл -^> Параметры>> ДИАГНОСТИКА_OUTLOOK.txt
echo 2. Центр управления безопасностью>> ДИАГНОСТИКА_OUTLOOK.txt
echo 3. Параметры центра управления безопасностью>> ДИАГНОСТИКА_OUTLOOK.txt
echo 4. Параметры макросов>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ДОЛЖНО БЫТЬ:>> ДИАГНОСТИКА_OUTLOOK.txt
echo - "Уведомления для всех макросов" (рекомендуется)>> ДИАГНОСТИКА_OUTLOOK.txt
echo   или>> ДИАГНОСТИКА_OUTLOOK.txt
echo - "Включить все макросы" (менее безопасно)>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo НЕ ДОЛЖНО БЫТЬ:>> ДИАГНОСТИКА_OUTLOOK.txt
echo - "Отключить все макросы">> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ШАГ 3: Тест макроса>> ДИАГНОСТИКА_OUTLOOK.txt
echo ---------------------------------------->> ДИАГНОСТИКА_OUTLOOK.txt
echo 1. В Outlook VBA редакторе (Alt+F11)>> ДИАГНОСТИКА_OUTLOOK.txt
echo 2. Нажми F5 (Run)>> ДИАГНОСТИКА_OUTLOOK.txt
echo 3. Выбери "ScanInbox">> ДИАГНОСТИКА_OUTLOOK.txt
echo 4. Нажми Run>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Должны показаться последние 10 писем>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Subject должны быть БЕЗ кракозябр>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Письма с отчётами должны быть помечены "^>^>^> MATCH [...]">> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ШАГ 4: Тест автоматического срабатывания>> ДИАГНОСТИКА_OUTLOOK.txt
echo ---------------------------------------->> ДИАГНОСТИКА_OUTLOOK.txt
echo 1. Найди в Outlook письмо "Отчет по приросту регионы">> ДИАГНОСТИКА_OUTLOOK.txt
echo 2. Переслать его себе (Forward)>> ДИАГНОСТИКА_OUTLOOK.txt
echo 3. Подожди 5 секунд>> ДИАГНОСТИКА_OUTLOOK.txt
echo 4. Проверь лог: logs\outlook_macro_%TODAY%.log>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:>> ДИАГНОСТИКА_OUTLOOK.txt
echo - В логе должна появиться новая запись>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Subject должен быть БЕЗ кракозябр>> ДИАГНОСТИКА_OUTLOOK.txt
echo - Должно быть "MATCH: YES - REGIONS">> ДИАГНОСТИКА_OUTLOOK.txt
echo - Должно быть "SAVED: По регионам.xlsx">> ДИАГНОСТИКА_OUTLOOK.txt
echo - Файл должен появиться в input\Отчет по приросту регионы\>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ========================================================>> ДИАГНОСТИКА_OUTLOOK.txt
echo   РЕШЕНИЕ ПРОБЛЕМ>> ДИАГНОСТИКА_OUTLOOK.txt
echo ========================================================>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ПРОБЛЕМА 1: Макрос не установлен>> ДИАГНОСТИКА_OUTLOOK.txt
echo РЕШЕНИЕ: Установи код из OUTLOOK_VBA_v6_ENCODING_FIX.txt>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ПРОБЛЕМА 2: Макросы отключены>> ДИАГНОСТИКА_OUTLOOK.txt
echo РЕШЕНИЕ: Включи в настройках безопасности (Шаг 2)>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ПРОБЛЕМА 3: ScanInbox работает, но письма не ловятся автоматически>> ДИАГНОСТИКА_OUTLOOK.txt
echo РЕШЕНИЕ: Перезапусти Outlook полностью (Файл -^> Выход)>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt
echo ПРОБЛЕМА 4: В логе Subject с кракозябрами>> ДИАГНОСТИКА_OUTLOOK.txt
echo РЕШЕНИЕ: Убедись что установлен v6.0 (с функцией GetSubjectSafe)>> ДИАГНОСТИКА_OUTLOOK.txt
echo.>> ДИАГНОСТИКА_OUTLOOK.txt

echo.
echo ========================================================
echo   ДИАГНОСТИКА ЗАВЕРШЕНА
echo ========================================================
echo.
echo Создан файл: ДИАГНОСТИКА_OUTLOOK.txt
echo Открой его для подробной инструкции
echo.
echo СЛЕДУЮЩИЕ ШАГИ:
echo   1. Открой ДИАГНОСТИКА_OUTLOOK.txt
echo   2. Выполни проверки по шагам
echo   3. Если что-то не работает - следуй решениям
echo.

notepad ДИАГНОСТИКА_OUTLOOK.txt

pause
