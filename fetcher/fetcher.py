import argparse
import logging
import json
import yaml
import glob

from tqdm import tqdm

import insert
import gather

from mdz import MDZDataSource
from abo import ABODataSource
from anno import AnnoDataSource
from bsb import BSBDataSource
from datasource import DataSource

from concurrent.futures import ThreadPoolExecutor, as_completed

def get_items(yaml_file: str):
    """
    Retrieve and save items listed in the provided sources YAML file
    """
    with open(yaml_file, 'r') as file:
        sources = yaml.safe_load(file)

    # Map YAML source names to their respective DataSource implementations
    fetcher_classes: dict[str, type[DataSource]] = {
        "mdz": MDZDataSource,
        "abo": ABODataSource,
        "anno": AnnoDataSource,
        "bsb": BSBDataSource
    }

    for source in sources:
        logging.info(f"Processing source: {source}")
        source_class = fetcher_classes[source]() # type: ignore

        for title_id in sources[source]['title_ids']:
            tid = sources[source]['title_ids']
            logging.info(f"Fetching data for title ID: {title_id}")

            # MDZ, ABO
            if isinstance(tid, list):
                source_class.fetch(title_id)
            # ANNO has extra metadata for min/max
            elif isinstance(tid, dict):
                source_class.fetch(title_id, *tid[title_id].values())

def run_gather(batch):
    """
    Ingest a list of .txt files and process into JSON lines.
    Used by ThreadPoolExecutor to parallelize the processing in convert_files_to_jsonl.

    :param batch: List of file paths to process
    :return: List of JSON lines
    """

    # Process each file in the batch and collect JSON lines
    lines = []
    for file_path in batch:
        json_nl = gather.process_file(file_path)
        if json_nl:
            # If process_file returns a dict, append as JSON line
            lines.append(json.dumps(json_nl) + "\n")
    return lines


def convert_files_to_jsonl(filename: str = 'data/all.jsonl', batch_size: int = 64, max_workers: int = 4):
    """
      Find all .txt files under 'data' directory and save them to all.jsonl
        in chunks of 64 files.
    """
    def chunked(iterable, n):
        """Yield successive n-sized chunks from iterable."""
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]
            
    files = glob.glob('data/**/*.txt', recursive=True)
    logging.info(f"{len(files)} files to process")
    total = len(files)

    with ThreadPoolExecutor(max_workers=max_workers) as executor, open(filename, 'w') as outfile:
        futures = [executor.submit(run_gather, batch) for batch in chunked(files, batch_size)]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Converting JSONL"):
            try:
                output = future.result()
                outfile.writelines(output)
                
                total = total - batch_size if total > batch_size else 0
                logging.debug(output[-1][:120]) # log first 120 chars of last entry
                logging.info(f"{len(files)-total}/{len(files)} files")
                
            except Exception as e:
                logging.error("Error converting file")
                logging.error(e)
                logging.error(e.__traceback__)

    logging.info(f"{len(files)} files gathered into {filename}")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    :return: Parsed arguments
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(description='Download data, parse, and insert into a Typesense collection.')
    
    parser.add_argument('yaml_file', type=str, help='Path to the YAML file to configure sources')
    parser.add_argument('--jsonl_file', type=str, default='data/all.jsonl', help='Path to the JSONL file to write and use')
   
    parser = insert.add_insert_args(parser)
    parser = insert.add_typesense_args(parser)

    args = parser.parse_args()
    insert.validate_typesense_args(args)

    return args

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    args = parse_args()

    get_items(args.yaml_file)
    convert_files_to_jsonl(filename=args.jsonl_file, batch_size=args.batch_size)

    client = insert.create_typesense_client(
        host=args.typesense_fetcher_host,
        port=args.typesense_port,
        protocol=args.typesense_protocol,
        path=args.typesense_path,
        api_key=args.api_key
    )
    
    insert.insert(
        jsonl_file=args.jsonl_file,
        client=client,
        wait=args.wait_for_healthy,
        batch_size=args.batch_size
    )

