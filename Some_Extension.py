# This file is a template about how to extend the main reddit network to implement your moderation additions

import Reddit
import time
import Plot
import copy

# extend or override original data structures here
class Network(Reddit.Network):
    def __init__(self):
        Reddit.Network.__init__(self)
        self.new_exciting_property = 0.0

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
    ms_users: [Reddit.User] = [my_reddit.ls_users[0]]
    for user in my_reddit.ls_users:
        # filter for the 10 most successful users
        if user.success > ms_users[0].success:
            i = 0
            while i < len(ms_users):
                if user.success < ms_users[i].success:
                    break
                i += 1
            ms_users.insert(i, user)
            ms_users = ms_users[max(0, len(ms_users) - 10):len(ms_users)]

    # find most successful extremist users
    ms_extremist_users: [Reddit.User] = [copy.deepcopy(my_reddit.ls_users[0])]
    ms_extremist_users[0].success = -1000
    for user in my_reddit.ls_users:
        # filter for the 10 most successful users
        if user.success > ms_extremist_users[0].success and (user.fake_bias > 0.8 or user.fake_bias < 0.2):
            i = 0
            while i < len(ms_extremist_users):
                if user.success < ms_extremist_users[i].success:
                    break
                i += 1
            ms_extremist_users.insert(i, user)
            ms_extremist_users = ms_extremist_users[max(0, len(ms_extremist_users) - 10):len(ms_extremist_users)]

    # finish
    print(f"Simulation finished after {time.process_time() - start_time} seconds")
