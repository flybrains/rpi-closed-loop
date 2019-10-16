from gpiozero import OutputDevice as stepper_pin
from datetime import datetime
import asyncio
from .activators.stepdir import *
import time

DIRECTION_CCW = 0   # Clockwise
DIRECTION_CW  = 1   # Counter-Clockwise

def micros():
    return int(time.time() * 1000000)

class Stepper:
    def __init__(self, profile, dir_pin=21, step_pin=20, ms_pins=[19,16,26]):
        self._profile = profile
        self._start_time = datetime.now()
        self._last_step_time_us = 0
        self._activator = StepDirActivator(dir_pin, step_pin, ms_pins)

    @property
    def position(self):
        return self._profile._current_steps

    @property
    def direction(self):
        return self._profile._direction

    @property
    def acceleration(self):
        return self._profile._acceleration

    @property
    def is_moving(self):
        return self._profile.distance_to_go != 0

    @property
    def distance_to_go(self):
        return self._profile.distance_to_go

    def set_pulse_width(self, pulse_width_us):
        self._activator.set_pulse_width(pulse_width_us)

    def set_target_speed(self, speed):
        self._profile.set_target_speed(speed)

    def set_acceleration(self, acceleration):
        self._profile.set_acceleration(acceleration)

    def configure_microsteps(self):
        self._activator.configure_microsteps()

    async def run(self):
        if await self.run_at_speed():
            self._profile.compute_new_speed()
        return self.is_moving

    async def run_at_speed(self):
        """
        Implements steps according to the current step interval.
        Differs from run() in that it does not call compute_new_speed().
        You must call this at least once per step.
        Returns true if a step occurred.
        """
        # Dont do anything unless we actually have a step interval
        # Dont do anything unless we have somewhere to go
        if not self._profile._step_interval_us or not self._profile.distance_to_go:
            return False

        # Time since this class was created in micrseconds.
        # Basically the Arduino micros() function.
        # time_us = (datetime.now() - self._start_time).total_seconds() * 1000000
        current_time_us = micros()

        next_step_time_us = self._last_step_time_us + self._profile._step_interval_us
        # if (current_time_us - self._last_step_time_us) >= self._profile._step_interval_us:
        if current_time_us >= next_step_time_us:
            # It is time to do a step

            if self._profile._direction == DIRECTION_CW:
            # Clockwise
                self._profile._current_steps += 1
            else:
                # Anticlockwise
                self._profile._current_steps -= 1
            self.step(self._profile._direction)

            self._last_step_time_us = current_time_us
            # self._next_step_time_us = current_time_us + self._step_interval_us
            return True
        else:
            # No step necessary at this time
            return False

    async def run_forever(self):
        while True:

            await self.run()
            await asyncio.sleep(0)

    def start(self):
        self._activator.start()
        self._run_forever_future = asyncio.ensure_future(self.run_forever())

    def move_to(self, absolute_steps):
        """
        Schedules move to an absolute number of steps.
        """
        if self._profile._target_steps != absolute_steps:
            self._profile._previous_target_steps = self._profile._target_steps
            self._profile._target_steps = absolute_steps
            self._profile.compute_new_speed()

    def move(self, relative_steps):
        """
        Schedules move to a number of steps relative to the current step count.
        """
        self.move_to(self._profile._current_steps + relative_steps)

    async def wait_on_move(self):
        while self.is_moving:
            await asyncio.sleep(0)


    def step(self, direction):
        self._activator.step(self._profile._direction)

    def set_current_position(self, position):
        self._profile.set_current_position(position)

    def abort(self):
        self.set_current_position(self._profile._current_steps)

    def reset_step_counter(self):
        self.set_current_position(0)

    def stop(self):
        """
        Shutdown the stepper, driver chip, etc.
        """
        self._run_forever_future.cancel()

    def predict_distance_to_go(self, target_steps):
        """
        Convenience function for any code that may want to know how many steps we will go
        """
        return target_steps - self._profile._current_steps

    def predict_direction(self, target_steps):
        """
        Convenience function for any code that may want to know what direction we would travel
        """
        return DIRECTION_CW if self.predict_distance_to_go(target_steps) > 0 else DIRECTION_CCW
