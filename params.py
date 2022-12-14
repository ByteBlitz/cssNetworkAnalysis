import numpy as np
import math


timestamp: int = 0
seed: int = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)

n = 2
sqrt_n = math.sqrt(n)


def get_n():
    return n


def get_sqrt_n():
    return sqrt_n
