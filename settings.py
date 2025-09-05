"""Configuration settings for the bath scraper"""

BASE_URL = "https://www.swm.de"
MAIN_BATHS_PAGE = f"{BASE_URL}/baeder"
CATEGORY_SUB_PAGES = [
    "hallenbaeder-muenchen",
    "saunen-muenchen", 
    "freibaeder-muenchen"
]
BATH_CAPACITY_ITEM = 'bath-capacity-item'
BATH_TYPE_SAUNA = "Sauna"
BATH_TYPE_HALLENBAD = "Hallenbad"
HEADER_CLASS = 'headline-xl'
OUTPUT_FILE_PREFIX = "scraping_results_"
