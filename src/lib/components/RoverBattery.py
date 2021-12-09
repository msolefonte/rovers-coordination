import random
import time
from lib.utils.constants import SLEEP_TIME_BATTERY


class RoverBattery:
    """
    The battery has a 5% probability of getting empty. Once empty, the rover enters in the low battery mode and spends
    three turns in the same location, disables networking and, if it was, stops acting as a leader. However, if the
    rover is stopped in a position and the antenna is deployed, the battery can not go down.
    """
    def __init__(self):
        self.low_battery_mode = False
        self.turns_spent_recharging = 0

        # Read from other components
        self.leader_id = self.leader_id
        self.node_id = self.node_id
        self.networking_disabled = self.networking_disabled
        self.movement_disabled = self.movement_disabled
        self.antenna_deployed = self.antenna_deployed

    def _enable_capabilities(self):
        self.low_battery_mode, self.networking_disabled, self.movement_disabled = False, False, False
        print('[INFO] Battery recharged. Low battery mode disabled', flush=True)

    def _disable_capabilities(self):
        print('[INFO] Battery low. Deploying solar panels', flush=True)
        self.low_battery_mode, self.networking_disabled, self.movement_disabled = True, True, True
        if self.leader_id == self.node_id:
            self.leader_id = None

    def _is_battery_low(self):
        return not self.antenna_deployed and random.randint(0, 100) < 5

    def _check_battery(self):
        if self.low_battery_mode:
            if self.turns_spent_recharging >= 3:
                self._enable_capabilities()
                self.turns_spent_recharging = 0
            else:
                print('[INFO] Recharging...', flush=True)
                self. turns_spent_recharging += 1
        elif self._is_battery_low():
            self._disable_capabilities()

    def _start_battery_check(self):
        while True:
            self._check_battery()
            time.sleep(SLEEP_TIME_BATTERY)
