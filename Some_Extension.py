# This file is a template about how to extend the main reddit network to implement your moderation additions
import speedup

import Reddit
import time
import Plot
import copy
import numpy as np
import Names


# extend or override original data structures here
def make_name():
    return "".join([np.random.choice(Names.names), " ", np.random.choice(Names.surnames)])


class Post:
    def __init__(self, creator, bias):
        fake_bias = Reddit.as_probability(Reddit.rng.normal(bias, 0.1))
        self.post = speedup.Post(Reddit.timestamp, creator, fake_bias)


class User(Reddit.User):
    def __init__(self, creator_bias, fake_bias, ls_subreddits, touch_grass_bias, usr_id, usr_subreddit_cap):
        Reddit.User.__init__(self, creator_bias, fake_bias, ls_subreddits, touch_grass_bias, usr_id, usr_subreddit_cap)
        self.name = make_name()


class Network(Reddit.Network):
    def __init__(self):
        Reddit.Network.__init__(self)
        # add property
        self.new_exciting_property = 0.0
        # override property
        self.ls_users = self.ls_users = np.array(
            [User(usr_id, self.usr_bias, self.usr_creator_bias, self.usr_touch_grass_bias,
                  self.ls_subreddits, self.usr_subreddit_cap)
             for usr_id in range(self.cnt_users)])

    def simulate_round(self):
        Reddit.Network.simulate_round(self)
        self.new_exciting_property += 1


# run your implementation here
if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    rounds = 10  # in per_round
    per_round = 12
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
    Plot.user_bias_histogram(my_reddit, "start")

    # simulate
    for i in range(rounds):
        round_timer = time.process_time()
        for _ in range(per_round):
            my_reddit.simulate_round()
        round_times.append(per_round / (time.process_time() - round_timer))
        print(f"{i + 1} of {rounds} rounds simulated in"
              f" {time.process_time() - round_timer} seconds")

        # plots after every round go here
        # Plot.user_bias_histogram(my_reddit, i)

    # finalize results
    my_reddit.finalize()

    # plot stuff
    Plot.users(my_reddit)
    Plot.posts(my_reddit)
    Plot.performance(round_times)

    # find most successful posts
    worst_post = copy.deepcopy(my_reddit.ls_posts[0])
    worst_post.success = -1000
    ms_posts = Reddit.most_successful(my_reddit.ls_posts, 10, lambda post: post.success, worst_post)

    # find most successful users
    worst_user = copy.deepcopy(my_reddit.ls_users[0])
    worst_user.success = -1000
    ms_users = Reddit.most_successful(my_reddit.ls_users, 10, lambda user: user.success, worst_user)

    # find most successful extremist users
    ms_extremist_users = Reddit.most_successful(my_reddit.ls_users, 10,
                                                lambda user: user.success
                                                if user.fake_bias > 0.8 or user.fake_bias < 0.2
                                                else -1000,
                                                worst_user)

    # finish
    print(f"Simulation finished after {time.process_time() - start_time} seconds")
