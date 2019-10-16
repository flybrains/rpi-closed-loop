from gpiozero import Device
from stepper_driver.motor import Stepper
from stepper_driver import config
import time
import asyncio
from stepper_driver.profiles import accel
import numpy as np

def initialize_stepper(max_rpm, acceleration):
    stepper = Stepper(accel.AccelProfile())
    stepper.start()
    steps_per_rev = 800
    stepper.set_target_speed(steps_per_rev*(max_rpm/60))
    stepper.set_acceleration(acceleration)
    stepper.set_pulse_width(2)
    stepper.configure_microsteps()
    return stepper

def get_value(index):
    values = list(np.arange(0,10000,1))
    return values[index]

def get_runstate():
    pass
    return None

async def move(stepper):

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

def run_stepper(stepper):
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(move(stepper))

    finally:
        loop.close()


if __name__=='__main__':
    stepper = initialize_stepper(2000, 1000)
    run_stepper(stepper)