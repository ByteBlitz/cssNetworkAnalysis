import copy


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


def as_probability(val):
    """Keep numbers in [0,1] with this function. """
    return min(max(val, 0), 1)
