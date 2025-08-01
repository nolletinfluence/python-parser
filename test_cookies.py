#!/usr/bin/env python3
"""
Тестирование обработки cookies на немецких сайтах
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cookies(url, site_name):
    """Тестирование cookies для конкретного сайта"""
    ua = UserAgent()
    
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',  # Немецкий язык
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    
    print(f"\n{'='*60}")
    print(f"ТЕСТИРОВАНИЕ COOKIES: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # Создаем сессию
        session = requests.Session()
        session.headers.update(headers)
        
        # Первый запрос - получаем страницу и cookies
        print("\n1. Первый запрос (получение cookies)...")
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"   Статус: {response.status_code}")
        print(f"   Cookies получены: {len(session.cookies)}")
        for cookie in session.cookies:
            print(f"     {cookie.name}: {cookie.value}")
        
        # Анализируем страницу на наличие cookie banner
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n2. Поиск cookie banner...")
        
        # Ищем различные варианты cookie banner
        cookie_selectors = [
            '[id*="cookie"]',
            '[class*="cookie"]',
            '[id*="banner"]',
            '[class*="banner"]',
            '[id*="consent"]',
            '[class*="consent"]',
            'button[onclick*="cookie"]',
            'a[onclick*="cookie"]'
        ]
        
        cookie_elements = []
        for selector in cookie_selectors:
            elements = soup.select(selector)
            if elements:
                cookie_elements.extend(elements)
                print(f"   Найдены элементы с селектором '{selector}': {len(elements)}")
        
        # Ищем кнопки принятия cookies по тексту
        cookie_buttons = soup.find_all(['button', 'a'], string=re.compile(r'accept|akzeptieren|einverstanden|ok|zulassen|alle|all', re.I))
        
        if cookie_buttons:
            print(f"   Найдены кнопки cookies: {len(cookie_buttons)}")
            for i, button in enumerate(cookie_buttons[:3]):
                print(f"     Кнопка {i+1}: '{button.get_text(strip=True)}'")
        
        # Пытаемся принять cookies
        if cookie_elements or cookie_buttons:
            print("\n3. Попытка принятия cookies...")
            
            # Метод 1: POST запрос с данными формы
            forms = soup.find_all('form')
            for form in forms:
                form_action = form.get('action', '')
                if not form_action.startswith('http'):
                    form_action = url + form_action
                
                # Ищем скрытые поля
                hidden_inputs = form.find_all('input', type='hidden')
                form_data = {}
                for hidden in hidden_inputs:
                    form_data[hidden.get('name', '')] = hidden.get('value', '')
                
                # Добавляем данные для принятия cookies
                form_data.update({
                    'accept': '1',
                    'cookies': '1',
                    'consent': '1'
                })
                
                try:
                    print(f"   Отправка POST запроса на: {form_action}")
                    post_response = session.post(form_action, data=form_data, timeout=30)
                    print(f"   POST статус: {post_response.status_code}")
                    break
                except Exception as e:
                    print(f"   Ошибка POST: {e}")
                    continue
            
            # Метод 2: Простой GET запрос с параметрами
            try:
                print("   Отправка GET запроса с параметрами cookies...")
                cookie_url = url + "?cookies=1&accept=1"
                cookie_response = session.get(cookie_url, timeout=30)
                print(f"   GET статус: {cookie_response.status_code}")
            except Exception as e:
                print(f"   Ошибка GET: {e}")
        
        # Финальный запрос
        print("\n4. Финальный запрос...")
        final_response = session.get(url, timeout=30)
        final_response.raise_for_status()
        
        print(f"   Финальный статус: {final_response.status_code}")
        print(f"   Финальные cookies: {len(session.cookies)}")
        
        # Проверяем, есть ли контент
        final_soup = BeautifulSoup(final_response.text, 'html.parser')
        links = final_soup.find_all('a', href=True)
        print(f"   Найдено ссылок: {len(links)}")
        
        # Ищем ссылки на участников
        exhibitor_links = []
        for link in links:
            link_text = link.get_text(strip=True).lower()
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                exhibitor_links.append(link.get_text(strip=True))
        
        if exhibitor_links:
            print(f"   Найдены ссылки на участников: {len(exhibitor_links)}")
            for link in exhibitor_links[:5]:
                print(f"     - {link}")
        else:
            print("   Ссылки на участников не найдены")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании {url}: {e}")
        return False

def main():
    """Основная функция"""
    print("ТЕСТИРОВАНИЕ ОБРАБОТКИ COOKIES НА НЕМЕЦКИХ САЙТАХ")
    print("="*80)
    
    # Тестируем оба сайта
    sites = [
        ("https://www.messe-stuttgart.de/eltefa/", "ELTEFA"),
        ("https://www.ihm.de/de/home", "IHM")
    ]
    
    for url, name in sites:
        test_cookies(url, name)
    
    print(f"\n{'='*80}")
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 