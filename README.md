# tgv-prototype

A prototype application to support TGV bid

## Overview

The project consists of three parts

- a set of scripts to get OCR data and related metadata from a variety of holding libraries (in `fetcher/`)
- scripts to populate a search backend using Typesense (`fetcher/insert.py`)
- a demo frontend against the Typesense API  (`frontend/`)

It is supported by a number of utility functions (`fetcher/utils.py`)

Most functionality in the Python scripts can be used either as a module or from the command-line.

It is accompanied by files which specify a containerised application, split over `./compose.yml` and the Dockerfiles in `docker/`.

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

`insert.py` deletes any existing Typesense collection, creates a new one, and inserts the documents from the JSON file into the search backend.

### Search frontend

I include a very simple demonstration (thanks to Copilot for Business) of how Typesense integration might look on the frontend. We certainly want to use snippets/highlighted "hits", [which Typesense supports](https://typesense.org/docs/27.1/api/search.html#results-parameters:~:text=wasted%20CPU%20cycles.-,highlight_fields,-no).

## Usage

### Install/Setup

0. Create a `.env` file (see samples below)
1. Run `docker-compose up` from the root of the project directory
2. Visit application at localhost:80

### Development 

Some useful commands

- `docker-compose build --no-cache [SERVICE_NAME]` to rebuild images from scratch
- `docker-compose up --recreate [SERVICE_NAME]` to start application and/or individual services (and their dependencies), recreating the containers without rebuilding the images. Useful if `compose.yml` has changed.

It is important to keep track of when environment variables are being "injected" into the application. Sometimes it is done during the image build and other times it is done during runtime.

#### Sample `.env` file for local testing

```bash
TYPESENSE_API_KEY=
# The hostname for typesense as viewed by the frontend
TYPESENSE_HOST=localhost
# The hostname for typesense as viewed by ngnix (working as a reverse proxy within the Docker network)
TYPESENSE_UPSTREAM_HOST=typesense
# The hostname for typesense as viewed by the python-fetcher service (which goes via the reverse proxy)
TYPESENSE_FETCHER_HOST=nginx
TYPESENSE_PORT=80
TYPESENSE_PROTOCOL=http
TYPESENSE_PATH="/api"

```

#### Sample `.env` file for deployment to AWH

UNTESTED!

```bash
TYPESENSE_API_KEY=
TYPESENSE_HOST=
TYPESENSE_UPSTREAM_HOST=localhost
TYPESENSE_FETCHER_HOST=localhost
TYPESENSE_PORT=80
TYPESENSE_PROTOCOL=https
TYPESENSE_PATH="/api"
```

#### Fetching and loading the full corpus

Currently, the application fetches, gathers, and loads a very small sample of the total corpus, which is useful for testing purposes. To load the full corpus, make changes to `docker/Dockerfile.python-fetcher` so that it resembles the below:

```dockerfile
...
RUN chmod +x /app/get_items.sh
RUN /app/get_items.sh
...
```

## Design

There are three services defined in compose.yml:

- `nginx`
- `python-fetcher`
- `typesense`

`nginx` hosts the frontend and reverse proxies `/api` to `/` in `typesense`. 

The frontend served by `nginx` needs to have an API key to authenticate requests to `typesense` (which also needs to know this API key when launched). This is all arranged in the relevant Dockerfiles, and uses key-value pairs set in `.env` (which is not checked into source control). 

`typesense` is the database and is available over HTTP within the docker network `alpha` (this is largely irrelevant for now).

`python-fetcher` retrieves the data, post-processes it and produces an image containing the data in JSONL format. Every time the container is launched, it inserts the documents from this JSONL file into `typesense` via HTTP. It deletes any existing collections before doing so.

### Notes for deployment to AWH

There are some things to note before deployment to AHW given the "sidecar" pattern:

- `fetcher/insert.py` assumes that the database (Typesense) is available at `nginx` (hard-coded for the moment)
- `frontend` assumes that the database API is available at `${TYPESENSE_HOST}:${TYPESENSE_PORT}` under `${TYPESENSE_PATH}` (typically `/api`)
- `nginx` assumes that `typesense` makes its HTTP API available at on `$TYPESENSE_UPSTREAM_HOST}` at port 8081, which is referenced in `nginx.conf`
    - This implies that `TYPESENSE_UPSTREAM_HOST` needs changing when deploying to AHW 