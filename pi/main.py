import sys
import time
import asyncio
import numpy as np
from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname

from gpiozero import Device
from stepper import initialize_stepper
from stepper_driver.motor import Stepper
from stepper_driver import config
from stepper_driver.profiles import accel

import flow_controller
import led_controller
from socket_utils import initialize_socket_connection, poll_socket, split_data, check_data_for_cfg
from encoder import initialize_encoder, get_position, kill_encoder

# EXPERIMENT CONFIGS
# 0 = Wait state
# 1 = Closed loop motor, constant odor
# 2 = Closed loop motor, 1D proportional odor

class SlidingQueue(object):
    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.queue = []
    
    def put(self, item):
        if len(self.queue) < self.maxlen:
            self.queue.append(item)
        else:
            self.queue.pop(0)
            self.queue.append(item)
        return None

    def get(self):
        ret = self.queue.pop(-1)
        return ret

def get_value():
    return myqueue

async def run(stepper):
    stepper.set_current_position(0)
    ct = 1
    
    while runstate:
        stepper.set_current_position(get_value(ct-1))
        val = get_value(ct)
        stepper.move_to(val)
        await asyncio.sleep(0)
    if await stepper.wait_on_move():
        pass
    else:
        stepper.stop()

myqueue = SlidingQueue(10)

sock = initialize_socket_connection(5000)
stepper = initialize_stepper(2000,2000)
counter, last_click = initialize_encoder()
mfc1, mfc2, mfc3 = flow_controller.initialize_mfc()
l1, l2 = led_controller.initialize_led()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run(stepper))
finally:
    loop.close()
    
            


 
