from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
	from coapthon.caching.cache import CacheKey, CacheElement

from cachetools import Cache # type: ignore

__author__ = 'Emilio Vallati'
class CoapCache:
    def __init__(self, max_dim:int) -> None:
        """

        :param max_dim:
        """
        self.cache:Optional[Cache] = None

    def update(self, key:CacheKey, element:CacheElement) -> None:
        """

        :param key:
        :param element:
        :return:
        """
        raise NotImplementedError

    def get(self, key:CacheKey) -> CacheElement:
        """

        :param key:
        :return: CacheElement
        """
        raise NotImplementedError

    def is_full(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def is_empty(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def debug_print(self) -> str:
        """

        :return:
        """
        raise NotImplementedError
