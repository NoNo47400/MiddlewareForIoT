from __future__ import annotations
from typing import Optional

from coapthon.layers.forwardLayer import ForwardLayer
from coapthon.resources.resource import Resource
from coapthon.server.coap import CoAP
from coapthon.reverse_proxy.coap import CoAP as ReverseCoAP
from coapthon import defines

__author__ = 'Giacomo Tanganelli'


class RemoteResource(Resource):
    def __init__(self, name:str, remote_server:defines.ServerT, remote_path:str, coap_server:Optional[CoAP|ForwardLayer|ReverseCoAP]=None, visible:Optional[bool]=True, observable:Optional[bool]=True, allow_children:Optional[bool]=True) -> None:
        super(RemoteResource, self).__init__(name, coap_server, visible=visible, observable=observable,
                                             allow_children=allow_children)
        self.remote_path = remote_path
        self.remote_server = remote_server
