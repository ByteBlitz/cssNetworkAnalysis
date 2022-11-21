import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import Reddit


def user_bias_histogram(my_reddit, title):
    for i in range(Reddit.getN()):
        plt.hist([u.bias.bias[i] for u in my_reddit.ls_users])
        plt.title(f"User Bias Histogram [{title}] of Bias [{i}]")
        plt.show()

    return

def sr_bias_histogram(my_reddit, t)


def users(my_reddit):

    print([usr.bias.norm()] for usr in my_reddit.ls_users)

    plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    plt.title("Average User Bias")
    plt.show()

    for i in range(Reddit.getN()):
        plt.hist([u.bias.bias[i] for u in my_reddit.ls_users], log=True)
        plt.title("Logged User Bias {} Diagram".format(i))
        plt.show()

    plt.hist([u.created_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Creation")
    plt.show()

    plt.hist([u.viewed_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Consumption")
    plt.show()

    for i in range(Reddit.getN()):

        plt.hexbin([u.bias.bias[i] for u in my_reddit.ls_users], [u.success for u in my_reddit.ls_users],
                   norm=mcolors.LogNorm())
        plt.title("User Success/Bias {}".format(i))
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
    for i in range(Reddit.getN()):

        plt.hexbin([p.bias.bias[i] for p in my_reddit.ls_posts], [p.score() for p in my_reddit.ls_posts],
                   norm=mcolors.LogNorm())
        plt.title("Post Score/Bias {}".format(i))
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
