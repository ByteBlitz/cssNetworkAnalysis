import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import Reddit
import numpy as np


def user_bias_histogram(my_reddit, title):
    for i in range(Reddit.get_n()):
        plt.hist([u.bias[i] for u in my_reddit.ls_users])
        plt.title(f"User Bias Histogram [{title}] of Bias [{i}]")
        plt.show()

    return


def users(my_reddit):
    plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    plt.title("Average User Bias")
    plt.show()

    for i in range(Reddit.get_n()):
        plt.hist([u.bias[i] for u in my_reddit.ls_users], log=True)
        plt.title(f"Logged User Bias {i} Diagram")
        plt.show()

    plt.hist([u.created_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Creation")
    plt.show()

    plt.hist([u.viewed_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Consumption")
    plt.show()

    for i in range(Reddit.get_n()):
        plt.hexbin([u.bias[i] for u in my_reddit.ls_users], [np.sum(u.success) for u in my_reddit.ls_users],
                   norm=mcolors.LogNorm())
        plt.title(f"User Success/Bias {i}")
        plt.show()

    return


def posts(my_reddit):
    plt.plot(range(1, len(my_reddit.stats_post_biases)), my_reddit.stats_post_biases[1:], 'r-')
    plt.title("Average Post Bias")
    plt.show()

    plt.hist([p.views for p in my_reddit.ls_posts], log=True, color='r')
    plt.title("Post Views")
    plt.show()

    plt.hist([p.score() for p in my_reddit.ls_posts], log=True, color='r')
    plt.title("Post Score")
    plt.show()

    for i in range(Reddit.get_n()):
        plt.hexbin([p.bias[i] for p in my_reddit.ls_posts], [p.score() for p in my_reddit.ls_posts],
                   norm=mcolors.LogNorm())
        plt.title(f"Post Score/Bias {i}")
        plt.show()

    plt.hexbin([p.score() for p in my_reddit.ls_posts], [np.sum(p.success) for p in my_reddit.ls_posts],
               norm=mcolors.LogNorm())
    plt.title("Post Success/Score")
    plt.show()

    return


def performance(round_times):
    plt.plot(range(0, len(round_times)), round_times, 'g-')
    plt.title("Performance Evaluation")
    plt.show()

    return
