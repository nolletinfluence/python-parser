import requests
import pandas as pd
import time
import re
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

class ExhibitionScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.exhibitors_data = []
        self.contacts_data = []
        self.contact_finder = ContactFinder()
        
    def setup_driver(self):
        """Настройка веб-драйвера"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def get_page_content(self, url, use_selenium=False):
        """Получение содержимого страницы"""
        try:
            if use_selenium:
                driver = self.setup_driver()
                driver.get(url)
                time.sleep(5)  # Ждем загрузки JavaScript
                content = driver.page_source
                driver.quit()
                return content
            else:
                headers = {'User-Agent': self.ua.random}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def scrape_eltefa(self):
        """Парсинг выставки ELTEFA"""
        logger.info("Начинаем парсинг ELTEFA...")
        url = "https://www.messe-stuttgart.de/eltefa/?hl=de-DE"
        
        # Получаем основную страницу
        content = self.get_page_content(url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем ссылку на список участников
        exhibitors_link = None
        links = soup.find_all('a', href=True)
        for link in links:
            if any(keyword in link.text.lower() for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                exhibitors_link = link['href']
                break
        
        if exhibitors_link:
            if not exhibitors_link.startswith('http'):
                exhibitors_link = f"https://www.messe-stuttgart.de{exhibitors_link}"
            
            # Парсим страницу участников
            self.scrape_eltefa_exhibitors(exhibitors_link)
        else:
            logger.warning("Ссылка на участников не найдена")
    
    def scrape_eltefa_exhibitors(self, url):
        """Парсинг участников ELTEFA"""
        content = self.get_page_content(url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем блоки с участниками
        exhibitor_blocks = soup.find_all(['div', 'article'], class_=re.compile(r'exhibitor|aussteller|company'))
        
        for block in exhibitor_blocks:
            try:
                name = self.extract_text(block, ['h1', 'h2', 'h3', '.company-name', '.exhibitor-name'])
                city = self.extract_text(block, ['.city', '.location', '[data-city]'])
                country = self.extract_text(block, ['.country', '[data-country]'])
                website = self.extract_link(block, 'a[href*="http"]')
                email = self.extract_email(block)
                
                if name:
                    self.exhibitors_data.append({
                        'Name': name.strip(),
                        'City': city.strip() if city else '',
                        'Country': country.strip() if country else '',
                        'Website': website if website else '',
                        'Email': email if email else ''
                    })
                    logger.info(f"Добавлен участник: {name}")
                    
            except Exception as e:
                logger.error(f"Ошибка при парсинге участника: {e}")
    
    def scrape_ihm(self):
        """Парсинг выставки IHM"""
        logger.info("Начинаем парсинг IHM...")
        url = "https://www.ihm.de/en/home?hl=de-DE"
        
        content = self.get_page_content(url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем ссылку на список участников
        exhibitors_link = None
        links = soup.find_all('a', href=True)
        for link in links:
            if any(keyword in link.text.lower() for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                exhibitors_link = link['href']
                break
        
        if exhibitors_link:
            if not exhibitors_link.startswith('http'):
                exhibitors_link = f"https://www.ihm.de{exhibitors_link}"
            
            self.scrape_ihm_exhibitors(exhibitors_link)
        else:
            logger.warning("Ссылка на участников не найдена")
    
    def scrape_ihm_exhibitors(self, url):
        """Парсинг участников IHM"""
        content = self.get_page_content(url, use_selenium=True)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем блоки с участниками
        exhibitor_blocks = soup.find_all(['div', 'article'], class_=re.compile(r'exhibitor|aussteller|company'))
        
        for block in exhibitor_blocks:
            try:
                name = self.extract_text(block, ['h1', 'h2', 'h3', '.company-name', '.exhibitor-name'])
                city = self.extract_text(block, ['.city', '.location', '[data-city]'])
                country = self.extract_text(block, ['.country', '[data-country]'])
                website = self.extract_link(block, 'a[href*="http"]')
                email = self.extract_email(block)
                
                if name:
                    self.exhibitors_data.append({
                        'Name': name.strip(),
                        'City': city.strip() if city else '',
                        'Country': country.strip() if country else '',
                        'Website': website if website else '',
                        'Email': email if email else ''
                    })
                    logger.info(f"Добавлен участник: {name}")
                    
            except Exception as e:
                logger.error(f"Ошибка при парсинге участника: {e}")
    
    def extract_text(self, element, selectors):
        """Извлечение текста по селекторам"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None
    
    def extract_link(self, element, selector):
        """Извлечение ссылки"""
        link = element.select_one(selector)
        if link and link.get('href'):
            href = link['href']
            if not href.startswith('http'):
                href = f"https://{href}"
            return href
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
    
    def save_to_excel(self, filename="exhibition_data.xlsx"):
        """Сохранение данных в Excel"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Сохраняем данные участников
                if self.exhibitors_data:
                    df_exhibitors = pd.DataFrame(self.exhibitors_data)
                    df_exhibitors.to_excel(writer, sheet_name='Exhibitors', index=False)
                    logger.info(f"Сохранено {len(self.exhibitors_data)} участников")
                
                # Сохраняем данные контактов
                if self.contacts_data:
                    df_contacts = pd.DataFrame(self.contacts_data)
                    df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
                    logger.info(f"Сохранено {len(self.contacts_data)} контактов")
            
            logger.info(f"Данные сохранены в файл: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
    
    def run(self):
        """Запуск парсинга"""
        logger.info("Начинаем парсинг выставок...")
        
        # Парсим ELTEFA
        self.scrape_eltefa()
        
        # Парсим IHM
        self.scrape_ihm()
        
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
    scraper = ExhibitionScraper()
    scraper.run() 