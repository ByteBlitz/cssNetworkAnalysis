def most_successful(seq, cnt, metric):
    """Can be used to find the [cnt] most successful items from [seq] concerning [metric]"""
    ms_list = [seq[0]]
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


def as_probability(val):
    """Keep numbers in [0,1] with this function. """
    return min(max(val, 0), 1)


class Watchlist:
    """Circular queue implementation to keep track of suspicious Users. """
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
