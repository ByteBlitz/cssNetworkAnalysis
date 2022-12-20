import numpy as np
import numpy.linalg as linalg
import params as pms
import Post
import funcs as f


class Moderation:
    def __init__(self, ls_users, ls_subreddits, ls_posts):
        # goal
        self.bias = pms.MOD_BIAS
        self.zones = pms.MOD_ZONES

        # power
        self.scan_users = pms.MOD_SCAN_USERS
        self.scan_posts = pms.MOD_SCAN_POSTS
        self.fault = 1 / pms.MOD_ACCURACY

        # data
        self.ls_posts = ls_posts
        self.ls_users: np.ndarray = ls_users
        self.ls_subreddits: np.ndarray = ls_subreddits
        self.watchlist = f.Watchlist(self.scan_users)  # users that are critical and detected are listed here

        # statistics
        self.soft_action = 0
        self.midi_action = 0
        self.hard_action = 0

    # helper methods
    def distance(self, post: Post.Post):
        """Returns a slightly distorted estimate for the distance between the biases of a Post and the Moderation. """
        return pms.rng.normal(linalg.norm(self.bias - post.bias) * pms.SQRT_N, self.fault)

    # penalties in interventions

    def soft(self, post: Post):
        """Bans Post from the hot-queue. """
        post.not_hot = True
        self.soft_action += 1

    def middle(self, post: Post):
        """Puts User on watchlist. """
        self.watchlist.append(self.ls_users[post.creator])
        self.midi_action += 1

    def hard(self, post: Post):
        """Bans User for 24h. """
        self.ls_users[post.creator].banned = 24
        self.hard_action += 1

    # @profile
    def intervene(self):
        """Function that scans new Posts and blacklisted Users for suspicious content and punishes if necessary.
        Can run once every timestep. """
        # Choose random new posts.
        posts = pms.rng.choice(self.ls_posts, min(self.scan_posts - len(self.watchlist.data), len(self.ls_posts)),
                               replace=False).tolist()

        # Collect posts from blacklisted users.
        for user in self.watchlist.get():
            posts.append(user.last_post)

        # Check the posts for their message. Punish if necessary.
        for post in posts:
            if self.ls_users[post.creator].banned:
                # Skip user if already banned
                continue

            if self.distance(post) < self.zones[0]:
                # Close to moderation's opinion, no action taken.
                pass

            elif self.distance(post) < self.zones[1]:
                # On the verge. Shadow-ban their posts to prevent them from pulling the center apart.
                self.soft(post)
                if pms.rng.random() < 0.1:  # User notices punishment with p=0.1.
                    self.ls_users[post.creator].more_extreme(self.bias)

            elif self.distance(post) < self.zones[2]:
                # Critical users. Keep them on the watchlist.
                self.soft(post)
                self.middle(post)
                if pms.rng.random() < 0.2:  # User notices punishment with p=0.2.
                    self.ls_users[post.creator].more_extreme(self.bias)
            else:
                # Users with extremist opinions. Ban them for now.
                self.soft(post)
                self.middle(post)
                self.hard(post)
                if pms.rng.random() < 0.333:  # User notices punishment with p=0.333.
                    self.ls_users[post.creator].more_extreme(self.bias)
