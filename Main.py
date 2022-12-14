import time
import copy
import Reddit
import Plot
import numpy as np
import numpy.linalg as linalg
import params as pms
import funcs as f

if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    rounds = 20  # in per_round
    per_round = 6
    round_times = []

    # build
    my_reddit = Reddit.Network()
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
    Plot.subreddits(my_reddit, "start")

    # simulate
    for i in range(rounds):
        round_timer = time.process_time()
        for _ in range(per_round):
            my_reddit.simulate_round()
        round_times.append(per_round / (time.process_time() - round_timer))
        print(f"{i + 1} of {rounds} rounds simulated in"
              f" {time.process_time() - round_timer} seconds")

        # plots after every round go here
        Plot.plot_round(my_reddit)
        # Plot.user_bias_histogram(my_reddit, i)

    Plot.save_gif()
    # finalize results
    my_reddit.finalize()

    # plot stuff
    Plot.users(my_reddit)
    Plot.subreddits(my_reddit, "end")
    Plot.posts(my_reddit)
    Plot.performance(round_times)

    # find most successful posts
    worst_post = copy.deepcopy(my_reddit.ls_posts[0])
    worst_post.success = np.array([-1000 for _ in range(pms.get_n())])
    ms_posts = f.most_successful(my_reddit.ls_posts, 10, lambda p: np.sum(p.success), worst_post)

    # find most successful users
    worst_user = copy.deepcopy(my_reddit.ls_users[0])
    worst_user.success = np.array([-1000 for _ in range(pms.get_n())])
    ms_users = f.most_successful(my_reddit.ls_users, 10, lambda u: np.sum(u.success), worst_user)

    # find most successful extremist users
    ms_extremist_users = f.most_successful(my_reddit.ls_users, 10,
                                           lambda u: np.sum(u.success)
                                           if linalg.norm(u.bias) > 1.6 or linalg.norm(u.bias) < 0.4
                                           else -1000,
                                           worst_user)

    zones = [0, 0, 0, 0]
    for user in my_reddit.ls_users:
        if my_reddit.moderation.distance(user) < my_reddit.moderation.zones[0]:
            zones[0] += 1
        elif my_reddit.moderation.distance(user) < my_reddit.moderation.zones[1]:
            zones[1] += 1
        elif my_reddit.moderation.distance(user) < my_reddit.moderation.zones[2]:
            zones[2] += 1
        else:
            zones[3] += 1

    # finish
    print(f"Simulation finished after {time.process_time() - start_time} seconds")
