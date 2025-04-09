import argparse
import json
import os
import time

from tqdm import tqdm
import typesense

def wait_for_healthy(client):
    while True:
        try:
            health = client.operations.is_healthy()
            if health:
                print("Typesense service is healthy.")
                break
        except Exception as e:
            print(f"Waiting for Typesense service to be healthy: {e}")
        time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description='Load JSONL data into a Typesense collection.')
    parser.add_argument('jsonl_file', type=str, help='Path to the JSONL file')
    parser.add_argument('--batch-size', type=int, default=256, help='Number of documents to insert in each batch')
    parser.add_argument('--wait-for-healthy', action='store_true', help='Wait for Typesense service to be healthy before inserting data')
    args = parser.parse_args()

    api_key = os.getenv('TYPESENSE_API_KEY')
    if not api_key:
        raise ValueError("TYPESENSE_API_KEY environment variable is not set")

    client = typesense.Client({
        'nodes': [{
            'host': 'nginx',  
            'port': '80',       
            'protocol': 'http',
            'path': '/api'    
        }],
        'api_key': api_key,
        'connection_timeout_seconds': 2
    })

    if args.wait_for_healthy:
        wait_for_healthy(client)

    schema = {
        'name': 'documents',
        'fields': [
            {'name': 'local_path', 'type': 'string'},
            {'name': 'source', 'type': 'string'},
            {'name': 'title_id', 'type': 'string'},
            {'name': 'title_full', 'type': 'string'},
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