import time
import numpy as np
import numpy.linalg as linalg
import dill
import Reddit
import Plot
import params as pms
import funcs as f

if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    round_times = []

    # build
    my_reddit = Reddit.Network()
    print(f"----------------------------------------\n"
          f"Simulating a Reddit-like Network with \n"
          f"- {pms.USR_COUNT} Users and \n"
          f"- {pms.SR_COUNT} Subreddits \n"
          f"for {pms.ROUNDS}x{pms.PER_ROUND} time steps \n"
          f"---------------------------------------- \n")

    print(f"Data structures built in {time.process_time() - start_time} seconds")

    # plots in the beginning
    Plot.user_bias_histogram(my_reddit, "start")
    Plot.subreddits(my_reddit, "start")

    # simulate
    for i in range(pms.ROUNDS):
        round_timer = time.process_time()
        for _ in range(pms.PER_ROUND):
            my_reddit.simulate_round()
        round_times.append(pms.PER_ROUND / (time.process_time() - round_timer))
        print(f"{i + 1} of {pms.ROUNDS} rounds simulated in"
              f" {time.process_time() - round_timer} seconds")

        # plots after every round go here
        Plot.plot_round(my_reddit)
        # Plot.user_bias_histogram(my_reddit, i)

    # finalize results
    my_reddit.finalize()

    # plot stuff
    Plot.users(my_reddit)
    Plot.subreddits(my_reddit, "end")
    Plot.posts(my_reddit)
    Plot.performance(round_times)
    Plot.save_gif()

    # find most successful posts
    ms_posts = f.most_successful(my_reddit.ls_posts, 10, lambda p: np.sum(p.success))

    # find most successful users
    ms_users = f.most_successful(my_reddit.ls_users, 10, lambda u: np.sum(u.success))

    # find most successful extremist users
    ms_extremist_users = f.most_successful(my_reddit.ls_users, 10,
                                           lambda u: np.sum(u.success)
                                           if linalg.norm(u.bias) > 1.6 or linalg.norm(u.bias) < 0.4
                                           else -1000)

    # See, how many users are in each zone.
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

    # save data structures
    my_data = [
        pms,
        my_reddit,
        ms_users,
        ms_extremist_users,
        ms_posts,
        zones
    ]
    with open(f"results/{pms.ID}/data.pkl", 'wb') as file:
        dill.dump(my_data, file)

    # use following lines to reimport a saved state
    # with open(f"results/{pms.ID}/data.pkl", 'rb') as file:
    #     my_data = dill.load(file)

    # finish
    print(f"Simulation finished after {time.process_time() - start_time} seconds")
