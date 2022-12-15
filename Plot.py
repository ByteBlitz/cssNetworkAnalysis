import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import Reddit
import numpy as np
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

    def add_plot_to_gif(self):
        """Function gets called after plot has been made and just saves it. """
        filename = f'images/frame_{self.gif_name}_{self.image_num}.png'
        self.filenames.append(filename)
        plt.savefig(filename, dpi=96, facecolor=self.bg_color)

        self.image_num += 1

    def create_gif(self):
        """Builds gif from saved frames. """
        frames = []

        with imageio.get_writer(f'images/{self.gif_name}.gif', mode='I') as writer:
            for filename in self.filenames:
                image = imageio.imread(filename)
                writer.append_data(image)
                frames.append(image)
            for _ in range(5):
                image = imageio.imread(self.filenames[len(self.filenames) - 1])
                writer.append_data(image)
                frames.append(image)
        
        export_name = f'images/{self.gif_name}_slow.gif'
        k_args = {'duration': 0.5}
        imageio.mimsave(export_name, frames, 'GIF', **k_args)

        # Remove files
        for filename in set(self.filenames):
            os.remove(filename)


my_gif = Gif('2dUser')
other_gif = Gif('2dSR')
sub_count_gif = Gif('SubCount')
user_count_gif = Gif('UserCount')


def plot_round(my_reddit: Reddit.Network):
    plt.hist2d([u.bias[0] for u in my_reddit.ls_users], [u.bias[1] for u in my_reddit.ls_users], range=[[0, 1], [0, 1]],
               bins=[200, 200])
    my_gif.add_plot_to_gif()
    plt.close()

    plt.hist2d([s.bias[0] for s in my_reddit.ls_subreddits], [s.bias[1] for s in my_reddit.ls_subreddits],
               range=[[0, 1], [0, 1]], bins=[100, 100])
    other_gif.add_plot_to_gif()
    plt.close()

    plt.hist([u.users for u in my_reddit.ls_subreddits], log=True)
    plt.title("Subreddit User-Count")
    sub_count_gif.add_plot_to_gif()
    plt.close()

    plt.hist([len(u.subreddits) for u in my_reddit.ls_users], log=True)
    plt.title("User Subreddit-Count")
    user_count_gif.add_plot_to_gif()
    plt.close()


def save_gif():
    my_gif.create_gif()
    other_gif.create_gif()
    sub_count_gif.create_gif()
    user_count_gif.create_gif()


def user_bias_histogram(my_reddit, title):
    # for i in range(Reddit.get_n()):
    #     plt.hist([u.bias[i] for u in my_reddit.ls_users])
    #     plt.title(f"User Bias Histogram [{title}] of Bias [{i}]")
    #     plt.show()

    plt.hexbin([u.bias[0] for u in my_reddit.ls_users], [u.bias[1] for u in my_reddit.ls_users], bins='log')
    plt.title(f"2d User Bias Distribution [{title}]")
    plt.show()

    return


def users(my_reddit):
    plt.plot(range(len(my_reddit.stats_biases)), my_reddit.stats_biases)
    plt.title("Average User Bias")
    plt.show()

    for i in range(pms.N):
        plt.hist([u.bias[i] for u in my_reddit.ls_users], log=True)
        plt.title(f"Logged User Bias {i} Diagram")
        plt.show()

    plt.hist([u.created_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Creation")
    plt.show()

    plt.hist([u.viewed_posts for u in my_reddit.ls_users], log=True)
    plt.title("User Consumption")
    plt.show()

    plt.hist([len(u.subreddits) for u in my_reddit.ls_users], log=True)
    plt.title("User SR-Count")
    plt.show()

    for i in range(pms.N):
        plt.hexbin([u.bias[i] for u in my_reddit.ls_users], [np.sum(u.success) for u in my_reddit.ls_users],
                   norm=mcolors.LogNorm())
        plt.title(f"User Success/Bias {i}")
        plt.show()

    plt.hexbin([u.bias[0] for u in my_reddit.ls_users], [u.bias[1] for u in my_reddit.ls_users], bins='log')
    plt.title("2d User Bias Distribution [end]")
    plt.show()

    return


def subreddits(my_reddit, title):
    plt.hist2d([s.bias[0] for s in my_reddit.ls_subreddits], [s.bias[1] for s in my_reddit.ls_subreddits],
               range=[[0, 1], [0, 1]], bins=[100, 100])
    plt.title(f"2d SR Bias Distribution [{title}]")
    plt.show()


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

    for i in range(pms.N):
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
