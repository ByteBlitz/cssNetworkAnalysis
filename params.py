import os
from datetime import datetime
import numpy as np
import numpy.linalg as linalg
import math
import funcs as f

# project name
NAME: str = "2D"

# metadata and deterministic randomization
timestamp: int = 0
seed: int = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)

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

SR_BIAS = np.array([0.5 for _ in range(N)])


def make_user_bias():
    return np.clip(np.array([rng.beta(3.1, 2.7) if i % 2 == 0 else rng.beta(4.9, 5.2) for i in range(N)]), 0, 1)


def make_importance():
    imp = np.array([rng.uniform(0.3, 5.0) if i % 2 == 0 else rng.uniform(1.0, 6.0) for i in range(N)])
    return imp / linalg.norm(imp) * SQRT_N


def make_online_bias():
    return f.as_probability(rng.normal(USR_ONLINE_BIAS, 0.2))


def make_create_bias():
    return f.as_probability(rng.normal(USR_CREATE_BIAS, 0.01))


# moderation
MODERATION = True
MOD_BIAS = np.array([0.5 for _ in range(N)])
MOD_ZONES = np.array([0.2, 0.3, 0.4]) * SQRT_N / math.sqrt(2)
# MOD_ZONES = np.array([0.35, 0.45, 0.5])

MOD_SCAN_POSTS = 200
# MOD_SCAN_POSTS = 20
# MOD_SCAN_USERS = min(int(USR_COUNT * 0.05), MOD_SCAN_POSTS)
MOD_SCAN_USERS = 32
# MOD_SCAN_USERS = 4
MOD_ACCURACY = 30

EX_ZONES = np.array([0.25, 0.4, 0.5]) * SQRT_N / math.sqrt(2)

# identification
ID = NAME + "_" + datetime.now().strftime("[%Y,%m,%d_%H,%M,%S]") + "_" + "[USR=" + str(USR_COUNT) + ",SR=" + str(SR_COUNT) + "]" + "_" + "[" + ("MOD" if MODERATION else "UNMOD") + ",A=" + str(MOD_ACCURACY) + ",P=" + str(MOD_SCAN_POSTS) + ",U=" + str(MOD_SCAN_USERS) + "]"

print(ID)
os.makedirs(f"results/{ID}/gifs")
os.mkdir(f"results/{ID}/plots")
