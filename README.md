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

0. Create a `.env` file with `TYPESENSE_API_KEY=` and your choice of key
1. Run `docker-compose up` from the root of the project directory
2. Change the API key in `frontend/index.html` to match the key (TODO: Use envsubst)
3. Visit application at localhost:80

## Design

TODO