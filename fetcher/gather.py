import argparse
import os
import json
from abo import ABODataSource
from mdz import MDZDataSource
from anno import AnnoDataSource

DATA_DIRECTORY = "data"

def process_file(file_path):
    """Process a single file based on its source."""
    source = file_path.split(os.sep)[1]
    if source == "anno.onb.ac.at":
        return AnnoDataSource.process(file_path, DATA_DIRECTORY)
    elif source == "api.digitale-sammlungen.de":
        return MDZDataSource.process(file_path, DATA_DIRECTORY)
    elif source == "iiif.onb.ac.at":
        return ABODataSource.process(file_path, DATA_DIRECTORY)
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .txt files and produce line-delimited JSON output.")
    parser.add_argument("files", nargs='+', help="List of .txt files to process.")
    args = parser.parse_args()

    for file_path in args.files:
        json_nl = process_file(file_path)
        if json_nl:
            print(json.dumps(json_nl))
