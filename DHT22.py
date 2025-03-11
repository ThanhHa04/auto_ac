import random
import time

class DHT22:
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        temperature = random.uniform(15.0, 30.0)  
        humidity = random.uniform(30.0, 70.0)
        time.sleep(55)
        
        return temperature, humidity

def readSensor(pin):
    sensor = DHT22(pin)
    return sensor.read()
    time.sleep(5)