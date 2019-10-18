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

from flow_controller import initialize_mfc, change_mfc_dutycycles
from led_controller import initialize_led, change_led_dutycycles
from socket_utils import initialize_socket_connection, poll_socket, split_data, check_data_for_cfg
from encoder import initialize_encoder, get_position, kill_encoder


async def produce_setpoints(socket, queue):

    while True:
        await asyncio.sleep(0)
        item = poll_socket(socket)
        runstate, setpoints = split_data(item)
        await queue.put(setpoints)
        if runstate==0:
             break
    await queue.put(None)



async def consume_and_set(queue):

    # Initialize Hardware - Not experiment-specific
    position, last_click = initialize_encoder()
    stepper = initialize_stepper(2000,2000)
    led1, led2 = initialize_led()
    mfc1, mfc2, mfc3 = initialize_mfc()

    while True:
        setpoints = await queue.get()
        if setpoints is None:
            break
        else:
            # Unpack hardware setpoints
            [motor_target, mfc1_sp, mfc2_sp, mfc3_sp, led1_sp, led2_sp] = setpoints
            position, last_click = get_position(position, last_click)

            # Set motor pos from enconder and command new move
            stepper.set_current_position(position)
            stepper.moveto(motor_target)

            # Set MFC and LED pulse-width levels
            change_led_dutycycles(led1, led2, led1_sp, led2_sp)
            change_mfc_dutycycles(mfc1, mfc2, mfc3, mfc1_sp, mfc2_sp, mfc3_sp)

            await asyncio.sleep(0)

    if await stepper.wait_on_move():
        pass
    else:
        stepper.stop()
        kill_encoder()



socket = initialize_socket_connection(5000)
loop = asyncio.get_event_loop()
queue = asyncio.Queue(loop=loop)
producer_coro = produce_setpoints(socket, queue)
consumer_coro = consume_and_set(queue)
loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
loop.close()
