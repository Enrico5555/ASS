#!/usr/bin/python3.5
#coding: utf-8

import socket
from struct import unpack, pack
import threading
import os, sys
from time import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
global as_neighbors
as_neighbors = []
global as_neighbors_log
as_neighbors_log = []
global my_as_ip
my_as_ip = ''
global my_as_mask
my_as_mask = ''
global my_as_id
my_as_id = 0

reachability = []
reachability_log = []

hosts = []

connections = []

RECIEVE_BUFFER = 4096
LISTEN_PORT= 57809
REQUESTED_CONNECTION = 1
ACCEPTED_CONNECTION = 2
REQUESTED_DISCONNECTION = 3
ACCEPTED_DISCONNECTION = 4


#log OP
CONNECTION_SUCCESS = 1
CONNECTION_TIMEOUT = 2
CONNECTION_ERROR = 3



def server_loop():
	while running:
		(client_socket, address) = server_socket.accept()
		init_as_connection(address, client_socket)
	server_socket.close()

def client_loop(ip, cli_socket):
	global as_neighbors
	cli_socket.settimeout(None)
	while True: #TODO while connected
		packet = cli_socket.recv(RECIEVE_BUFFER)
		if not packet:
			continue
		first_byte = packet[0];
		if(int(first_byte) == REQUESTED_CONNECTION):
			#is connection request
			#add dictionary
			dictn = parse_connection_packet(packet);
			if(len([p for p in as_neighbors if p['as_id'] == dictn['as_id']])>0):
				continue
			as_neighbors.append({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id'], 'route':dictn['as_id'], 'cost': 0})#TODO cost
			print(my_as_ip + ';' + my_as_mask + ';' + str(my_as_id))
			#send connection ack
			packet = create_connection_packet(type=ACCEPTED_CONNECTION, as_id=my_as_id , ip=my_as_ip, mask=my_as_mask )
			cli_socket.send(packet)
		elif(int(first_byte) == REQUESTED_DISCONNECTION):
			dictn = parse_conenction_packet(packet)
			for ngh in as_neighbors[:]:
				if(ngh['as_id'] == dictn['as_id']):
					as_neighbors.remove(ngh)
			packet = create_connection_packet(type=ACCEPTED_CONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
			cli_socket.send(packet)

def init_as_connection(ip, cli_socket):
	thread = threading.Thread(target = client_loop, args=(ip, cli_socket))
	thread.daemon = True
	global	connections
	connections.append({'socket': cli_socket, 'ip': ip, 'thread': thread})
	thread.start()

def parse_connection_packet(buffer):
	if (len(buffer) != 11):
		print(buffer)
		print(len(buffer))
		print ("no sea fofi")
		return 0
	b = []
	b = unpack("=BHBBBBBBBB",buffer);
	as_id = int(b[1])
	ip = str(b[2])+"."+str(b[3])+"."+str(b[4])+"."+str(b[5])
	mask  = str(b[6])+"."+str(b[7])+"."+str(b[8])+"."+str(b[9])
	dic = {'type':b[0], 'as_id':as_id ,'ip':ip, 'mask':mask }
	print(dic)
	return dic

def create_connection_packet(**dictn):
	print(dictn)
	return pack("=BHBBBBBBBB",dictn['type'],dictn['as_id'],*[ord(chr(int(x))) for x in (dictn['ip']+"."+dictn['mask']).split(".")])

def parse_reachability_packet(buffer):
	if (len(buffer) < 18):
		print ("no sea fofi")
		return 0
	b = []
	b = unpack("hi",buffer[:6]);
	as_id = int(b[1])
	destination_amount = b[2]
	destinantions = []
	#for i in range(0,destination_amount):
	ip = str(b[2])+"."+str(b[3])+"."+str(b[4])+"."+str(b[5])
	mask  = str(b[6])+"."+str(b[7])+"."+str(b[8])+"."+str(b[9])
	return {'type':b[0], 'as_id':as_id ,'ip':ip, 'mask':mask }

def create_reachability_packet(**dictn):
	return pack("=BhBBBBBBBB",dictn['type'],dictn['as_id'],*[ord(chr(int(x))) for x in (dictn['ip']+"."+dictn['mask']).split(".")])


def create_socket(ip, port):
	cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cli_socket.connect((ip, port))
	if not cli_socket:
		print("no se pudo conectar a esa dir IP")
		return 0
	cli_socket.settimeout(5)
	return cli_socket


def main():
	# setup
	while True:
		global my_as_ip
		my_as_ip = str(input("Escriba la IP del sistema autónomo: "))
		if my_as_ip == '' or  not my_as_ip:
			print("Ip no válida")
		else:
			break


	while True:
		global my_as_mask
		my_as_mask= str(input('Escriba la máscara: '))
		if my_as_mask == '' or  not my_as_mask:
			print("Máscara no válida")
		else:
			break

	while True:
		try:
			global	my_as_id
			my_as_id= int(input('Escriba el numero de sistema autónomo: '))
			if not my_as_mask:
				print("id no válida")
			else:
				break
		except Exception:
			print("id no válida")


	server_socket.bind(('0.0.0.0', LISTEN_PORT))
	server_socket.listen(5)
	thread = threading.Thread(target=server_loop)
	thread.daemon = True
	thread.start()

	choice = -1
	global	connection
	global as_neighbors_log
	global as_neighbors
	while choice != 0:
		choice = int(input('Qué desea hacer?\n1 - Agregar vecino.\n2 - Desconectar vecino.\n3 - Mostrar vecinos.\n0 - Salir.\n'))
		if choice == 0:
			# TODO: close socket
			for connection in connections:
				connections['socket'].close()
			running = False
		if choice == 1:
			vc_ip = str(input('Escriba la IP del vecino: '))
			vc_mask = str(input('Escriba la máscara del vecino: '))
			vc_number = int(input('Escriba el numero de sistema autónomo vecino: '))

			cli_socket = create_socket(vc_ip, LISTEN_PORT)

			again = True
			while again:
				packet = create_connection_packet(type=REQUESTED_CONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
				cli_socket.send(packet)
				#sent_time=time()

				try:
					packet = cli_socket.recv(RECIEVE_BUFFER)
				except socket.timeout:
					as_neighbors_log.append({'op': CONNECTION_TIMEOUT, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection timeout'})
					answer = ''
					while answer != 'y' and answer != 'n':
						answer = str(input('Conexión duró más de 5 segundos, reintentar? [y/n] '))
					if(answer == 'y'):
						break
					elif(answer == 'n'):
						cli_socket.close()
						again = False
						break

				except socket.error:
					print('Error de conexión del socket!\n')
					as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection error'})
					cli_socket.close()
					again = False
					break
				else:
					again = False
					if not packet:
						continue
					if(int(packet[0]) == ACCEPTED_CONNECTION): #Not sure if works, ==2: accept connection
						dictn = parse_connection_packet(packet)

						as_neighbors.append({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id'], 'route':dictn['as_id'], 'cost': 0})#TODO cost
						as_neighbors_log.append({'op': CONNECTION_SUCCESS, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection success'}) # op: 1 = CREATE
						init_as_connection(vc_ip,cli_socket)
						print("¡Conexión Exitosa!\n")
					else:
						print('¡Error de paquete!\n')
						cli_socket.close()
						as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': vc_number, 'message':'Packet error'})


		elif choice == 2: #DISCONNECT
			vc_number = str(input('Escriba el numero de sistema autónomo vecino a desconectar: '))
			found = [p for p in as_neighbors if p['as_id'] == vc_number]
			if(len(found) == 0):
				print('No existe ese s.a. en los vecinos')
				break
			neighbor = found[0]
			for connection in connections:
				if connection['ip'] == neighbor['ip']:
					cli_socket = connection['socket']
			if not cli_socket:
				print('No existe ese s.a. en los vecinos')
				as_neighbors.remove(neighbor)
				break

			again = True
			while again:
				packet = create_connection_packet(type=REQUESTED_DISCONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
				cli_socket.send(packet)
				try:
					packet = cli_socket.recv(RECIEVE_BUFFER)
				except socket.timeout:
					as_neighbors_log.append({'op': CONNECTION_TIMEOUT, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Disconection timeout'})
					answer = str(input('Confirmación de desconexión duró más de 5 segundos, desconectando...'))
					cli_socket.close()
					again = False
					print('¡Desconexión Exitosa!\n')
					break

				except socket.error:
					print('¡Error de conexión del socket!\n')
					as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Conection error'})
					cli_socket.close()
					again = True
					break
				else:
					again = False
					if(int(packet[0]) == ACCEPTED_DISCONNECTION): #Not sure if works, == 3: accept connection
						dictn = parse_connection_packet(packet)
						as_neighbors.remove(neighbor)
						as_neighbors_log.append({'op': DISCONNECTION_SUCCESS, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Disonection success'}) # op: 1 = CREATE
						cli_socket.close()
						print('¡Desconexión Exitosa!\n')
					else:
						print('¡Error de paquete!\n')
						cli_socket.close()
						as_neighbors_log.append({'op': DISCONNECTION_ERROR, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Packet error'})

		elif choice == 3:
			print( as_neighbors)
		else:
			print("No sea fofi x2")


if __name__ == "__main__":
	#esto corre de primero
	main()
