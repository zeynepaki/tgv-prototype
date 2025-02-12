# tgv-prototype

A prototype application to support TGV bid

## Overview

The project consists of three parts

- a set of scripts to get OCR data and related metadata from a variety of holding libraries
- scripts to populate a search backend using Typesense
- a demo frontend against the Typesense API.

It is supported by a number of utility functions.

Most functionality in the Python scripts can be used either as a module or from the command-line.

Typesense hostname, port, and API key needs to be set across a number of scripts.

### Data and metadata retrieval 

Supported sources

- anno.onb.ac.at (`anno.py`)
- api.digitale-sammlungen.de (`mdz.py`)
- iiif.onb.ac.at/ABO (`abo.py`)

We also support gathering `digitale-sammlungen.de` item IDs from the BSB calendar pages (e.g. https://digipress.digitale-sammlungen.de/calendar/newspaper/bsbmult00000129). This functionality is in `bsb.py` and produces item IDs that can be used with the `mdz.py` script. It is currently not working correctly.

`gather.py` takes the `.txt` files produced by each of these retrievers and produces a single newline delimited JSON file, which can be then loaded into the search backend.

We used `requests_cache` during development to help reduce the number of requests to remote servers. 

### Search backend

Requires a working installation of Typesense. A `compose.yml` to use with e.g. Docker Compose is provided for convenience.

`insert.py` deletes any exisiting Typesense collection, creates a new one, and inserts the documents from the JSON file into the search backend.

### Search frontend

I include a very simple demonstration (thanks to Copilot for Business) of how Typesense integration might look on the frontend. We certainly want to use snippets/highlighted "hits", [which Typesense supports](https://typesense.org/docs/27.1/api/search.html#results-parameters:~:text=wasted%20CPU%20cycles.-,highlight_fields,-no).

## Usage

### Install/Setup

1. Create a `virtualenv` (tested with Python 3.10.13) and install Python dependencies in `requirements.txt`
2. Activate the virtual environment
3. Set the shell environment variable `TYPESENSE_API_KEY` to a strong secret
4. Run `docker-compose up` from the root of the project directory
5. (if using) Change the API key in `frontend/index.html` to match the strong secret
6. (if using) Serve the frontend from the root of `./frontend`

### Retrieve

Use the scripts `anno.py`, `mdz.py`, and `abo.py` to retrieve data from these sources. The data will be in `data`. Each `.txt` file corresponds to a page of a source.

To replicate the corpus from the original study, run the commands in `get_items.sh`. Alternatively, the pre-downloaded corpus can be found on Teams/OneDrive (untar into `./data`).

It should be fine to work with a small subset of these for development purposes. 

### Gather

Once all sources are downloaded, run `gather.py`, which takes as argument(s) a path to a text. 

I use GNU Parallel to quickly do this e.g. (from the project root directory):

```bash
find data -type f -name "*.txt" | parallel -j 4 -N 64 --bar python gather.py > all.jsonl
```

We do this because later on we might like to "enrich" the records with various bits of post-processing unrelated to their collection.

### Insert

Finally, use `insert.py`, which takes a path to a newline-delimited JSONL file and inserts each record into the running Typesense instance. For example,

```bash
python insert.py all.jsonl
```