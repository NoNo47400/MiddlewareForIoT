#!C:\Users\noelj\Desktop\MQTT_TP\venv\Scripts\python.exe

from __future__ import annotations
from typing import Optional, cast

import time
from coapthon import defines

from coapthon.resources.resource import Resource
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.server.coap import CoAP

__author__ = 'Giacomo Tanganelli'


class BasicResource(Resource):
    def __init__(self, name:Optional[str]="BasicResource", coap_server:Optional[CoAP]=None):
        super(BasicResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Basic Resource"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_GET(self, request:Request) -> BasicResource:
        return self

    def render_PUT(self, request:Request) -> BasicResource:
        self.edit_resource(request)
        return self

    def render_POST(self, request:Request) -> BasicResource:
        return cast(BasicResource, self.init_resource(request, BasicResource()))

    def render_DELETE(self, request:Request) -> bool:
        return True


class Storage(Resource):
    def __init__(self, name:Optional[str]="StorageResource", coap_server:Optional[CoAP]=None):
        super(Storage, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Storage Resource for PUT, POST and DELETE"

    def render_GET(self, request:Request) -> Resource:
        return self

    def render_POST(self, request:Request) -> Resource:
        return self.init_resource(request, BasicResource())


class Child(Resource):
    def __init__(self, name:Optional[str]="ChildResource", coap_server:Optional[CoAP]=None):
        super(Child, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = ""

    def render_GET(self, request:Request) -> Resource:
        return self

    def render_PUT(self, request:Request) -> Resource:
        self.payload = request.payload
        return self

    def render_POST(self, request:Request) -> Resource:
        res = BasicResource()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request:Request) -> bool:
        return True


class Separate(Resource):

    def __init__(self, name:Optional[str]="Separate", coap_server:Optional[CoAP]=None):
        super(Separate, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Separate"
        self.max_age = 60

    def render_GET(self, request:Request) -> Separate:
        return self.render_GET_separate(request)

    def render_GET_separate(self, request:Request) -> Separate:
        time.sleep(5)
        return self

    def render_POST(self, request:Request) -> Separate:
        return self.render_POST_separate(request)

    def render_POST_separate(self, request:Request) -> Separate:
        self.payload = request.payload
        return self

    def render_PUT(self, request:Request) -> Separate:
        return self.render_PUT_separate(request)

    def render_PUT_separate(self, request:Request) -> Separate:
        self.payload = request.payload
        return self

    def render_DELETE(self, request:Request) -> bool:
        return self.render_DELETE_separate(request)

    def render_DELETE_separate(self, request:Request) -> bool:
        return True


class Long(Resource):

    def __init__(self, name:Optional[str]="Long", coap_server:Optional[CoAP]=None):
        super(Long, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Long Time"

    def render_GET(self, request:Request) -> Resource:
        time.sleep(10)
        return self


class Big(Resource):

    def __init__(self, name:Optional[str]="Big", coap_server:Optional[CoAP]=None):
        super(Big, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = """\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. \
Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. \
Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. \
Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. Phasellus \
nec leo luctus, blandit lorem sit amet, interdum metus. Duis efficitur volutpat magna, ac \
ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. Nunc eget augue \
ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, \
facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id \
sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. \
Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. Quisque eu hendrerit\
 urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in rutrum massa.\
 Praesent tristique turpis dui, at ultricies lorem fermentum at. Vivamus sit amet ornare neque, \
a imperdiet nisl. Quisque a iaculis libero, id tempus lacus. Aenean convallis est non justo \
consectetur, a hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque \
nec eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. Ut orci \
enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros eget fermentum.\
Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at tempus ornare. Phasellus \
dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus in nisl efficitur,\
 a luctus justo tempus. Fusce finibus libero eget velit finibus iaculis. Morbi rhoncus purus \
vel vestibulum ullamcorper. Sed ac metus in urna fermentum feugiat. Nulla nunc diam, sodales \
aliquam mi id, varius porta nisl. Praesent vel nibh ac turpis rutrum laoreet at non odio. \
Phasellus ut posuere mi. Suspendisse malesuada velit nec mauris convallis porta. Vivamus \
sed ultrices sapien, at cras amet."""

    def render_GET(self, request:Request) -> Resource:
        return self

    def render_POST(self, request:Request) -> Resource:
        if request.payload is not None:
            self.payload = request.payload
        return self


class voidResource(Resource):
    def __init__(self, name:Optional[str]="Void") -> None:
        super(voidResource, self).__init__(name)


class XMLResource(Resource):
    def __init__(self, name:Optional[str]="XML") -> None:
        super(XMLResource, self).__init__(name)
        self.value = 0
        self.payload = (defines.Content_types["application/xml"], "<value>"+str(self.value)+"</value>")

    def render_GET(self, request:Request) -> Resource:
        return self


class MultipleEncodingResource(Resource):
    def __init__(self, name:Optional[str]="MultipleEncoding") -> None:
        super(MultipleEncodingResource, self).__init__(name)
        self.value = 0
        self.payload = str(self.value)
        self.content_type = [defines.Content_types["application/xml"], defines.Content_types["application/json"]]

    def render_GET(self, request:Request) -> MultipleEncodingResource:
        if request.accept == defines.Content_types["application/xml"]:
            self.payload = (defines.Content_types["application/xml"],  "<value>"+str(self.value)+"</value>")
        elif request.accept == defines.Content_types["application/json"]:
            self.payload = (defines.Content_types["application/json"], "{'value': '"+str(self.value)+"'}")
        elif request.accept == defines.Content_types["text/plain"]:
            self.payload = (defines.Content_types["text/plain"], str(self.value))
        return self

    def render_PUT(self, request:Request) -> MultipleEncodingResource:
        self.edit_resource(request)
        return self

    def render_POST(self, request:Request) -> MultipleEncodingResource:
        return cast(MultipleEncodingResource, self.init_resource(request, MultipleEncodingResource()))


class ETAGResource(Resource):
    def __init__(self, name:Optional[str]="ETag") -> None:
        super(ETAGResource, self).__init__(name)
        self.count = 0
        self.payload = "ETag resource"
        self.etag = str(self.count)

    def render_GET(self, request:Request) -> ETAGResource:
        return self

    def render_POST(self, request:Request) -> ETAGResource:
        self.payload = request.payload
        self.count += 1
        self.etag = str(self.count)
        return self

    def render_PUT(self, request:Request) -> ETAGResource:
        self.payload = request.payload
        return self


class AdvancedResource(Resource):
    def __init__(self, name:Optional[str]="Advanced") -> None:
        super(AdvancedResource, self).__init__(name)
        self.payload = "Advanced resource"

    def render_GET_advanced(self, request:Request, response:Response) -> tuple[AdvancedResource, Response]:
        response.payload = self.payload
        response.max_age = 20
        response.code = defines.Codes.CONTENT.number
        return self, response

    def render_POST_advanced(self, request:Request, response:Response) -> tuple[AdvancedResource, Response]:
        self.payload = request.payload
        from coapthon.messages.response import Response
        assert(isinstance(response, Response))
        response.payload = b"Response changed through POST"
        response.code = defines.Codes.CREATED.number
        return self, response

    def render_PUT_advanced(self, request:Request, response:Response) -> tuple[AdvancedResource, Response]:
        self.payload = request.payload
        from coapthon.messages.response import Response
        assert(isinstance(response, Response))
        response.payload = b"Response changed through PUT"
        response.code = defines.Codes.CHANGED.number
        return self, response

    def render_DELETE_advanced(self, request:Request, response:Response) -> tuple[bool, Response]:
        response.payload = b"Response deleted"
        response.code = defines.Codes.DELETED.number
        return True, response


class AdvancedResourceSeparate(Resource):
    def __init__(self, name:Optional[str]="Advanced") -> None:
        super(AdvancedResourceSeparate, self).__init__(name)
        self.payload = "Advanced resource"

    def render_GET_advanced(self, request:Request, response:Response) -> AdvancedResourceSeparate:
        return self.render_GET_separate()

    def render_POST_advanced(self, request:Request, response:Response) -> tuple[AdvancedResourceSeparate, Response]:
        return self, response, self.render_POST_separate

    def render_PUT_advanced(self, request, response):

        return self, response, self.render_PUT_separate

    def render_DELETE_advanced(self, request, response):
        return self, response, self.render_DELETE_separate

    def render_GET_separate(self, request:Request, response:Response) -> AdvancedResourceSeparate:
        time.sleep(5)
        response.payload = self.payload
        response.max_age = 20
        return self

    def render_POST_separate(self, request, response):
        self.payload = request.payload
        response.payload = "Response changed through POST"
        return self, response

    def render_PUT_separate(self, request, response):
        self.payload = request.payload
        response.payload = "Response changed through PUT"
        return self, response

    def render_DELETE_separate(self, request, response):
        response.payload = "Response deleted"
        return True, response
