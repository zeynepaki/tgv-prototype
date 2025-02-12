import argparse
import json
import os

from tqdm import tqdm
import typesense

def main():
    parser = argparse.ArgumentParser(description='Load JSONL data into a Typesense collection.')
    parser.add_argument('jsonl_file', type=str, help='Path to the JSONL file')
    parser.add_argument('--batch-size', type=int, default=256, help='Number of documents to insert in each batch')
    args = parser.parse_args()

    api_key = os.getenv('TYPESENSE_API_KEY')
    if not api_key:
        raise ValueError("TYPESENSE_API_KEY environment variable is not set")

    client = typesense.Client({
        'nodes': [{
            'host': 'localhost',  
            'port': '8108',       
            'protocol': 'http'    
        }],
        'api_key': api_key,
        'connection_timeout_seconds': 2
    })

    schema = {
        'name': 'documents',
        'fields': [
            {'name': 'local_path', 'type': 'string'},
            {'name': 'source', 'type': 'string'},
            {'name': 'title_id', 'type': 'string'},
            {'name': 'datum', 'type': 'string', 'optional': True},
            {'name': 'page_number', 'type': 'string'},
            {'name': 'remote_path', 'type': 'string'},
            {'name': 'image_url', 'type': 'string'},
            {'name': 'ocr_text_original', 'type': 'string', 'locale': 'de'},
            {'name': 'ocr_text_stripped', 'type': 'string', 'locale': 'de'},
        ]
    }

    # Delete the collection if it already exists
    try:
        client.collections['documents'].delete()
        print("Existing collection 'documents' deleted.")
    except typesense.exceptions.ObjectNotFound:
        print("Collection 'documents' does not exist. Creating a new one.")

    client.collections.create(schema)

    with open(args.jsonl_file, 'r') as f:
        lines = f.readlines()
        batch = []
        for line in tqdm(lines, desc="Loading data"):
            document = json.loads(line)
            batch.append(document)
            if len(batch) == args.batch_size:
                client.collections['documents'].documents.import_(batch)
                batch = []
        if batch:
            client.collections['documents'].documents.import_(batch)

if __name__ == '__main__':
    main()
