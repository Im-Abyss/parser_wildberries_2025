import requests
import random
import time
import os
import json
from bs4 import BeautifulSoup, Tag
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
                    product_data = self.parse_product_card(card)
                    if product_data:
                        products.append(product_data)

                print(f'Обработана страница {page}, найдено товаров: {len(product_cards)}')

            except Exception as e:
                print(f'Ошибка при обработке страницы: {e}')
                continue

        return products

    def parse_product_card(self, card: Tag):

        """
        Вернёт информацию о карточке
        товара, не открывая саму страницу товара.
        Для понимания ниже будет функция 'parse_product_detail'
        """

        try:
            link_elem = card.find('a', class_='porduct-card__link')
            if not link_elem:
                return None
            
            product_url = urljoin('https://www.wildberries.ru', link_elem.get('href'))

            name_elem = card.find('span', class_='product-card__name')
            name = name_elem.text.replace('/', '').strip() if name_elem else "Название не найдено"

            price_elem = card.find('ins', class_='price__lower-price wallet-price red-price')
            price = False # ниже будет функция для "очистки" цены

            rating_elem = card.find('div', class_='product-card__rating-wrap rating--DCKHb override--kkSDk')
            rating = rating_elem.text.strip() if rating_elem else "Рейтинг не найден"

            img_elem = card.find('img')
            preview_img = img_elem.get('src') if img_elem else None

            return{
                'name': name,
                'price': price,
                'raiting': rating,
                'url': product_url,
                'preview_image': preview_img
            }
        
        except Exception as e:
            print(f'Ошибка при парсинге карточки из поиска: {str(e)}')
            return None

    def parse_product_detail(self, product_url):

        """
        Вернёт данные открытой 
        страницы отдельного товара
        """

        try:
            self.driver.get(product_url)
            time.sleep(random.uniform(3, 5))

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(By.CLASS_NAME, "productPageContent--jaf94")
            )

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            name_elem = soup.find('h1', class_='productTitle--J2W7I')
            name = name_elem.text.strip() if name_elem else "Название не найдено"

            price_elem = soup.find('ins', class_='priceBlockFinalPrice--iToZR wallet--N1t3o')
            price = False # ниже будет функция для "очистки" цены

            desc_elem = soup.find('p', class_='descriptionText--Jq9n2')
            description = desc_elem.text.strip() if desc_elem else "Описание не найдено"

            # парсеры характеристик и изображений так же будут ниже
            characteristics = False

            images = False

            reviews_count_elem = soup.find('ins', class_='productReviewRating--gQDQG')
            reviews_count = reviews_count_elem.text.strip() if reviews_count_elem else "0"

            rating_elem = soup.find('span', class_='productReviewCount--hAvps')
            rating = rating_elem.text.strip() if rating_elem else "Рейтинг не найден"

            print(f'Парсинг товара "{name}" завершён')

            return {
                'name': name,
                'price': price,
                'description': description,
                'characteristics': characteristics,
                'images': images,
                'reviews_count': reviews_count,
                'rating': rating,
                'url': product_url
            }
        
        except Exception as e:
            print(f'Ошибка при парсинге страницы товара {product_url}\n{str(e)}')
            return None
        
    def clean_price(self, price_text):

        """
        Вернёт всё
        """

        if not price_text:
            return "Цена не найдена"
        
        cleaned_price = price_text.replace('\xa0', ' ')
        cleaned_price = cleaned_price.replace('&nbsp;', ' ') # на всякий случай
        cleaned_price = cleaned_price.strip()

        return cleaned_price
    
    def parse_characteristcs(self, soup) -> dict:

        """
        Вернёт характеристики товара
        в виде словаря
        """

        pass