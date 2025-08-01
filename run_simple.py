#!/usr/bin/env python3
"""
Простой скрипт для запуска парсера выставок (версия без эмодзи)
"""

import sys
import logging
from exhibition_scraper import ExhibitionScraper
from advanced_scraper import AdvancedExhibitionScraper

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска"""
    print("=" * 60)
    print("EXHIBITION SCRAPER - Парсер выставок")
    print("=" * 60)
    print()
    print("Выберите режим работы:")
    print("1. Базовый парсер (быстрый)")
    print("2. Продвинутый парсер (детальный)")
    print("3. Парсер только с requests (без Selenium)")
    print("4. Тестирование cookies")
    print("5. Только тестирование")
    print("6. Выход")
    print()
    
    while True:
        try:
            choice = input("Введите номер (1-6): ").strip()
            
            if choice == "1":
                print("\n[ЗАПУСК] Базовый парсер...")
                scraper = ExhibitionScraper()
                scraper.run()
                print("[ГОТОВО] Базовый парсер завершен!")
                break
                
            elif choice == "2":
                print("\n[ЗАПУСК] Продвинутый парсер...")
                scraper = AdvancedExhibitionScraper()
                scraper.run()
                print("[ГОТОВО] Продвинутый парсер завершен!")
                break
                
            elif choice == "3":
                print("\n[ЗАПУСК] Парсер только с requests...")
                from requests_only_scraper import RequestsOnlyScraper
                scraper = RequestsOnlyScraper()
                scraper.run()
                print("[ГОТОВО] Парсер с requests завершен!")
                break
                
            elif choice == "4":
                print("\n[ТЕСТ] Тестирование cookies...")
                from test_cookies import main as cookie_main
                cookie_main()
                break
                
            elif choice == "5":
                print("\n[ТЕСТ] Запуск тестирования...")
                from test_scraper import main as test_main
                test_main()
                break
                
            elif choice == "6":
                print("\n[ВЫХОД] До свидания!")
                sys.exit(0)
                
            else:
                print("[ОШИБКА] Неверный выбор. Попробуйте снова (1-6).")
                
        except KeyboardInterrupt:
            print("\n\n[ПРЕРВАНО] Работа прервана пользователем.")
            sys.exit(0)
        except Exception as e:
            print(f"\n[ОШИБКА] {e}")
            print("Попробуйте снова или выберите другой режим.")

if __name__ == "__main__":
    main() 