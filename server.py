#!/usr/bin/python3.5

import socket
from struct import unpack, pack
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
		init_as_connection(address, client_socket)
	server_socket.close()

def client_loop(ip, socket, neigbor):
	while True: #TODO while connected
		packet = socket.recv(1024)
		if not packet: break
		first_byte = packet[0];
		if(int(first_byte) == 1):
			#is connection request
			dictn = parse_connection_packet(packet);
			#send connection ack
			socket.send()
		else if(int(first_byte) == 2):
			
			as_neighbors.append({'ip': vc_ip, 'mask': vc_mask, 'as_id': vc_number})
			as_neighbors_log.append({'op': 1, 'timestamp': 0, 'origin': None}) # op: 1 = CREATE
			else if(int(first_byte) == 4):
				
				else if(int(first_byte) == 3):


def init_as_connection(ip, socket):
	thread = threading.Thread(target = client_loop, args=(ip, socket))
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
			for connection in connections:
				connection['socket'].close()
			running = False
		if choice == 1:
			vc_ip = str(raw_input('Escriba la IP del vecino'))
			vc_mask = str(raw_input('Escriba la mascara del vecino: '))
			vc_number = str(raw_input('Escriba el numero de sistema autonomo vecino: '))
			socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket.connect(vc_ip, 57809)
			if not socket: break
			init_as_connection(vc_ip, socket)
			# TODO: connect to new AS
			packet = create_connection_packet({'type':1, 'as_id':as_id ,'ip':ip, 'mask':mask })
			socket.send(packet)
		if choice == 2:
			host_ip = str(raw_input('Escriba la IP del host: '))
			hosts.append(host_ip)

def new_connection(b):

def parse_connection_packet(buffer):
	if (len(buffer)) != 11):
		print ("no sea fofi")
		return 0
	b =[]
	b = unpack("BBBBBBBBBBB",buffer);
	as_id = b[1]+b[2]
	ip = str(b[3])+"."+str(b[4])+"."+str(b[5])+"."+str(b[6])
	mask  = str(b[7])+"."+str(b[8])+"."+str(b[9])+"."+str(b[10])
	return {'type':b[0], 'as_id':as_id ,'ip':ip, 'mask':mask }

def create_connection_packet(**dictn):
	return pack("BhBBBBBBBB",dictn['type'], dictn['as_id'], *[ord(chr(int(x))) for x in dictn['ip'].split(".")], *[ord(chr(int(x))) for x in dictn['mask'].split(".")])

if __name__ == "__main__":
	#esto corre de primero
	main()
