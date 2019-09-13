import sys
import time
import threading
from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname

class Coordinator(object):
    def __init__(self):
        self._created = time.time()


def initialize_socket_connection(PORT, PACKET_SIZE):
    SERVER_PORT = PORT
    SIZE = PACKET_SIZE
    HOSTNAME = gethostbyname('0.0.0.0')
    SOCKET_CONN_1 = socket(AF_INET, SOCK_DGRAM)
    SOCKET_CONN_1.bind((HOSTNAME, SERVER_PORT))
    return SOCKET_CONN_1

def check_data_for_cfg(data):
    if data.startswith('<'):
        cfg = data[1:-1].split(',')
    else
        cfg = []
    return cfg


def poll_socket(sock):
    (data,addr) = sock.recvfrom(SIZE)
    return data

def motor_control():
    return 1

def odor_gradient():
    return 1

def main():

    coordinator = Coordinator()

    # initialize socket connection
    sock = initialize_socket_connection(5000, 1024)

    motor_control_thread = threading.Thread(target=motor_control, args=())
    odor_gradient_thread = threading.Thread(target=odor_gradient, args=())

    initialize

    while True:
        data = poll_socket(sock)
        cfg,  = check_if_data_is_config(data)

        if cfg==[]:
            pass

        else:
            safelyKillThread()
            startNewThread()





if __name__=='__main__':
    main()





while True:

sys.exit()
