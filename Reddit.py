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
import math
import copy

import Names
import Helper
import numpy as np
import scipy as sp
import numpy.linalg as linalg

# global vars
timestamp: int = 0
seed = np.random.randint(0, 1024)
rng = np.random.default_rng(seed=seed)


# functions
def get_n():
    return 2


def get_sqrt_n():
    return 1.44


def as_probability(val):
    """Keep numbers in [0,1] with this function. """
    return min(max(val, 0), 1)


def most_successful(seq, cnt, metric, worst):
    """Can be used to find the [cnt] most successful items from [seq] concerning [metric]"""
    ms_list = [copy.deepcopy(worst)]
    for item in seq:
        if metric(item) > metric(ms_list[0]):
            i = 0
            while i < len(ms_list):
                if metric(item) < metric(ms_list[i]):
                    break
                i += 1
            ms_list.insert(i, item)
            ms_list = ms_list[max(0, len(ms_list) - cnt):len(ms_list)]

    return ms_list


# objects
class Post:
    # FIXME [assuming]:
    # all posts are of similar quality and similarly convincing

    # @profile
    def __init__(self, creator, bias):
        # properties
        self.creation = timestamp
        self.creator: int = creator
        self.bias = np.clip(rng.normal(bias, 0.1), 0, 1)
        # TODO: come up with a better standard deviation
        self.ups = 1
        self.downs = 0

        # moderation
        self.not_hot = False  # is set True if Moderator detects this post and avoids it getting into hot queue

        # statistics
        self.views = 1
        self.success = np.full(get_n(), 0.0, float)

    def score(self):
        return self.ups - self.downs

    def weight(self):
        return max(math.log(self.score(), 10) if self.score() > 0 else 0, 0.1)

    # @profile
    def hot(self):
        """The hot formula. Should match the equivalent function in postgres. """
        s = self.score()
        order = math.log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else 0 if s == 0 else -1
        hours = timestamp - self.creation
        return 0 if self.not_hot else round(sign * order + hours / 12, 7)

    def get_hot(post):
        """Needed as a sorting criteria. """
        return post.hot()


class Subreddit:
    def __init__(self, bias_list: np.ndarray, tolerance, id):
        # post queues
        self.hot = []
        self.new = []

        # properties
        self.id = id
        self.bias = np.clip(rng.normal(bias_list, 0.2), 0, 1)

        # moderation
        self.banned = False

        # statistics
        self.stat_bias = [np.clip(rng.normal(bias_list, 0.2), 0, 1)]
        self.users = 0

    def enqueue(self, post: Post):
        self.new.append(post)
        self.hot.append(post)

    def get_hot(self):
        return [] if self.banned else self.hot[max(-5, -len(self.hot)): -1]

    def get_new(self):
        return [] if self.banned else self.new[max(-5, -len(self.new)): -1]

    # @profile
    def current_bias(self):
        """Return bias-vector over hot-queue weighted by the hot-score. """
        num = np.full(get_n(), 0.0, float)
        den = 0.0

        for post in self.hot:
            num += post.bias * post.hot()
            den += post.hot()

        return num / den if not den == 0 else np.full(get_n(), 0.5, float)

    def update_bias(self):
        """Update the subreddit bias. Old values are weighted double. """
        self.bias = (self.stat_bias[-1] * 9 + self.current_bias()) / 10
        self.stat_bias.append(self.bias)

    def __lt__(self, other):
        return self.id < other.id


class User:
    # FIXME [assuming]:
    # everyone is equally smart
    # only upvotes/downvotes as regulators
    # repetition effect not taken into account, introduce vulnerability variable
    def __init__(self, usr_id: int, bias_list: np.array, online_bias: float, create_bias: float,
                 ls_subreddits: np.array, usr_subreddit_cap: int):
        # properties
        self.id: int = usr_id
        self.name: str = Names.generateName()

        # self.bias = np.clip(rng.normal(bias_list, 0.2), 0, 1)
        self.bias = Helper.getUserBias()
        self.importance = Helper.getImportance()
        self.online_bias = as_probability(rng.normal(online_bias, 0.2))
        self.create_bias = as_probability(rng.normal(create_bias, 0.01))
        self.hot_bias = 0.7
        self.last_post = None

        # moderation
        self.banned = 0

        # statistics
        self.viewed_posts: int = 0
        self.created_posts: int = 0
        self.success = np.full(get_n(), 0.0, float)
        self.left = 0
        self.entered = 0

        # get subreddits
        self.usr_subreddit_cap = usr_subreddit_cap
        probs = [1 / max(linalg.norm(sr.bias - self.bias), 0.001) for sr in ls_subreddits]
        s = sum(probs)
        probs = [p / s for p in probs]

        self.subreddits = rng.choice(ls_subreddits,
                                     rng.choice(range(1, min(len(ls_subreddits), usr_subreddit_cap) + 1)),
                                     replace=False,
                                     p=probs)

        for subreddit in self.subreddits:
            subreddit.users += 1

    # @profile
    def create_post(self):
        self.created_posts += 1
        post = Post(self.id, self.bias)
        self.last_post = post

        # select up to 3 subreddits to post on
        for subreddit in rng.choice(self.subreddits, rng.choice(min(3, len(self.subreddits)) + 1), replace=False):
            subreddit.enqueue(post)

        return post

    # @profile
    def consume_post(self, ls_subreddits):
        # be disgruntled if no subreddits are left
        # if len(self.subreddits) == 0 and rng.random() < 0.97:
        #     return

        # maybe enter a new subreddit, introducing hard cap
        # if self.usr_subreddit_cap - len(self.subreddits) > 0 \
        #         and (self.usr_subreddit_cap - len(self.subreddits)) / self.usr_subreddit_cap < rng.random() * 1.5:
        #     other_srs = np.setdiff1d(ls_subreddits, self.subreddits)
        #     probs = np.array([linalg.norm((self.bias - sr.bias) * self.importance) ** (1/5) for sr in other_srs])
        #     probs = probs / sum(probs)
        #     new_sr = rng.choice(other_srs, p=probs)

        #     np.append(self.subreddits, new_sr)
        #     new_sr.users += 1
        #     self.entered += 1

        if len(self.subreddits) == 0:
            return

        subreddit = rng.choice(self.subreddits)
        posts = []
        if self.hot_bias > rng.random():
            posts = subreddit.get_hot()
        else:
            posts = subreddit.get_new()

        if len(posts) == 0:
            return

        # get weighted bias confirmation
        for post in posts:
            # statistics
            self.viewed_posts += 1
            post.views += 1

            # vote on posts
            diff = linalg.norm((self.bias - post.bias))  # * self.importance)

            if diff < 0.2 * get_sqrt_n():
                post.ups += 1
            elif diff > 0.8 * get_sqrt_n():
                post.downs += 1

            # adjust own bias
            new_bias = self.bias
            if diff < 0.1 * get_sqrt_n():
                new_bias = np.clip(self.bias + 0.1 * (post.bias - self.bias), 0, 1)
                post.success += abs(new_bias - self.bias)
            elif diff > get_sqrt_n() * (1 - 0.1):
                new_bias = np.clip(self.bias - 0.1 * (post.bias - self.bias), 0, 1)
                post.success -= abs(new_bias - self.bias)

            self.bias = new_bias

        biases = np.array([p.bias for p in posts])
        weights = np.array([p.weight() for p in posts])

        # get repetition bias
        # if np.std(biases) < 0.2:
        #     self.bias = np.clip(self.bias + 0.05 * (np.average(biases, axis=0, weights=weights) - self.bias), 0, 1)

        # maybe leave subreddits
        # if linalg.norm((np.average(biases, axis=0, weights=weights) - self.bias) * self.importance)\
        #         * (len(self.subreddits) / self.usr_subreddit_cap) < rng.random() * 1.5:
        #     np.delete(self.subreddits, np.where(self.subreddits == subreddit))
        #     subreddit.users -= 1
        #     self.left += 1

    # @profile
    def switch_subreddit(self, all_subs: np.ndarray):
        # TODO
        # Users should switch subreddits when they are dissatisfied
        cnt_sub = len(self.subreddits)

        # Create local copy?
        self_reddits = self.subreddits
        self_reddits = np.random.permutation(self_reddits)
        # Delete subreddits that we do not agree with anymore
        for sub in self_reddits:
            p = np.clip(
                (cnt_sub + 1) / (self.usr_subreddit_cap + 1) * (get_sqrt_n() - linalg.norm(self.bias - sub.bias)), 0, 1)
            if p > rng.random() * 0.1 + 0.9:
                self_reddits = np.delete(self_reddits, np.argwhere(self_reddits == sub))
                sub.users -= 1
                cnt_sub -= 1
                self.left += 1

        # Disgruntled users stay away for a while
        if cnt_sub == 0:
            if rng.random() < 0.97:
                self.subreddits = self_reddits
                return

        # Add new subreddits that the user agrees with
        array_dif = np.setdiff1d(all_subs, self_reddits)
        array_dif = np.random.permutation(array_dif)
        for sub in array_dif:
            p = (cnt_sub + 1) / (self.usr_subreddit_cap + 1) * linalg.norm(self.bias - sub.bias)
            if p < rng.random() * 0.05:
                self_reddits = np.append(self_reddits, sub)
                sub.users += 1
                cnt_sub += 1
                self.entered += 1

        # Apply changes
        self.subreddits = self_reddits

    def more_extreme(self, state_bias):
        self.bias = np.clip(self.bias - (state_bias - self.bias) * 0.05, 0, 1)


class Moderation:
    def __init__(self, bias, zones, check_users, check_posts, ls_users, ls_subreddits, ls_posts):
        # goal
        self.bias = bias  # np.array([0.3, 0.5]), interesting if we vary this opinion
        self.zones = zones  # np.array([0.2, 0.35, 0.45]) * get_sqrt_n(), this defines the borders of how Moderator reacts
        # to opinions (depending on how far they are from the own Opinion

        # power
        self.check_users = check_users
        self.check_posts = check_posts

        # data
        self.ls_users: np.ndarray = ls_users
        self.ls_subreddits: np.ndarray = ls_subreddits
        self.ls_susreddits: np.ndarray = np.zeros(len(ls_subreddits))
        self.ls_posts = ls_posts
        self.blacklist = Helper.Blacklist(check_users)  # users that are critical and detected are listed here

    # helper methods
    def distance(self, post: Post):
        return rng.normal(linalg.norm(self.bias - post.bias) * get_sqrt_n(), 0.05)

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
            self.ls_susreddits[sr.id] += 1
            sr.users -= 1
            # if self.ls_susreddits[sr.id] > sr.users / 3 + 4:
            #     sr.banned = True

        opponent.subreddits = np.empty(0)

    # no intervention
    def intervene_anarchistic(self):
        pass

    # state intervenes if opinion bias is too far from own opinion
    def intervene_moderated(self):
        # scan new successful posts
        posts = rng.choice(self.ls_posts, min(self.check_posts - len(self.blacklist.data), len(self.ls_posts)),
                           replace=False).tolist()
        for user in self.blacklist.get():
            user: User
            posts.append(user.last_post)

        for post in posts:
            p = rng.random()
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


class Network:
    def __init__(self):
        # moderation type: True -> anarchy, False -> China
        self.moderation_type = False

        # quantities
        self.cnt_subreddits = 200
        self.cnt_users = 2000

        # subreddit properties
        self.sr_bias = np.array([0.5, 0.5])
        self.sr_tolerance = np.full(get_n(), 0.4, float)

        # user properties
        # FIXME:
        self.usr_bias = np.array([0.5, 0.5])
        self.usr_online_bias = 0.60
        self.usr_create_bias = 0.03
        self.usr_subreddit_cap = 3

        # ls_s
        self.ls_subreddits = np.array(
            [Subreddit(self.sr_bias, self.sr_tolerance, i) for i in range(self.cnt_subreddits)])
        self.ls_users = np.array(
            [User(usr_id, self.usr_bias, self.usr_online_bias, self.usr_create_bias,
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
        self.moderation: Moderation = Moderation(np.array([0.5, 0.5]), np.array([0.2, 0.35, 0.45]) * get_sqrt_n(),
                                                 50, 200, self.ls_users, self.ls_subreddits, self.ls_posts)

    # @profile
    def simulate_round(self):
        global timestamp

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
            if user.online_bias > rng.random():
                # TODO: reset tmp (doesn't exist yet)
                if user.create_bias > rng.random():
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

        timestamp += 1

    def finalize(self):
        for post in self.ls_posts:
            self.ls_users[post.creator].success += post.success

        for user in self.ls_users:
            self.left += user.left
            self.entered += user.entered
