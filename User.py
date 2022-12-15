import numpy as np
import numpy.linalg as linalg
import Names
import Post
import params as pms


class User:
    """Vertex actor that can create and consume posts and change its position in the graph as well as in the
    opinion-space. """
    def __init__(self, usr_id: int, ls_subreddits: np.array):
        # properties
        self.id: int = usr_id
        self.name: str = Names.generateName()

        self.bias = pms.make_user_bias()
        self.importance = pms.make_importance()
        self.online_bias = pms.make_online_bias()
        self.create_bias = pms.make_create_bias()
        self.hot_bias = pms.USR_HOT_BIAS

        # moderation
        self.last_post = None
        self.banned = 0

        # statistics
        self.viewed_posts: int = 0
        self.created_posts: int = 0
        self.success = np.full(pms.N, 0.0, float)
        self.left = 0
        self.entered = 0

        # get subreddits
        self.usr_subreddit_cap = pms.USR_SUBREDDIT_CAP
        probs = [1 / max(linalg.norm(sr.bias - self.bias), 0.001) for sr in ls_subreddits]
        s = sum(probs)
        probs = [p / s for p in probs]

        self.subreddits = pms.rng.choice(ls_subreddits,
                                         pms.rng.choice(range(1, min(len(ls_subreddits), self.usr_subreddit_cap) + 1)),
                                         replace=False,
                                         p=probs)

        for subreddit in self.subreddits:
            subreddit.users += 1

    # @profile
    def create_post(self):
        """Create Post, hand it to a Subreddit and return it to the caller. """
        self.created_posts += 1
        self.last_post = Post.Post(self.id, self.bias)

        # Select a Subreddit to post on.
        for subreddit in pms.rng.choice(self.subreddits, 1, replace=False):
            subreddit.enqueue(self.last_post)

        return self.last_post

    # @profile
    def consume_post(self, ls_subreddits):
        """Lets a User consume a post and change their bias based on it. """
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

        subreddit = pms.rng.choice(self.subreddits)
        posts = []
        if self.hot_bias > pms.rng.random():
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

            diff = linalg.norm((self.bias - post.bias) * self.importance)

            # vote on posts
            if diff < 0.2 * pms.SQRT_N:
                post.ups += 1
            elif diff > 0.8 * pms.SQRT_N:
                post.downs += 1

            # adjust own bias
            new_bias = self.bias
            if diff < 0.1 * pms.SQRT_N:
                new_bias = np.clip(self.bias + 0.1 * (post.bias - self.bias), 0, 1)
                post.success += abs(new_bias - self.bias)
            elif diff > pms.SQRT_N * (1 - 0.1):
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
        """Makes a User reevaluate their Subreddit choices. """
        cnt_sub = len(self.subreddits)

        # Create local copy?
        self_reddits = self.subreddits
        self_reddits = np.random.permutation(self_reddits)
        # Delete subreddits that we do not agree with anymore
        for sub in self_reddits:
            p = np.clip(
                (cnt_sub + 1) / (self.usr_subreddit_cap + 1) * (pms.SQRT_N - linalg.norm(self.bias - sub.bias)),
                0, 1)
            if p > pms.rng.random() * 0.1 + 0.9:
                self_reddits = np.delete(self_reddits, np.argwhere(self_reddits == sub))
                sub.users -= 1
                cnt_sub -= 1
                self.left += 1

        # Disgruntled users stay away for a while
        if cnt_sub == 0:
            if pms.rng.random() < 0.97:
                self.subreddits = self_reddits
                return

        # Add new subreddits that the user agrees with
        array_dif = np.setdiff1d(all_subs, self_reddits)
        array_dif = np.random.permutation(array_dif)
        for sub in array_dif:
            p = (cnt_sub + 1) / (self.usr_subreddit_cap + 1) * linalg.norm(self.bias - sub.bias)
            if p < pms.rng.random() * 0.05:
                self_reddits = np.append(self_reddits, sub)
                sub.users += 1
                cnt_sub += 1
                self.entered += 1

        # Apply changes
        self.subreddits = self_reddits

    def more_extreme(self, state_bias):
        """Users distance themselves from the Moderation's opinion, when they notice being punished. """
        self.bias = np.clip(self.bias - (state_bias - self.bias) * 0.05, 0, 1)
