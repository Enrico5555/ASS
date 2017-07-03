#!/usr/bin/python3.5

import socket
import threading
import os, sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True

as_neighbors = []
as_neighbors_log = []

hosts = []

connections = []

def server_loop():
	while running:
		(client_socket, address) = server_socket.accept()
		# create thread to receive new messages
	server_socket.close()

def client_loop():
	while True:
		print('YOLO')

def init_as_connection(ip, socket):
	thread = threading.Thread(target = client_loop)
	thread.daemon = True
	connections.append({'socket': socket, 'ip': ip, 'thread': thread})
	thread.start()

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
		choice = int(raw_input('Que desea hacer?\n1 - Agregar vecino.\n2 - Agregar host.\n0 - Salir.\n'))
		if choice == 0:
			# TODO: close socket
			running = False
		if choice == 1:
			vc_ip = str(raw_input('Escriba la IP del vecino'))
			vc_mask = str(raw_input('Escriba la mascara del vecino: '))
			vc_number = str(raw_input('Escriba el numero de sistema autonomo vecino: '))

			# TODO: connect to new AS
			# add only if connection is successful!
			as_neighbors.append({'ip': vc_ip, 'mask': vc_mask, 'as_id': vc_number})
			as_neighbors_log.append({'op': 1, 'timestamp': 0, 'origin': None}) # op: 1 = CREATE
		if choice == 2:
			host_ip = str(raw_input('Escriba la IP del host: '))
			hosts.append(host_ip)

if __name__ == "__main__":
	#esto corre de primero    
	main()
