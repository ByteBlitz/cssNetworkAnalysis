import numpy as np
import random

names = np.array(["Max", "Yuri", "Frederick", "Fabian"])
surnames = np.array(["Mueller", "Maier", "Schmidt", "Doe"])


def generateName():
    name = random.choice(names.tolist())
    surname = random.choice(surnames.tolist())
    return name + " " + surname
