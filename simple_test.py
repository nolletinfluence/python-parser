#!/usr/bin/env python3
"""
Простой тест парсера без Selenium
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_simple_parsing():
    """Простой тест парсинга без Selenium"""
    ua = UserAgent()
    exhibitors_data = []
    
    # Тестовые URL
    test_urls = [
        "https://www.messe-stuttgart.de/eltefa/?hl=de-DE",
        "https://www.ihm.de/en/home?hl=de-DE"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"Тестируем URL: {url}")
            
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем любые ссылки
            links = soup.find_all('a', href=True)
            logger.info(f"Найдено {len(links)} ссылок на странице")
            
            # Ищем потенциальные ссылки на участников
            exhibitor_links = []
            for link in links:
                text = link.get_text(strip=True).lower()
                if any(keyword in text for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                    exhibitor_links.append({
                        'text': link.get_text(strip=True),
                        'href': link['href']
                    })
            
            logger.info(f"Найдено {len(exhibitor_links)} потенциальных ссылок на участников")
            
            # Добавляем тестовые данные
            exhibitors_data.append({
                'Name': f'Test Company from {url.split("/")[2]}',
                'City': 'Test City',
                'Country': 'Germany',
                'Website': url,
                'Email': 'test@example.com'
            })
            
        except Exception as e:
            logger.error(f"Ошибка при тестировании {url}: {e}")
    
    # Сохраняем тестовые данные
    if exhibitors_data:
        df = pd.DataFrame(exhibitors_data)
        filename = "test_data.xlsx"
        df.to_excel(filename, index=False)
        logger.info(f"Тестовые данные сохранены в {filename}")
        return True
    else:
        logger.warning("Нет данных для сохранения")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ПРОСТОЙ ТЕСТ ПАРСЕРА")
    print("=" * 60)
    
    success = test_simple_parsing()
    
    if success:
        print("\n[УСПЕХ] Тест завершен успешно!")
        print("Проверьте файл test_data.xlsx")
    else:
        print("\n[ОШИБКА] Тест не прошел") 