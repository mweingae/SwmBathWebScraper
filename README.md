# SwmBathWebScraper

A Python-based web scraper designed to extract information about swimming and sauna facilities (baths) from the Stadtwerke München (SWM) website. This tool helps monitor and collect data about Munich's public baths.

## Features

- Scrapes bath information from all SWM facility pages
- Extracts essential details including:
  - Organization ID
  - Bath name
  - Bath type (e.g., indoor pool, sauna)
- Handles different types of bath pages (regular pools, saunas, indoor pools)
- Saves data in a structured CSV format with date-stamped filenames
- Console logging of the scraping process

## Data Processing

The scraper includes data processing features:
- Consolidation of duplicate entries
- Resolution of unknown facility names
- Removal of redundant suffixes (e.g., " – Hallenbad und Sauna")
- Sorting of results by name and type

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
3. Process and consolidate the collected data
4. Save the results to a CSV file with the current date
5. Display a summary of the extracted data in the console

## Output

The data is saved in CSV format with the following columns:
- id: Organization unit ID
- name: Bath facility name (cleaned and standardized)
- type: Facility type (e.g., Sauna, Hallenbad)

The output filename includes the current date in ISO format:
Example: `scraping_results_2025-09-05.csv`
