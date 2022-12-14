import numpy as np
import numpy.linalg as linalg
import params as pms
import Post
import Subreddit
import User


class Blacklist:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = []
        self.pointer = 0

    def append(self, e: object):
        if len(self.data) < self.capacity:
            self.data.append(e)
        else:
            self.data[self.pointer] = e
            self.pointer = (self.pointer + 1) % self.capacity

    def get(self):
        return self.data


class Moderation:
    def __init__(self, bias, zones, check_users, check_posts, ls_users, ls_subreddits, ls_posts):
        # goal
        self.bias = bias  # np.array([0.3, 0.5]), interesting if we vary this opinion
        self.zones = zones  # np.array([0.2, 0.35, 0.45]) * get_sqrt_n()
        # to opinions (depending on how far they are from the own Opinion

        # power
        self.check_users = check_users
        self.check_posts = check_posts

        # data
        self.ls_users: np.ndarray = ls_users
        self.ls_subreddits: np.ndarray = ls_subreddits
        self.ls_sus_reddits: np.ndarray = np.zeros(len(ls_subreddits))
        self.ls_posts = ls_posts
        self.blacklist = Blacklist(check_users)  # users that are critical and detected are listed here

    # helper methods
    def distance(self, post: Post.Post):
        return pms.rng.normal(linalg.norm(self.bias - post.bias) * pms.get_sqrt_n(), 0.05)

    # penalties in interventions

    def soft(self, post: Post):
        post.not_hot = True

    def middle(self, post: Post):
        opponent: User = self.ls_users[post.creator]  # person who sent it
        self.blacklist.append(opponent)

    def hard(self, post: Post):
        opponent: User = self.ls_users[post.creator]  # person who sent it
        opponent.banned = 24
        for sr in opponent.subreddits:
            sr: Subreddit
            self.ls_sus_reddits[sr.id] += 1
            sr.users -= 1
            # if self.ls_sus_reddits[sr.id] > sr.users / 3 + 4:
            #     sr.banned = True

        opponent.subreddits = np.empty(0)

    # no intervention
    def intervene_anarchistic(self):
        pass

    # state intervenes if opinion bias is too far from own opinion
    def intervene_moderated(self):
        # scan new successful posts
        posts = pms.rng.choice(self.ls_posts, min(self.check_posts - len(self.blacklist.data), len(self.ls_posts)),
                               replace=False).tolist()
        for user in self.blacklist.get():
            user: User
            posts.append(user.last_post)

        for post in posts:
            p = pms.rng.random()
            opponent: User = self.ls_users[post.creator]

            if self.distance(post) < self.zones[0]:
                # nice people
                pass

            elif self.distance(post) < self.zones[1]:
                # not so nice people
                self.soft(post)
                if p < 0.1:  # probability of 0.1 -> user realises
                    opponent.more_extreme(self.bias)

            elif self.distance(post) < self.zones[2]:
                # not nice people
                self.soft(post)
                self.middle(post)
                if p < 0.2:  # again a probability of 0.2 -> user realises
                    opponent.more_extreme(self.bias)
            else:
                # extremists
                self.soft(post)
                self.middle(post)
                self.hard(post)
                if p < 0.333:  # again a probability of 0.333 -> user realises
                    opponent.more_extreme(self.bias)
