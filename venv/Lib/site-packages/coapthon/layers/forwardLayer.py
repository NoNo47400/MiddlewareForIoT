from __future__ import annotations
from typing import Optional, cast

import copy
import logging
from coapclient import HelperClient
from coapthon.messages.request import Request
from coapthon.resources.resource import Resource
from coapthon.messages.response import Response
from coapthon.resources.remoteResource import RemoteResource
from coapthon.transaction import Transaction
from coapthon.server.coap import CoAP
from coapthon.forward_proxy.coap import CoAP as ForwardCoAP
from coapthon.reverse_proxy.coap import CoAP as ReverseCoAP
from coapthon import defines
from coapthon.utils import parse_uri

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class ForwardLayer(object):
    """
    Class used by Proxies to forward messages.
    """
    def __init__(self, server:CoAP|ForwardCoAP|ReverseCoAP) -> None:
        self._server = server

    def receive_request(self, transaction:Transaction) -> Transaction:
        """
        Setup the transaction for forwarding purposes on Forward Proxies.
         
        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction
        """
        uri = transaction.request.proxy_uri
        if uri is None:
            transaction.response = Response()
            transaction.response.destination = transaction.request.source
            transaction.response.token = transaction.request.token
            transaction.response.type = defines.Types["RST"]
            transaction.response.code = defines.Codes.BAD_REQUEST.number
            return transaction

        host, port, path = parse_uri(uri)
        path = str("/" + path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        return self._forward_request(transaction, (host, port), path)

    def receive_request_reverse(self, transaction:Transaction) -> Transaction:
        """
        Setup the transaction for forwarding purposes on Reverse Proxies.
         
        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction
        """
        wkc_resource_is_defined = defines.DISCOVERY_URL in self._server.root
        path = str("/" + transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        if path == defines.DISCOVERY_URL and not wkc_resource_is_defined:
            transaction = self._server.resourceLayer.discover(transaction)
        else:
            new = False
            if transaction.request.code == defines.Codes.POST.number:
                new_paths = self._server.root.with_prefix(path)
                new_path = "/"
                for tmp in new_paths:
                    if len(tmp) > len(new_path):
                        new_path = tmp
                if path != new_path:
                    new = True
                path = new_path
            try:
                resource = cast(Resource, self._server.root[path])
            except KeyError:
                resource = None
            if resource is None or path == '/':
                # Not Found
                transaction.response.code = defines.Codes.NOT_FOUND.number
            else:
                transaction.resource = resource
                transaction = self._handle_request(transaction, new)
        return transaction

    @staticmethod
    def _forward_request(transaction:Transaction, destination:defines.ServerT, path:str) -> Transaction:
        """
        Forward requests.

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :param destination: the destination of the request (IP, port)
        :param path: the path of the request.
        :rtype : Transaction
        :return: the edited transaction
        """
        client = HelperClient(destination)
        request = Request()
        request.options = copy.deepcopy(transaction.request.options)
        del request.block2
        del request.block1
        del request.uri_path
        del request.proxy_uri
        del request.proxy_schema
        # TODO handle observing
        del request.observe
        # request.observe = transaction.request.observe

        request.uri_path = path
        request.destination = destination
        request.payload = transaction.request.payload
        request.code = transaction.request.code
        response = client.send_request(request)
        client.stop()
        if response is not None:
            transaction.response.payload = response.payload
            transaction.response.code = response.code
            transaction.response.options = response.options
        else:
            transaction.response.code = defines.Codes.SERVICE_UNAVAILABLE.number

        return transaction

    def _handle_request(self, transaction:Transaction, new_resource:bool) -> Transaction:
        """
        Forward requests. Used by reverse proxies to also create new virtual resources on the proxy 
        in case of created resources
        
        :type new_resource: bool
        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :param new_resource: if the request will generate a new resource 
        :return: the edited transaction
        """
        client = HelperClient(cast(RemoteResource, transaction.resource).remote_server)
        request = Request()
        request.options = copy.deepcopy(transaction.request.options)
        del request.block2
        del request.block1
        del request.uri_path
        del request.proxy_uri
        del request.proxy_schema
        # TODO handle observing
        del request.observe
        # request.observe = transaction.request.observe

        request.uri_path = "/".join(transaction.request.uri_path.split("/")[1:])
        request.destination = cast(RemoteResource, transaction.resource).remote_server
        request.payload = transaction.request.payload
        request.code = transaction.request.code
        logger.debug("forward_request - " + str(request))
        response = client.send_request(request)
        client.stop()
        logger.debug("forward_response - " + str(response))
        transaction.response.payload = response.payload
        transaction.response.code = response.code
        transaction.response.options = response.options
        if response.code == defines.Codes.CREATED.number:
            lp = transaction.response.location_path
            del transaction.response.location_path
            transaction.response.location_path = transaction.request.uri_path.split("/")[0] + "/" + lp
            # TODO handle observing
            if new_resource:
                resource = RemoteResource('server', cast(RemoteResource, transaction.resource).remote_server, lp, coap_server=self,
                                          visible=True,
                                          observable=False,
                                          allow_children=True)
                self._server.add_resource(transaction.response.location_path, resource)	# type: ignore[union-attr]
        if response.code == defines.Codes.DELETED.number:
            del self._server.root["/" + transaction.request.uri_path]
        return transaction
