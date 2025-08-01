#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы парсера выставок
"""

import logging
from exhibition_scraper import ExhibitionScraper
from advanced_scraper import AdvancedExhibitionScraper

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_scraper():
    """Тестирование базового парсера"""
    logger.info("=== Тестирование базового парсера ===")
    
    try:
        scraper = ExhibitionScraper()
        
        # Тестируем только одну выставку для экономии времени
        logger.info("Тестируем парсинг ELTEFA...")
        scraper.scrape_eltefa()
        
        logger.info(f"Найдено участников: {len(scraper.exhibitors_data)}")
        
        if scraper.exhibitors_data:
            logger.info("Примеры найденных участников:")
            for i, exhibitor in enumerate(scraper.exhibitors_data[:3]):
                logger.info(f"{i+1}. {exhibitor}")
        
        # Сохраняем результаты
        scraper.save_to_excel("test_basic_results.xlsx")
        logger.info("Базовый парсер протестирован успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка в базовом парсере: {e}")

def test_advanced_scraper():
    """Тестирование продвинутого парсера"""
    logger.info("=== Тестирование продвинутого парсера ===")
    
    try:
        scraper = AdvancedExhibitionScraper()
        
        # Тестируем только одну выставку
        logger.info("Тестируем продвинутый парсинг ELTEFA...")
        scraper.scrape_eltefa_advanced()
        
        logger.info(f"Найдено участников: {len(scraper.exhibitors_data)}")
        
        if scraper.exhibitors_data:
            logger.info("Примеры найденных участников:")
            for i, exhibitor in enumerate(scraper.exhibitors_data[:3]):
                logger.info(f"{i+1}. {exhibitor}")
        
        # Сохраняем результаты
        scraper.save_to_excel("test_advanced_results.xlsx")
        logger.info("Продвинутый парсер протестирован успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка в продвинутом парсере: {e}")

def test_contact_finder():
    """Тестирование поиска контактов"""
    logger.info("=== Тестирование поиска контактов ===")
    
    try:
        from contact_finder import ContactFinder
        
        finder = ContactFinder()
        
        # Тестируем поиск контактов для тестовой компании
        test_company = "Siemens"
        contacts = finder.find_contacts_for_company(test_company)
        
        logger.info(f"Найдено контактов для {test_company}: {len(contacts)}")
        
        if contacts:
            logger.info("Примеры найденных контактов:")
            for i, contact in enumerate(contacts[:3]):
                logger.info(f"{i+1}. {contact}")
        
        logger.info("Поиск контактов протестирован успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка в поиске контактов: {e}")

def main():
    """Основная функция тестирования"""
    logger.info("Начинаем тестирование парсера выставок...")
    
    # Тестируем базовый парсер
    test_basic_scraper()
    
    print("\n" + "="*50 + "\n")
    
    # Тестируем продвинутый парсер
    test_advanced_scraper()
    
    print("\n" + "="*50 + "\n")
    
    # Тестируем поиск контактов
    test_contact_finder()
    
    logger.info("Тестирование завершено!")

if __name__ == "__main__":
    main() 