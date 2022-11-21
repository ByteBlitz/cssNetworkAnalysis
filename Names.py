import numpy as np
import random

names = np.array(["Max", "Yuri", "Frederick", "Fabian"])
surnames = np.array(["Mueller", "Maier", "Schmidt", "Doe"])

def generateName():
    name = random.choice(names)
    surname = random.choice(surnames)
    return name + " " + surname