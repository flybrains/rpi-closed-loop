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


async def produce(socket, slidingqueue):
    while True:
        await asyncio.sleep(0)
        item = poll_socket(socket)
        await queue.put(item)
        
        #IF CONDITION IN ITEM BREAK LOOP
        
    await queue.put(None)
    

async def consume(queue):
    while True:
        item = await queue.get()
        if item is None:
            break

        await asyncio.sleep(0)

socket = initialize_socket_connection(5000)
loop = asyncio.get_event_loop()
queue = asyncio.Queue(loop=loop)
producer_coro = produce(socket, queue)
consumer_coro = consume(queue)
loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
loop.close()





#def get_value():
#    return myqueue
#
#async def run(stepper):
#    stepper.set_current_position(0)
#    ct = 1
#    
#    while runstate:
#        stepper.set_current_position(get_value(ct-1))
#        val = get_value(ct)
#        stepper.move_to(val)
#        await asyncio.sleep(0)
#    if await stepper.wait_on_move():
#        pass
#    else:
#        stepper.stop()
#
#myqueue = SlidingQueue(10)
#
#sock = initialize_socket_connection(5000)
#stepper = initialize_stepper(2000,2000)
#counter, last_click = initialize_encoder()
#mfc1, mfc2, mfc3 = flow_controller.initialize_mfc()
#l1, l2 = led_controller.initialize_led()

#loop = asyncio.get_event_loop()
#try:
#    loop.run_until_complete(run(stepper))
#finally:
#    loop.close()
#    
            


 
