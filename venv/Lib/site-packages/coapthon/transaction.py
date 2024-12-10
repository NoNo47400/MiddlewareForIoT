
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import threading

if TYPE_CHECKING:
	from coapthon.caching.cache import CacheElement
	from coapthon.messages.request import Request
	from coapthon.messages.response import Response
	from coapthon.resources.resource import Resource

__author__ = 'Giacomo Tanganelli'


class Transaction(object):
    """
    Transaction object to bind together a request, a response and a resource.
    """
    def __init__(self, request:Optional[Request]=None, response:Optional[Response]=None, resource:Optional[Resource]=None, timestamp:Optional[float]=None) -> None:
        """
        Initialize a Transaction object.

        :param request: the request
        :param response: the response
        :param resource: the resource interested by the transaction
        :param timestamp: the timestamp of the transaction
        """
        self._response = response
        self._request = request
        self._resource = resource
        self._timestamp:float = timestamp
        self._completed = False
        self._block_transfer = False
        self.notification = False
        self.separate_timer:Optional[threading.Timer] = None
        self.retransmit_thread:Optional[threading.Thread] = None
        self.retransmit_stop:Optional[threading.Event] = None
        self._lock = threading.RLock()

        self.cacheHit = False
        self.cached_element:Optional[CacheElement] = None

    def __enter__(self):	# type:ignore
        self._lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb): # type:ignore
        self._lock.release()

    @property
    def response(self) -> Response:
        """
        Return the response.

        :return: the response
        :rtype: Response
        """
        return self._response

    @response.setter
    def response(self, value:Response) -> None:
        """
        Set the response.

        :type value: Response
        :param value: the response to be set in the transaction
        """
        self._response = value

    @property
    def request(self) -> Request:
        """
        Return the request.

        :return: the request
        :rtype: Request
        """
        return self._request

    @request.setter
    def request(self, value:Request) -> None:
        """
        Set the request.

        :type value: Request
        :param value: the request to be set in the transaction
        """
        self._request = value

    @property
    def resource(self) -> Resource:
        """
        Return the resource.

        :return: the resource
        :rtype: Resource
        """
        return self._resource

    @resource.setter
    def resource(self, value:Resource) -> None:
        """
        Set the resource.

        :type value: Resource
        :param value: the resource to be set in the transaction
        """
        self._resource = value

    @property
    def timestamp(self) -> float:
        """
        Return the timestamp.

        :return: the timestamp
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, t:float) -> None:
        """
        Set the timestamp.

        :param t: the timestamp of the transaction
        """
        self._timestamp = t

    @property
    def completed(self) -> bool:
        """
        Return the completed attribute.

        :return: True, if transaction is completed
        """
        return self._completed

    @completed.setter
    def completed(self, b:bool) -> None:
        """
        Set the completed attribute.

        :param b: the completed value
        :type b: bool
        """
        # assert isinstance(b, bool)
        self._completed = b

    @property
    def block_transfer(self) -> bool:
        """
        Return the block_transfer attribute.

        :return: True, if transaction is blockwise
        """
        return self._block_transfer

    @block_transfer.setter
    def block_transfer(self, b:bool) -> None:
        """
        Set the block_transfer attribute.

        :param b: the block_transfer value
        :type b: bool
        """
        # assert isinstance(b, bool)
        self._block_transfer = b
