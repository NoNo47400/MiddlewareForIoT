# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Optional, Union, cast, Tuple
import binascii

from coapthon import defines
from coapthon import utils
from coapthon.messages.option import Option

__author__ = 'Giacomo Tanganelli'


class Message(object):
    """
    Class to handle the Messages.
    """
    def __init__(self) -> None:
        """
        Data structure that represent a CoAP message
        """
        self._type:Optional[int] = None
        self._mid:Optional[int] = None
        self._token:Optional[bytes] = None
        self._options:list[Option] = []
        self._payload:Optional[bytes] = None
        self._destination:Optional[defines.ServerT] = None
        self._source:Optional[defines.ServerT] = None
        self._code:Optional[int] = None
        self._acknowledged:Optional[bool] = None
        self._rejected:Optional[bool] = None
        self._timeouted:Optional[bool] = None
        self._cancelled:Optional[bool] = None
        self._duplicated:Optional[bool] = None
        self._timestamp:Optional[float] = None
        self._version:int = 1

    @property
    def version(self) -> int:
        """
        Return the CoAP version

        :return: the version
        """
        return self._version

    @version.setter
    def version(self, v:int) -> None:
        """
        Sets the CoAP version

        :param v: the version
        :raise AttributeError: if value is not 1
        """
        if not isinstance(v, int) or v != 1:
            raise AttributeError
        self._version = v

    @property
    def type(self) -> int:
        """
        Return the type of the message.

        :return: the type
        """
        return self._type

    @type.setter
    def type(self, value:int) -> None:
        """
        Sets the type of the message.

        :type value: Types
        :param value: the type
        :raise AttributeError: if value is not a valid type
        """
        if value not in list(defines.Types.values()):
            raise AttributeError
        self._type = value

    @property
    def mid(self) -> int:
        """
        Return the mid of the message.

        :return: the MID
        """
        return self._mid

    @mid.setter
    def mid(self, value:int) -> None:
        """
        Sets the MID of the message.

        :type value: Integer
        :param value: the MID
        :raise AttributeError: if value is not int or cannot be represented on 16 bits.
        """
        if not isinstance(value, int) or value > 65536:
            raise AttributeError
        self._mid = value

    @mid.deleter
    def mid(self) -> None:
        """
        Unset the MID of the message.
        """
        self._mid = None

    @property
    def token(self) -> bytes:
        """
        Get the Token of the message.

        :return: the Token
        """
        return self._token

    @token.setter
    def token(self, value:bytes) -> None:
        """
        Set the Token of the message.

        :type value: Bytes
        :param value: the Token
        :raise AttributeError: if value is longer than 256
        """
        if value is None:
            self._token = value
            return
        if not isinstance(value, bytes):
            value = bytes(value, 'utf-8')

        if len(value) > 256:
            raise AttributeError
        self._token = value

    @token.deleter
    def token(self) -> None:
        """
        Unset the Token of the message.
        """
        self._token = None

    @property
    def options(self) -> list[Option]:
        """
        Return the options of the CoAP message.

        :rtype: list
        :return: the options
        """
        return self._options

    @options.setter
    def options(self, value:list[Option]) -> None:
        """
        Set the options of the CoAP message.

        :type value: list
        :param value: list of options
        """
        if value is None:
            value = []
        assert isinstance(value, list)
        self._options = value

    @property
    def payload(self) -> bytes:
        """
        Return the payload.

        :return: the payload
        """
        return self._payload

    @payload.setter
    def payload(self, value:Union[bytes,Tuple[int, bytes]]) -> None:
        """
        Sets the payload of the message and eventually the Content-Type

        :param value: the payload
        """
        if isinstance(value, tuple):
            content_type, payload = value
            self.content_type = content_type
            self._payload = payload
        else:
            self._payload = value

    @property
    def destination(self) -> defines.ServerT:
        """
        Return the destination of the message.

        :rtype: tuple
        :return: (ip, port)
        """
        return self._destination

    @destination.setter
    def destination(self, value:defines.ServerT) -> None:
        """
        Set the destination of the message.

        :type value: tuple
        :param value: (ip, port)
        :raise AttributeError: if value is not a ip and a port.
        """
        if value is not None and (not isinstance(value, tuple) or len(value)) != 2:
            raise AttributeError
        self._destination = value

    @property
    def source(self) -> Optional[defines.ServerT]:
        """
        Return the source of the message.

        :rtype: tuple
        :return: (ip, port)
        """
        return self._source

    @source.setter
    def source(self, value:defines.ServerT) -> None:
        """
        Set the source of the message.

        :type value: tuple
        :param value: (ip, port)
        :raise AttributeError: if value is not a ip and a port.
        """
        if not isinstance(value, tuple) or len(value) != 2:
            raise AttributeError
        self._source = value

    @property
    def code(self) -> int:
        """
        Return the code of the message.

        :rtype: Codes
        :return: the code
        """
        return self._code

    @code.setter
    def code(self, value:int) -> None:
        """
        Set the code of the message.

        :type value: Codes
        :param value: the code
        :raise AttributeError: if value is not a valid code
        """
        if value not in list(defines.Codes.LIST.keys()) and value is not None:
            raise AttributeError
        self._code = value

    @property
    def acknowledged(self) -> bool:
        """
        Checks if is this message has been acknowledged.

        :return: True, if is acknowledged
        """
        return self._acknowledged

    @acknowledged.setter
    def acknowledged(self, value:bool) -> None:
        """
        Marks this message as acknowledged.

        :type value: Boolean
        :param value: if acknowledged
        """
        assert (isinstance(value, bool))
        self._acknowledged = value
        if value:
            self._timeouted = False
            self._rejected = False
            self._cancelled = False

    @property
    def rejected(self) -> bool:
        """
        Checks if this message has been rejected.

        :return: True, if is rejected
        """
        return self._rejected

    @rejected.setter
    def rejected(self, value:bool) -> None:
        """
        Marks this message as rejected.

        :type value: Boolean
        :param value: if rejected
        """
        assert (isinstance(value, bool))
        self._rejected = value
        if value:
            self._timeouted = False
            self._acknowledged = False
            self._cancelled = True

    @property
    def timeouted(self) -> bool:
        """
        Checks if this message has timeouted. Confirmable messages in particular
        might timeout.

        :return: True, if has timeouted
        """
        return self._timeouted

    @timeouted.setter
    def timeouted(self, value:bool) -> None:
        """
        Marks this message as timeouted. Confirmable messages in particular might
        timeout.

        :type value: Boolean
        :param value:
        """
        # assert (isinstance(value, bool))
        self._timeouted = value
        if value:
            self._acknowledged = False
            self._rejected = False
            self._cancelled = True

    @property
    def duplicated(self) -> bool:
        """
        Checks if this message is a duplicate.

        :return: True, if is a duplicate
        """
        return self._duplicated

    @duplicated.setter
    def duplicated(self, value:bool) -> None:
        """
        Marks this message as a duplicate.

        :type value: Boolean
        :param value: if a duplicate
        """
        # assert (isinstance(value, bool))
        self._duplicated = value

    @property
    def timestamp(self) -> float:
        """
        Return the timestamp of the message.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value:float) -> None:
        """
        Set the timestamp of the message.

        :type value: timestamp
        :param value: the timestamp
        """
        self._timestamp = value

    def _already_in(self, option:Option) -> bool:
        """
        Check if an option is already in the message.

        :type option: Option
        :param option: the option to be checked
        :return: True if already present, False otherwise
        """
        for opt in self._options:
            if option.number == opt.number:
                return True
        return False

    def add_option(self, option:Option) -> None:
        """
        Add an option to the message.

        :type option: Option
        :param option: the option
        :raise TypeError: if the option is not repeatable and such option is already present in the message
        """
        assert isinstance(option, Option)
        repeatable = defines.OptionRegistry.LIST[option.number].repeatable
        if not repeatable:
            ret = self._already_in(option)
            if ret:
                raise TypeError("Option : %s is not repeatable", option.name)
            else:
                self._options.append(option)
        else:
            self._options.append(option)

    def del_option(self, option:Option) -> None:
        """
        Delete an option from the message

        :type option: Option
        :param option: the option
        """
        # assert isinstance(option, Option)
        while option in list(self._options):
            self._options.remove(option)

    def del_option_by_name(self, name:str) -> None:
        """
        Delete an option from the message by name

        :type name: String
        :param name: option name
        """
        for o in list(self._options):
            # assert isinstance(o, Option)
            if o.name == name:
                self._options.remove(o)

    def del_option_by_number(self, number:int) -> None:
        """
        Delete an option from the message by number

        :type number: Integer
        :param number: option naumber
        """
        for o in list(self._options):
            # assert isinstance(o, Option)
            if o.number == number:
                self._options.remove(o)

    @property
    def etag(self) -> list[bytes]:
        """
        Get the ETag option of the message.

        :rtype: list
        :return: the ETag values or [] if not specified by the request
        """
        value:list[bytes] = []
        for option in self.options:
            if option.number == defines.OptionRegistry.ETAG.number:
                value.append(cast(bytes, option.value))
        return value

    @etag.setter
    def etag(self, etag:Union[bytes,list]) -> None:
        """
        Add an ETag option to the message.

        :param etag: the etag
        """
        if not isinstance(etag, list):
            etag = [etag]
        for e in etag:
            option = Option()
            option.number = defines.OptionRegistry.ETAG.number
            if not isinstance(e, bytes):
                e = bytes(e, "utf-8")
            option.value = e
            self.add_option(option)

    @etag.deleter
    def etag(self) -> None:
        """
        Delete an ETag from a message.

        """
        self.del_option_by_number(defines.OptionRegistry.ETAG.number)

    @property
    def content_type(self) -> int:
        """
        Get the Content-Type option of a response.

        :return: the Content-Type value or 0 if not specified by the response
        """
        value = 0
        for option in self.options:
            if option.number == defines.OptionRegistry.CONTENT_TYPE.number:
                value = int(option.value)
        return value

    @content_type.setter
    def content_type(self, content_type:int) -> None:
        """
        Set the Content-Type option of a response.

        :type content_type: int
        :param content_type: the Content-Type
        """
        option = Option()
        option.number = defines.OptionRegistry.CONTENT_TYPE.number
        option.value = int(content_type)
        self.add_option(option)

    @content_type.deleter
    def content_type(self) -> None:
        """
        Delete the Content-Type option of a response.
        """

        self.del_option_by_number(defines.OptionRegistry.CONTENT_TYPE.number)

    @property
    def observe(self) -> Optional[int]:
        """
        Check if the request is an observing request.

        :return: 0, if the request is an observing request
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.OBSERVE.number:
                # if option.value is None:
                #    return 0
                if option.value is None:
                    return 0
                return cast(int, option.value)
        return None

    @observe.setter
    def observe(self, ob:int) -> None:
        """
        Add the Observe option.

        :param ob: observe count
        """
        option = Option()
        option.number = defines.OptionRegistry.OBSERVE.number
        option.value = ob
        self.del_option_by_number(defines.OptionRegistry.OBSERVE.number)
        self.add_option(option)

    @observe.deleter
    def observe(self) -> None:
        """
        Delete the Observe option.
        """
        self.del_option_by_number(defines.OptionRegistry.OBSERVE.number)

    @property
    def block1(self) -> Optional[defines.BlockT]:
        """
        Get the Block1 option.

        :return: the Block1 value
        """
        value:Optional[defines.BlockT] = None
        for option in self.options:
            if option.number == defines.OptionRegistry.BLOCK1.number:
                value = utils.parse_blockwise(cast(int, option.value))
        return value

    @block1.setter
    def block1(self, value:defines.BlockT) -> None:
        """
        Set the Block1 option.

        :param value: the Block1 value
        """
        option = Option()
        option.number = defines.OptionRegistry.BLOCK1.number
        num, m, size = value
        if size > 512:
            szx = 6
        elif 256 < size <= 512:
            szx = 5
        elif 128 < size <= 256:
            szx = 4
        elif 64 < size <= 128:
            szx = 3
        elif 32 < size <= 64:
            szx = 2
        elif 16 < size <= 32:
            szx = 1
        else:
            szx = 0

        v = (num << 4)
        v |= (m << 3)
        v |= szx

        option.value = v
        self.add_option(option)

    @block1.deleter
    def block1(self) -> None:
        """
        Delete the Block1 option.
        """
        self.del_option_by_number(defines.OptionRegistry.BLOCK1.number)

    @property
    def block2(self) -> Optional[defines.BlockT]:
        """
        Get the Block2 option.

        :return: the Block2 value
        """
        value = None
        for option in self.options:
            if option.number == defines.OptionRegistry.BLOCK2.number:
                value = utils.parse_blockwise(cast(int, option.value))
        return value

    @block2.setter
    def block2(self, value:defines.BlockT) -> None:
        """
        Set the Block2 option.

        :param value: the Block2 value
        """
        option = Option()
        option.number = defines.OptionRegistry.BLOCK2.number
        num, m, size = value
        if size > 512:
            szx = 6
        elif 256 < size <= 512:
            szx = 5
        elif 128 < size <= 256:
            szx = 4
        elif 64 < size <= 128:
            szx = 3
        elif 32 < size <= 64:
            szx = 2
        elif 16 < size <= 32:
            szx = 1
        else:
            szx = 0

        v  = (num << 4)
        v |= (m << 3)
        v |= szx

        option.value = v
        self.add_option(option)

    @block2.deleter
    def block2(self) -> None:
        """
        Delete the Block2 option.
        """
        self.del_option_by_number(defines.OptionRegistry.BLOCK2.number)

    @property
    def size1(self) -> Optional[int]:
        value:Optional[int] = None
        for option in self.options:
            if option.number == defines.OptionRegistry.SIZE1.number:
                value = cast(int, option.value) if option.value is not None else 0
        return value

    @size1.setter
    def size1(self, value:int) -> None:
        option = Option()
        option.number = defines.OptionRegistry.SIZE1.number
        option.value = value
        self.add_option(option)

    @size1.deleter
    def size1(self) -> None:
        self.del_option_by_number(defines.OptionRegistry.SIZE1.number)

    @property
    def size2(self) -> Optional[int]:
        """
        Get the Size2 option.

        :return: the Size2 value
        """
        value:Optional[int] = None
        for option in self.options:
            if option.number == defines.OptionRegistry.SIZE2.number:
                value = cast(int, option.value)
        return value

    @size2.setter
    def size2(self, value:int) -> None:
        """
        Set the Size2 option.

        :param value: the Block2 value
        """
        option = Option()
        option.number = defines.OptionRegistry.SIZE2.number
        option.value = value
        self.add_option(option)

    @size2.deleter
    def size2(self) -> None:
        """
        Delete the Size2 option.
        """
        self.del_option_by_number(defines.OptionRegistry.SIZE2.number)

    @property
    def line_print(self) -> str:
        """
        Return the message as a one-line string.

        :return: the string representing the message
        """
        inv_types = {v: k for k, v in defines.Types.items()}

        if self._code is None:
            self._code = defines.Codes.EMPTY.number

        token = binascii.hexlify(self._token).decode("utf-8") if self._token is not None else str(None)

        msg = "From {source}, To {destination}, {type}-{mid}, {code}-{token}, ["\
            .format(source=self._source, destination=self._destination, type=inv_types[self._type], mid=self._mid,
                    code=defines.Codes.LIST[self._code].name, token=token)
        for opt in self._options:
            if 'Block' in opt.name:
                msg += f"{opt.name}: {utils.parse_blockwise(cast(int, opt.value))}, "
            else:
                msg += "{opt.name}: {opt.value}, "
        msg += "]"
        if self.payload is not None:
            if isinstance(self.payload, dict):
                tmp = list(self.payload.values())[0][0:20]
            else:
                tmp = self.payload[0:20]
            msg += f" {tmp!r}...{len(self.payload)} bytes"
        else:
            msg += " No payload"
        return msg

    def __str__(self) -> str:
        return self.line_print

    def pretty_print(self) -> str:
        """
        Return the message as a formatted string.

        :return: the string representing the message
        """
        msg = "Source: " + str(self._source) + "\n"
        msg += "Destination: " + str(self._destination) + "\n"
        inv_types = {v: k for k, v in defines.Types.items()}
        msg += "Type: " + str(inv_types[self._type]) + "\n"
        msg += "MID: " + str(self._mid) + "\n"
        if self._code is None:
            self._code = 0
        token = binascii.hexlify(self._token).decode("utf-8") if self._token is not None else str(None)
        msg += "Code: " + str(defines.Codes.LIST[self._code].name) + "\n"
        msg += "Token: " + token + "\n"
        for opt in self._options:
            msg += str(opt)
        msg += "Payload: " + "\n"
        msg += str(self._payload) + "\n"
        return msg
