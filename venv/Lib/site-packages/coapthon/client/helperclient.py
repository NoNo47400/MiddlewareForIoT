#
#	helperclient.py
#
#	This is a patched version of the CoAPthon client/helperclient.py file.
#
#	Original auhtor: Giacomo Tanganelli
#	Patches by: Andreas Kraft
#
#	see https://github.com/Tanganelli/CoAPthon3
#
#
#	Overview about the patches:
#
#	- Fixed: when receiving a response, the response is put back into the queue if the response is not for the request (.mid attribute)
#

from __future__ import annotations
from typing import Callable, Any, Optional

import random
# from multiprocessing import Queue
from queue import Queue	# akr replace with a normal queue
from queue import Empty

import socket
import threading
from coapthon.messages.message import Message
from coapthon import defines
from coapthon.client.coap import CoAP
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.utils import generate_random_token

__author__ = 'Giacomo Tanganelli'


class HelperClient(object):
    """
    Helper Client class to perform requests to remote servers in a simplified way.
    """
    def __init__(self, server:defines.ServerT, sock:socket.socket=None, cb_ignore_read_exception:Callable=None, cb_ignore_write_exception:Callable=None) -> None:
        """
        Initialize a client to perform request to a server.

        :param server: the remote CoAP server
        :param sock: if a socket has been created externally, it can be used directly
        :param cb_ignore_read_exception: Callback function to handle exception raised during the socket read operation
        :param cb_ignore_write_exception: Callback function to handle exception raised during the socket write operation 
        """
        self.server = server
        self.protocol = CoAP(self.server, random.randint(1, 65535), self._wait_response, sock=sock,
                             cb_ignore_read_exception=cb_ignore_read_exception, cb_ignore_write_exception=cb_ignore_write_exception)
        self.queue:Queue = Queue()

    def _wait_response(self, message:Message) -> None:
        """
        Private function to get responses from the server.

        :param message: the received message
        """
        if message is None or message.code != defines.Codes.CONTINUE.number:
            self.queue.put(message)

    def stop(self) -> None:
        """
        Stop the client.
        """
        self.protocol.close()
        self.queue.put(None)

    def close(self) -> None:
        """
        Close the client.
        """
        self.stop()

    def _thread_body(self, request:Request, callback:Callable) -> None:
        """
        Private function. Send a request, wait for response and call the callback function.

        :param request: the request to send
        :param callback: the callback function
        """
        self.protocol.send_message(request)
        while not self.protocol.stopped.isSet():
            response = self.queue.get(block=True)
            callback(response)

    def cancel_observing(self, response:Response, send_rst:bool) -> None:  # pragma: no cover
        """
        Delete observing on the remote server.

        :param response: the last received response
        :param send_rst: if explicitly send RST message
        :type send_rst: bool
        """
        if send_rst:
            message = Message()
            message.destination = self.server
            message.code = defines.Codes.EMPTY.number
            message.type = defines.Types["RST"]
            message.token = response.token
            message.mid = response.mid
            self.protocol.send_message(message)
        self.stop()

    def get(self, path:str, callback:Optional[Callable]=None, timeout:Optional[int]=None, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.GET, path)
        request.token = generate_random_token(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def get_non(self, path:str, callback:Optional[Callable]=None, timeout:Optional[int]=None, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request_non(defines.Codes.GET, path)
        request.token = generate_random_token(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def observe(self, path:str, callback:Callable, timeout:Optional[int]=None, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a GET with observe on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon notifications
        :param timeout: the timeout of the request
        :return: the response to the observe request
        """
        request = self.mk_request(defines.Codes.GET, path)
        request.observe = 0

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def delete(self, path:str, callback:Optional[Callable]=None, timeout:Optional[int]=None, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a DELETE on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.DELETE, path)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def post(self, path:str, payload:bytes, callback:Optional[Callable]=None, timeout:Optional[int]=None, no_response:Optional[bool]=False, **kwargs:Any) -> Response:  # pragma: no cover
        """
        Perform a POST on a certain path.

        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.POST, path)
        request.token = generate_random_token(2)
        request.payload = payload

        if no_response:
            request.add_no_response()
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout, no_response=no_response)

    def put(self, path:str, payload:bytes, callback:Optional[Callable]=None, timeout:Optional[int]=None, no_response:Optional[bool]=False, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.PUT, path)
        request.token = generate_random_token(2)
        request.payload = payload

        if no_response:
            request.add_no_response()
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout, no_response=no_response)

    def discover(self, callback:Optional[Callable]=None, timeout:Optional[float]=None, **kwargs:Any) -> Optional[Response]:  # pragma: no cover
        """
        Perform a Discover request on the server.

        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.GET, defines.DISCOVERY_URL)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def send_request(self, request:Request, callback:Optional[Callable]=None, timeout:Optional[float]=None, no_response:Optional[bool]=False) -> Optional[Response]:  # pragma: no cover
        """
        Send a request to the remote server.

        :param request: the request to send
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :param no_response: whether to await a response from the request
        :return: the response
        """
        
        if callback is not None:
            thread = threading.Thread(target=self._thread_body, args=(request, callback))
            thread.start()
            return None
        else:
            self.protocol.send_message(request, no_response=no_response)
            if no_response:
                return None
            try:
                while True:
                    response = self.queue.get(block=True, timeout=timeout)
                    if response is not None:
                        if response.mid == request.mid:
                            return response
                        if response.type == defines.Types["NON"]:
                            return response
                        self.queue.put(response)	# akr: put back the response if it is not for the request
                    else:
                        return response
            except Empty:
                #if timeout is set
                response = None
            return response

    def send_empty(self, empty:Message) -> None:  # pragma: no cover
        """
        Send empty message.

        :param empty: the empty message
        """
        self.protocol.send_message(empty)

    def mk_request(self, method:defines.CodeItem, path:str) -> Request:
        """
        Create a request.

        :param method: the CoAP method
        :param path: the path of the request
        :return:  the request
        """
        request = Request()
        request.destination = self.server
        request.code = method.number
        request.uri_path = path
        return request

    def mk_request_non(self, method:defines.CodeItem, path:str) -> Request:
        """
        Create a request.

        :param method: the CoAP method
        :param path: the path of the request
        :return:  the request
        """
        request = Request()
        request.destination = self.server
        request.code = method.number
        request.uri_path = path
        request.type = defines.Types["NON"]
        return request


