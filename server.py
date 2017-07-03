#!/usr/bin/python3.5

import socket
import threading
import os, sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True

def server_loop():
	while running:
		(client_socket, address) = server_socket.accept()
		# create thread to receive new messages
	server_socket.close()

def main():
	# setup
	as_ip = str(raw_input('Escriba la IP del sistema autonomo: '))
	as_mask = str(raw_input('Escriba la mascara: '))
	as_number = int(raw_input('Escriba el numero de sistema autonomo: '))

	server_socket.bind(('0.0.0.0', 57809))
	server_socket.listen(5)

	thread = threading.Thread(target=server_loop)
	thread.daemon = True
	thread.start()

	choice = -1
	while choice != 0:
		choice = int(raw_input('Que desea hacer?\n1 - Agregar vecino.\n2 - Salir\n'))
		if choice == 0:
			# TODO: close socket
			running = False
		if choice == 1:
			vc_ip = str(raw_input('Escriba la IP del vecino'))
			vc_mask = str(raw_input('Escriba la mascara del vecino: '))
			vc_number = str(raw_input('Escriba el numero de sistema autonomo vecino: '))

if __name__ == "__main__":
	#esto corre de primero    
	main()
