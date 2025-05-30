import argparse
import os
import json

import utils

DATA_DIRECTORY = "data"

def process_anno_onb_ac_at(file_path):
    SOURCE_ID = "anno.onb.ac.at"
    TEXT_URL = "https://anno.onb.ac.at/cgi-content/annoshow?text={title_id}|{datum}|{page_number}"
    IMAGE_URL= "https://anno.onb.ac.at/cgi-content/annoshow?call={title_id}|{datum}|{page_number}|{zoom_level}"

    TITLE_MAP = {
        'sam': 'Der Sammler. Ein Unterhaltungsblatt',
        'vlb': 'Vaterländische Blätter'
    }

    parts = file_path.split(os.sep)
    title_id = parts[2]
    datum = parts[3]
    page_number = parts[-1].split('.')[0]

    remote_path = TEXT_URL.format(title_id=title_id, datum=datum, page_number=page_number)
    image_url = IMAGE_URL.format(title_id=title_id, datum=datum, page_number=page_number, zoom_level='100')

    ocr_text = utils.read_multi_encoding(file_path)
    ocr_text_stripped = utils.remove_newlines(ocr_text)

    return {
        "local_path": file_path,
        "source": SOURCE_ID,
        "title_id": title_id,
        "title_full": TITLE_MAP[title_id],
        "datum": datum,
        "page_number": page_number,
        "remote_path": remote_path,
        "image_url": image_url,
        "ocr_text_original": ocr_text,
        "ocr_text_stripped": ocr_text_stripped,
    }

def process_api_digitale_sammlungen_de(file_path):
    SOURCE_ID = "api.digitale-sammlungen.de"
    
    parts = file_path.split(os.sep)
    title_id = parts[2]
    label = parts[-1].split('.')[0]

    with open(os.path.join(DATA_DIRECTORY, SOURCE_ID, title_id, 'json', 'manifest.json'), 'r', encoding='utf-8') as file:
        manifest = json.load(file)
    
    title_full = manifest['label']

    remote_path = None
    image_url = None
    for sequence in manifest['sequences']:
        for canvas in sequence['canvases']:
            if label == canvas['label']:
                remote_path = canvas['seeAlso']['@id']
                for image in canvas['images']:
                    original_image_url = image['resource']['@id']
                    image_url = original_image_url.replace('/full/full/', '/full/2400,/')
                    break
    
    with open(file_path, 'r') as file:
        ocr_text = file.read()

    ocr_text_stripped = utils.remove_newlines(ocr_text)

    return {
        "local_path": file_path,
        "source": SOURCE_ID,
        "title_id": title_id,
        "title_full": title_full,
        "page_number": label,
        "remote_path": remote_path,
        "image_url": image_url,
        "ocr_text_original": ocr_text,
        "ocr_text_stripped": ocr_text_stripped,
    }


def process_iiif_onb_ac_at(file_path):
    SOURCE_ID = "iiif.onb.ac.at"

    parts = file_path.split(os.sep)
    title_id = parts[3]
    project_id = parts[2]
    label = parts[-1].split('.')[0]

    with open(os.path.join(DATA_DIRECTORY, SOURCE_ID, project_id, title_id, 'json', 'manifest.json'), 'r', encoding='utf-8') as file:
        manifest = json.load(file)
    
    title_full = manifest['label']

    remote_path = None
    image_url = None
    for sequence in manifest['sequences']:
        for canvas in sequence['canvases']:
            if label == canvas['label']:
                for content in canvas.get('otherContent', []):
                    for resource in content.get('resources', []):
                        if resource['resource']['format'] == 'text/plain':
                            remote_path = resource['resource']['@id']
                            break
                for image in canvas['images']:
                    original_image_url = image['resource']['@id']
                    image_url = original_image_url.replace('/full/full/', '/full/,2400/')
                    break

    with open(file_path, 'r') as file:
        ocr_text = file.read()

    ocr_text_stripped = utils.remove_newlines(ocr_text)

    return {
        "local_path": file_path,
        "source": SOURCE_ID,
        "title_id": title_id,
        "title_full": title_full,
        "page_number": label,
        "remote_path": remote_path,
        "image_url": image_url,
        "ocr_text_original": ocr_text,
        "ocr_text_stripped": ocr_text_stripped,
    }

def process_file(file_path):
    """Process a single file based on its source."""
    source = file_path.split(os.sep)[1]
    if source == "anno.onb.ac.at":
        return process_anno_onb_ac_at(file_path)
    elif source == "api.digitale-sammlungen.de":
        return process_api_digitale_sammlungen_de(file_path)
    elif source == "iiif.onb.ac.at":
        return process_iiif_onb_ac_at(file_path)
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Process .txt files and produce line-delimited JSON output.")
    parser.add_argument("files", nargs='+', help="List of .txt files to process.")
    args = parser.parse_args()

    for file_path in args.files:
        json_nl = process_file(file_path)
        if json_nl:
            print(json.dumps(json_nl))

if __name__ == "__main__":
    main()
