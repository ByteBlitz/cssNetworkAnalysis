import numpy as np
import params as pms

names = np.array(["Max", "Yuri", "Frederick", "Fabian"])
surnames = np.array(["Mueller", "Maier", "Schmidt", "Doe"])


def generateName():
    """Generates a random name to identify a user. """
    return "".join([pms.rng.choice(names), " ", pms.rng.choice(surnames)])
