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

import numpy as np

# global vars
timestamp: int = 0
seed = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)


# functions
<<<<<<< HEAD
def getN():
    return 5

=======
>>>>>>> d1dbc4f564c31d25258b73ac66788fc901cbff74
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

    def __init__(self, creator, bias):
        # properties
        self.creation = timestamp
        self.creator: int = creator
        self.fake_bias = as_probability(rng.normal(bias, 0.1))
        # TODO: come up with a better standard deviation
        self.ups = 1
        self.downs = 0

        # statistics
        self.views = 1
        self.success = 0.0

    def score(self):
        return self.ups - self.downs

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
    def __init__(self, bias, tolerance):
        # post queues
        self.hot = []
        self.new = []

        # properties
        self.bias = as_probability(rng.normal(bias, 0.2))
        self.tolerance = as_probability(rng.normal(tolerance, 0.2))

        # statistics
        self.stat_bias = []
        self.users = 0

    def enqueue(self, post: Post):
        self.new.append(post)
        self.hot.append(post)
        # amortize sorting by either using a binary heap or splitting time steps into insertion, then sort

    def get_bias(self):
        num = 0.0
        den = 0.0
        for post in self.hot:
            num += post.fake_bias * post.hot()
            den += post.hot()
        return num / den if not den == 0 else 0.5


class User:
    # FIXME [assuming]:
    # everyone is equally smart
    # only upvotes/downvotes as regulators
    # repetition effect not taken into account, introduce vulnerability variable
    def __init__(self, usr_id, fake_bias, creator_bias, touch_grass_bias, ls_subreddits, usr_subreddit_cap):
        # properties
        self.id: int = usr_id
        self.fake_bias: float = as_probability(rng.normal(fake_bias, 0.2))
        # TODO: n dimensions for n > 1 , n e Z
        self.creator_bias: float = as_probability(rng.normal(creator_bias, 0.01))
        self.touch_grass_bias: float = as_probability(rng.normal(touch_grass_bias, 0.2))
        self.subreddits: [Subreddit] = []
        # TODO: convert to array of arrays of subreddits, the bias towards the subreddit and the respective positions
        #  in the hot/new list

        # statistics
        self.viewed_posts: int = 0
        self.created_posts: int = 0
        self.success: float = 0.0

        # get subreddits
        probs = [1 / max(abs(sr.bias - self.fake_bias), 0.001) for sr in ls_subreddits]
        s = sum(probs)
        probs = [p / s for p in probs]

        self.subreddits = rng.choice(ls_subreddits,
                                     rng.integers(1, min(len(ls_subreddits), usr_subreddit_cap) + 1),
                                     replace=False,
                                     p=probs)

        for subreddit in self.subreddits:
            subreddit.users += 1

    # function that evaluates if a user agrees to a post
    def agree(self, post, threshold):
        """Evaluates, whether the user agrees with a post enough, to change their opinion"""
        # TODO: get me a proper function of agreement
        # make it probabilistic
        # take into account repetition effects (equivalent to acceleration)
        # take into account herd bias
        # importance array
        return abs(self.fake_bias - post.fake_bias) < threshold

    def disagree(self, post, threshold):
        """Evaluates, whether the user disagrees with a post enough, to change their opinion"""
        # TODO: get me a proper function of disagreement
        return abs(self.fake_bias - post.fake_bias) > (1 - threshold)

    def vote(self, post):
        if self.agree(post, 0.2):
            post.ups += 1
        elif self.disagree(post, 0.2):
            post.downs += 1

    def new_bias(self, post):
        if self.agree(post, 0.1):
            # post can inc one's fake bias maximum 20%
            new_bias = as_probability((self.fake_bias * 5 + post.fake_bias) / 6)
            post.success += abs(self.fake_bias - new_bias)
            self.fake_bias = new_bias
        elif self.disagree(post, 0.1):
            # post can dec one's fake bias by maximum 16%
            new_bias = as_probability((self.fake_bias * 7 - post.fake_bias) / 6)
            post.success -= abs(self.fake_bias - new_bias)
            self.fake_bias = new_bias

    def create_post(self):
        self.created_posts += 1
        post = Post(self.id, self.fake_bias)

        # select up to 3 subreddits to post on
        for subreddit in rng.choice(self.subreddits, rng.choice(min(3, len(self.subreddits)) + 1), replace=False):
            subreddit.enqueue(post)

        return post

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
            self.new_bias(post)


class Network:
    def __init__(self):
        # quantities
<<<<<<< HEAD
        self.cnt_subreddits = 30
        self.cnt_users = 10000

        # subreddit properties
        self.sr_bias = Bias([0.5 for i in range(getN())])
        self.sr_tolerance = Bias([0.4 for i in range(getN())])

        # user properties
        self.usr_bias = Bias([0.5 for i in range(getN())])
=======
        self.cnt_subreddits = 50
        self.cnt_users = 10000

        # subreddit properties
        self.sr_bias = 0.5
        self.sr_tolerance = 0.4

        # user properties
        self.usr_bias = 0.5
>>>>>>> d1dbc4f564c31d25258b73ac66788fc901cbff74
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

    def simulate_round(self):
        self.stats_user_bias_sum = 0.0
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
                self.stats_post_bias_sum += post.fake_bias
                self.ls_posts.append(post)

            # 2: consume posts
            else:
                user.consume_post()

            # update statistics
            self.stats_user_bias_sum += user.fake_bias

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


