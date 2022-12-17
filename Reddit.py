import params as pms
import numpy as np
import numpy.linalg as linalg
import Post
import User
import Subreddit
import Moderation


# Copyright Max Osterried, 2022
# on Github: https://github.com/ByteBlitz/cssNetworkAnalysis


class Network:
    def __init__(self):
        # vertices and posts
        self.ls_subreddits = np.array([Subreddit.Subreddit(i) for i in range(pms.SR_COUNT)])
        self.ls_users = np.array([User.User(usr_id, self.ls_subreddits) for usr_id in range(pms.USR_COUNT)])
        self.ls_posts: list[Post] = []

        # moderation
        self.moderation: Moderation = Moderation.Moderation(self.ls_users, self.ls_subreddits, self.ls_posts)

        # statistics
        self.stats_post_bias_sum = np.zeros(0)
        self.stats_user_bias_sum = np.zeros(0)
        self.stats_biases = []
        self.stats_post_biases = []
        self.left = 0
        self.entered = 0

    # @profile
    def simulate_round(self):
        """Simulate one timestep, equivalent to one hour in the network. """
        self.stats_user_bias_sum = 0.0

        # simulate Users
        user: User
        for user in self.ls_users:
            # update statistics
            self.stats_user_bias_sum += linalg.norm(user.bias)

            # filter banned Users
            if user.banned > 0:
                user.banned -= 1
                continue

            # Will the User go online?
            if user.online_bias > pms.rng.random():
                # Will the User post something?
                if user.create_bias > pms.rng.random():
                    post = user.create_post()
                    self.stats_post_bias_sum += linalg.norm(post.bias)
                    self.ls_posts.append(post)
                # Else, the User will consume some Posts.
                else:
                    user.consume_post()

                user.switch_subreddit()

        # Simulate Subreddits. Calculate their bias.
        for subreddit in self.ls_subreddits:
            subreddit.update_bias()

        # Simulate Moderation if wanted.
        if pms.MODERATION:
            self.moderation.intervene()

        # statistics
        self.stats_biases.append(self.stats_user_bias_sum / pms.USR_COUNT)
        self.stats_post_biases.append(self.stats_post_bias_sum / len(self.ls_posts)
                                      if not len(self.ls_posts) == 0 else 0.5)
        pms.timestamp += 1

    def finalize(self):
        """Adds up User success as well as Subreddit switching dynamics. """
        for post in self.ls_posts:
            self.ls_users[post.creator].success += post.success

        for user in self.ls_users:
            self.left += user.left
            self.entered += user.entered
