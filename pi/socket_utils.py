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
    runstate = int(toks[0])
    motor_target = int(toks[1])
    mfc1_sp = float(toks[2])
    mfc2_sp = float(toks[3])
    mfc3_sp = float(toks[4])
    led1_sp = float(toks[5])
    led2_sp = float(toks[6])

    return runstate, [motor_target,mfc1_sp,mfc2_sp,mfc3_sp,led1_sp,led2_sp]

def check_data_for_cfg(data):
    data = data.decode("utf-8")
    print(data)
    if data.startswith('$'):
        cfg = int(data[1])
    else:
        cfg = 0
    return cfg
