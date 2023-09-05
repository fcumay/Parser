import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from src.db import insert_data_into_mongodb
from src.db import Section

lamoda_urls = {
    Section.women: "https://www.lamoda.ru/women-home/?sitelink=topmenuW",
    Section.men: "https://www.lamoda.ru/men-home/?sitelink=topmenuM",
    Section.kids: "https://www.lamoda.ru/kids-home/?sitelink=topmenuK"
}

lamoda_base = "https://www.lamoda.ru"


async def get_page(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Ошибка при получении страницы: {response.status}")
                return None
    except aiohttp.client_exceptions.ServerDisconnectedError:
        print(f"Ошибка: сервер разорвал соединение, повторяем запрос...")
        return await get_page(session, url)  # Повторить запрос


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
            print('No page content in HTML-code')
            return 1


def get_categories(page_content):
    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        categories = []
        for category in soup.find_all(
                "a", class_="d-header-topmenu-category__link"):
            category_link = lamoda_base + category["href"]
            categories.append(category_link)
        return categories
    return []


async def process_category(session, category_url, clothes_data):
    category_content = await get_page(session, category_url)
    if category_content:
        num_pages = get_number_of_pages(category_content)
        for page_number in range(1, num_pages + 1):
            page_url = f"{category_url}?page={page_number}"
            print(f"{page_url}  {page_number}")
            parse_lamoda_category(await get_page(session, page_url), clothes_data, category_url)


async def main(section):
    clothes_data = {}
    async with aiohttp.ClientSession() as session:
        page_content = await get_page(session, lamoda_urls[section])
        if page_content:
            categories = get_categories(page_content)
            tasks = [
                process_category(
                    session,
                    category_url,
                    clothes_data) for category_url in categories]
            await asyncio.gather(*tasks)
    print(f"\nStart work with DB\n")
    insert_data_into_mongodb(section, clothes_data)
    print(f"\nFinish work with DB\n")
