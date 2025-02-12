import argparse
import logging
import re

import requests_cache
import tqdm

import utils 

logging.basicConfig(level=logging.INFO)

SOURCE_ID = "digipress.digitale-sammlungen.de"
BASE_URL = "https://digipress.digitale-sammlungen.de"
CALENDAR_URL = "https://digipress.digitale-sammlungen.de/calendar/newspaper/{title_id}"

def extract_bsb_id(url):
    pattern = r'bsb\d+(_\d+)*_u\d+'
    match = re.search(pattern, url)
    if match:
        return match.group(0)
    else:
        return None

def get_calendar_hrefs(title_id, session):
    calendar_url = CALENDAR_URL.format(title_id=title_id)
    all_hrefs = utils.get_all_hrefs(calendar_url, session=session)
    year_hrefs = [BASE_URL + h for h in all_hrefs if ('calendar' in h and title_id in h)]
    all_calendar_hrefs = []
    for yh in year_hrefs:
        ah = utils.get_all_hrefs(yh, session=session)
        all_calendar_hrefs.extend(BASE_URL + h for h in ah if ('calendar' in h and title_id in h))
    
    all_calendar_hrefs = list(set(all_calendar_hrefs))

    return all_calendar_hrefs

def get_item_ids_from_calendar_hrefs(calendar_hrefs, session):
    all_item_hrefs = []
    
    for ch in calendar_hrefs:
        ah = utils.get_all_hrefs(ch, session=session)
        all_item_hrefs.extend(BASE_URL + h for h in ah if ('view' in h))

    dedup_item_hrefs = list(set(all_item_hrefs))
    return [extract_bsb_id(href) for href in dedup_item_hrefs]

def main():
    parser = argparse.ArgumentParser(description="Fetch item_ids for a given BSB title_id, via calendar entry point.")
    parser.add_argument("title_id", type=str, help="The title ID to fetch data for.")
    
    args = parser.parse_args()
    
    session = requests_cache.CachedSession("devel")
    calendar_hrefs = get_calendar_hrefs(title_id=args.title_id, session=session)
    item_ids = get_item_ids_from_calendar_hrefs(calendar_hrefs, session=session)

    item_ids.sort()
    for item_id in item_ids:
        print(item_id)
    return

if __name__ == "__main__":
    main()