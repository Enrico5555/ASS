#!/usr/bin/python3.5

import socket
from struct import unpack, pack
import threading
import os, sys
from time import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True

as_neighbors = []
as_neighbors_log = []

hosts = []

connections = []

RECIEVE_BUFFER = 4096
LISTEN_PORT= 57809
REQUESTED_CONNECTION = 1
ACCEPTED_CONNECTION = 2
REQUESTED_DESCONNECTION = 3
ACCEPTED_DESCONNECTION = 4

def server_loop():
	while running:
		(client_socket, address) = server_socket.accept()
		init_as_connection(address, client_socket)
	server_socket.close()

def client_loop(ip, socket):
	while True: #TODO while connected
		packet = socket.recv(RECIEVE_BUFFER)
		if not packet: break
		first_byte = packet[0];
		if(int(first_byte) == 1):
			#is connection request
			dictn = parse_connection_packet(packet);
			#send connection ack
			socket.send()
		else if(int(first_byte) == 2):
			
			as_neighbors.append({'ip': vc_ip, 'mask': vc_mask, 'as_id': vc_number})
			as_neighbors_log.append({'op': 1, 'timestamp': 0, 'origin': None}) 
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
	as_ip = str(raw_input('Escriba la mascara: '))
	as_number = int(raw_input('Escriba el numero de sistema autonomo: '))

	server_socket.bind(('0.0.0.0', LISTEN_PORT))
	server_socket.listen(5)
	thread = threading.Thread(target=server_loop)
	thread.daemon = True
	thread.start()

	choice = -1
	while choice != 0:
		choice = int(raw_input('Que desea hacer?\n1 - Agregar vecino.\n2 - Agregar host.\n3 - Desconectar vecino.\n0 - Salir.\n'))
		if choice == 0:
			# TODO: close socket
			for connection in connections:
				connection['socket'].close()
			running = False
		if choice == 1:
			vc_ip = str(raw_input('Escriba la IP del vecino'))
			vc_mask = str(raw_input('Escriba la mascara del vecino: '))
			vc_number = str(raw_input('Escriba el numero de sistema autonomo vecino: '))
			
			socket = cocket(vc_ip, LISTEN_PORT)
			
			packet = create_connection_packet({'type':REQUESTED_CONNECTION, 'as_id':int(as_number) ,'ip':as_ip, 'mask':as_ip })
			socket.send(packet)
			#sent_time=time()
			
			try:
				packet = socket.recv(RECIEVE_BUFFER)
			except socket.timeout, e:
				do:
					answer = str(raw_input('Conexión duró más de 5 segundos, ¿reintentar? y/n')
				while(answer != 'y' && answer != 'n')
				as_neighbors_log.append({'op': 1, 'timestamp': 0, 'origin': None})
			except socket.error, e:
				
			else:
				if(int(packet[0]) == 2): #Not sure if works, ==2: accept connection
					dictn = parse_connection_packet(packet)
					as_neighbors.append({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id'], 'route':dictn['as_id'], 'cost': 0})#TODO cost
					 # op: 1 = CREATE
					

		if choice == 2:
			host_ip = str(raw_input('Escriba la IP del host: '))
			hosts.append(host_ip)
		
		if choice == 3:
			

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
	
	
def cSocket(ip, port):
	socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket.connect(ip, port)
	if not socket: 
		print("no se pudo conectar a esa dir IP")
		break
	socket.settimeout(5)
	return socket

if __name__ == "__main__":
	#esto corre de primero
	main()

def disconnectNeighbor():
	
	
