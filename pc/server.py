import sys
from socket import socket, AF_INET, SOCK_DGRAM

RPI_IP = '129.85.243.21'
RPI_PORT = 5000
PACKET_SIZE = 1024

SOCK_CONN_1=socket(AF_INET, SOCK_DGRAM)


i = 0
while True:
    SOCK_CONN_1.sendto(str.encode('{}'.format(i%9)), (RPI_IP, RPI_PORT))
    i = i+1
sys.exit()
