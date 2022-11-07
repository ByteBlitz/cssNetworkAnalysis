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
# everyone should be connected to so
# add touch grass bias
# add ignoring as a valid option
# sort posts by relevance (binary heap)
# replace or reset users
# views for posts (debugging reasons)
# success rating for posts (top 50 in pulling people into their direction)


import random
import time

# imports
import numpy as np
import matplotlib.pyplot as plt


# functions
def as_probability(val):
    return min(max(val, 0), 1)


def random_connection(val, high):
    while True:
        rand = np.random.randint(0, high)
        if not val == rand:
            return rand


# define objects
class Post:
    # FIXME [assuming]:
    # all posts are of similar quality and similarly convincing
    fake_bias: float
    upvotes: int
    views: int

    # age: int = 0
    # lifetime: int = 3

    def __init__(self, bias):
        self.fake_bias = as_probability(np.random.normal(bias, 0.1))
        self.upvotes = 1
        self.views = 1
        # TODO: come up with a better standard deviation


class User:
    # FIXME [assuming]:
    # everyone is equally smart
    # only upvotes/downvotes as regulators
    # repetition effect not taken into account, introduce vulnerability variable

    # TODO: define types

    # the range of fakeness an agent likes to enjoy his news
    fake_bias = 0.0
    # how likely an agent is to create a post in a given round
    creator_bias = 0.0

    # statistics
    viewed_posts = 0
    created_posts = 0

    # check_bias = 0.0

    def __init__(self, fake_bias, creator_bias, check_bias):
        self.fake_bias = fake_bias
        self.creator_bias = creator_bias
        self.in_post = []
        # self.check_bias = check_bias

    def __init__(self, fake_bias, fake_dev, creator_bias, creator_dev, check_bias, check_dev):
        self.fake_bias = as_probability(np.random.normal(fake_bias, fake_dev))
        self.creator_bias = as_probability(np.random.normal(creator_bias, creator_dev))
        self.in_post = []
        # self.check_bias = as_probability(np.random.normal(check_bias, check_dev))

    # function that evaluates if a user agrees to a post
    def agree(self, post, threshold):

        # TODO: get me a proper function of agreement
        return abs(self.fake_bias - post.fake_bias) < threshold

    def disagree(self, post, threshold):

        # TODO: get me a proper function of disagreement
        return abs(self.fake_bias - post.fake_bias) > (1 - threshold)

    def vote(self, post):

        # TODO: include ignore
        if self.agree(post, 0.2):
            post.upvotes += 1
        elif self.disagree(post, 0.2):
            post.upvotes -= 1

    def new_bias(self, post):

        # TODO: include ignore
        if self.agree(post, 0.1):
            # post can inc one's fake bias maximum 20%
            self.fake_bias = max(min((self.fake_bias * 5 + post.fake_bias) / 6, 1), 0)
        else:
            # post can dec one's fake bias by maximum 16%
            self.fake_bias = max(min((self.fake_bias * 7 - post.fake_bias) / 6, 1), 0)

    def create_post(self):

        self.created_posts += 1

        # make post
        post = Post(self.fake_bias)

        # transmit post
        return post

    def consume_post(self):

        # take (random) post out of the agent's buffer
        while len(self.in_post) != 0:
            post = self.in_post.pop()

            if post is None:
                continue

            self.viewed_posts += 1
            post.views += 1

            # interact
            self.vote(post)

            # reweigh bias
            self.new_bias(post)


# build network
# FIXME: using reduced complexity with n nodes, no subreddits but random connections
class Network:
    # change for network size and connectivity
    user_number = 5
    connection_number = 200

    # change properties of the Users
    # TODO: connect the touch grass factor with user behavior
    touch_grass_bias = 0.3
    aa_fake_bias = 0.2
    creator_bias = 0.03
    check_bias = 0.1

    aa_post_bias = 0

    users = []
    posts = []
    connections = np.empty(user_number, dtype=object)

    fake_biases = []
    post_biases = []

    post_fake_bias_sum = 0

    # helper structures
    duplicate_map = {}

    # counts
    connection_count = 0

    def __init__(self):
        # build nodes (Users)
        for _ in range(self.user_number):
            self.users.append(User(self.aa_fake_bias, 0.1, self.creator_bias, 0.1, self.check_bias, 0.1))

        # build edges (Connections/Subreddits)
        # FIXME: double connections exist
        # TODO: connections should be weighted
        for i in range(self.user_number):
            self.connections[i] = []

        # initializing duplicate map
        for i in range(self.user_number):
            self.duplicate_map[i] = []

        # generating random connections
        connection_count = 0
        while connection_count < self.connection_number:
            # draw random user
            u = np.random.randint(0, self.user_number)

            # and connect to other random user
            v = random_connection(u, self.user_number)

            # check if we didn't already generate this connection
            if v not in self.duplicate_map[u]:
                self.duplicate_map[u].append(v)
                connection_count += 1

        self.connections = self.duplicate_map

    def simulate_round(self):
        # simulate users
        user_fake_bias_sum = 0.0
        for i, user in enumerate(self.users):
            # TODO: return from own posts
            user_fake_bias_sum += user.fake_bias
            # TODO: case 0: touch grass
            # case 1: create post
            if random.random() < self.creator_bias:

                # user creates a post
                post = user.create_post()
                self.posts.append(post)
                self.post_fake_bias_sum += post.fake_bias
                # and it lands in every buffer of his connections
                for u in self.connections[i]:
                    self.users[u].in_post.append(post)

            # case 2: consume post
            else:
                user.consume_post()
        self.aa_fake_bias = user_fake_bias_sum / self.user_number

        # Do not ever iterate all posts! Horrible complexity!
        # The average is calculated when creating the post
        # TODO: kill post if too old (somewhere else, maybe in the consume queue)
        self.aa_post_bias = self.post_fake_bias_sum / max(len(self.posts), 1)

        self.fake_biases.append(self.aa_fake_bias)
        self.post_biases.append(self.aa_post_bias)


# run network for n rounds
if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    rounds = 20  # in per_round
    per_round = 50
    round_times = []

    # build
    my_reddit = Network()
    print(f"----------------------------------------\n"
          f"Simulating a Reddit-like Network with \n"
          f"- {my_reddit.user_number} Users, \n"
          f"- {my_reddit.connection_number} Connections and \n"
          f"- a starting bias of {my_reddit.aa_fake_bias} \n"
          f"for {rounds}x{per_round} time steps \n"
          f"---------------------------------------- \n")

    print(f"Data structures built in {time.process_time() - start_time} seconds")

    # plots in the beginning
    plt.hist([u.fake_bias for u in my_reddit.users])
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
        plt.hist([u.fake_bias for u in my_reddit.users])
        plt.title(f"User Bias Histogram [{i + 1}]")
        plt.show()

    print(f"Simulation finished after {time.process_time() - start_time} seconds")

    # plot stuff
    plt.plot(range(len(my_reddit.fake_biases)), my_reddit.fake_biases)
    plt.title("Average User Bias")
    plt.show()

    plt.hist([u.fake_bias for u in my_reddit.users])
    plt.title("User Bias Histogram")
    plt.show()

    plt.plot(range(1, len(my_reddit.post_biases)), my_reddit.post_biases[1:], 'r-')
    plt.title("Average Post Bias")
    plt.show()

    plt.plot(range(0, len(round_times)), round_times, 'g-')
    plt.title("Performance Evaluation")
    plt.show()
