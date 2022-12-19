import os
from datetime import datetime
import numpy as np
import numpy.linalg as linalg
import math
import funcs as f

# project name
NAME: str = "Test"

# metadata and deterministic randomization
timestamp: int = 0
seed: int = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=1024)

# simulation times
ROUNDS = 40
PER_ROUND = 12

# opinion dimensions
N = 2
SQRT_N = math.sqrt(N)

# users and subreddits
USR_COUNT = 2000
SR_COUNT = 112

USR_ONLINE_BIAS = 0.60
USR_CREATE_BIAS = 0.016
USR_SUBREDDIT_CAP = 20

USR_HOT_BIAS = 0.7

SR_BIAS = np.array([0.5, 0.5])


def make_user_bias():
    elem_one = rng.beta(3.1, 2.7)
    elem_two = rng.beta(4.9, 5.2)
    return np.clip(np.array([elem_one, elem_two]), 0, 1)


def make_importance():
    imp = np.array([rng.uniform(0.3, 5.0), rng.uniform(1.0, 6.0)])
    return imp / linalg.norm(imp) * SQRT_N


def make_online_bias():
    return f.as_probability(rng.normal(USR_ONLINE_BIAS, 0.2))


def make_create_bias():
    return f.as_probability(rng.normal(USR_CREATE_BIAS, 0.01))


# moderation
MODERATION = True
MOD_BIAS = np.array([0.5, 0.5])
MOD_ZONES = np.array([0.6, 0.7, 0.8]) * SQRT_N

MOD_SCAN_POSTS = 150
MOD_SCAN_USERS = min(int(USR_COUNT * 0.05), MOD_SCAN_POSTS)
MOD_ACCURACY = 100

# identification
ID = "_".join([NAME, datetime.now().strftime("[%Y:%m:%d %H:%M:%S]"),
               "[" + str(USR_COUNT) + "USR:" + str(SR_COUNT) + "SR]",
               "[" + ("MOD:" if MODERATION else "UNMOD:") +
               str(MOD_ACCURACY) + "A:" + str(MOD_SCAN_POSTS) + "P:" + str(MOD_SCAN_USERS) + "U]"])
print(ID)
os.makedirs(f"results/{ID}/gifs")
os.mkdir(f"results/{ID}/plots")
