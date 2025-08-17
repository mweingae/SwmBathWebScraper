import requests
import json
from bs4 import BeautifulSoup
from settings import *

def scrape_swm_bath_data():
    
    scraped_data = {}

    links = get_bath_pages(MAIN_BATHS_PAGE, CATEGORY_SUB_PAGES)
    
    with requests.Session() as session:
        for link in links:
            print(f"Scraping data from: {link}")
            try:
                
                bath_response = session.get(link, timeout=10)
                bath_response.raise_for_status()  
                bath_soup = BeautifulSoup(bath_response.content, 'html.parser')
            
                is_success= extract_from_items(bath_soup, scraped_data)
                if not is_success:
                    print(f"No bath-capacity-item found on {link}. Skipping.")
            
            except requests.RequestException as e:
                print(f"Error accessing {link}: {e}")
            
    return scraped_data

def get_bath_pages(page_url: str, paths: "list[str]") -> set:
    
    links = set()

    with requests.Session() as session:
        for path in paths:
            sub_page_url = f"{page_url}/{path}"

            try:
                response = session.get(sub_page_url, timeout=10)
                response.raise_for_status()

            except requests.RequestException as e:
                print(f"Error accessing the page {sub_page_url}: {e}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                href = str(a_tag['href'])
                if '/baeder/' in href and href != '/baeder/':
                    full_url = f"{BASE_URL}{href}" if href.startswith('/') else href
                    links.add(full_url)
        
    print(f"Found {len(links)} unique bath pages to scrape.")
    return links

def extract_from_items(item_soup: BeautifulSoup, result: dict) -> bool:
    
    has_extract = False
    items = item_soup.find_all(BATH_CAPACITY_ITEM)
     
    if not items:
        return False
                
    for item in items:
        organization_id = item.get('organization-unit-id')
        bath_type = item.get('icon-name')

        if organization_id and bath_type:
            has_extract = True

            bath_name_attr = item.get('bath-name')
            if bath_name_attr in [BATH_TYPE_SAUNA, BATH_TYPE_HALLENBAD]:
                bath_name = get_bath_name_from_header(item_soup)
            else:
                bath_name = bath_name_attr

            data = {
                "id": int(organization_id),
                "name": bath_name,
                "type": bath_type,
            }
            result[data["id"]] = data
    
    return has_extract

def get_bath_name_from_header(soup: BeautifulSoup) -> str:

    item = soup.find('h1', class_=HEADER_CLASS)

    if item:
        return item.get_text()
    else:
        return "Unknown"

def log_and_save_results(data: "dict[int, dict]"):
    
    result_list = list(data.values())

    result_list.sort(key=lambda item: (item['name'], item['type']))

    for item in result_list:
        print(f"Organization ID: {item['id']}, Bath Name: {item['name']}, Type: {item['type']}")
    
    print(f"Data extracted in total: {len(result_list)} items")

    with open(OUTPUT_FILE, 'w', encoding='UTF-8') as jsonf:
        json.dump(result_list, jsonf, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    
    print("--- Start Scraping SWM Websites ---")

    extracted_info = scrape_swm_bath_data()
    
    print("\n--- Scraping Complete ---")

    if extracted_info:

        log_and_save_results(extracted_info)
    
    else:
        print("No data was extracted.")