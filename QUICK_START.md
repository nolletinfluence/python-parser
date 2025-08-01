# 🚀 Быстрый старт - Парсер выставок

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск парсера

**Вариант 1: Интерактивный запуск**
```bash
python run.py
```

**Вариант 2: Прямой запуск продвинутого парсера**
```bash
python advanced_scraper.py
```

**Вариант 3: Если проблемы с кодировкой в Windows**
```bash
python run_simple.py
```

## Решение проблем

### Проблема с кодировкой в Windows
Если получаете ошибку `UnicodeEncodeError: 'charmap' codec can't encode character`:

1. **Используйте `run_simple.py`** вместо `run.py`
2. **Или измените кодировку консоли:**
   ```cmd
   chcp 65001
   ```
3. **Или запустите в PowerShell** вместо cmd

### Проблема с Chrome WebDriver
Если Selenium не может найти Chrome:
```bash
pip install --upgrade webdriver-manager
```

## Результат
После выполнения в папке появится файл `advanced_exhibition_data.xlsx` с данными участников выставок. 