import time
import copy
import Reddit
import Plot

if __name__ == '__main__':
    # vars
    start_time = time.process_time()
    rounds = 10  # in per_round
    per_round = 12
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
                                                if user.bias.norm() > 0.8 or user.bias.norm() < 0.2
                                                else -1000,
                                                worst_user)

    # finish
    print(f"Simulation finished after {time.process_time() - start_time} seconds")
