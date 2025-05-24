from abc import ABC, abstractmethod
from typing import Any, Iterator, List

import requests_cache

class DataSource(ABC):
    """
    Abstract base class for data sources.
    """

    @abstractmethod
    def __init__(self, source_id: str, cache_name: str = "devel"):
        """
        Initialize the data source
        :param cache_name: Name of the cache for requests
        """
        self.session = requests_cache.CachedSession(cache_name)
        self.source_id = source_id

    @abstractmethod
    def fetch(self, item_id: str):
        """
        Fetch data from the data source based on an item_id query.
        """
        pass
