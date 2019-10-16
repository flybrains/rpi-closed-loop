from gpiozero import PWMLED
from time import sleep

def initialize_mfc():

    mfc_pin1 = 5
    mfc_pin2 = 6
    mfc_pin3 = 13

    # Although these are not LEDs,
    # PWMLED is the easiest pwm implementation
    # in gpiozero and will be used for mfcs
    mfc1 = PWMLED(mfc_pin1)
    mfc2 = PWMLED(mfc_pin2)
    mfc3 = PWMLED(mfc_pin3)

    return mfc1, mfc2, mfc3

def change_dutycycles(p1, p2, p3, ds1, ds2, ds3):
    p1.value = ds1
    p2.value = ds2
    p3.value = ds3
    return None
