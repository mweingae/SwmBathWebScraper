import requests
import csv
from datetime import date
import time
from bs4 import BeautifulSoup
from settings import *

def scrape_swm_bath_data():
    """
    Main function to scrape bath facility data from SWM (Stadtwerke München) website.
    Collects information about different baths and saunas including their IDs, names, and types.
    
    Returns:
        list[dict]: List of dictionaries containing bath data, each with 'id', 'name', and 'type' fields
    """
    scraped_data = []

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

def get_bath_pages(page_url: str, paths: list[str]) -> set:
    """
    Retrieves all swimming pool page URLs from the SWM website by crawling category pages.
    
    Args:
        page_url (str): The base URL of the main baths page
        paths (list[str]): List of category sub-page paths to crawl
        
    Returns:
        set: A set of unique URLs for individual bath pages
    """
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

def extract_from_items(item_soup: BeautifulSoup, result: list[dict]) -> bool:
    """
    Extracts bath information from BeautifulSoup parsed HTML content.
    
    Args:
        item_soup (BeautifulSoup): Parsed HTML content of a bath page
        result (dict): Dictionary to store the extracted bath information
        
    Returns:
        bool: True if bath capacity information was found and extracted, False otherwise
    """
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
                "name": bath_name.removesuffix(" – Hallenbad und Sauna"),
                "type": bath_type,
            }
            result.append(data)
    
    return has_extract

def get_bath_name_from_header(soup: BeautifulSoup) -> str:
    """
    Extracts the bath name from the page header when it's not available in the capacity item.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content of a bath page
        
    Returns:
        str: The name of the bath found in the header, or 'Unknown' if not found
    """
    item = soup.find('h1', class_=HEADER_CLASS)

    if item:
        return item.get_text()
    else:
        return "Unknown"
    
def consolidate_results(results: list[dict]) -> list[dict]:
    """
    Consolidates bath data by removing duplicates and handling unknown names.
    
    Args:
        results (list[dict]): List of dictionaries containing bath information
        
    Returns:
        list[dict]: Consolidated list with duplicates removed and unknown names resolved
        
    Note:
        When duplicate IDs are found, entries with known names are preferred over 'Unknown' names.
    """
    consolidated_results = []
    count = len(results)

    for i in range(0, count):
        item = results[i]
        is_unique = True

        for j in range(i+1, count):
            comparer_item = results[j]
            if item["id"] == comparer_item["id"]:
                is_unique = False
                if comparer_item["name"] == "Unknown":
                    results[j] = item
                    break
                else:
                    break
        
        if is_unique:
            consolidated_results.append(item)
    
    return consolidated_results

def log_and_save_results(data: list[dict]):
    """
    Logs the extracted bath data to console and saves it to a CSV file.
    
    Args:
        data (list[dict]): List of dictionaries containing bath information with fields:
            - id: Organization ID
            - name: Bath facility name
            - type: Type of facility (e.g., sauna, indoor pool)
    
    Note:
        The output file name includes the current date (ISO format) and is prefixed
        with the value defined in settings.OUTPUT_FILE_PREFIX
    """
    
    data.sort(key=lambda item: (item['name'], item['type']))

    for item in data:
        print(f"Organization ID: {item['id']}, Bath Name: {item['name']}, Type: {item['type']}")
    
    print(f"Data extracted in total: {len(data)} items")

    file_name = OUTPUT_FILE_PREFIX + date.fromtimestamp(time.time()).isoformat() + ".csv"
    with open(file_name, 'w', encoding='UTF-8', newline='') as csvf:
        fieldnames = ['id', 'name', 'type']
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    print("--- Start Scraping SWM Websites ---")
    extracted_info = scrape_swm_bath_data()
    results = consolidate_results(extracted_info)
    
    print("\n--- Scraping Complete ---")
    if extracted_info:
        log_and_save_results(results)
    else:
        print("No data was extracted.")
