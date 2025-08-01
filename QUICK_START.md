# 🚀 Быстрый старт - Парсер выставок

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск парсера

**Вариант 1: Интерактивный запуск**
```bash
python run_simple.py
```

**Вариант 2: Парсер только с requests (рекомендуется)**
```bash
python requests_only_scraper.py
```

**Вариант 3: Прямой запуск продвинутого парсера**
```bash
python advanced_scraper.py
```

**Вариант 4: Простой тест без Selenium**
```bash
python simple_test.py
```

## Решение проблем

### Проблема с ChromeDriver в Windows
Если получаете ошибку `[WinError 193] %1 не является приложением Win32`:

1. **Используйте парсер только с requests:**
   ```bash
   python requests_only_scraper.py
   ```
2. **Или выберите опцию 3 в интерактивном меню**
3. **Или установите Chrome браузер** (если не установлен)

### Проблема с кодировкой в Windows
Если получаете ошибку `UnicodeEncodeError: 'charmap' codec can't encode character`:

1. **Используйте `run_simple.py`** вместо `run.py`
2. **Или измените кодировку консоли:**
   ```cmd
   chcp 65001
   ```
3. **Или запустите в PowerShell** вместо cmd

### Проблема с пустым Excel файлом
Если получаете ошибку `At least one sheet must be visible`:
- Это означает, что парсер не смог найти данные на сайтах
- Попробуйте запустить простой тест: `python simple_test.py`

## Рекомендации

### Для Windows пользователей:
1. **Начните с `requests_only_scraper.py`** - он не требует ChromeDriver
2. **Если нужен полный функционал**, установите Chrome браузер
3. **Для тестирования** используйте `simple_test.py`

### Для Linux/Mac пользователей:
1. Любой из парсеров должен работать
2. При проблемах с ChromeDriver установите Chrome

## Альтернативные решения

### Если ChromeDriver не работает:
1. Запустите `python requests_only_scraper.py`
2. Установите Chrome браузер вручную
3. Скачайте ChromeDriver с https://chromedriver.chromium.org/

### Если сайты блокируют доступ:
1. Попробуйте позже (возможно, временная блокировка)
2. Используйте VPN
3. Запустите простой тест для проверки функционала

## Результат
После выполнения в папке появится файл `requests_exhibition_data.xlsx` с данными участников выставок. 