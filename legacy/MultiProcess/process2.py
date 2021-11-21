import random
import time
def generateData():
    print('Data from 2:',random.random())

if __name__ == "__main__":
    while True:
        generateData()
        time.sleep(2)