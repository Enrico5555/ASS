#!/usr/bin/python
# For testing only!

import socket

IP = '127.0.0.1'

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((IP, 57809))
