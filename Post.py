import numpy as np
import math
import params as pms


def get_hot(post):
    """Doubles the 'hot' method. Needed as a sorting criteria. """
    return post.hot()


class Post:
    """A class representing posts featuring some information about the post and some weighting methods. """
    def __init__(self, creator, bias):
        # properties
        self.creation: int = pms.timestamp
        self.creator: int = creator
        self.bias = np.clip(pms.rng.normal(bias, 0.1), 0, 1)
        self.ups = 1
        self.downs = 0

        # moderation
        self.not_hot: bool = False  # True iff Moderator doesn't want this post to reach the hot-queue

        # statistics
        self.views = 1
        self.success = np.zeros(pms.N)

    def score(self):
        """Returns the unweighted difference between upvotes and downvotes. """
        return self.ups - self.downs

    def weight(self):
        """Returns the cognitive weight of a post based on the logarithm of its score. """
        return max(math.log(self.score(), 10) if self.score() > 0 else 0, 0.1)

    # @profile
    def hot(self):
        """Returns a hot-score closely related to Reddits official hot-score. Based on score and age. """
        s = self.score()
        order = math.log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else 0 if s == 0 else -1
        hours = self.creation - pms.timestamp
        return 0 if self.not_hot else round(sign * order + hours / 12, 7)
