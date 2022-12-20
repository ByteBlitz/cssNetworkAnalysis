import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import Reddit
import numpy as np
import numpy.linalg as linalg
import params as pms

# code by: https://towardsdatascience.com/basics-of-gifs-with-pythons-matplotlib-54dd544b6f30
import os
import imageio


class Gif:
    def __init__(self, gif_name):
        self.gif_name = gif_name
        self.filenames = []
        self.bg_color = '#ffffff'
        self.image_num = 0

    # @profile
    def add_plot_to_gif(self):
        """Function gets called after plot has been made and just saves it. """
        filename = f'results/{pms.ID}/gifs/frame_{self.gif_name}_{self.image_num}.png'
        self.filenames.append(filename)
        plt.savefig(filename, dpi=96)

        self.image_num += 1

    # @profile
    def create_gif(self):
        """Builds gif from saved frames. """
        frames = []

        with imageio.get_writer(f'results/{pms.ID}/gifs/{self.gif_name}.gif', mode='I') as writer:
            for filename in self.filenames:
                image = imageio.imread(filename)
                writer.append_data(image)
                frames.append(image)
            for _ in range(5):
                image = imageio.imread(self.filenames[len(self.filenames) - 1])
                writer.append_data(image)
                frames.append(image)

        export_name = f'results/{pms.ID}/gifs/{self.gif_name}_slow.gif'
        k_args = {'duration': 0.5}
        imageio.mimsave(export_name, frames, 'GIF', **k_args)

        # Remove files
        for filename in set(self.filenames):
            os.remove(filename)


usr_hexbin_gif = Gif('2dUser')
sr_hexbin_gif = Gif('2dSR')
sub_count_gif = Gif('SubCount')
user_count_gif = Gif('UserCount')
mod_zones_gif = Gif('ModZones')


# @profile
def plot_round(my_reddit: Reddit.Network):
    plt.hexbin([u.bias[0] for u in my_reddit.ls_users], [u.bias[1] for u in my_reddit.ls_users],
               bins='log', extent=[0, 1, 0, 1])
    usr_hexbin_gif.add_plot_to_gif()
    plt.close()

    plt.hexbin([s.bias[0] for s in my_reddit.ls_subreddits], [s.bias[1] for s in my_reddit.ls_subreddits],
               bins='log', extent=[0, 1, 0, 1])
    sr_hexbin_gif.add_plot_to_gif()
    plt.close()

    plt.hist([u.users for u in my_reddit.ls_subreddits], log=True)
    plt.title("Subreddit User-Count")
    sub_count_gif.add_plot_to_gif()
    plt.close()

    zones = [0, 0, 0, 0]
    ex_zones = pms.EX_ZONES
    for user in my_reddit.ls_users:
        distance = linalg.norm(user.bias - my_reddit.moderation.bias)
        if distance < ex_zones[0]:
            zones[0] += 1
        elif distance < ex_zones[1]:
            zones[1] += 1
        elif distance < ex_zones[2]:
            zones[2] += 1
        else:
            zones[3] += 1

    print(f"Zones: {[(zone / len(my_reddit.ls_users)) for zone in zones]}")

    plt.bar([0, 1, 2, 3], [zones[i] for i in range(4)], color=['green', 'yellow', 'orange', 'red'], log=False)
    plt.title("Extremity of Users")
    plt.xticks([0, 1, 2, 3])
    mod_zones_gif.add_plot_to_gif()
    plt.close()

    plt.hist([len(u.subreddits) for u in my_reddit.ls_users], log=True)
    plt.title("User Subreddit-Count")
    user_count_gif.add_plot_to_gif()
    plt.close()


# @profile
def save_gif():
    usr_hexbin_gif.create_gif()
    sr_hexbin_gif.create_gif()
    sub_count_gif.create_gif()
    user_count_gif.create_gif()
    mod_zones_gif.create_gif()


def user_bias_histogram(my_reddit, title):
    plt.hexbin([u.bias[0] for u in my_reddit.ls_users], [u.bias[1] for u in my_reddit.ls_users],
               bins='log', extent=[0, 1, 0, 1])
    plt.title(f"2d User Bias Distribution [{title}]")
    plt.savefig(f"results/{pms.ID}/plots/usr_bias[{title}]")
    plt.show()

    return


def users(my_reddit):
    # Discontinued, could be replaced with data on the distance between Users and Moderation.
    # plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    # plt.title("Average User Bias")
    # plt.show()

    for i in range(pms.N):
        plt.hist([u.bias[i] for u in my_reddit.ls_users], log=True)
        plt.title(f"Logged User Bias {i} Diagram")
        plt.savefig(f"results/{pms.ID}/plots/usr_bias_hist[{i}]")
        plt.show()

    # discontinued, read from the gif instead
    # plt.hist([len(u.subreddits) for u in my_reddit.ls_users], log=True)
    # plt.title("User SR-Count")
    # plt.show()

    for i in range(pms.N):
        plt.hexbin([u.bias[i] for u in my_reddit.ls_users], [np.sum(u.success) for u in my_reddit.ls_users],
                   norm=mcolors.LogNorm())
        plt.title(f"User Success/Bias {i}")
        plt.savefig(f"results/{pms.ID}/plots/usr_success_bias[{i}]")
        plt.show()

    user_bias_histogram(my_reddit, "end")

    return


def subreddits(my_reddit, title):
    plt.hexbin([s.bias[0] for s in my_reddit.ls_subreddits], [s.bias[1] for s in my_reddit.ls_subreddits],
               bins='log', extent=[0, 1, 0, 1])
    plt.title(f"2d SR Bias Distribution [{title}]")
    plt.savefig(f"results/{pms.ID}/plots/sr_bias[{title}]")
    plt.show()


def posts(my_reddit):
    # discontinued, closely related to usr_bias anyway
    # plt.plot(range(1, len(my_reddit.stats_post_biases)), my_reddit.stats_post_biases[1:], 'r-')
    # plt.title("Average Post Bias")
    # plt.show()

    plt.hist([p.views for p in my_reddit.ls_posts], log=True, color='r')
    plt.title("Post Views")
    plt.savefig(f"results/{pms.ID}/plots/p_views")
    plt.show()

    plt.hist([p.score() for p in my_reddit.ls_posts], log=True, color='r')
    plt.title("Post Score")
    plt.savefig(f"results/{pms.ID}/plots/p_score]")
    plt.show()

    for i in range(pms.N):
        plt.hexbin([p.bias[i] for p in my_reddit.ls_posts], [p.score() for p in my_reddit.ls_posts],
                   norm=mcolors.LogNorm())
        plt.title(f"Post Score/Bias {i}")
        plt.savefig(f"results/{pms.ID}/plots/p_score_bias[{i}]")
        plt.show()

    plt.hexbin([p.score() for p in my_reddit.ls_posts], [np.sum(p.success) for p in my_reddit.ls_posts],
               norm=mcolors.LogNorm())
    plt.title("Post Success/Score")
    plt.savefig(f"results/{pms.ID}/plots/p_success_score")
    plt.show()

    return


def performance(round_times):
    plt.plot(range(0, len(round_times)), round_times, 'g-')
    plt.title("Performance Evaluation")
    plt.savefig(f"results/{pms.ID}/plots/performance")
    plt.show()

    return
