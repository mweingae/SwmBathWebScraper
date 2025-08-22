# SwmBathWebScraper

A Python-based web scraper designed to extract information about swimming and sauna facilities (baths) from the Stadtwerke München (SWM) website. This tool helps monitor and collect data about Munich's public baths.

## Features

- Scrapes bath information from all SWM facility pages
- Extracts essential details including:
  - Organization ID
  - Bath name
  - Bath type (e.g., indoor pool, sauna)
- Handles different types of bath pages (regular pools, saunas, indoor pools)
- Saves data in a structured JSON format
- Scrapped data is also logged over console

## Requirements

- Python 3.8+
- Required packages (listed in `requirements.txt`):
  - requests
  - beautifulsoup4

## Usage

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the scraper:
   ```bash
   python scrape_bath_pages.py
   ```

The script will:
1. Crawl through all bath category pages
2. Extract information from each individual bath page
3. Save the collected data to a JSON file
4. Display a summary of the extracted data in the console

## Output

The data is saved in JSON format with the following structure:
```json
[
    {
        "id": <organization-unit-id>,
        "name": <bath-name>,
        "type": <bath-type>
    },
    ...
]
```
