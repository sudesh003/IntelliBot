import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import threading

def crawl_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        lock = threading.Lock()  # Create a lock

        # Define a function to extract links from a page
        def extract_links_from_page(page_soup):
            page_links = set()
            for a_tag in page_soup.find_all('a', href=True):
                link = a_tag['href']
                if link.startswith('http') or link.startswith('https'):
                    page_links.add(link)
            return page_links

        # Collect links from the initial page
        links.update(extract_links_from_page(soup))

        # Use ThreadPoolExecutor to parallelize link extraction
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Define a function to fetch and extract links from a URL
            def fetch_and_extract(url):
                try:
                    response = requests.get(url)
                    page_soup = BeautifulSoup(response.text, 'html.parser')
                    page_links = extract_links_from_page(page_soup)

                    # Acquire the lock before updating the shared set
                    with lock:
                        links.update(page_links)
                    # Check the size of the set and stop if it exceeds the threshold
                    if len(links) >100:
                        executor.shutdown(wait=False)  # Stop the thread pool
                except Exception as e:
                    print(f"Error fetching {url}: {e}")

            # Submit tasks to the thread pool
            futures = [executor.submit(fetch_and_extract, link) for link in links]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        # Return the unique crawled links
        return list(links)[:100]
    except Exception as e:
        return f"Error: {e}"

# lst = crawl_website('https://refactoring.guru/design-patterns')
# print(lst)
