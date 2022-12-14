import numpy as np
import params as pms
import Post


class Subreddit:
    def __init__(self, bias_list: np.ndarray, sr_id):
        # post queues
        self.hot = []
        self.new = []

        # properties
        self.id = sr_id
        self.bias = np.clip(pms.rng.normal(bias_list, 0.2), 0, 1)

        # moderation
        self.banned = False

        # statistics
        self.stat_bias = [np.clip(pms.rng.normal(bias_list, 0.2), 0, 1)]
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
        num = np.full(pms.get_n(), 0.0, float)
        den = 0.0

        for post in self.hot:
            num += post.bias * post.hot()
            den += post.hot()

        return num / den if not den == 0 else np.full(pms.get_n(), 0.5, float)

    def update_bias(self):
        """Update the subreddit bias. Old values are weighted double. """
        self.bias = (self.stat_bias[-1] * 9 + self.current_bias()) / 10
        self.stat_bias.append(self.bias)

    def __lt__(self, other):
        return self.id < other.id
