import networkx as nx
from collections import Counter
import pandas as pd
import numpy as np
from itertools import chain


def add_story_to_lists(story, list_of_counters, day_cut_off=5):
    break_in_obs = day_cut_off*4
    for i in range(0, len(story)-break_in_obs):
        if story[i] != -1 and story[i+break_in_obs] != -1:
            list_of_counters[story[i]][story[i+break_in_obs]] += 1


def nested_lists_of_count_to_pandas_edgelist(nested_lists_of_counters, h3_ids):
    sum_iter = [sum(count.values()) for count in nested_lists_of_counters]
    data = [(counter[col]/n_obs, n_obs, row, col) for row, (counter, n_obs)
            in enumerate(zip(nested_lists_of_counters, sum_iter))
            for col in counter]
    probs = [dat for dat, _, _, _ in data]
    source = [h3_ids[row] for _, _, row, _ in data]
    target = [h3_ids[col] for _, _, _, col in data]
    n_obs = [n_ob for _, n_ob, _, _ in data]
    pd_edgelist = pd.DataFrame({
        'source': source,
        'target': target,
        'prob': probs,
        'N': n_obs}
    )
    return pd_edgelist


def count_transitions(list_of_stories, unique_ids, day_cut_off=5):
    final_list = [Counter() for _ in unique_ids]
    id_to_int = {key: i for i, key in enumerate(unique_ids)}
    id_to_int[-1] = -1
    list_of_stories_int = [[id_to_int[key]
                            for key in story] for story in list_of_stories]
    for story in list_of_stories_int:
        add_story_to_lists(story, final_list, day_cut_off)

    return final_list


def make_transition(list_of_h3_stories, day_cut_off=5,
                    ret_edgelist=False, ret_id_map=False):
    """
    Returns transition matrix and a list to map numbers to h3_indices
    """
    # Covert lists of states to a list of unique states
    unique_ids = list(set(chain.from_iterable(list_of_h3_stories)))
    list_of_counters = count_transitions(list_of_h3_stories, unique_ids,
                                         day_cut_off)
    pd_edgelist = nested_lists_of_count_to_pandas_edgelist(
        list_of_counters, unique_ids)
    pd_edgelist['neglogprob'] = pd_edgelist.apply(
        lambda x: -np.log(x['prob']), axis=1)
    net = nx.convert_matrix.from_pandas_edgelist(
                pd_edgelist, create_using=nx.DiGraph,
                edge_attr=['prob', 'N', 'neglogprob'])

    return net
