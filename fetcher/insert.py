import argparse
import json
import os
import time

from tqdm import tqdm
import typesense

def insert(jsonl_file: str, client: typesense.Client, wait: bool = False, batch_size: int = 256):
    """
    Load data from JSONL file and insert it into Typesense collection.
    :param client: Typesense client
    :param wait: Wait for Typesense service to be healthy before inserting data
    """
    if wait:
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

    with open(jsonl_file, 'r') as f:
        lines = f.readlines()
        batch = []
        for line in tqdm(lines, desc="Loading data"):
            document = json.loads(line)
            batch.append(document)
            if len(batch) == batch_size:
                client.collections['documents'].documents.import_(batch)
                batch = []
        if batch:
            client.collections['documents'].documents.import_(batch)

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

def create_typesense_client(host, port, protocol, path, api_key):
    """
    Create and return a Typesense client instance
    :param host: Typesense host
    :param port: Typesense port
    :param protocol: Typesense protocol
    :param path: Typesense path
    :param api_key: Typesense API key
    """

    client = typesense.Client({
        'nodes': [{
            'host': host,
            'port': port,
            'protocol': protocol,
            'path': path
        }],
        'api_key': api_key,
        'connection_timeout_seconds': 2
    })
    
    return client

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    :return: Parsed arguments
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(description='Load JSONL data into a Typesense collection.')

    parser.add_argument('jsonl_file', type=str, help='Path to the JSONL file')
    parser = add_insert_args(parser)
    parser = add_typesense_args(parser)
    
    args = parser.parse_args()
    validate_typesense_args(args)

    if not os.path.exists(args.jsonl_file):
        raise FileNotFoundError(f"JSONL file '{args.jsonl_file}' does not exist.")

    return args

def add_insert_args(parser: argparse.ArgumentParser):
    """
    Add args for data insertion
    """
    parser.add_argument('--batch-size', type=int, default=256, help='Number of documents to insert in each batch')
    parser.add_argument('--wait-for-healthy', action='store_true', help='Wait for Typesense service to be healthy before inserting data')
    return parser

def add_typesense_args(parser: argparse.ArgumentParser):
    """
    Add Typesense-related arguments to the argument parser.
    :param parser: Argument parser
    """
    parser.add_argument('--api-key', type=str, help='Typesense API key', default=os.getenv('TYPESENSE_API_KEY'))
    parser.add_argument('--typesense-port', type=str, help='Typesense port', default=os.getenv('TYPESENSE_FETCHER_PORT'))
    parser.add_argument('--typesense-protocol', type=str, help='Typesense protocol', default=os.getenv('TYPESENSE_FETCHER_PROTOCOL'))
    parser.add_argument('--typesense-path', type=str, help='Typesense path', default=os.getenv('TYPESENSE_FETCHER_PATH'))
    parser.add_argument('--typesense-fetcher-host', type=str, help='Typesense fetcher host', default=os.getenv('TYPESENSE_FETCHER_HOST'))

    return parser

def validate_typesense_args(args):
    """
    Validate Typesense-related arguments.
    :param args: Parsed arguments
    """
    
    if not args.api_key:
        raise ValueError("TYPESENSE_API_KEY environment variable is not set or passed as --api-key")
    if not args.typesense_port:
        raise ValueError("TYPESENSE_FETCHER_PORT environment variable is not set or passed as --typesense-port")
    if not args.typesense_protocol:
        raise ValueError("TYPESENSE_FETCHER_PROTOCOL environment variable is not set or passed as --typesense-protocol")
    if not args.typesense_path:
        raise ValueError("TYPESENSE_FETCHER_PATH environment variable is not set or passed as --typesense-path")
    if not args.typesense_fetcher_host:
        raise ValueError("TYPESENSE_FETCHER_HOST environment variable is not set or passed as --typesense-fetcher-host")


if __name__ == '__main__':

    args = parse_args()

    client = create_typesense_client(
        host=args.typesense_fetcher_host,
        port=args.typesense_port,
        protocol=args.typesense_protocol,
        path=args.typesense_path,
        api_key=args.api_key
    )

    insert(args.jsonl_file, client, wait=args.wait_for_healthy, batch_size=args.batch_size)
    print("Data inserted into Typesense collection 'documents'.")
