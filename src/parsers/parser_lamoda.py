import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from src.config import Config
from log_config import setup_logging
import logging

setup_logging()


class LamodaParser:
    def __init__(self, controller):
        self._session = None
        self._controller = controller

    async def _start_session(self):
        self._session = aiohttp.ClientSession()

    async def _close_session(self):
        if self._session:
            await self._session.close()

    async def _get_page(self, url):
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Error {response.status}")
                    return None
        except aiohttp.ClientConnectorError:
            logging.info(f"Try again connect to page")
            return await self._get_page(url)

    def _parse_lamoda_category(self, page_content, category_data, category_url):
        if page_content:
            soup = BeautifulSoup(page_content, "html.parser")
            product_cards = soup.find_all("div", class_="x-product-card__card")
            for product_card in product_cards:
                product_price_element = product_card.find(
                    "span", class_="x-product-card-description__price-new")
                if product_price_element is None:
                    product_price_element = product_card.find(
                        "span", class_="x-product-card-description__price-single")
                if product_price_element:
                    product_price = product_price_element.text
                    product_price = int(product_price.replace(' ', '')[:-1])
                else:
                    product_price = "No price information"

                product_name_element = product_card.find(
                    "div", class_="x-product-card-description__product-name")
                if product_name_element:
                    product_name = product_name_element.text.strip()
                else:
                    product_name = "No name information"

                store_element = product_card.find(
                    "div", class_="x-product-card-description__brand-name")
                if store_element:
                    store_name = store_element.text.strip()
                else:
                    store_name = "No shop information"

                category_data.setdefault(category_url, []).append({
                    "Name": product_name,
                    "Price": product_price,
                    "Shop": store_name
                })

    def _get_number_of_pages(self, category_content):
        if category_content:
            page_content_str = category_content
            match = re.search(r'"pages":(\d+)', page_content_str)
            if match:
                pages_value = match.group(1)
                # return int(pages_value)
                return 2
            else:
                logging.warning(f"No page content in HTML-code")
                return 1

    def _get_categories(self, page_content):
        if page_content:
            soup = BeautifulSoup(page_content, "html.parser")
            categories = []
            for category in soup.find_all(
                    "a", class_="d-header-topmenu-category__link"):
                category_link = Config.lamoda.lamoda_base + category["href"]
                categories.append(category_link)
            return categories
        return []

    async def _process_category(self, category_url, clothes_data):
        category_content = await self._get_page(category_url)
        if category_content:
            num_pages = self._get_number_of_pages(category_content)
            for page_number in range(1, num_pages + 1):
                page_url = f"{category_url}?page={page_number}"
                logging.debug(f"{page_url}  {page_number}")
                self._parse_lamoda_category(await self._get_page(page_url), clothes_data, category_url)

    async def start_parser(self, section):
        clothes_data = {}
        await self._start_session()
        page_content = await self._get_page(Config.lamoda.lamoda_urls[section])
        if page_content:
            categories = self._get_categories(page_content)
            tasks = [
                self._process_category(
                    category_url,
                    clothes_data) for category_url in categories]
            await asyncio.gather(*tasks)
        logging.info(f"Start work with DB")
        self._controller.lamoda.insert_data_into_mongodb(section, clothes_data)
        logging.info(f"Finish work with DB")
        await self._close_session()
