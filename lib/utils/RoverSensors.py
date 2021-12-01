import math
import numpy as np
import random
import time
from .constants import SLEEP_TIME_SENSORS


class RoverSensors:
    def __init__(self):
        self.all_sensors = list()
        self.lectures = list()

        self.temperature = list()
        self.pressure = list()
        self.wind_speed = list()
        self.wind_direction = list()

        # Engine sensors

        self.location = self.location
        self.speedometer = self.speedometer
        
        # K Means
        self.label = None

    @staticmethod
    def _generate_sensor_lecture(sensor, mean, standard_deviation):
        generated_value = np.random.normal(mean, standard_deviation, 1)[0]
        sensor.append(generated_value)
        return generated_value

    def _update_temperature(self):
        # Min : -77 Celcius, Max : -13 Celcius, Mean : -55 Celcius
        air_mean = np.random.normal(-55.0, 8.0, 1)[0]
        air_std = np.random.randint(1, 8)

        return RoverSensors._generate_sensor_lecture(self.temperature, air_mean, air_std)
    
    def _update_pressure(self):
        return RoverSensors._generate_sensor_lecture(self.pressure,  725.0, 48.0)
    
    def _update_wind_speed(self):
        return RoverSensors._generate_sensor_lecture(self.wind_speed,  7.0, 2.0)
        
    def _update_wind_direction(self):
        x_wind_movement = random.randint(-1, 1)
        y_wind_movement = random.randint(-1, 1)
        
        last_wind_direction = math.atan2(y_wind_movement, x_wind_movement)/math.pi*180
        self.pressure.append(last_wind_direction)
        return last_wind_direction
    
    def update(self):
        last_temperature = self._update_temperature()
        last_pressure = self._update_pressure()
        last_wind_speed = self._update_wind_speed()
        last_wind_direction = self._update_wind_direction()

        self.all_sensors.append([last_temperature, last_pressure, last_wind_speed, last_wind_direction])
        self.lectures.append({"temperature": last_temperature, "pressure": last_pressure,
                              "wind_speed": last_wind_speed, "wind_direction": last_wind_direction})
        
    def k_means(self):
        try:
            from kneed import KneeLocator
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score

            kmeans_kwargs = {
                "init": "random",
                "n_init": 10,
                "max_iter": 300,
                "random_state": 23,
            }

            # A list holds the SSE values for each k
            sse = []
            for k in range(1, 11):
                kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
                kmeans.fit(np.array(self.all_sensors))
                sse.append(kmeans.inertia_)

            kl = KneeLocator(
                range(1, 11), sse, curve="convex", direction="decreasing"
            )

            kmeans = KMeans(
                init="random",
                n_clusters=kl.elbow,
                n_init=10,
                max_iter=300,
                random_state=23
            )

            kmeans.fit(np.array(self.all_sensors))

            self.label = kmeans.fit_predict(np.array(self.all_sensors))
            return self.label
        except ValueError:
            pass

    def _start_sensors(self):
        while True:
            time.sleep(SLEEP_TIME_SENSORS)
            self.update()

            print(self.lectures)
            if len(self.lectures) > 0:
                self.lectures[-1]['positioning-system'] = self.location
                self.lectures[-1]['speedometer'] = self.speedometer
                print('[DEBU] Sensors lecture:', self.lectures[-1])
                # print('[INFO] Sensors KMeans:', self.k_means())
