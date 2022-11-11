# Copyright Max Osterried, 2022
# on Github: https://github.com/ByteBlitz/cssNetworkAnalysis
# using the style guide at https://peps.python.org/pep-0008/
import math
# useful pages:
# https://www.python-graph-gallery.com
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
#
#
# FIXME [assuming]:
# Used for declaring implicit simplifications and assumptions, that might impact precision.
#

# TODO:
# everyone should be connected to so
# add touch grass bias
# add ignoring as a valid option
# sort posts by relevance (binary heap)
# replace or reset users
# views for posts (debugging reasons)
# success rating for posts (top 50 in pulling people into their direction)


# imports
import random
import time
import numpy as np
import matplotlib.pyplot as plt

# global vars
timestamp: int = 0


# functions
def as_probability(val):
    return min(max(val, 0), 1)


def get_hot(post):
    return post.hot()


def random_connection(val, high):
    while True:
        rand = np.random.randint(0, high)
        if not val == rand:
            return rand


# objects
class Post:
    # FIXME [assuming]:
    # all posts are of similar quality and similarly convincing

    def __init__(self, bias):
        # properties
        self.fake_bias = as_probability(np.random.normal(bias, 0.1))
        # TODO: come up with a better standard deviation
        self.creation = timestamp
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


class Subreddit:
    def __init__(self, bias, tolerance):
        # post queues
        self.posts = 0
        self.hot = []
        self.new = []

        # properties
        self.bias = as_probability(np.random.normal(bias, 0.2))
        self.tolerance = as_probability(np.random.normal(tolerance, 0.2))

        # statistics

    def enqueue(self, post: Post):
        self.posts += 1
        self.new.append(post)
        self.hot.append(post)
        # amortize sorting by either using a binary heap or splitting time steps into insertion, then sort


class User:
    # FIXME [assuming]:
    # everyone is equally smart
    # only upvotes/downvotes as regulators
    # repetition effect not taken into account, introduce vulnerability variable
    def __init__(self, fake_bias, creator_bias, touch_grass_bias):
        # properties
        self.fake_bias: float = as_probability(np.random.normal(fake_bias, 0.2))
        self.creator_bias: float = as_probability(np.random.normal(creator_bias, 0.2))
        self.touch_grass_bias: float = as_probability(np.random.normal(touch_grass_bias, 0.2))
        self.subreddits = []
        # TODO: convert to array of arrays of subreddits, the bias towards the subreddit and the respective positions in the hot/new list

        # statistics
        self.viewed_posts: int = 0
        self.created_posts: int = 0

    # function that evaluates if a user agrees to a post
    def agree(self, post, threshold):
        """Evaluates, whether the user agrees with a post enough, to change their opinion"""
        # TODO: get me a proper function of agreement
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
            self.fake_bias = max(min((self.fake_bias * 5 + post.fake_bias) / 6, 1), 0)
        elif self.disagree(post, 0.1):
            # post can dec one's fake bias by maximum 16%
            self.fake_bias = max(min((self.fake_bias * 7 - post.fake_bias) / 6, 1), 0)

    def create_post(self):
        self.created_posts += 1
        post = Post(self.fake_bias)

        # select up to 3 subreddits to post on
        for subreddit in random.choices(self.subreddits, k=random.randint(1, min(3, len(self.subreddits)))):
            subreddit.enqueue(post)

        return post

    def consume_post(self):
        # select subreddit
        # TODO: add option to stay on a subreddit
        subreddit = random.choice(self.subreddits)

        # take the first 5 posts from the subreddits "hot" queue
        # TODO: select between hot/new also keep position in queue for continuous scrolling
        for i in range(0, min(5, len(subreddit.hot))):
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
        self.cnt_subreddits = 20
        self.cnt_users = 2000

        # subreddit properties
        self.sr_bias = 0.5
        self.sr_tolerance = 0.4

        # user properties
        self.usr_bias = 0.5
        self.usr_touch_grass_bias = 0.4
        self.usr_creator_bias = 0.03
        self.usr_subreddit_cap = 10

        # ls_s
        self.ls_subreddits = []
        self.ls_users = []
        self.ls_posts = []

        # statistics
        self.stats_post_bias_sum = 0.0
        self.stats_user_bias_sum = 0.0
        self.stats_biases = []
        self.stats_post_biases = []

        # build subreddits
        for _ in range(self.cnt_subreddits):
            self.ls_subreddits.append(Subreddit(self.sr_bias, self.sr_tolerance))

        # build users and give them a random assortment of subreddits
        for _ in range(self.cnt_users):
            user = User(self.usr_bias, self.usr_creator_bias, self.usr_touch_grass_bias)
            user.subreddits = random.choices(self.ls_subreddits,
                                             k=random.randint(1, min(self.cnt_subreddits, self.usr_subreddit_cap)))
            self.ls_users.append(user)

    def simulate_round(self):
        self.stats_user_bias_sum = 0.0
        # simulate users
        for user in self.ls_users:
            # TODO: add switching subreddits
            # 0: sleep
            if user.touch_grass_bias > random.random():
                # TODO: reset tmp (doesn't exist yet)
                pass

            # 1: create posts
            elif user.creator_bias > random.random():
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
            subreddit.hot.sort(key=get_hot, reverse=True)
            # cut the hot lists to be the first [50] elements
            subreddit.hot = subreddit.hot[0:50]

        self.stats_biases.append(self.stats_user_bias_sum / len(self.ls_users))
        self.stats_post_biases.append(self.stats_post_bias_sum / len(self.ls_posts))


# run network for n rounds
if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    rounds = 100  # in per_round
    per_round = 480
    round_times = []

    # build
    my_reddit = Network()
    print(f"----------------------------------------\n"
          f"Simulating a Reddit-like Network with \n"
          f"- {my_reddit.cnt_users} Users, \n"
          f"- {my_reddit.cnt_subreddits} Subreddits and \n"
          f"- a starting user bias of {my_reddit.usr_bias} \n"
          f"for {rounds}x{per_round} time steps \n"
          f"---------------------------------------- \n")

    print(f"Data structures built in {time.process_time() - start_time} seconds")

    # plots in the beginning
    plt.hist([u.fake_bias for u in my_reddit.ls_users])
    plt.title("User Bias Histogram [start]")
    plt.show()

    # simulate
    for i in range(rounds):
        round_timer = time.process_time()
        for _ in range(per_round):
            my_reddit.simulate_round()
        round_times.append(per_round / (time.process_time() - round_timer))
        print(f"{i + 1} of {rounds} rounds simulated in"
              f" {time.process_time() - round_timer} seconds")

        # plots after every round go here
        # plt.hist([u.fake_bias for u in my_reddit.ls_users])
        # plt.title(f"User Bias Histogram [{i + 1}]")
        # plt.show()

    print(f"Simulation finished after {time.process_time() - start_time} seconds")

    # plot stuff
    plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    plt.title("Average User Bias")
    plt.show()

    plt.hist([u.fake_bias for u in my_reddit.ls_users])
    plt.title("User Bias Histogram")
    plt.show()

    plt.plot(range(1, len(my_reddit.stats_post_biases)), my_reddit.stats_post_biases[1:], 'r-')
    plt.title("Average Post Bias")
    plt.show()

    plt.plot(range(0, len(round_times)), round_times, 'g-')
    plt.title("Performance Evaluation")
    plt.show()
