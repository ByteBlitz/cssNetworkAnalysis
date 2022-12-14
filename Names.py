import numpy as np
import params as pms

names = np.array(["Max", "Yuri", "Frederick", "Fabian"])
surnames = np.array(["Mueller", "Maier", "Schmidt", "Doe"])


def generateName():
    name = pms.rng.choice(names)
    surname = pms.rng.choice(surnames)
    return name + " " + surname
