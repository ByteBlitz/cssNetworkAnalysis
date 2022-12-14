# Copyright Max Osterried, 2022
# on Github: https://github.com/ByteBlitz/cssNetworkAnalysis
# using the style guide at https://peps.python.org/pep-0008/
# useful pages:
# https://www.python-graph-gallery.com
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
#
#
# FIXME [assuming]:
# Used for declaring implicit simplifications and assumptions, that might impact precision.
#
# TODO:
# replace or reset users or make them change their opinion in downtime
# implement china reddit
# improve agreement function


# imports
import params as pms
import numpy as np
import numpy.linalg as linalg
import Post
import User
import Subreddit
import Moderation


class Network:
    def __init__(self):
        # moderation type: True -> anarchy, False -> China
        self.moderation_type = True

        # quantities
        self.cnt_subreddits = 100
        self.cnt_users = 1000

        # subreddit properties
        self.sr_bias = np.array([0.5, 0.5])
        self.sr_tolerance = np.full(pms.get_n(), 0.4, float)

        # user properties
        # FIXME:
        self.usr_bias = np.array([0.5, 0.5])
        self.usr_online_bias = 0.60
        self.usr_create_bias = 0.03
        self.usr_subreddit_cap = 3

        # ls_s
        self.ls_subreddits = np.array(
            [Subreddit.Subreddit(self.sr_bias, i) for i in range(self.cnt_subreddits)])
        self.ls_users = np.array(
            [User.User(usr_id, self.usr_bias, self.usr_online_bias, self.usr_create_bias,
                       self.ls_subreddits, self.usr_subreddit_cap)
             for usr_id in range(self.cnt_users)])

        # tmp = np.clip(rng.normal(self.usr_consume_bias, 0.1, self.cnt_users), 0, 1)
        # self.ls_consume_bias = tmp / np.sum(tmp)
        # tmp = np.clip(rng.normal(self.usr_create_bias, 0.01, self.cnt_users), 0, 1)
        # self.ls_create_bias = tmp / np.sum(tmp)

        self.ls_posts: list[Post] = []

        # statistics
        self.stats_post_bias_sum = 0.0
        self.stats_user_bias_sum = 0.0
        self.stats_biases = []
        self.stats_post_biases = []
        self.left = 0
        self.entered = 0

        # build moderation
        self.moderation: Moderation = Moderation.Moderation(np.array([0.5, 0.5]),
                                                            np.array([0.2, 0.35, 0.45]) * pms.get_sqrt_n(),
                                                            50, 200, self.ls_users, self.ls_subreddits, self.ls_posts)

    # @profile
    def simulate_round(self):
        self.stats_user_bias_sum = 0.0

        # simulate users
        user: User
        for user in self.ls_users:
            # update statistics
            self.stats_user_bias_sum += linalg.norm(user.bias)

            if user.banned > 0:
                user.banned -= 1
                continue

            # 0: online?
            if user.online_bias > pms.rng.random():
                # TODO: reset tmp (doesn't exist yet)
                if user.create_bias > pms.rng.random():
                    post = user.create_post()
                    self.stats_post_bias_sum += linalg.norm(post.bias)
                    self.ls_posts.append(post)
                else:
                    user.consume_post(self.ls_subreddits)

            user.switch_subreddit(self.ls_subreddits)

        for subreddit in self.ls_subreddits:
            # sort the hot lists
            subreddit.hot.sort(key=Post.get_hot, reverse=False)
            # cut the hot lists to be the first [50] elements
            subreddit.hot = subreddit.hot[0:50]
            # calculate and save the new subreddit bias
            new_bias = subreddit.current_bias()
            subreddit.stat_bias.append(new_bias)
            subreddit.bias = new_bias

        self.stats_biases.append(self.stats_user_bias_sum / self.cnt_users)
        self.stats_post_biases.append(self.stats_post_bias_sum / len(self.ls_posts)
                                      if not len(self.ls_posts) == 0 else 0.5)

        if self.moderation_type:
            self.moderation.intervene_anarchistic()
        else:
            self.moderation.intervene_moderated()

        pms.timestamp += 1

    def finalize(self):
        for post in self.ls_posts:
            self.ls_users[post.creator].success += post.success

        for user in self.ls_users:
            self.left += user.left
            self.entered += user.entered
