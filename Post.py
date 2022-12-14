import numpy as np
import math
import params as pms


def get_hot(post):
    """Needed as a sorting criteria. """
    return post.hot()


class Post:
    # FIXME [assuming]:
    # all posts are of similar quality and similarly convincing

    # @profile
    def __init__(self, creator, bias):
        # properties
        self.creation = pms.timestamp
        self.creator: int = creator
        self.bias = np.clip(pms.rng.normal(bias, 0.1), 0, 1)
        # TODO: come up with a better standard deviation
        self.ups = 1
        self.downs = 0

        # moderation
        self.not_hot = False  # is set True if Moderator detects this post and avoids it getting into hot queue

        # statistics
        self.views = 1
        self.success = np.full(pms.get_n(), 0.0, float)

    def score(self):
        return self.ups - self.downs

    def weight(self):
        return max(math.log(self.score(), 10) if self.score() > 0 else 0, 0.1)

    # @profile
    def hot(self):
        s = self.score()
        order = math.log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else 0 if s == 0 else -1
        hours = self.creation - pms.timestamp
        return 0 if self.not_hot else round(sign * order + hours / 12, 7)
