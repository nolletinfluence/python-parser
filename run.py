#!/usr/bin/env python3
"""
Простой скрипт для запуска парсера выставок
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
    print("🎪 EXHIBITION SCRAPER - Парсер выставок")
    print("=" * 60)
    print()
    print("Выберите режим работы:")
    print("1. Базовый парсер (быстрый)")
    print("2. Продвинутый парсер (детальный)")
    print("3. Только тестирование")
    print("4. Выход")
    print()
    
    while True:
        try:
            choice = input("Введите номер (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Запуск базового парсера...")
                scraper = ExhibitionScraper()
                scraper.run()
                print("✅ Базовый парсер завершен!")
                break
                
            elif choice == "2":
                print("\n🚀 Запуск продвинутого парсера...")
                scraper = AdvancedExhibitionScraper()
                scraper.run()
                print("✅ Продвинутый парсер завершен!")
                break
                
            elif choice == "3":
                print("\n🧪 Запуск тестирования...")
                from test_scraper import main as test_main
                test_main()
                break
                
            elif choice == "4":
                print("\n👋 До свидания!")
                sys.exit(0)
                
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Работа прервана пользователем.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("Попробуйте снова или выберите другой режим.")

if __name__ == "__main__":
    main() 