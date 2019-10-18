from RPi import GPIO
from time import sleep

def initialize_encoder():
    clk = 7
    dt = 8
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    last_click = GPIO.input(clk)

    return 800000, last_click


def get_position(counter, clkLastState):
    clkState = GPIO.input(7)
    dtState = GPIO.input(8)
    if clkState != clkLastState:
        if dtState != clkState:
            counter += 1
        else:
            counter -= 1
    clkLastState = clkState

    return counter, clkLastState

def kill_encoder():
    GPIO.cleanup()
