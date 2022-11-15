import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def user_bias_histogram(my_reddit, title):
    plt.hist([u.fake_bias for u in my_reddit.ls_users])
    plt.title(f"User Bias Histogram [{title}]")
    plt.show()

    return


def users(my_reddit):
    plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    plt.title("Average User Bias")
    plt.show()

    plt.hist([u.fake_bias for u in my_reddit.ls_users], log=True)
    plt.title("Logged User Bias Histogram")
    plt.show()

    plt.hist([u.created_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Creation")
    plt.show()

    plt.hist([u.viewed_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Consumption")
    plt.show()

    plt.hexbin([u.fake_bias for u in my_reddit.ls_users], [u.success for u in my_reddit.ls_users],
               norm=mcolors.LogNorm())
    plt.title("User Success/Bias")
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

    plt.hexbin([p.fake_bias for p in my_reddit.ls_posts], [p.score() for p in my_reddit.ls_posts],
               norm=mcolors.LogNorm())
    plt.title("Post Score/Bias")
    plt.show()

    plt.hexbin([p.score() for p in my_reddit.ls_posts], [p.success for p in my_reddit.ls_posts],
               norm=mcolors.LogNorm())
    plt.title("Post Success/Score")
    plt.show()

    return


def performance(round_times):
    plt.plot(range(0, len(round_times)), round_times, 'g-')
    plt.title("Performance Evaluation")
    plt.show()

    return
