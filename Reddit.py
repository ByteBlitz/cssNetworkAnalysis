# Copyright Max Osterried, 2022
# on Github: https://github.com/ByteBlitz/cssNetworkAnalysis
# using the style guide at https://peps.python.org/pep-0008/
# useful pages:
# https://www.python-graph-gallery.com
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
#
#
# FIXME [assuming]:
# Used for declaring implicit simplifications and assumptions, that might impact precision.
#
# TODO:
# replace or reset users or make them change their opinion in downtime
# imports
import math
import copy

import Names
import numpy as np
import scipy as sp
import numpy.linalg as linalg

# global vars
timestamp: int = 0
seed = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)


# functions
def get_n():
    return 4


def get_sqrt_n():
    return 2


def as_probability(val):
    """Keep numbers in [0,1] with this function. """
    return min(max(val, 0), 1)


def most_successful(seq, cnt, metric, worst):
    """Can be used to find the [cnt] most successful items from [seq] concerning [metric]"""
    ms_list = [copy.deepcopy(worst)]
    for item in seq:
        if metric(item) > metric(ms_list[0]):
            i = 0
            while i < len(ms_list):
                if metric(item) < metric(ms_list[i]):
                    break
                i += 1
            ms_list.insert(i, item)
            ms_list = ms_list[max(0, len(ms_list) - cnt):len(ms_list)]

    return ms_list


# objects
class Post:
    # FIXME [assuming]:
    # all posts are of similar quality and similarly convincing

    @profile
    def __init__(self, creator, bias):
        # properties
        self.creation = timestamp
        self.creator: int = creator
        self.bias = np.clip(rng.normal(bias, 0.1), 0, 1)
        # TODO: come up with a better standard deviation
        self.ups = 1
        self.downs = 0

        # statistics
        self.views = 1
        self.success = np.full(get_n(), 0.0, float)

    @profile
    def score(self):
        return self.ups - self.downs

    @profile
    def hot(self):
        """The hot formula. Should match the equivalent function in postgres."""
        s = self.score()
        order = math.log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else 0 if s == 0 else -1
        hours = timestamp - self.creation
        return round(sign * order + hours / 12, 7)

    def get_hot(post):
        """Needed as a sorting criteria. """
        return post.hot()


class Subreddit:
    def __init__(self, bias_list: [float], tolerance):
        # post queues
        self.hot = []
        self.new = []

        # properties
        self.bias = np.clip(rng.normal(bias_list, 0.2), 0, 1)
        # tolerance

        # statistics
        self.stat_bias = []
        self.users = 0

    def enqueue(self, post: Post):
        self.new.append(post)
        self.hot.append(post)
        # amortize sorting by either using a binary heap or splitting time steps into insertion, then sort

    @profile
    def get_bias(self):
        """Return bias-vector over hot-queue weighted by the hot-score. """
        num = np.full(get_n(), 0.0, float)
        den = 0.0

        for post in self.hot:
            num += post.bias * post.hot()
            den += post.hot()

        return num / den if not den == 0 else np.full(get_n(), 0.5, float)


class User:
    # FIXME [assuming]:
    # everyone is equally smart
    # only upvotes/downvotes as regulators
    # repetition effect not taken into account, introduce vulnerability variable
    def __init__(self, usr_id: int, bias_list: np.array, creator_bias: float, touch_grass_bias: float,
                 ls_subreddits: np.array, usr_subreddit_cap: int):
        # properties
        self.id: int = usr_id
        self.name: str = Names.generateName()
        self.bias = np.clip(rng.normal(bias_list, 0.2), 0, 1)

        self.creator_bias: float = as_probability(rng.normal(creator_bias, 0.01))
        self.touch_grass_bias: float = as_probability(rng.normal(touch_grass_bias, 0.2))
        self.subreddits: [Subreddit] = []
        # TODO: convert to array of arrays of subreddits, the bias towards the subreddit and the respective positions
        #  in the hot/new list

        # statistics
        self.viewed_posts: int = 0
        self.created_posts: int = 0
        self.success = np.full(get_n(), 0.0, float)

        # get subreddits
        probs = [1 / max(linalg.norm(sr.bias - self.bias), 0.001) for sr in ls_subreddits]
        s = sum(probs)
        probs = [p / s for p in probs]

        self.subreddits = rng.choice(ls_subreddits,
                                     rng.integers(1, min(len(ls_subreddits), usr_subreddit_cap) + 1),
                                     replace=False,
                                     p=probs)

        for subreddit in self.subreddits:
            subreddit.users += 1

    @profile
    def agree(self, post_bias, threshold):
        """Evaluates, whether the user agrees with a post enough, to change their opinion"""
        # TODO: get me a proper function of agreement
        # make it probabilistic
        # take into account repetition effects (equivalent to acceleration)
        # take into account herd bias
        # importance array
        # return abs(self.fake_bias - post.fake_bias) < threshold
        return linalg.norm(self.bias - post_bias) < threshold

    @profile
    def disagree(self, post_bias, threshold):
        """Evaluates, whether the user disagrees with a post enough, to change their opinion"""
        # TODO: get me a proper function of disagreement
        # return abs(self.fake_bias - post.fake_bias) > (1 - threshold)
        return linalg.norm(self.bias - post_bias) > (get_sqrt_n() - threshold)

    @profile
    def vote(self, post):
        if self.agree(post.bias, 0.2 * get_sqrt_n()):
            post.ups += 1
        elif self.disagree(post.bias, 0.2 * get_sqrt_n()):
            post.downs += 1

    @profile
    def new_bias(self, user_bias, post, influence):
        if self.agree(post.bias, 0.1 * get_sqrt_n()):
            new_bias = np.clip(self.bias * 0.8 + post.bias * 0.2, 0, 1)
            post.success += linalg.norm((self.bias - new_bias))
            self.bias = new_bias
        elif self.disagree(post.bias, 0.1 * get_sqrt_n()):
            # FIXME
            new_bias = np.clip(self.bias * 1.2 - post.bias * 0.2, 0, 1)
            post.success -= linalg.norm((self.bias - new_bias))
            self.bias = new_bias

    @profile
    def create_post(self):
        self.created_posts += 1
        post = Post(self.id, self.bias)

        # select up to 3 subreddits to post on
        for subreddit in rng.choice(self.subreddits, rng.choice(min(3, len(self.subreddits)) + 1), replace=False):
            subreddit.enqueue(post)

        return post

    @profile
    def consume_post(self):
        # select subreddit
        # TODO: add option to stay on a subreddit
        subreddit = rng.choice(self.subreddits)

        # take the first 5 posts from the subreddits "hot" queue
        # TODO: select between hot/new also keep position in queue for continuous scrolling
        for i in range(max(-5, -len(subreddit.hot)), -1):
            post = subreddit.hot[i]

            # interact
            self.viewed_posts += 1
            post.views += 1
            self.vote(post)

            # reweigh bias
            self.new_bias(self.bias, post, 0.2)


class Network:
    def __init__(self):
        # quantities
        self.cnt_subreddits = 20
        self.cnt_users = 1000

        # subreddit properties
        self.sr_bias = np.array([0.2 + 0.6/get_n() * i for i in range(get_n())])
        self.sr_tolerance = np.full(get_n(), 0.4, float)

        # user properties
        # FIXME:
        self.usr_bias = np.array([0.2 + 0.6/get_n() * i for i in range(get_n())])
        self.usr_touch_grass_bias = 0.4
        self.usr_creator_bias = 0.03
        self.usr_subreddit_cap = 10

        # ls_s
        self.ls_subreddits = np.array([Subreddit(self.sr_bias, self.sr_tolerance) for _ in range(self.cnt_subreddits)])
        self.ls_users = np.array(
            [User(usr_id, self.usr_bias, self.usr_creator_bias, self.usr_touch_grass_bias,
                  self.ls_subreddits, self.usr_subreddit_cap)
             for usr_id in range(self.cnt_users)])
        self.ls_posts: [Post] = []

        # statistics
        self.stats_post_bias_sum = 0.0
        self.stats_user_bias_sum = 0.0
        self.stats_biases = []
        self.stats_post_biases = []

    @profile
    def simulate_round(self):
        self.stats_user_bias_sum = 0.0
        # TODO: try to partition users for benchmark reasons
        # simulate users
        for user in self.ls_users:
            # TODO: add switching subreddits
            # 0: sleep
            if user.touch_grass_bias > rng.random():
                # TODO: reset tmp (doesn't exist yet)
                pass

            # 1: create posts
            elif user.creator_bias > rng.random():
                post = user.create_post()
                self.stats_post_bias_sum += linalg.norm(post.bias)
                self.ls_posts.append(post)

            # 2: consume posts
            else:
                user.consume_post()

            # update statistics
            self.stats_user_bias_sum += linalg.norm(user.bias)

        for subreddit in self.ls_subreddits:
            # sort the hot lists
            subreddit.hot.sort(key=Post.get_hot, reverse=False)
            # cut the hot lists to be the first [50] elements
            subreddit.hot = subreddit.hot[0:50]
            # calculate and save the new subreddit bias
            new_bias = subreddit.get_bias()
            subreddit.stat_bias.append(new_bias)
            subreddit.bias = new_bias

        self.stats_biases.append(self.stats_user_bias_sum / self.cnt_users)
        self.stats_post_biases.append(self.stats_post_bias_sum / len(self.ls_posts)
                                      if not len(self.ls_posts) == 0 else 0.5)
        global timestamp
        timestamp += 1

    def finalize(self):
        for post in self.ls_posts:
            self.ls_users[post.creator].success += post.success
