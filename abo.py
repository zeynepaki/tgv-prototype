import argparse
import json
import logging
import os

import requests_cache
import tqdm

import utils

PROJECT_ID = "ABO"
SOURCE_ID = "iiif.onb.ac.at"
IIIF_MANIFEST_URL = "https://iiif.onb.ac.at/presentation/{project}/{id}/manifest"

def download_files(item_id, output_dir, session, resource_format):
    os.makedirs(output_dir, exist_ok=True)

    manifest_url = IIIF_MANIFEST_URL.format(project=PROJECT_ID, id=item_id)
    print(manifest_url)    
    manifest = session.get(manifest_url).json()
    
    json_dir = os.path.join(output_dir, 'json')
    os.makedirs(json_dir, exist_ok=True)
    manifest_filename = os.path.join(output_dir, 'json', 'manifest.json')
    with open(manifest_filename, 'w', encoding='utf-8') as manifest_file:
        json.dump(manifest, manifest_file, ensure_ascii=False, indent=4)
    
    for sequence in manifest['sequences']:
        for canvas in tqdm.tqdm(sequence['canvases']):
            label = canvas['label']
            for content in canvas.get('otherContent', []):
                for resource in content.get('resources', []):
                    resource_id = resource['resource']['@id']
                    format = resource['resource']['format']
                    
                    if format == resource_format:
                        response = session.get(resource_id)
                        extension = 'txt' if resource_format == 'text/plain' else 'html'

                        ext_dir = os.path.join(output_dir, extension)
                        os.makedirs(ext_dir, exist_ok=True)
                        
                        filename = os.path.join(output_dir, extension, f"{label}.{extension}")
                        
                        with open(filename, 'wb') as file:
                            file.write(response.content)
                        
                        logging.info(f"Downloaded {extension.upper()} file for {label} to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Download HOCR files for given item IDs.")
    parser.add_argument("item_ids", type=str, nargs='+', help="The item IDs to download HOCR files for.")
    args = parser.parse_args()

    session = requests_cache.CachedSession("devel")

    item_ids = args.item_ids
    
    for item_id in item_ids:
        item_dir = os.path.join('data', SOURCE_ID, PROJECT_ID)
        os.makedirs(item_dir, exist_ok=True)        

        already = utils.list_directories(f"data/{SOURCE_ID}/{PROJECT_ID}")
        if item_id not in already:
            item_dir = os.path.join('data', SOURCE_ID, PROJECT_ID, item_id)
            
            os.makedirs(item_dir, exist_ok=True)
            download_files(item_id=item_id, output_dir=item_dir, resource_format="text/plain", session=session)
    
if __name__ == "__main__":
    main()