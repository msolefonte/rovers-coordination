import numpy as np
import random
import math

class Sensors():
    
    def __init__(self, operation_area, max_speed):
        self.operation_area = [
            [int(operation_area.split(',')[0]), int(operation_area.split(',')[1])],
            [int(operation_area.split(',')[2]), int(operation_area.split(',')[3])]
        ]
        
        self.max_speed = max_speed
         # Sensors
        self.all_sensors = list()
        self.messages = list()
        
        self.speedometer = list()
        self.location = list()
        self.temperature = list()
        self.pressure = list()
        self.wind_speed = list()
        self.wind_direction = list()
        
        self.last_speedometer = {'x': 0, 'y': 0}
        self.last_location = {'x': 0, 'y': 0}
        
        # BIAS SENSORs
        
        self.air_mean = np.random.normal(-55, 8, 1)[0]
        self.air_std = np.random.randint(1, 8)
        
        # K_means
        self.label = None
        
    def _move(self):
        x_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)
        y_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)

        if self.last_location['x'] + x_movement < self.operation_area[0][0]:
            x_movement = self.operation_area[0][0] - self.last_location['x']
        if self.last_location['x'] + x_movement > self.operation_area[1][0]:
            x_movement = self.operation_area[1][0] - self.last_location['x']
        if self.last_location['y'] + y_movement < self.operation_area[0][1]:
            y_movement = self.operation_area[0][1] - self.last_location['y']
        if self.last_location['y'] + y_movement > self.operation_area[1][1]:
            y_movement = self.operation_area[1][1] - self.last_location['y']

        self.last_location = {'x': self.last_location['x'] + x_movement,
                              'y': self.last_location['y'] + y_movement}
        self.last_speedometer = {'x': x_movement, 'y': y_movement}
        
        self.location.append(self.last_location)
        self.speedometer.append(self.last_speedometer)
        
        
    def _get_temperature(self):
        
        # Min : -77 Celcius, Max : -13 Celcius, Mean : -55 Celcius
        air_temperature_celcius = np.random.normal(self.air_mean, self.air_std, 1)[0]
        
        #pressure_pascals = np.random.normal(725, 48, 1)
        #rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.temperature.append(air_temperature_celcius)
        return air_temperature_celcius
    
    def _get_pressure(self):
        
        pressure_pascals = np.random.normal(725, 48, 1)[0]
        #rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.pressure.append(pressure_pascals)
        return pressure_pascals
    
    def _get_wind_speed(self):

        last_wind_speed = np.random.normal(7, 2, 1)[0]
        #rems_sensors = np.concatenate((air_temperature_celcius, pressure_pascals))
        self.wind_direction.append(last_wind_speed)
        return last_wind_speed
        
    def _get_wind_direction(self):
        x_wind_movement = random.randint(-1, 1)
        y_wind_movement = random.randint(-1, 1)
        
        last_wind_direction = math.atan2(y_wind_movement,x_wind_movement)/math.pi*180
        self.pressure.append(last_wind_direction)
        return last_wind_direction
    
    def update(self):
        
        self._move()
        last_temperature = self._get_temperature()
        last_pressure = self._get_pressure()
        last_wind_speed = self._get_wind_speed()
        last_wind_direction = self._get_wind_direction()
        
        self.all_sensors.append([self.last_location['x'], self.last_location['y'],
                         last_temperature, last_pressure, last_wind_speed, last_wind_direction])
        
        self.messages.append({"location(x)" : self.last_location['x'],
                         "location(y)" : self.last_location['y'],
                         "temperature:" : last_temperature, "pressure:" : last_pressure, 
                         "wind_speed:" : last_wind_speed, "wind_direction:" : last_wind_direction})
        
    def k_means(self):
        
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
            init = "random",
            n_clusters = kl.elbow,
            n_init = 10,
            max_iter = 300,
            random_state= 23
        )
        
        kmeans.fit(np.array(self.all_sensors))
        
        self.label = kmeans.fit_predict(np.array(self.all_sensors))
        return self.label