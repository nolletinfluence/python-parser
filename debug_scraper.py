#!/usr/bin/env python3
"""
Отладочный скрипт для анализа структуры страниц
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_page(url):
    """Анализ структуры страницы"""
    ua = UserAgent()
    
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"\n{'='*80}")
        print(f"АНАЛИЗ СТРАНИЦЫ: {url}")
        print(f"{'='*80}")
        
        # 1. Ищем ссылки на участников
        print("\n1. ПОИСК ССЫЛОК НА УЧАСТНИКОВ:")
        links = soup.find_all('a', href=True)
        exhibitor_links = []
        
        for link in links:
            link_text = link.get_text(strip=True).lower()
            link_href = link.get('href', '').lower()
            
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer', 'teilnehmen']):
                exhibitor_links.append({
                    'text': link.get_text(strip=True),
                    'href': link['href']
                })
                print(f"  Найдена ссылка: '{link.get_text(strip=True)}' -> {link['href']}")
        
        if not exhibitor_links:
            print("  Ссылки на участников не найдены")
        
        # 2. Анализируем структуру страницы
        print("\n2. СТРУКТУРА СТРАНИЦЫ:")
        print(f"  Всего ссылок: {len(links)}")
        print(f"  Всего div элементов: {len(soup.find_all('div'))}")
        print(f"  Всего h1-h6 элементов: {len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))}")
        
        # 3. Ищем потенциальные блоки участников
        print("\n3. ПОТЕНЦИАЛЬНЫЕ БЛОКИ УЧАСТНИКОВ:")
        
        # По классам
        specific_selectors = [
            '.exhibitor-item', '.aussteller-item', '.company-item',
            '.exhibitor-card', '.aussteller-card', '.exhibitor-list-item',
            '.aussteller-list-item', '[data-exhibitor]', '[data-aussteller]',
            '.exhibitor', '.aussteller'
        ]
        
        for selector in specific_selectors:
            blocks = soup.select(selector)
            if blocks:
                print(f"  Селектор '{selector}': найдено {len(blocks)} блоков")
                for i, block in enumerate(blocks[:3]):  # Показываем первые 3
                    text = block.get_text(strip=True)[:100]
                    print(f"    Блок {i+1}: {text}...")
        
        # 4. Ищем блоки с заголовками и ссылками
        print("\n4. БЛОКИ С ЗАГОЛОВКАМИ И ССЫЛКАМИ:")
        all_divs = soup.find_all('div')
        candidate_blocks = []
        
        for div in all_divs:
            has_title = div.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            has_link = div.find('a', href=True)
            has_text = div.get_text(strip=True)
            
            if (has_title and has_link and 
                len(has_text) > 10 and len(has_text) < 500 and
                not any(skip_word in has_text.lower() for skip_word in 
                       ['exhibition management', 'navigation', 'menu', 'footer', 'header', 'cookie'])):
                candidate_blocks.append(div)
        
        print(f"  Найдено {len(candidate_blocks)} потенциальных блоков")
        
        for i, block in enumerate(candidate_blocks[:5]):  # Показываем первые 5
            title = block.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
            title_text = title.get_text(strip=True) if title else "Нет заголовка"
            text = block.get_text(strip=True)[:100]
            print(f"    Блок {i+1}: '{title_text}' -> {text}...")
        
        # 5. Показываем все заголовки
        print("\n5. ВСЕ ЗАГОЛОВКИ НА СТРАНИЦЕ:")
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for i, header in enumerate(headers[:10]):  # Показываем первые 10
            print(f"  {header.name}: {header.get_text(strip=True)}")
        
        return exhibitor_links
        
    except Exception as e:
        logger.error(f"Ошибка при анализе {url}: {e}")
        return []

def main():
    """Основная функция"""
    print("ОТЛАДОЧНЫЙ АНАЛИЗ СТРАНИЦ ВЫСТАВОК")
    print("="*80)
    
    # Анализируем основные страницы
    urls = [
        "https://www.messe-stuttgart.de/eltefa/?hl=de-DE",
        "https://www.ihm.de/en/home?hl=de-DE"
    ]
    
    for url in urls:
        analyze_page(url)
    
    print(f"\n{'='*80}")
    print("АНАЛИЗ ЗАВЕРШЕН")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 