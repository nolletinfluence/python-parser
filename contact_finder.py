import requests
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

logger = logging.getLogger(__name__)

class ContactFinder:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua.random})
        
    def setup_driver(self):
        """Настройка веб-драйвера"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def search_linkedin_contacts(self, company_name):
        """Поиск контактов через LinkedIn"""
        contacts = []
        try:
            # Поиск через LinkedIn (используем поиск Google для обхода ограничений)
            search_query = f'site:linkedin.com "{company_name}" "CEO" OR "Geschäftsführer" OR "Managing Director"'
            contacts.extend(self.search_google_for_contacts(search_query, "LinkedIn"))
            
            search_query = f'site:linkedin.com "{company_name}" "HR Manager"'
            contacts.extend(self.search_google_for_contacts(search_query, "LinkedIn"))
            
            search_query = f'site:linkedin.com "{company_name}" "Sales Manager"'
            contacts.extend(self.search_google_for_contacts(search_query, "LinkedIn"))
            
        except Exception as e:
            logger.error(f"Ошибка при поиске в LinkedIn: {e}")
        
        return contacts
    
    def search_xing_contacts(self, company_name):
        """Поиск контактов через Xing"""
        contacts = []
        try:
            # Поиск через Xing
            search_query = f'site:xing.com "{company_name}" "CEO" OR "Geschäftsführer" OR "Managing Director"'
            contacts.extend(self.search_google_for_contacts(search_query, "Xing"))
            
            search_query = f'site:xing.com "{company_name}" "HR Manager"'
            contacts.extend(self.search_google_for_contacts(search_query, "Xing"))
            
            search_query = f'site:xing.com "{company_name}" "Sales Manager"'
            contacts.extend(self.search_google_for_contacts(search_query, "Xing"))
            
        except Exception as e:
            logger.error(f"Ошибка при поиске в Xing: {e}")
        
        return contacts
    
    def search_google_for_contacts(self, search_query, source):
        """Поиск контактов через Google"""
        contacts = []
        try:
            # Используем Google Custom Search API или парсинг результатов
            # Для демонстрации создаем заглушку
            logger.info(f"Поиск в {source}: {search_query}")
            
            # Здесь будет реальная логика поиска
            # Пока возвращаем тестовые данные
            if "CEO" in search_query or "Geschäftsführer" in search_query:
                contacts.append({
                    'name': 'John Doe',
                    'position': 'CEO',
                    'email': 'john.doe@company.com',
                    'source': source
                })
            
        except Exception as e:
            logger.error(f"Ошибка при поиске в Google: {e}")
        
        return contacts
    
    def search_company_website(self, company_name, website_url):
        """Поиск контактов на сайте компании"""
        contacts = []
        try:
            if not website_url:
                return contacts
            
            # Получаем содержимое страницы
            response = self.session.get(website_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем страницу контактов
            contact_links = soup.find_all('a', href=True)
            contact_page_url = None
            
            for link in contact_links:
                if any(keyword in link.text.lower() for keyword in ['kontakt', 'contact', 'team', 'about']):
                    contact_page_url = link['href']
                    break
            
            if contact_page_url:
                if not contact_page_url.startswith('http'):
                    contact_page_url = f"{website_url.rstrip('/')}/{contact_page_url.lstrip('/')}"
                
                contacts.extend(self.parse_contact_page(contact_page_url, company_name))
            
        except Exception as e:
            logger.error(f"Ошибка при поиске на сайте компании: {e}")
        
        return contacts
    
    def parse_contact_page(self, url, company_name):
        """Парсинг страницы контактов"""
        contacts = []
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем блоки с контактными лицами
            contact_blocks = soup.find_all(['div', 'section'], class_=re.compile(r'contact|team|person|staff'))
            
            for block in contact_blocks:
                try:
                    name = self.extract_contact_name(block)
                    position = self.extract_contact_position(block)
                    email = self.extract_contact_email(block)
                    
                    if name and position:
                        # Проверяем, подходит ли должность
                        if self.is_target_position(position):
                            contacts.append({
                                'name': name,
                                'position': position,
                                'email': email,
                                'source': f"{company_name} Website"
                            })
                
                except Exception as e:
                    logger.error(f"Ошибка при парсинге контакта: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы контактов: {e}")
        
        return contacts
    
    def extract_contact_name(self, element):
        """Извлечение имени контакта"""
        # Ищем имя в заголовках или специальных элементах
        name_selectors = ['h1', 'h2', 'h3', '.name', '.person-name', '[data-name]']
        for selector in name_selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None
    
    def extract_contact_position(self, element):
        """Извлечение должности контакта"""
        # Ищем должность
        position_selectors = ['.position', '.title', '.job-title', '[data-position]']
        for selector in position_selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None
    
    def extract_contact_email(self, element):
        """Извлечение email контакта"""
        text = element.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def is_target_position(self, position):
        """Проверка, является ли должность целевой"""
        target_positions = [
            'ceo', 'geschäftsführer', 'managing director', 'chief executive officer',
            'hr manager', 'human resources manager', 'personal manager',
            'sales manager', 'vertriebsleiter', 'verkaufsleiter'
        ]
        
        position_lower = position.lower()
        return any(target in position_lower for target in target_positions)
    
    def find_contacts_for_company(self, company_name, website_url=None):
        """Основной метод поиска контактов для компании"""
        all_contacts = []
        
        # Поиск через LinkedIn
        linkedin_contacts = self.search_linkedin_contacts(company_name)
        all_contacts.extend(linkedin_contacts)
        
        # Поиск через Xing
        xing_contacts = self.search_xing_contacts(company_name)
        all_contacts.extend(xing_contacts)
        
        # Поиск на сайте компании
        if website_url:
            website_contacts = self.search_company_website(company_name, website_url)
            all_contacts.extend(website_contacts)
        
        # Удаляем дубликаты
        unique_contacts = []
        seen_combinations = set()
        
        for contact in all_contacts:
            combination = (contact['name'], contact['position'])
            if combination not in seen_combinations:
                unique_contacts.append(contact)
                seen_combinations.add(combination)
        
        return unique_contacts 