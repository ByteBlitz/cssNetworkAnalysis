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
        self.all_subreddits = ls_subreddits
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

    def touch_grass(self):
        """Spend an hour offline and change your opinion in real human contact.
        Currently not used for the sake of simplicity. """
        self.bias = np.clip(pms.rng.normal(self.bias, 0.01), 0, 1)

    def edge_dist(self):
        """Get the distance to the closest edge in every variable.
        Useful to prevent users from taking extremely radical positions too easily. """
        return np.array([min(self.bias[i], 1 - self.bias[i]) for i in range(pms.N)])

    # @profile
    def join_sr(self):
        """Join one subreddit chosen by how close your opinions are. """
        probs = [1 / max(linalg.norm(sr.bias - self.bias), 0.001) for sr in self.all_subreddits]
        s = sum(probs)
        probs = [p / s for p in probs]

        sr = pms.rng.choice(self.all_subreddits, 1, replace=False, p=probs)[0]
        while sr in self.subreddits:
            sr = pms.rng.choice(self.all_subreddits, 1, replace=False, p=probs)[0]

        self.subreddits = np.append(self.subreddits, sr)
        sr.users += 1
        self.entered += 1

    def leave_sr(self):
        """Leave any of your subreddits. """
        sr = pms.rng.choice(self.subreddits)

        self.subreddits = np.delete(self.subreddits, np.where(self.subreddits == sr))
        sr.users -= 1
        self.left += 1

    def create_post(self):
        """Create Post, hand it to a Subreddit and return it to the caller. """
        self.created_posts += 1
        self.last_post = Post.Post(self.id, self.bias)

        # Select a Subreddit to post on.
        if len(self.subreddits) == 0:
            self.join_sr()

        for subreddit in pms.rng.choice(self.subreddits, 1, replace=False):
            subreddit.enqueue(self.last_post)

        return self.last_post

    # @profile
    def consume_post(self):
        """Lets a User consume a post and change their bias based on it. """

        if len(self.subreddits) == 0:
            return

        subreddit = pms.rng.choice(self.subreddits)
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

            w_diff = linalg.norm((self.bias - post.bias) * self.importance)
            bias_diff = post.bias - self.bias

            # vote on posts
            if w_diff < 0.2 * pms.SQRT_N:
                post.ups += 1
            elif w_diff > 0.8 * pms.SQRT_N:
                post.downs += 1

            # adjust own bias
            new_bias = self.bias
            if w_diff < 0.05 * pms.SQRT_N:
                new_bias = np.clip(self.bias + 0.5 * bias_diff, 0, 1)
                post.success += abs(new_bias - self.bias)
            elif w_diff > pms.SQRT_N * 0.9:
                new_bias = np.clip(self.bias - 0.01 * self.edge_dist() * bias_diff / max(linalg.norm(bias_diff), 0.01),
                                   0, 1)
                post.success -= abs(new_bias - self.bias)

            self.bias = new_bias

        biases = np.array([p.bias for p in posts])
        weights = np.array([p.weight() for p in posts])

        # Leave current subreddit if you're dissatisfied.
        if linalg.norm((np.average(biases, axis=0, weights=weights) - self.bias) * self.importance) \
                * (len(self.subreddits) / self.usr_subreddit_cap) * 0.25 > pms.rng.random():
            self.subreddits = np.delete(self.subreddits, np.where(self.subreddits == subreddit))
            subreddit.users -= 1
            self.left += 1

        # Repetition Bias. Deactivated for simplicity.
        # get repetition bias
        # if np.std(biases) < 0.2:
        #     self.bias = np.clip(self.bias + 0.01 * (np.average(biases, axis=0, weights=weights) - self.bias), 0, 1)

    # @profile
    def switch_subreddit(self):
        """Makes a User reevaluate their Subreddit choices. """
        cnt_sub = len(self.subreddits)

        # User leaves any Subreddit if he's in too many.
        if cnt_sub > 0 and (1 - (self.usr_subreddit_cap - cnt_sub) / self.usr_subreddit_cap) * 0.25 > pms.rng.random():
            self.leave_sr()

        # User joins a new Subreddit he agrees with if he is in too few.
        if self.usr_subreddit_cap > cnt_sub and (
                self.usr_subreddit_cap - cnt_sub) / self.usr_subreddit_cap * 0.25 > pms.rng.random():
            self.join_sr()

    def more_extreme(self, state_bias):
        """Users distance themselves from the Moderation's opinion by at most 0.02, when they notice being punished. """
        self.bias = np.clip(
            self.bias - (state_bias - self.bias) / max(linalg.norm(state_bias - self.bias), 0.01)
            * self.edge_dist() * 0.02, 0, 1)
