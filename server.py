#!/usr/bin/python

import socket
from struct import unpack, pack
import os, sys

def main():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('0.0.0.0', 57809))
	server_socket.listen(5)

	while True:
		(client_socket, address) = server_socket.accept()
		#ct = client_thread(client_socket)
		#ct.run()

	server_socket.close()

def new_connection(b):

def parse_bytes(buffer):
	if (len(buffer)) != 11):
		print ("no sea fofi")
		return 0
	b =[]
	b = unpack("BBBBBBBBBBB",buffer);
	as_id = b[1]+b[2]
	ip = str(b[3])+"."+str(b[4])+"."+str(b[5])+"."+str(b[6])
	mask  = str(b[7])+"."+str(b[8])+"."+str(b[9])+"."+str(b[10])
	return {'type':b[0], 'as_id':as_id ,'ip':ip, 'mask':mask }

def write_bytes(**dictn):
		return pack("BhBBBBBBBB",dictn['type'], dictn['as_id'], *[ord(chr(int(x))) for x in dictn['ip'].split(".")], *[ord(chr(int(x))) for x in dictn['mask'].split(".")])

if __name__ == "__main__":
	#esto corre de primero
	main()
