import requests
import pandas as pd
import time
import re
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import logging
from contact_finder import ContactFinder

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedExhibitionScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.exhibitors_data = []
        self.contacts_data = []
        self.contact_finder = ContactFinder()
        
    def setup_driver(self):
        """Настройка веб-драйвера"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        try:
            # Попытка использовать webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"Ошибка с webdriver-manager: {e}")
            try:
                # Попытка найти ChromeDriver в PATH
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                logger.error(f"Не удалось запустить ChromeDriver: {e2}")
                raise Exception("ChromeDriver не найден. Установите Chrome браузер и ChromeDriver.")
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def get_page_content(self, url, use_selenium=False, wait_time=5):
        """Получение содержимого страницы"""
        try:
            if use_selenium:
                driver = self.setup_driver()
                driver.get(url)
                time.sleep(wait_time)
                
                # Прокручиваем страницу для загрузки динамического контента
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                content = driver.page_source
                driver.quit()
                return content
            else:
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def scrape_eltefa_advanced(self):
        """Продвинутый парсинг выставки ELTEFA"""
        logger.info("Начинаем продвинутый парсинг ELTEFA...")
        
        # Основная страница
        main_url = "https://www.messe-stuttgart.de/eltefa/?hl=de-DE"
        content = self.get_page_content(main_url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем различные варианты ссылок на участников
        exhibitor_urls = []
        
        # Поиск по тексту ссылок
        links = soup.find_all('a', href=True)
        for link in links:
            link_text = link.get_text(strip=True).lower()
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer', 'teilnehmen']):
                href = link['href']
                if not href.startswith('http'):
                    href = f"https://www.messe-stuttgart.de{href}"
                exhibitor_urls.append(href)
        
        # Поиск по URL
        for link in links:
            href = link['href'].lower()
            if any(keyword in href for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                if not link['href'].startswith('http'):
                    full_url = f"https://www.messe-stuttgart.de{link['href']}"
                else:
                    full_url = link['href']
                if full_url not in exhibitor_urls:
                    exhibitor_urls.append(full_url)
        
        # Если не нашли прямых ссылок, пробуем стандартные пути
        if not exhibitor_urls:
            standard_paths = [
                "/eltefa/aussteller/",
                "/eltefa/exhibitors/",
                "/eltefa/teilnehmer/",
                "/aussteller/",
                "/exhibitors/"
            ]
            for path in standard_paths:
                test_url = f"https://www.messe-stuttgart.de{path}"
                exhibitor_urls.append(test_url)
        
        # Парсим каждую найденную страницу
        for url in exhibitor_urls[:3]:  # Ограничиваем количество для демонстрации
            logger.info(f"Парсим страницу: {url}")
            self.scrape_eltefa_exhibitors_page(url)
    
    def scrape_eltefa_exhibitors_page(self, url):
        """Парсинг страницы участников ELTEFA"""
        content = self.get_page_content(url, use_selenium=True, wait_time=8)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Различные селекторы для поиска участников
        exhibitor_selectors = [
            '.exhibitor-item',
            '.aussteller-item',
            '.company-item',
            '.exhibitor-card',
            '.aussteller-card',
            '[data-exhibitor]',
            '[class*="exhibitor"]',
            '[class*="aussteller"]',
            '[class*="company"]',
            'article',
            '.card',
            '.item'
        ]
        
        exhibitor_blocks = []
        for selector in exhibitor_selectors:
            blocks = soup.select(selector)
            if blocks:
                exhibitor_blocks.extend(blocks)
                logger.info(f"Найдено {len(blocks)} блоков с селектором: {selector}")
        
        # Если не нашли по селекторам, ищем по структуре
        if not exhibitor_blocks:
            # Ищем повторяющиеся блоки
            all_divs = soup.find_all('div')
            for div in all_divs:
                if div.find('h1') or div.find('h2') or div.find('h3'):
                    if div.find('a') or div.find('p'):
                        exhibitor_blocks.append(div)
        
        # Ограничиваем количество для демонстрации
        exhibitor_blocks = exhibitor_blocks[:20]
        
        for block in exhibitor_blocks:
            try:
                exhibitor_data = self.extract_exhibitor_data(block)
                if exhibitor_data and exhibitor_data['Name']:
                    self.exhibitors_data.append(exhibitor_data)
                    logger.info(f"Добавлен участник: {exhibitor_data['Name']}")
                    
            except Exception as e:
                logger.error(f"Ошибка при парсинге участника: {e}")
    
    def scrape_ihm_advanced(self):
        """Продвинутый парсинг выставки IHM"""
        logger.info("Начинаем продвинутый парсинг IHM...")
        
        # Основная страница
        main_url = "https://www.ihm.de/en/home?hl=de-DE"
        content = self.get_page_content(main_url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем ссылки на участников
        exhibitor_urls = []
        
        links = soup.find_all('a', href=True)
        for link in links:
            link_text = link.get_text(strip=True).lower()
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                href = link['href']
                if not href.startswith('http'):
                    href = f"https://www.ihm.de{href}"
                exhibitor_urls.append(href)
        
        # Стандартные пути для IHM
        if not exhibitor_urls:
            standard_paths = [
                "/aussteller/",
                "/exhibitors/",
                "/teilnehmer/",
                "/en/exhibitors/",
                "/de/aussteller/"
            ]
            for path in standard_paths:
                test_url = f"https://www.ihm.de{path}"
                exhibitor_urls.append(test_url)
        
        # Парсим каждую найденную страницу
        for url in exhibitor_urls[:3]:
            logger.info(f"Парсим страницу: {url}")
            self.scrape_ihm_exhibitors_page(url)
    
    def scrape_ihm_exhibitors_page(self, url):
        """Парсинг страницы участников IHM"""
        content = self.get_page_content(url, use_selenium=True, wait_time=8)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Селекторы для IHM
        exhibitor_selectors = [
            '.exhibitor-item',
            '.aussteller-item',
            '.company-item',
            '.exhibitor-card',
            '.aussteller-card',
            '[data-exhibitor]',
            '[class*="exhibitor"]',
            '[class*="aussteller"]',
            '[class*="company"]',
            'article',
            '.card',
            '.item'
        ]
        
        exhibitor_blocks = []
        for selector in exhibitor_selectors:
            blocks = soup.select(selector)
            if blocks:
                exhibitor_blocks.extend(blocks)
                logger.info(f"Найдено {len(blocks)} блоков с селектором: {selector}")
        
        # Ограничиваем количество для демонстрации
        exhibitor_blocks = exhibitor_blocks[:20]
        
        for block in exhibitor_blocks:
            try:
                exhibitor_data = self.extract_exhibitor_data(block)
                if exhibitor_data and exhibitor_data['Name']:
                    self.exhibitors_data.append(exhibitor_data)
                    logger.info(f"Добавлен участник: {exhibitor_data['Name']}")
                    
            except Exception as e:
                logger.error(f"Ошибка при парсинге участника: {e}")
    
    def extract_exhibitor_data(self, element):
        """Извлечение данных участника из элемента"""
        try:
            # Извлечение названия компании
            name = self.extract_company_name(element)
            
            # Извлечение города
            city = self.extract_city(element)
            
            # Извлечение страны
            country = self.extract_country(element)
            
            # Извлечение веб-сайта
            website = self.extract_website(element)
            
            # Извлечение email
            email = self.extract_email(element)
            
            if name:
                return {
                    'Name': name.strip(),
                    'City': city.strip() if city else '',
                    'Country': country.strip() if country else '',
                    'Website': website if website else '',
                    'Email': email if email else ''
                }
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных участника: {e}")
        
        return None
    
    def extract_company_name(self, element):
        """Извлечение названия компании"""
        # Приоритетные селекторы для названия
        name_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '.company-name', '.exhibitor-name', '.name',
            '.title', '.headline',
            '[data-name]', '[data-company]',
            'strong', 'b'
        ]
        
        for selector in name_selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                text = found.get_text(strip=True)
                if len(text) > 2 and len(text) < 100:  # Фильтруем слишком короткие и длинные тексты
                    return text
        
        # Если не нашли по селекторам, ищем первый значимый текст
        text_elements = element.find_all(['p', 'span', 'div'], recursive=False)
        for text_elem in text_elements:
            text = text_elem.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 50:
                return text
        
        return None
    
    def extract_city(self, element):
        """Извлечение города"""
        # Селекторы для города
        city_selectors = [
            '.city', '.location', '.place',
            '[data-city]', '[data-location]',
            '.address', '.location-info'
        ]
        
        for selector in city_selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        
        # Поиск по тексту
        text = element.get_text()
        # Простой паттерн для поиска города (заглавная буква + строчные)
        city_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        cities = re.findall(city_pattern, text)
        
        # Фильтруем известные города Германии
        german_cities = ['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt', 'Stuttgart', 
                        'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig', 'Bremen', 'Dresden',
                        'Hannover', 'Nuremberg', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld']
        
        for city in cities:
            if city in german_cities:
                return city
        
        return None
    
    def extract_country(self, element):
        """Извлечение страны"""
        # Селекторы для страны
        country_selectors = [
            '.country', '.nation',
            '[data-country]', '[data-nation]'
        ]
        
        for selector in country_selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        
        # Поиск по тексту
        text = element.get_text()
        countries = ['Germany', 'Deutschland', 'USA', 'United States', 'UK', 'United Kingdom',
                    'France', 'Italy', 'Spain', 'Netherlands', 'Belgium', 'Switzerland', 'Austria']
        
        for country in countries:
            if country.lower() in text.lower():
                return country
        
        return 'Germany'  # По умолчанию для немецких выставок
    
    def extract_website(self, element):
        """Извлечение веб-сайта"""
        # Ищем ссылки
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('http') and not any(domain in href for domain in ['messe-stuttgart.de', 'ihm.de']):
                return href
        
        # Ищем в тексте
        text = element.get_text()
        url_pattern = r'https?://[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            if not any(domain in url for domain in ['messe-stuttgart.de', 'ihm.de']):
                return url
        
        return None
    
    def extract_email(self, element):
        """Извлечение email"""
        text = element.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def search_contacts(self, company_name, website_url=None):
        """Поиск контактных лиц для компании"""
        logger.info(f"Поиск контактов для: {company_name}")
        return self.contact_finder.find_contacts_for_company(company_name, website_url)
    
    def save_to_excel(self, filename="advanced_exhibition_data.xlsx"):
        """Сохранение данных в Excel"""
        try:
            # Проверяем, есть ли данные для сохранения
            if not self.exhibitors_data and not self.contacts_data:
                logger.warning("Нет данных для сохранения")
                return
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Сохраняем данные участников
                if self.exhibitors_data:
                    df_exhibitors = pd.DataFrame(self.exhibitors_data)
                    df_exhibitors.to_excel(writer, sheet_name='Exhibitors', index=False)
                    logger.info(f"Сохранено {len(self.exhibitors_data)} участников")
                else:
                    # Создаем пустой лист с заголовками
                    df_exhibitors = pd.DataFrame(columns=['Name', 'City', 'Country', 'Website', 'Email'])
                    df_exhibitors.to_excel(writer, sheet_name='Exhibitors', index=False)
                    logger.info("Создан пустой лист участников")
                
                # Сохраняем данные контактов
                if self.contacts_data:
                    df_contacts = pd.DataFrame(self.contacts_data)
                    df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
                    logger.info(f"Сохранено {len(self.contacts_data)} контактов")
                else:
                    # Создаем пустой лист с заголовками
                    df_contacts = pd.DataFrame(columns=['Company Name', 'Full Name', 'Position', 'Email', 'Source'])
                    df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
                    logger.info("Создан пустой лист контактов")
            
            logger.info(f"Данные сохранены в файл: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
    
    def run(self):
        """Запуск продвинутого парсинга"""
        logger.info("Начинаем продвинутый парсинг выставок...")
        
        # Парсим ELTEFA
        self.scrape_eltefa_advanced()
        
        # Парсим IHM
        self.scrape_ihm_advanced()
        
        # Поиск контактов для каждой компании
        for exhibitor in self.exhibitors_data:
            contacts = self.search_contacts(exhibitor['Name'], exhibitor.get('Website'))
            for contact in contacts:
                self.contacts_data.append({
                    'Company Name': exhibitor['Name'],
                    'Full Name': contact.get('name', ''),
                    'Position': contact.get('position', ''),
                    'Email': contact.get('email', ''),
                    'Source': contact.get('source', '')
                })
        
        # Сохраняем результаты
        self.save_to_excel()

if __name__ == "__main__":
    scraper = AdvancedExhibitionScraper()
    scraper.run() 