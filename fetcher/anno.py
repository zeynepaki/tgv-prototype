import argparse
import logging
import os

import requests_cache
import tqdm

import utils 

logging.basicConfig(level=logging.INFO)

SOURCE_ID = "anno.onb.ac.at"
BASE_URL = "https://anno.onb.ac.at"
TEXT_URL = "https://anno.onb.ac.at/cgi-content/annoshow?text={title_id}|{datum}|{page_number}"
IMAGE_URL= "https://anno.onb.ac.at/cgi-content/annoshow?call={title_id}|{datum}|{page_number}|{zoom_level}"

def get_valid_datums(title_id, session):
    TITLE_BASE = "/cgi-content/anno?apm=0&aid={}".format(title_id)
    title_url = BASE_URL + TITLE_BASE
    all_hrefs = utils.get_all_hrefs(title_url, session=session)
    year_hrefs = [BASE_URL + h for h in all_hrefs if ('datum=' in h)]
    
    all_ymd_hrefs = []
    for yh in year_hrefs:
        ah = utils.get_all_hrefs(yh, session=session)
        all_ymd_hrefs.extend(h for h in ah if ('datum=' in h))

    valid_datums = [utils.get_query_value(u, key='datum') for u in all_ymd_hrefs]
    
    valid_datums = list(set(valid_datums))

    return valid_datums

def get_text_for_datum(title_id, datum, page_number, session):
    vd_uri = TEXT_URL.format(title_id=title_id, datum=datum, page_number='x')
    folder = f"data/{SOURCE_ID}/{title_id}/{datum}/txt"
    path_on_disk = folder + '/' + f"{SOURCE_ID}_{title_id}_{datum}.txt"
    utils.download_remote_file(vd_uri, path=path_on_disk, session=session)
    return path_on_disk

def main():
    parser = argparse.ArgumentParser(description="Fetch text for a given title_id and optional date range.")
    parser.add_argument("title_id", type=str, help="The title ID to fetch data for.")
    parser.add_argument("--min", type=str, help="The minimum date in YYYYMMDD format.", default=None)
    parser.add_argument("--max", type=str, help="The maximum date in YYYYMMDD format.", default=None)
    parser.add_argument("--list-available", action="store_true", help="List all valid datums in alphabetical order.")
    
    args = parser.parse_args()
    
    session = requests_cache.CachedSession("devel")
    valid_datums = get_valid_datums(title_id=args.title_id, session=session)
    
    if args.min:
        valid_datums = [d for d in valid_datums if d >= args.min]
    if args.max:
        valid_datums = [d for d in valid_datums if d <= args.max]
    
    if args.list_available:
        valid_datums.sort()
        for datum in valid_datums:
            print(datum)
        return
    
    folder = f"data/{SOURCE_ID}/{args.title_id}"
    os.makedirs(folder, exist_ok=True)

    already = utils.list_directories(folder)
    
    for vd in tqdm.tqdm(valid_datums):
        if vd not in already:
            path_on_disk = get_text_for_datum(title_id=args.title_id, datum=vd, page_number='x', session=session)
            utils.split_anno_x_file(path_on_disk, folder + '/' + vd + '/txt')
            utils.delete_file(path_on_disk)
        else:
            continue

if __name__ == "__main__":
    main()