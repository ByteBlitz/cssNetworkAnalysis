import numpy as np
import params as pms
import Post


class Subreddit:
    """A subreddit class featuring a hot-(priority)-queue and a new-stack. """
    def __init__(self, sr_id):
        # post queues
        self.hot = []
        self.new = []

        # properties
        self.id = sr_id
        self.bias = np.clip(pms.rng.normal(pms.SR_BIAS, 0.2), 0, 1)

        # moderation
        # We removed the ban option for subreddits because usually the same people will quickly find together on a
        # new but similar subreddit anyway.

        # statistics
        self.stat_bias = [self.bias]
        self.users = 0

    def sort_hot(self):
        """Sorts the hot-queue and cuts it to keep complexity bounded. """
        # sort the hot queue
        self.hot.sort(key=Post.get_hot, reverse=False)
        # Only the first 5 elements can be seen.
        # The next 10 elements may have a realistic chance of overtaking by downvotes and age of the first batch.
        # The first 5 elements of the new-stack are still evaluated.
        self.hot = self.hot[0:15] + self.get_new()

    def enqueue(self, post: Post):
        self.new.append(post)
        self.hot.append(post)

        # Sort the hot queue as soon as it hits 50 entries.
        if len(self.hot) >= 50:
            self.sort_hot()

    def get_hot(self):
        """Return a list of the 5 hottest posts. """
        return self.hot[0: min(5, len(self.hot))]

    def get_new(self):
        """Return a list of the 5 newest posts. """
        return self.new[max(-5, -len(self.new)): -1]

    # @profile
    def current_bias(self):
        """Return bias-vector over hot-queue weighted by the hot-score. """
        num = np.full(pms.N, 0.0, float)
        den = 0.0

        for post in self.hot:
            num += post.bias * post.hot()
            den += post.hot()

        return num / den if not den == 0 else np.full(pms.N, 0.5, float)

    def update_bias(self):
        """Update the subreddit bias. Old values are weighted more to account for some kind of memory. """
        self.bias = (self.stat_bias[-1] * 9 + self.current_bias()) / 10
        self.stat_bias.append(self.bias)

    def __lt__(self, other):
        return self.id < other.id
