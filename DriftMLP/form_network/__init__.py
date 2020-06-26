from collections import Counter
from itertools import chain
from typing import List

import igraph
import numpy as np
import pandas as pd


def add_story_to_lists(story: List[int], list_of_counters: List[Counter], day_cut_off: int = 5,
                       observations_per_day: int = 4) -> None:
    """

    Parameters
    ----------
    story : List[int]
        A list containing a trajectory of states where each observations is `1/observations_per_day` apart in days.
    list_of_counters : List[Counter]
        The list of counters to update. Stores numbers of observations going for [i] to [j].
    day_cut_off : int
        A cut off that is the number in days. The transition matrix is estimated for state p_i -> p_{i+1} in day_cut_off days.
    observations_per_day : int
        The number of observations per day in story. e.g. 6 hourly observation implies 4 observations per day

    Returns
    -------
    None
        Just updates list_of_counters by assigning to the reference.

    """
    break_in_obs = day_cut_off * observations_per_day
    for i in range(0, len(story) - break_in_obs):
        if story[i] != -1 and story[i + break_in_obs] != -1:
            list_of_counters[story[i]][story[i + break_in_obs]] += 1
    return None


def nested_lists_of_count_to_pandas_edgelist(nested_lists_of_counters, h3_ids):
    sum_iter = [sum(count.values()) for count in nested_lists_of_counters]
    data = [(counter[col] / n_obs, n_obs, row, col) for row, (counter, n_obs)
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


def count_transitions(list_of_stories: List, unique_ids: List, **kwargs):
    final_list = [Counter() for _ in unique_ids]
    id_to_int = {key: i for i, key in enumerate(unique_ids)}
    id_to_int[-1] = -1
    list_of_stories_int = [[id_to_int[key]
                            for key in story] for story in list_of_stories]
    for story in list_of_stories_int:
        add_story_to_lists(story, final_list, **kwargs)

    return final_list


def pandas_to_igraph(pd_edge_df, pd_vertex_df):
    unique_ids = list(set(pd_edge_df['source'].to_list() + pd_edge_df['target'].to_list()))
    vertex_hash = {key: i for i, key in enumerate(unique_ids)}
    source_int = pd_edge_df['source'].map(vertex_hash)
    target_int = pd_edge_df['target'].map(vertex_hash)
    reordered_vertex_df = pd_vertex_df.loc[unique_ids]
    vertex_attrs = {'name': unique_ids,
                    'inN': reordered_vertex_df.iloc[:, 0].to_list(),
                    'outN': reordered_vertex_df.iloc[:, 1].to_list()}
    edge_attr_columns = ['prob', 'N', 'neglogprob']
    edge_attrs = {column: pd_edge_df[column].to_list() for column in edge_attr_columns}
    network = igraph.Graph(len(unique_ids),
                           edges=list(zip(source_int, target_int)),
                           directed=True,
                           vertex_attrs=vertex_attrs,
                           edge_attrs=edge_attrs)
    return network


def make_transition(list_of_h3_stories: List[List[int]], day_cut_off: int = 5, observations_per_day=4) -> igraph.Graph:
    """
    Returns transition matrix and a list to map numbers to h3_indices

    Parameters
    ----------
    list_of_h3_stories : List[List[int]]
        list of lists of h3 indices.
    day_cut_off : int
        A cut off that is the number in days. The transition matrix is estimated for state p_i -> p_{i+1} in day_cut_off days.
    observations_per_day : int
        The number of observations per day in story. e.g. 6 hourly observation implies 4 observations per day
    """

    # Covert lists of states to a list of unique states
    # Chain just appends
    unique_ids = list(set(chain.from_iterable(list_of_h3_stories)))
    # Make a list where entry [i][j] contains transitions from i to j.
    list_of_counters = count_transitions(list_of_h3_stories, unique_ids,
                                         day_cut_off=day_cut_off, observations_per_day=observations_per_day)

    pd_edgelist = nested_lists_of_count_to_pandas_edgelist(
        list_of_counters, unique_ids)

    ##We need negative log probabilities, easiest to do it here.
    pd_edgelist['neglogprob'] = pd_edgelist.apply(
        lambda x: -np.log(x['prob']), axis=1)
    ## N current contains vertex counts, replace it with edge observation counts.
    pd_edgelist['N'] = pd_edgelist.apply(
        lambda x: np.round(x['N'] * x['prob']), axis=1)
    pd_edgelist['N'] = pd_edgelist['N'].astype(int)
    pd_vertex_out_count = pd_edgelist.groupby('source').apply(lambda x: x['N'].sum())
    pd_vertex_in_count = pd_edgelist.groupby('target').apply(lambda x: x['N'].sum())
    pd_vertex_attr = pd.concat([pd_vertex_in_count, pd_vertex_out_count], axis=1)
    ###Convert pandas to a igraph network
    ###Credit to https://stackoverflow.com/questions/44400345/create-igraph-graph-from-pandas-dataframe/51901291
    net = pandas_to_igraph(pd_edgelist, pd_vertex_attr)

    return net
