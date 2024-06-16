import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import re
import pyshorteners

HEADERS = {'User-Agent': '', 'Accept-Language': 'en-IN, en;q=0.5'}
lock = threading.Lock()

def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        return title.text.strip() if title else ""
    except AttributeError:
        return ""

def get_price(soup):
    try:
        price_element = soup.find("span", attrs={'class': 'aok-offscreen'})
        price_string = price_element.string.strip() if price_element else ""
        price = re.search(r'\d[\d,\.]*', price_string).group().replace(',', '') if price_string else ""
        return int(float(price)) if price else 0
    except AttributeError:
        return 0

def get_product_details_amazon(link, final_list):
    data = {}
    new_webpage = requests.get("https://www.amazon.in" + link, headers=HEADERS)
    new_soup = BeautifulSoup(new_webpage.content, "html.parser")
    data['title'] = get_title(new_soup)
    data['price'] = get_price(new_soup)
    data['product_link'] = "https://www.amazon.in" + link
    data['platform'] = "Amazon"
    with lock:
        if len(final_list) < 10:
            final_list.append(data)

def get_title1(soup):
    try:
        title = soup.find("span", class_="VU-ZEz")
        return title.text.strip() if title else ""
    except AttributeError:
        return ""

def get_price1(soup):
    try:
        price = soup.find("div", class_="Nx9bqj CxhGGd").text.strip()
        return int(price.replace(",","")[1:]) if price else 0
    except AttributeError:
        return 0

def get_product_details_flipkart(link, final_list1):
    data = {}
    new_webpage = requests.get(link, headers=HEADERS)
    new_soup = BeautifulSoup(new_webpage.content, "html.parser")
    data['title'] = get_title1(new_soup)
    data['price'] = get_price1(new_soup)
    data['product_link'] = link
    data['platform'] = "Flipkart"
    with lock:
        if len(final_list1) < 10:
            final_list1.append(data)

def price_comparator(search_query):
    s = pyshorteners.Shortener()
    # Scraping Amazon
    amazon_url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}&ref=nb_sb_noss_2"
    amazon_webpage = requests.get(amazon_url, headers=HEADERS)
    amazon_soup = BeautifulSoup(amazon_webpage.content, "html.parser")
    amazon_links = amazon_soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})

    amazon_final_list = []
    amazon_executor = ThreadPoolExecutor(max_workers=50)
    for link in amazon_links:
        amazon_executor.submit(get_product_details_amazon, link.get('href'), amazon_final_list)
    amazon_executor.shutdown(wait=True)

    # Scraping Flipkart
    flipkart_url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}"
    flipkart_webpage = requests.get(flipkart_url, headers=HEADERS)
    flipkart_soup = BeautifulSoup(flipkart_webpage.content, "html.parser")
    flipkart_products = flipkart_soup.find_all("a", class_="CGtC98")

    flipkart_final_list = []
    flipkart_executor = ThreadPoolExecutor(max_workers=50)
    for product in flipkart_products:
        product_link = "https://www.flipkart.com" + product["href"]
        flipkart_executor.submit(get_product_details_flipkart, product_link, flipkart_final_list)
    flipkart_executor.shutdown(wait=True)

    # Combine results from Amazon and Flipkart
    combined_list = []
    combined_list.extend(amazon_final_list)
    combined_list.extend(flipkart_final_list)
    
    # Filter out items with price 0
    filtered_list = [item for item in combined_list if item["price"] != 0]
    
    # Sort by price
    filtered_list.sort(key=lambda x: x["price"])

    result = ""
    for item in filtered_list:
        short_url = s.tinyurl.short(item['product_link'])
        result += f"Title: {item['title']}\n"
        result += f"Price: Rs.{item['price']}\n"
        result += f"Platform: {item['platform']}\n"
        result += f"Product Link: {short_url}\n"
        result += "\n"

    return result

# # Example usage
# search_query = input("Enter the product name: ")
# price_comparator(search_query)
