from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname


def initialize_socket_connection(PORT):
    SERVER_PORT = PORT
    HOSTNAME = gethostbyname('0.0.0.0')
    SOCKET_CONN_1 = socket(AF_INET, SOCK_DGRAM)
    SOCKET_CONN_1.bind((HOSTNAME, SERVER_PORT))
    return SOCKET_CONN_1

def poll_socket(sock):
    (data,addr) = sock.recvfrom(1024)
    return data

def split_data(data):
    toks = data[1:-1].split(',')
    motor_target = toks[0]
    stpt1 = toks[1]
    stpt2 = toks[2]
    stpt3 = toks[3]
    return motor_target, stpt1, stpt2, stpt3

def check_data_for_cfg(data):
    data = data.decode("utf-8")
    print(data)
    if data.startswith('$'):
        cfg = int(data[1])
    else:
        cfg = 0
    return cfg