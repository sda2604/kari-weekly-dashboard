@echo off
chcp 65001 > nul
echo ========================================
echo Git Синхронизация с GitHub
echo ========================================
echo.

cd /d "%~dp0"

:: Проверка наличия .git
if exist ".git" (
    echo [✓] Git уже инициализирован
) else (
    echo [!] Инициализация Git...
    git init
    if %errorlevel% neq 0 (
        echo [✗] ОШИБКА: Не удалось инициализировать Git
        pause
        exit /b 1
    )
    echo [✓] Git инициализирован
)

:: Добавление remote origin
echo.
echo [!] Проверка remote origin...
git remote -v | findstr "origin" > nul
if %errorlevel% neq 0 (
    echo [!] Добавление remote origin...
    git remote add origin https://github.com/sda2604/kari-weekly-dashboard.git
    if %errorlevel% neq 0 (
        echo [✗] ОШИБКА: Не удалось добавить remote
        pause
        exit /b 1
    )
    echo [✓] Remote origin добавлен
) else (
    echo [✓] Remote origin уже существует
    git remote -v
)

:: Получение последних изменений из GitHub
echo.
echo [!] Получение изменений из GitHub...
git fetch origin main
if %errorlevel% neq 0 (
    echo [!] ВНИМАНИЕ: Не удалось получить изменения (возможно нет доступа)
)

:: Создание новой ветки для IT-review
echo.
echo [!] Создание ветки feature/it-compliance...
git checkout -b feature/it-compliance 2>nul
if %errorlevel% neq 0 (
    echo [!] Ветка уже существует, переключаемся...
    git checkout feature/it-compliance
)
echo [✓] Находимся в ветке feature/it-compliance

:: Проверка статуса
echo.
echo [!] Текущий статус:
git status --short

:: Добавление всех изменений
echo.
echo [!] Добавление файлов в staging...
git add .
echo [✓] Файлы добавлены

:: Коммит
echo.
echo [!] Создание коммита...
git commit -m "feat: IT-Compliance refactoring (v2.2.0)

- Секреты перенесены в .env
- Структурированное JSON логирование
- Централизованный error handling
- Валидация входных данных
- Полные Google Style docstrings
- Retry механизм для Telegram API
- Graceful degradation
- CHANGELOG.md
- requirements.txt с зависимостями

Соответствие стандартам ИТ: 41%% → 90%%+"

if %errorlevel% neq 0 (
    echo [!] ВНИМАНИЕ: Нечего коммитить или ошибка
    git status
) else (
    echo [✓] Коммит создан
)

:: Push в GitHub
echo.
echo [!] Push в GitHub...
echo [!] Это может запросить авторизацию...
echo.
git push -u origin feature/it-compliance
if %errorlevel% neq 0 (
    echo.
    echo [✗] ОШИБКА: Не удалось выполнить push
    echo.
    echo Возможные причины:
    echo 1. Требуется авторизация (введите логин/пароль или токен)
    echo 2. Нет прав доступа к репозиторию
    echo 3. Проблемы с сетью
    echo.
    echo Попробуйте вручную:
    echo git push -u origin feature/it-compliance
    pause
    exit /b 1
)

echo.
echo ========================================
echo [✓] УСПЕШНО!
echo ========================================
echo.
echo Ветка feature/it-compliance создана и загружена в GitHub
echo.
echo Следующие шаги:
echo 1. Откройте GitHub: https://github.com/sda2604/kari-weekly-dashboard
echo 2. Создайте Pull Request из feature/it-compliance в main
echo 3. Проверьте изменения и подтвердите merge
echo.
pause
