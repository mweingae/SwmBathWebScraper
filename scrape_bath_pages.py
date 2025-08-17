import requests
import json
from bs4 import BeautifulSoup

def scrape_swm_bath_data():
    """
    Scrapes the SWM website for bath information.
    Accesses the main baths page, follows each link to a bath,
    and extracts the organization-unit-id and bath-name.
    """
    base_url = "https://www.swm.de"
    main_baths_page = f"{base_url}/baeder"
    category_sub_pages = ["hallenbaeder-muenchen", "saunen-muenchen", "freibaeder-muenchen"]
    
    scraped_data = {}

    links = get_bath_pages(main_baths_page, category_sub_pages)
        
    # Follow each link to scrape the specific details
    for link in links:
        print(f"Scraping data from: {link}")
        try:
            
            bath_response = requests.get(link, timeout=10)
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

    for path in paths:
        sub_page_url = f"{page_url}/{path}"

        try:
            
            response = requests.get(sub_page_url, timeout=10)
            response.raise_for_status()  # Raises an exception for bad status codes

        except requests.RequestException as e:
            print(f"Error accessing the page {sub_page_url}: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to individual baths. The specific structure might vary,
        # so this is a robust way to find links that contain '/baeder/'
        # and are not the main page itself.
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/baeder/' in href and href != '/baeder/':
                # Construct the full URL if it's a relative path
                full_url = f"{page_url}{href}" if href.startswith('/') else href
                links.add(full_url)
        
    print(f"Found {len(links)} unique bath pages to scrape.")
    return links

def extract_from_items(item_soup: BeautifulSoup, result: dict) -> bool:
    # Use Beautiful Soup to find all bath-capacity-item tags
    # and extract the desired attributes.

    has_extract = False
    items = item_soup.find_all('bath-capacity-item')
     
    if not items:
        return False
                
    for item in items:
        organization_id = item.get('organization-unit-id')
        bath_type = item.get('icon-name')

        bath_name_attr = item.get('bath-name')
        if bath_name_attr == "Sauna" or bath_name_attr == "Hallenbad":
            bath_name = get_bath_name_from_header(item_soup)
        else:
            bath_name = bath_name_attr
                    
        if organization_id and bath_type:
            has_extract = True

            data = {
                "id": int(organization_id),
                "name": bath_name,
                "type": bath_type,
            }
            result[data["id"]] = data
    
    return has_extract

def get_bath_name_from_header(item_soup: BeautifulSoup) -> str:

    item = item_soup.find('h1', class_='headline-xl')

    if item:
        return item.get_text()
    else:
        return "Unknown"

def log_and_save_results(data: dict):
    
    result_list = list(data.values())

    result_list.sort(key=lambda item : item['type'], reverse=True)
    result_list.sort(key=lambda item : item['name'])

    for item in result_list:
        print(f"Organization ID: {item['id']}, Bath Name: {item['name']}, Type: {item['type']}")
    
    print(f"Data extracted in total: {len(result_list)} items")

    with open("scraping_results.json", 'w', encoding='UTF-8') as jsonf:
        json.dump(result_list, jsonf, indent=4)

if __name__ == "__main__":
    
    print("--- Start Scraping SWM Websites ---")

    extracted_info = scrape_swm_bath_data()
    
    print("\n--- Scraping Complete ---")

    if extracted_info:

        log_and_save_results(extracted_info)
    
    else:
        print("No data was extracted.")