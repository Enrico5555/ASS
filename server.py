#!/usr/bin/python

import socket

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

if __name__ == "__main__":
	#esto corre de primero    
	main()
