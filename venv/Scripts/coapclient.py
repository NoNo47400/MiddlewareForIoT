#!C:\Users\noelj\Desktop\MQTT_TP\venv\Scripts\python.exe

from __future__ import annotations
from typing import Optional

import getopt
import socket
import sys

from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from coapthon.messages.response import Response

__author__ = 'Giacomo Tanganelli'

client:Optional[HelperClient] = None


def usage() -> None:  # pragma: no cover
	print("Command:\tcoapclient.py -o -p [-P]")
	print("Options:")
	print("\t-o, --operation=\tGET|PUT|POST|DELETE|DISCOVER|OBSERVE")
	print("\t-p, --path=\t\t\tPath of the request")
	print("\t-P, --payload=\t\tPayload of the request")
	print("\t-f, --payload-file=\t\tFile with payload of the request")


def client_callback(response:Response) -> None:  # pragma: no cover
	print("Callback")


def client_callback_observe(response:Response) -> None:  # pragma: no cover
	global client
	print("Callback_observe")
	check = True
	while check:
		chosen = eval(input("Stop observing? [y/N]: "))
		if chosen != "" and not (chosen == "n" or chosen == "N" or chosen == "y" or chosen == "Y"):
			print("Unrecognized choose.")
			continue
		elif chosen == "y" or chosen == "Y":
			while True:
				rst = eval(input("Send RST message? [Y/n]: "))
				if rst != "" and not (rst == "n" or rst == "N" or rst == "y" or rst == "Y"):
					print("Unrecognized choose.")
					continue
				elif rst == "" or rst == "y" or rst == "Y":
					client.cancel_observing(response, True)
				else:
					client.cancel_observing(response, False)
				check = False
				break
		else:
			break


def main() -> None:  # pragma: no cover
	global client
	op = None
	path = None
	payload = None
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:p:P:f:", ["help", "operation=", "path=", "payload=",
															   "payload_file="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(str(err))  # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	for o, a in opts:
		if o in ("-o", "--operation"):
			op = a
		elif o in ("-p", "--path"):
			path = a
		elif o in ("-P", "--payload"):
			payload = a
		elif o in ("-f", "--payload-file"):
			with open(a, 'r') as f:
				payload = f.read()
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			usage()
			sys.exit(2)

	if op is None:
		print("Operation must be specified")
		usage()
		sys.exit(2)

	if path is None:
		print("Path must be specified")
		usage()
		sys.exit(2)

	if not path.startswith("coap://"):
		print("Path must be conform to coap://host[:port]/path")
		usage()
		sys.exit(2)

	host, port, path = parse_uri(path)
	try:
		tmp = socket.gethostbyname(host)
		host = tmp
	except socket.gaierror:
		pass
	client = HelperClient(server=(host, port))
	match op:
		case "GET":
			if path is None:
				print("Path cannot be empty for a GET request")
				usage()
				sys.exit(2) # TODO
			response = client.get(path)
			print(response.pretty_print())
			client.stop()
		case "OBSERVE":
			if path is None:
				print("Path cannot be empty for a GET request")
				usage()
				sys.exit(2) # TODO
			client.observe(path, client_callback_observe)
		case "DELETE":
			if path is None:
				print("Path cannot be empty for a DELETE request")
				usage()
				sys.exit(2)
			response = client.delete(path)
			print(response.pretty_print())
			client.stop()
		case "POST":
			if path is None:
				print("Path cannot be empty for a POST request")
				usage()
				sys.exit(2)	# TODO
			if payload is None:
				print("Payload cannot be empty for a POST request")
				usage()
				sys.exit(2) # TODO
			response = client.post(path, bytes(payload, 'utf-8'))
			print(response.pretty_print())
			client.stop()
		case "PUT":
			if path is None:
				print("Path cannot be empty for a PUT request")
				usage()
				sys.exit(2) # TODO
			if payload is None:
				print("Payload cannot be empty for a PUT request")
				usage()
				sys.exit(2) # TODO
			response = client.put(path, bytes(payload, 'utf-8'))
			print(response.pretty_print())
			client.stop()
		case "DISCOVER":
			response = client.discover()
			print(response.pretty_print())
			client.stop()
		case _:
			print("Operation not recognized")
			usage()
			sys.exit(2) # TODO


if __name__ == '__main__':  # pragma: no cover
	main()
