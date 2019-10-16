from gpiozero import OutputDevice as stepper_pin
import time

DIRECTION_CCW = 0   # Clockwise
DIRECTION_CW  = 1   # Counter-Clockwise

def sleep_microseconds(us_to_sleep):
    time.sleep(us_to_sleep / float(1000000))

class StepDirActivator:

    def __init__(self, dir_pin, step_pin, ms_pins):

        self._pulse_width_us = 2
        self._step_pin = stepper_pin(step_pin)
        self._dir_pin = stepper_pin(dir_pin)
        self._ms1_pin = stepper_pin(ms_pins[0])
        self._ms2_pin = stepper_pin(ms_pins[1])
        self._ms3_pin = stepper_pin(ms_pins[2])
        self._direction = None

    def configure_microsteps(self):
        self._ms1_pin.off()
        self._ms2_pin.on()
        self._ms3_pin.off()

    @property
    def pulse_width(self):
        return self._pulse_width_us

    def set_pulse_width(self, pulse_width_us):
        self._pulse_width_us = pulse_width_us

    def start(self):
        self._dir_pin.on()
        self._step_pin.off()

    def step(self, direction):
        """
        Unconditionally perform a step.
        """
        # log.debug('Step direction=%s pulse_width_us=%s', direction, self._pulse_width_us)
        if direction==DIRECTION_CCW:
            self._dir_pin.off()
        else:
            self._dir_pin.on()

        self._step_pin.on()

        sleep_microseconds(self._pulse_width_us)
        self._step_pin.off()
