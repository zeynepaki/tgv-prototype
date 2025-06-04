from datasource import DataSource

import logging
import re

import utils 

SOURCE_ID = "digipress.digitale-sammlungen.de"

class BSBDataSource(DataSource):
    """
    Data source for BSB (Bayerische Staatsbibliothek) IDs.
    """

    def __init__(self, 
                 source_id: str = SOURCE_ID, 
                 cache_name: str = "devel"):
        """
        Initialize the data source
        :param source_id: Source ID for the data source
        :param cache_name: Name of the cache for requests
        """
        self.source_id = source_id
        self.base_url = f"https://{source_id}"
        self.calendar_url = self.base_url + "/calendar/newspaper/{title_id}"

        super().__init__(source_id=source_id, cache_name=cache_name)
        
    def fetch(self, title_id: str):
        calendar_hrefs = self._get_calendar_hrefs(title_id=title_id)
        item_ids = self._get_item_ids_from_calendar_hrefs(calendar_hrefs)

        item_ids.sort()

        for item_id in item_ids:
            print(item_id)

    def _extract_bsb_id(self, url) -> str | None:
        pattern = r'bsb\d+(_\d+)*_u\d+'
        match = re.search(pattern, url)
        if match:
            return match.group(0)
        else:
            return None

    def _get_calendar_hrefs(self, title_id) -> list[str]:
        calendar_url = self.calendar_url.format(title_id=title_id)
        all_hrefs = utils.get_all_hrefs(calendar_url, session=self.session)
        year_hrefs = [self.base_url + h for h in all_hrefs if ('calendar' in h and title_id in h)]
        all_calendar_hrefs = []
        for yh in year_hrefs:
            ah = utils.get_all_hrefs(yh, session=self.session)
            all_calendar_hrefs.extend(self.base_url + h for h in ah if ('calendar' in h and title_id in h))
        
        all_calendar_hrefs = list(set(all_calendar_hrefs))

        return all_calendar_hrefs

    def _get_item_ids_from_calendar_hrefs(self, calendar_hrefs) -> list[str]:
        all_item_hrefs = []
        
        for ch in calendar_hrefs:
            ah = utils.get_all_hrefs(ch, session=self.session)
            all_item_hrefs.extend(self.base_url + h for h in ah if ('view' in h))

        dedup_item_hrefs = list(set(all_item_hrefs))
        hrefs = [self._extract_bsb_id(href) for href in dedup_item_hrefs]
        return [h for h in hrefs if h is not None]
    
    @staticmethod
    def process(file_path, data_directory):
        pass


if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Fetch item_ids for a given BSB title_id, via calendar entry point.")
    parser.add_argument("title_id", type=str, help="Title ID to fetch data for.")
    args = parser.parse_args()

    data_source = BSBDataSource(source_id=SOURCE_ID)
    data_source.fetch(args.title_id)
    