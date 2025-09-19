import requests
import random
import time
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class WbParser:
    def __init__(self, headless=True):
        self.setup_driver(headless)

    def setup_driver(self, headless=True):

        """
        Создание и настройка
        веб драйвера
        """

        chrome_options = Options()
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtention', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def search_products(self, query, max_pages=3) -> list:
        
        """
        Вернёт список найденных товаров
        по запросу в поисковой строке
        """

        products = []

        for page in range(1, max_pages + 1):
            search_url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}&page={page}"

            try:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(By.CLASS_NAME, "product-card__wrapper")
                )

                soup = BeautifulSoup(self.driver.page_source, 'html_parser')
                product_cards = soup.find_all('div', class_='product-card__wrapper')

                for card in product_cards:
                    product_data = False # тут будет метод, который соберёт инфу о товаре card
                    if product_data:
                        products.append(product_data)

                print(f'Обработана страница {page}, найдено товаров: {len(product_cards)}')

            except Exception as e:
                print(f'Ошибка при обработке страницы: {e}')
                continue

        return products
