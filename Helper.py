import numpy as np

# global vars
timestamp: int = 0
seed = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)

def getImportance():
	imp = np.array([np.random.uniform(0.3, 5.0), np.random.uniform(1.0, 6.0)])
	return imp / np.sum(imp)


def getUserBias():
	elem_one = np.random.beta(3.1, 2.7)
	elem_two = np.random.beta(4.9, 5.2)
	return np.clip(np.array([elem_one, elem_two]), 0, 1)


def getNewBias(user_bias, post, importance, agree):
	elem_one = elem_two = 0
	if agree:
		elem_one = user_bias[0] * (1 - importance[0]) + importance[0] * post.bias[0]
		elem_two = user_bias[1] * (1 - importance[1]) + importance[1] * post.bias[1]
	else:
		elem_one = user_bias[0] * (1 + importance[0]) - importance[0] * post.bias[0]
		elem_two = user_bias[1] * (1 + importance[1]) - importance[1] * post.bias[1]
	return np.clip(np.array([elem_one, elem_two]), 0, 1)






 