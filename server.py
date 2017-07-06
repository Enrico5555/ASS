#!/usr/bin/python3.5
#coding: utf-8

import socket
from struct import unpack, pack
import threading
import os, sys
from time import time

#SOCKET UTILIZADO PARA CONECTAR CON EL CLIENTE
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#INFO DEL NODO EN QUE ESTOY
global my_as_ip
my_as_ip = ''
global my_as_mask
my_as_mask = ''
global my_as_id
my_as_id = 0

#TABLAS DE VECINOS
global as_neighbors
as_neighbors = []
global as_neighbors_log
as_neighbors_log = []
as_neighbors_lock = threading.Lock()

#TABLAS DE ALCANZABILIDAD
global reachability
reachability = []
reachability_lock = threading.Lock()
global reachability_log
reachability_log = []
reachability_log_lock = threading.Lock()

class Router:
	def __init__(self, ip, mask):
		self.ip = ip
		self.mask = mask
		self.route = []

	def exend_route(self, route):
		self.route.extend(route)

	def add_to_route(self, as_id):
		self.route.insert(0,as_id)

	def __str__(self):
		return "{ 'ip': "+self.ip+", 'mask': "+self.mask+ ", 'route': "+str(self.route)+ " }"

	def __repr__(self):
		return "{ 'ip': "+self.ip+", 'mask': "+self.mask+ ", 'route': "+str(self.route)+ " }"

global connections
connections = []
connections_lock = threading.Lock()

running = True

#CONSTANTES
RECIEVE_BUFFER = 4096
LISTEN_PORT= 57809
REQUESTED_CONNECTION = 1
ACCEPTED_CONNECTION = 2
REQUESTED_DISCONNECTION = 3
ACCEPTED_DISCONNECTION = 4
REACHABILITY_UPDATE = 5
#log OP
CONNECTION_SUCCESS = 1
CONNECTION_TIMEOUT = 2
CONNECTION_ERROR = 3
DISCONNECTION_SUCCESS = 4
DISCONNECTION_ERROR = 5



def server_loop():
	while running:
		(client_socket, address) = server_socket.accept()
		init_as_connection(address, client_socket)
	server_socket.close()

#LISTENER PARA MENSAJES ENTRANTES
def client_loop(ip, cli_socket):
	global as_neighbors
	global reachability
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
			with as_neighbors_lock:
				as_neighbors.append({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id']})
				as_neighbors_log.append({'op': CONNECTION_SUCCESS, 'timestamp': time(), 'as_id': dictn['as_id'], 'message':'Conection success'})
				#print(my_as_ip + ';' + my_as_mask + ';' + str(my_as_id))
				#send connection ack

				print("\tSe ha logrado una conexión exitosa con: " + str({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id']}))
				packet = create_connection_packet(type=ACCEPTED_CONNECTION, as_id=my_as_id , ip=my_as_ip, mask=my_as_mask )
				try:
					cli_socket.send(packet)
				except socket.error:
					print("Error en conexión")
		elif(int(first_byte) == REQUESTED_DISCONNECTION):
			dictn = parse_connection_packet(packet)
			for ngh in as_neighbors[:]:
				if(ngh['as_id'] == dictn['as_id']):
					with as_neighbors_lock:
						as_neighbors.remove(ngh)
						as_neighbors_log.append({'op': DISCONNECTION_SUCCESS, 'timestamp': time(), 'as_id': dictn['as_id'], 'message':'Disconection success'})
			packet = create_connection_packet(type=ACCEPTED_DISCONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
			try:
				cli_socket.send(packet)
			except socket.error:
				print("Error en conexión")
			thread =None
			for connection in connections[:]:
				if(connection['ip'] == dictn['ip']):
					with connections_lock:
						connection['socket'].close()
						thread = connection['thread']
						connections.remove(connection)
			thread.join()
		elif(int(first_byte) == REACHABILITY_UPDATE):
			dictn = parse_reachability_packet(packet)
			print(packet)
			if dictn == 0:
				print("Error parseando paquete de alcanzabilidad")
				continue
			as_from = dictn['as_id']
			for destination in dictn['destinations']:
				dont_have_it = True
				for router in reachability:
					if router.ip ==  destination.ip and router.mask == destination.mask:
						if len(router.route) > (len(destination.route)+1):
							router.route = destination.route
							router.add_to_route(my_as_id)
						dont_have_it = False
						break
				if dont_have_it:
					destination.add_to_route(my_as_id)
					reachability.append(destination)

def init_as_connection(ip, cli_socket):
	thread = threading.Thread(target = client_loop, args=(ip, cli_socket))
	thread.daemon = True
	global	connections
	with connections_lock:
		connections.append({'socket': cli_socket, 'ip': ip, 'thread': thread})
	thread.start()

#DESCOMPONE EL PAQUETE PARA OBTENER SUS DATOS
#PAQUETES DE ( (REQUEST || ACCEPT) (CONNECTION || DISCONNECTION) )
def parse_connection_packet(buffer):
	if (len(buffer) != 11):
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

#COMPONE UN PAQUETE CON DATOS DE NODO
def create_connection_packet(**dictn):
	return pack("=BHBBBBBBBB",dictn['type'],dictn['as_id'],*[ord(chr(int(x))) for x in (dictn['ip']+"."+dictn['mask']).split(".")])

#DESCOMPONE EL PAQUETE PARA OBTENER SUS DATOS
#PAQUETES DE REACHABILITY UPDATE
def parse_reachability_packet(buffer):
	try:
		b = []
		b = unpack(">Bhi",buffer[:7])
		print(buffer)
		print(b)
		as_id = b[1]
		destination_amount = b[2]
		destinations = []
		byte_idx=7;
		for i in range(0,destination_amount):
			b = unpack(">BBBBBBBBh",buffer[byte_idx:byte_idx+10])
			print(b)
			ip = str(b[0])+"."+str(b[1])+"."+str(b[2])+"."+str(b[3])
			mask  = str(b[4])+"."+str(b[5])+"."+str(b[6])+"."+str(b[7])
			as_amount = b[8]
			router = Router(ip,mask)
			route = []
			byte_idx= byte_idx+10
			for j in range(0,as_amount):
				route.append(unpack(">h",buffer[byte_idx:byte_idx+2]))
				byte_idx=byte_idx+2
			router.route = route;
			destinations.append(router)
		return {'as_id':as_id,'destinations':destinations}
	except Exception as e:
		print("OS error: {0}".format(e))
		return 0

#COMPONE UN PAQUETE CON ACTUALIZACIONES DE ALCANZABILIDAD
def create_reachability_packet():
	packet = bytearray()
	packet.extend(pack(">Bhi",5, my_as_id, int(len(reachability))))
	for destination in reachability:
		packet.extend(pack(">BBBBBBBB",*[ord(chr(int(x))) for x in (destination.ip+"."+destination.mask).split(".")]))
		packet.extend(pack(">h",int(len(destination.route))))
		for ass in destination.route:
			packet.extend(pack(">h",ass))
	return packet

#CONECTA EL SOCKET CON EL SERVER
def create_socket(ip, port):
	cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	cli_socket.settimeout(5)
	try:
		cli_socket.connect((ip, port))
		return cli_socket
	except socket.timeout:
		print("No se pudo conectar a esa dirección IP\n")
		return 0

def send_reachability_loop():
	last_time = time()
	while True:
		if last_time + 30 <= time():
				global reachability
				if len(reachability) > 0:
					reachability_packet = create_reachability_packet()
					with as_neighbors_lock:
						for connection in connections:
							try:
								connection['socket'].send(reachability_packet)
							except socket.error:
								print("Error en conexión")
					print("Se ha mandado un paquete de alcanzabilidad")
					last_time = time()

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
	server_thread = threading.Thread(target=server_loop)
	server_thread.daemon = True
	server_thread.start()

	reachability_thread = threading.Thread(target=send_reachability_loop)
	reachability_thread.daemon = True
	reachability_thread.start()

	choice = -1
	global	connection
	global as_neighbors_log
	global as_neighbors
	global reachability
	global reachability_log
	while choice != 0:
		try:
			choice = int(input('¿Qué desea hacer?\n1 - Agregar vecino.\n2 - Desconectar vecino.\n3 - Mostrar vecinos.\n4 - Agregar router\n5 - Quitar router\n6 - Ver routers\n0 - Salir.\n'))
		except Exception:
			print("Escriba un número")
			continue
		if choice == 0:
			# TODO: close socket
			with connections_lock:
				for connection in connections:
					connection['socket'].close()
					connection['thread'].join()
				server_thread.join()
				reachability_thread.join()

		if choice == 1:
			vc_ip = str(input('Escriba la IP del vecino: '))
			vc_mask = str(input('Escriba la máscara del vecino: '))
			vc_number = int(input('Escriba el numero de sistema autónomo vecino: '))

			cli_socket = create_socket(vc_ip, LISTEN_PORT)
			if cli_socket == 0:
				continue
			while True:
				packet = create_connection_packet(type=REQUESTED_CONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
				try:
					cli_socket.send(packet)
					packet = cli_socket.recv(RECIEVE_BUFFER)
				except socket.timeout:
					with as_neighbors_lock:
						as_neighbors_log.append({'op': CONNECTION_TIMEOUT, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection timeout'})
					answer = ''
					while answer != 'y' and answer != 'n':
						answer = str(input('Conexión duró más de 5 segundos, reintentar? [y/n] '))
					if(answer == 'y'):
						continue
					elif(answer == 'n'):
						cli_socket.close()
						break

				except socket.error:
					print('Error de conexión del socket!\n')
					with as_neighbors_lock:
						as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection error'})
					cli_socket.close()
					break
				else:
					if not packet:
						print('Error de conexión del socket!\n')
						with as_neighbors_lock:
							as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection error'})
						cli_socket.close()
						break
					if(int(packet[0]) == ACCEPTED_CONNECTION): #Not sure if works, ==2: accept connection
						dictn = parse_connection_packet(packet)
						with as_neighbors_lock:
							as_neighbors.append({'ip': dictn['ip'], 'mask': dictn['mask'], 'as_id': dictn['as_id']})
							as_neighbors_log.append({'op': CONNECTION_SUCCESS, 'timestamp': time(), 'as_id': vc_number, 'message':'Conection success'}) # op: 1 = CREATE
							init_as_connection(vc_ip,cli_socket)
						print("¡Conexión Exitosa!\n")
						break
					else:
						print('¡Error de paquete!\n')
						cli_socket.close()
						with as_neighbors_lock:
							as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': vc_number, 'message':'Packet error'})
						break
		elif choice == 2: #DISCONNECT
			vc_number = str(input('Escriba el numero de sistema autónomo vecino a desconectar: '))
			found = [p for p in as_neighbors if p['as_id'] == vc_number]
			if(len(found) == 0):
				print('No existe ese s.a. en los vecinos')
				continue
			neighbor = found[0]

			for connection in connections:
				if connection['ip'] == neighbor['ip']:
					cli_socket = connection['socket']
					thread = connection['thread']
					this_connection = connection
			if not cli_socket or not thread:
				print('No existe ese s.a. en los vecinos')
				with as_neighbors_lock:
					as_neighbors.remove(neighbor)
				continue


			packet = create_connection_packet(type=REQUESTED_DISCONNECTION, as_id=my_as_id ,ip=my_as_ip, mask=my_as_mask )
			cli_socket.send(packet)
			try:
				packet = cli_socket.recv(RECIEVE_BUFFER)
			except socket.timeout:
				with as_neighbors_lock:
					as_neighbors_log.append({'op': CONNECTION_TIMEOUT, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Disconection timeout'})
				answer = str(input('Confirmación de desconexión duró más de 5 segundos, desconectando...'))


				print('¡Desconexión Exitosa!\n')

			except socket.error:
				print('¡Error de conexión del socket!\n')
				with as_neighbors_lock:
					as_neighbors_log.append({'op': CONNECTION_ERROR, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Conection error'})
			else:
				if(int(packet[0]) == ACCEPTED_DISCONNECTION): #Not sure if works, == 3: accept connection
					dictn = parse_connection_packet(packet)
					with as_neighbors_lock:
						as_neighbors.remove(neighbor)
						as_neighbors_log.append({'op': DISCONNECTION_SUCCESS, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Disonection success'}) # op: 1 = CREATE
					print('¡Desconexión Exitosa!\n')
				else:
					print('¡Error de paquete!\n')
					with as_neighbors_lock:
						as_neighbors_log.append({'op': DISCONNECTION_ERROR, 'timestamp': time(), 'as_id': neighbor['as_id'], 'message':'Packet error'})
			cli_socket.close()
			thread.join()
			with connections_lock:
				connections.remove(this_connection)
		elif choice == 3:
			print(str(as_neighbors).replace("}, ","}\n"))
		elif choice == 4:
			r_ip = str(input('Escriba la IP del router: '))
			r_mask = str(input('Escriba la máscara del router: '))
			with reachability_lock:
				router = Router(r_ip,r_mask)
				reachability.append(router)
				#TODO added reachability to LOG
		elif choice == 5:
			r_ip = str(input('Escriba la IP del router a borrar: '))
			r_mask = str(input('Escriba la máscara del router a borrar: '))
			for router in reachability[:]:
				if router.ip==r_ip and router.mask == r_mask:
					with reachability_lock:
						reachability.remove(router)
						#TODO removed reachability to LOG
		elif choice == 6:
			print(str(reachability).replace("}, ","}\n"))
		else:
			print("Escriba un número válido.\n")


if __name__ == "__main__":
	#esto corre de primero
	main()
