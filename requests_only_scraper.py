#!/usr/bin/env python3
"""
Парсер выставок только с requests (без Selenium)
"""

import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RequestsOnlyScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.exhibitors_data = []
        self.contacts_data = []
        
    def get_page_content(self, url):
        """Получение содержимого страницы с помощью requests"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            
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
        content = self.get_page_content(url)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем ссылку на список участников
        exhibitors_link = None
        links = soup.find_all('a', href=True)
        
        # Более точный поиск ссылок на участников
        for link in links:
            link_text = link.get_text(strip=True).lower()
            link_href = link.get('href', '').lower()
            
            # Ищем по тексту ссылки
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer', 'teilnehmen']):
                exhibitors_link = link['href']
                logger.info(f"Найдена ссылка на участников: {link_text} -> {exhibitors_link}")
                break
            
            # Ищем по URL
            if any(keyword in link_href for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                exhibitors_link = link['href']
                logger.info(f"Найдена ссылка на участников по URL: {link_href}")
                break
        
        if exhibitors_link:
            if not exhibitors_link.startswith('http'):
                exhibitors_link = f"https://www.messe-stuttgart.de{exhibitors_link}"
            
            # Парсим страницу участников
            self.scrape_eltefa_exhibitors(exhibitors_link)
        else:
            logger.warning("Ссылка на участников не найдена, пробуем стандартные пути...")
            # Пробуем стандартные пути
            standard_paths = [
                "/eltefa/aussteller/",
                "/eltefa/exhibitors/",
                "/eltefa/teilnehmer/",
                "/aussteller/",
                "/exhibitors/",
                "/teilnehmer/"
            ]
            for path in standard_paths:
                test_url = f"https://www.messe-stuttgart.de{path}"
                logger.info(f"Пробуем: {test_url}")
                self.scrape_eltefa_exhibitors(test_url)
                if self.exhibitors_data:  # Если нашли данные, прекращаем
                    break
    
    def scrape_eltefa_exhibitors(self, url):
        """Парсинг участников ELTEFA"""
        content = self.get_page_content(url)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Более точные селекторы для поиска участников
        exhibitor_blocks = []
        
        # 1. Ищем по специфичным классам
        specific_selectors = [
            '.exhibitor-item',
            '.aussteller-item', 
            '.company-item',
            '.exhibitor-card',
            '.aussteller-card',
            '.exhibitor-list-item',
            '.aussteller-list-item',
            '[data-exhibitor]',
            '[data-aussteller]',
            '.exhibitor',
            '.aussteller'
        ]
        
        for selector in specific_selectors:
            blocks = soup.select(selector)
            if blocks:
                exhibitor_blocks.extend(blocks)
                logger.info(f"Найдено {len(blocks)} блоков с селектором: {selector}")
        
        # 2. Если не нашли, ищем по структуре с более строгими критериями
        if not exhibitor_blocks:
            # Ищем блоки, которые содержат название компании и контактную информацию
            all_divs = soup.find_all('div')
            for div in all_divs:
                # Проверяем, что блок содержит заголовок и ссылку
                has_title = div.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                has_link = div.find('a', href=True)
                has_text = div.get_text(strip=True)
                
                # Фильтруем блоки с осмысленным содержимым
                if (has_title and has_link and 
                    len(has_text) > 10 and len(has_text) < 500 and
                    not any(skip_word in has_text.lower() for skip_word in 
                           ['exhibition management', 'navigation', 'menu', 'footer', 'header', 'cookie'])):
                    exhibitor_blocks.append(div)
        
        logger.info(f"Найдено {len(exhibitor_blocks)} потенциальных блоков участников")
        
        # Убираем дубликаты и ограничиваем количество
        unique_blocks = []
        seen_names = set()
        
        for block in exhibitor_blocks[:20]:  # Ограничиваем для демонстрации
            try:
                name = self.extract_text(block, ['h1', 'h2', 'h3', 'h4', '.company-name', '.exhibitor-name', 'strong', 'b'])
                
                # Фильтруем нежелательные названия
                if (name and len(name) > 2 and len(name) < 100 and
                    name not in seen_names and
                    not any(skip_word in name.lower() for skip_word in 
                           ['exhibition', 'management', 'navigation', 'menu', 'footer', 'header', 'cookie', 'privacy'])):
                    
                    seen_names.add(name)
                    unique_blocks.append(block)
                    
                    city = self.extract_text(block, ['.city', '.location', '[data-city]'])
                    country = self.extract_text(block, ['.country', '[data-country]'])
                    website = self.extract_link(block, 'a[href*="http"]')
                    email = self.extract_email(block)
                    
                    self.exhibitors_data.append({
                        'Name': name.strip(),
                        'City': city.strip() if city else '',
                        'Country': country.strip() if country else 'Germany',
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
        
        content = self.get_page_content(url)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Ищем ссылку на список участников
        exhibitors_link = None
        links = soup.find_all('a', href=True)
        
        # Более точный поиск ссылок на участников
        for link in links:
            link_text = link.get_text(strip=True).lower()
            link_href = link.get('href', '').lower()
            
            # Ищем по тексту ссылки
            if any(keyword in link_text for keyword in ['aussteller', 'exhibitor', 'teilnehmer', 'teilnehmen']):
                exhibitors_link = link['href']
                logger.info(f"Найдена ссылка на участников: {link_text} -> {exhibitors_link}")
                break
            
            # Ищем по URL
            if any(keyword in link_href for keyword in ['aussteller', 'exhibitor', 'teilnehmer']):
                exhibitors_link = link['href']
                logger.info(f"Найдена ссылка на участников по URL: {link_href}")
                break
        
        if exhibitors_link:
            if not exhibitors_link.startswith('http'):
                exhibitors_link = f"https://www.ihm.de{exhibitors_link}"
            
            self.scrape_ihm_exhibitors(exhibitors_link)
        else:
            logger.warning("Ссылка на участников не найдена, пробуем стандартные пути...")
            # Пробуем стандартные пути
            standard_paths = [
                "/aussteller/",
                "/exhibitors/",
                "/teilnehmer/",
                "/en/exhibitors/",
                "/de/aussteller/",
                "/en/aussteller/",
                "/de/exhibitors/"
            ]
            for path in standard_paths:
                test_url = f"https://www.ihm.de{path}"
                logger.info(f"Пробуем: {test_url}")
                self.scrape_ihm_exhibitors(test_url)
                if len(self.exhibitors_data) > 0:  # Если нашли данные, прекращаем
                    break
    
    def scrape_ihm_exhibitors(self, url):
        """Парсинг участников IHM"""
        content = self.get_page_content(url)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Более точные селекторы для поиска участников
        exhibitor_blocks = []
        
        # 1. Ищем по специфичным классам
        specific_selectors = [
            '.exhibitor-item',
            '.aussteller-item', 
            '.company-item',
            '.exhibitor-card',
            '.aussteller-card',
            '.exhibitor-list-item',
            '.aussteller-list-item',
            '[data-exhibitor]',
            '[data-aussteller]',
            '.exhibitor',
            '.aussteller'
        ]
        
        for selector in specific_selectors:
            blocks = soup.select(selector)
            if blocks:
                exhibitor_blocks.extend(blocks)
                logger.info(f"Найдено {len(blocks)} блоков с селектором: {selector}")
        
        # 2. Если не нашли, ищем по структуре с более строгими критериями
        if not exhibitor_blocks:
            # Ищем блоки, которые содержат название компании и контактную информацию
            all_divs = soup.find_all('div')
            for div in all_divs:
                # Проверяем, что блок содержит заголовок и ссылку
                has_title = div.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                has_link = div.find('a', href=True)
                has_text = div.get_text(strip=True)
                
                # Фильтруем блоки с осмысленным содержимым
                if (has_title and has_link and 
                    len(has_text) > 10 and len(has_text) < 500 and
                    not any(skip_word in has_text.lower() for skip_word in 
                           ['exhibition management', 'navigation', 'menu', 'footer', 'header', 'cookie'])):
                    exhibitor_blocks.append(div)
        
        logger.info(f"Найдено {len(exhibitor_blocks)} потенциальных блоков участников")
        
        # Убираем дубликаты и ограничиваем количество
        unique_blocks = []
        seen_names = set()
        
        for block in exhibitor_blocks[:20]:  # Ограничиваем для демонстрации
            try:
                name = self.extract_text(block, ['h1', 'h2', 'h3', 'h4', '.company-name', '.exhibitor-name', 'strong', 'b'])
                
                # Фильтруем нежелательные названия
                if (name and len(name) > 2 and len(name) < 100 and
                    name not in seen_names and
                    not any(skip_word in name.lower() for skip_word in 
                           ['exhibition', 'management', 'navigation', 'menu', 'footer', 'header', 'cookie', 'privacy'])):
                    
                    seen_names.add(name)
                    unique_blocks.append(block)
                    
                    city = self.extract_text(block, ['.city', '.location', '[data-city]'])
                    country = self.extract_text(block, ['.country', '[data-country]'])
                    website = self.extract_link(block, 'a[href*="http"]')
                    email = self.extract_email(block)
                    
                    self.exhibitors_data.append({
                        'Name': name.strip(),
                        'City': city.strip() if city else '',
                        'Country': country.strip() if country else 'Germany',
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
        """Поиск контактных лиц для компании (заглушка)"""
        logger.info(f"Поиск контактов для: {company_name}")
        # Возвращаем тестовые данные
        return [
            {
                'name': f'Test Contact {company_name}',
                'position': 'CEO',
                'email': f'ceo@{company_name.lower().replace(" ", "")}.com',
                'source': 'Test Data'
            }
        ]
    
    def save_to_excel(self, filename="requests_exhibition_data.xlsx"):
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
        """Запуск парсинга"""
        logger.info("Начинаем парсинг выставок (только requests)...")
        
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
    scraper = RequestsOnlyScraper()
    scraper.run() 