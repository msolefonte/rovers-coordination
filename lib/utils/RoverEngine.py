import random
import time
from .constants import SLEEP_TIME_ENGINE


class RoverEngine:
    def __init__(self, operation_area, max_speed):
        self.operation_area = operation_area
        self.max_speed = max_speed

        # Sensors
        self.movement_disabled = False
        self.speedometer = {'x': 0, 'y': 0}

    def _ensure_movement_is_on_range(self, x_movement, y_movement):
        if self.location['x'] + x_movement < self.operation_area[0][0]:
            x_movement = self.operation_area[0][0] - self.location['x']
        if self.location['x'] + x_movement > self.operation_area[1][0]:
            x_movement = self.operation_area[1][0] - self.location['x']
        if self.location['y'] + y_movement < self.operation_area[0][1]:
            y_movement = self.operation_area[0][1] - self.location['y']
        if self.location['y'] + y_movement > self.operation_area[1][1]:
            y_movement = self.operation_area[1][1] - self.location['y']

        return x_movement, y_movement

    def _move(self):
        x_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)
        y_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)

        x_movement, y_movement = self._ensure_movement_is_on_range(x_movement, y_movement)

        self.location = {'x': self.location['x'] + x_movement, 'y': self.location['y'] + y_movement}
        self.speedometer = {'x': x_movement, 'y': y_movement}

    def _start_engine(self):
        while True:
            if not self.movement_disabled:
                self._move()
                print('[INFO] Rover moved to new location', flush=True)
            time.sleep(SLEEP_TIME_ENGINE)
