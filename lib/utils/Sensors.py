import numpy as np
import random
import math


class Sensors:
    def __init__(self):
        self.all_sensors = list()
        self.messages = list()
        
        self.temperature = list()
        self.pressure = list()
        self.wind_speed = list()
        self.wind_direction = list()
        
        # Bias Sensors
        
        self.air_mean = np.random.normal(-55, 8, 1)[0]
        self.air_std = np.random.randint(1, 8)
        
        # K Means
        self.label = None
        
    def _get_temperature(self):
        # Min : -77 Celcius, Max : -13 Celcius, Mean : -55 Celcius
        air_temperature_celcius = np.random.normal(self.air_mean, self.air_std, 1)[0]
        
        # pressure_pascals = np.random.normal(725, 48, 1)
        # rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.temperature.append(air_temperature_celcius)
        return air_temperature_celcius
    
    def _get_pressure(self):
        pressure_pascals = np.random.normal(725, 48, 1)[0]
        # rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.pressure.append(pressure_pascals)
        return pressure_pascals
    
    def _get_wind_speed(self):
        last_wind_speed = np.random.normal(7, 2, 1)[0]
        # rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.wind_direction.append(last_wind_speed)
        return last_wind_speed
        
    def _get_wind_direction(self):
        x_wind_movement = random.randint(-1, 1)
        y_wind_movement = random.randint(-1, 1)
        
        last_wind_direction = math.atan2(y_wind_movement,x_wind_movement)/math.pi*180
        self.pressure.append(last_wind_direction)
        return last_wind_direction
    
    def update(self):
        last_temperature = self._get_temperature()
        last_pressure = self._get_pressure()
        last_wind_speed = self._get_wind_speed()
        last_wind_direction = self._get_wind_direction()
        
        self.all_sensors.append([last_temperature, last_pressure, last_wind_speed, last_wind_direction])
        self.messages.append({"temperature": last_temperature, "pressure": last_pressure,
                              "wind_speed": last_wind_speed, "wind_direction": last_wind_direction})

        if len(self.messages) > 0 and len(self.messages[:-1]) > 0:
            print('[INFO] Sensors lecture:', self.messages[:-1][0])
        
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
