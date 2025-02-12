import argparse
import json
import logging
import os

import requests_cache
import tqdm

import utils

SOURCE_ID = "api.digitale-sammlungen.de"
IIIF_MANIFEST_URL = "https://api.digitale-sammlungen.de/iiif/presentation/v2/{id}/manifest"

def download_hocr_files(item_id, output_dir, session):
    os.makedirs(output_dir, exist_ok=True)

    manifest_url = IIIF_MANIFEST_URL.format(id=item_id)
    print(manifest_url)    
    manifest = session.get(manifest_url).json()
    
    json_dir = os.path.join(output_dir, 'json')
    os.makedirs(json_dir, exist_ok=True)
    manifest_filename = os.path.join(json_dir, 'manifest.json')
    with open(manifest_filename, 'w', encoding='utf-8') as manifest_file:
        json.dump(manifest, manifest_file, ensure_ascii=False, indent=4)

    hocr_dir = os.path.join(output_dir, 'hocr')
    os.makedirs(hocr_dir, exist_ok=True)
    
    for sequence in manifest['sequences']:
        for canvas in tqdm.tqdm(sequence['canvases'], desc=f"Downloading {item_id}"):
            label = canvas['label']
            hocr_url = canvas['seeAlso']['@id']
            
            hocr_response = session.get(hocr_url)
            hocr_filename = os.path.join(hocr_dir, f"{label}.hocr")
            
            with open(hocr_filename, 'wb') as file:
                file.write(hocr_response.content)
            
            logging.info(f"Downloaded HOCR file for {label} to {hocr_filename}")

def main():
    parser = argparse.ArgumentParser(description="Download HOCR files for a given item ID.")
    parser.add_argument("item_id", type=str, help="The item ID to download HOCR files for.")
    args = parser.parse_args()

    session = requests_cache.CachedSession("devel")

    item_id = args.item_id
    
    item_dir = os.path.join('data', SOURCE_ID)
    os.makedirs(item_dir, exist_ok=True)        

    already = utils.list_directories(f"data/{SOURCE_ID}")
    if item_id not in already:
        item_dir = os.path.join('data', SOURCE_ID, item_id)
        os.makedirs(item_dir, exist_ok=True)
        download_hocr_files(item_id=item_id, output_dir=item_dir, session=session)
    
        input_dir = os.path.join(item_dir, 'hocr')
        output_dir = os.path.join(item_dir, 'txt')
        os.makedirs(output_dir, exist_ok=True)
        utils.convert_all_hocr_files(input_dir, output_dir)

if __name__ == "__main__":
    main()
