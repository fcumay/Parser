import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from src.config import Config
from src.di import container_controller
from log_config import setup_logging
import logging

setup_logging()


async def get_page(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.error(f"Error {response.status}")
                return None
    except aiohttp.client_exceptions.ServerDisconnectedError:
        logging.info(f"Try again connect to page")
        return await get_page(session, url)


def parse_lamoda_category(page_content, category_data, category_url):
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


def get_number_of_pages(category_content):
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


def get_categories(page_content):
    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        categories = []
        for category in soup.find_all(
                "a", class_="d-header-topmenu-category__link"):
            category_link = Config.lamoda.lamoda_base + category["href"]
            categories.append(category_link)
        return categories
    return []


async def process_category(session, category_url, clothes_data):
    category_content = await get_page(session, category_url)
    if category_content:
        num_pages = get_number_of_pages(category_content)
        for page_number in range(1, num_pages + 1):
            page_url = f"{category_url}?page={page_number}"
            logging.debug(f"{page_url}  {page_number}")
            parse_lamoda_category(await get_page(session, page_url), clothes_data, category_url)


async def main(section):
    clothes_data = {}
    async with aiohttp.ClientSession() as session:
        page_content = await get_page(session, Config.lamoda.lamoda_urls[section])
        if page_content:
            categories = get_categories(page_content)
            tasks = [
                process_category(
                    session,
                    category_url,
                    clothes_data) for category_url in categories]
            await asyncio.gather(*tasks)
    logging.info(f"Start work with DB")
    container_controller.lamoda.insert_data_into_mongodb(section, clothes_data)
    logging.info(f"Finish work with DB")
