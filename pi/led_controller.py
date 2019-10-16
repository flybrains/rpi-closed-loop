from gpiozero import PWMLED
from time import sleep

def initialize_led():

    mfc_pin1 = 5
    mfc_pin2 = 6
    
    l1 = PWMLED(mfc_pin1)
    l2 = PWMLED(mfc_pin2)

    return l1, l2

def change_dutycycles(p1, p2, ds1, ds2):
    p1.value = ds1
    p2.value = ds2

    return None