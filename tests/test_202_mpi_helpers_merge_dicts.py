import pytest

from nest_server.mpi.helpers import merge_dicts

# Recorder status (contains "n_events")


def test_merge_recorder_single_rank_with_events_is_unwrapped():
    data = [
        {"n_events": 2, "events": {"senders": [1, 2], "times": [0.1, 0.2]}},
        {"n_events": 0, "events": {"senders": [], "times": []}},
    ]
    assert merge_dicts(data) == data[0]


def test_merge_recorder_multiple_ranks_with_events():
    events_0 = {"senders": [1], "times": [0.1]}
    events_1 = {"senders": [2, 2], "times": [0.2, 0.3]}
    data = [
        {"n_events": 1, "events": events_0},
        {"n_events": 2, "events": events_1},
    ]
    assert merge_dicts(data) == {"n_events": [1, 2], "events": [events_0, events_1]}


def test_merge_recorder_no_events():
    data = [{"n_events": 0, "events": {}}, {"n_events": 0, "events": {}}]
    assert merge_dicts(data) == {"n_events": [], "events": []}


def test_merge_recorder_list_values():
    # Several recorders per rank: values are filtered by per-index n_events
    data = [
        {"n_events": [1, 0], "label": ["a", "b"]},
        {"n_events": [0, 2], "label": ["c", "d"]},
    ]
    assert merge_dicts(data) == {"n_events": [1, 2], "label": ["a", "d"]}


# Generic status dictionaries


def test_merge_ignores_empty_dicts():
    assert merge_dicts([{}, {"a": 1}, {}]) == {"a": 1}


def test_merge_all_empty_dicts():
    assert merge_dicts([{}, {}]) == {}


def test_merge_disjoint_keys():
    assert merge_dicts([{"a": 1}, {"b": 2}]) == {"a": 1, "b": 2}


def test_merge_scalar_keeps_first_value():
    assert merge_dicts([{"a": 1}, {"a": 2}]) == {"a": 1}


def test_merge_lists_are_concatenated():
    assert merge_dicts([{"a": [1, 2]}, {"a": [3]}, {"a": []}]) == {"a": [1, 2, 3]}


def test_merge_mixed_scalar_and_list_values():
    assert merge_dicts([{"a": 1}, {"a": [2, 3]}]) == {"a": [1, 2, 3]}
    assert merge_dicts([{"a": [1]}, {"a": 2}]) == {"a": [1, 2]}


def test_merge_collection_with_model():
    data = [
        {"model": "iaf_psc_alpha", "V_m": -70.0},
        {"model": "iaf_psc_alpha", "V_m": -65.0},
    ]
    assert merge_dicts(data) == {"model": ["iaf_psc_alpha", "iaf_psc_alpha"], "V_m": [-70.0, -65.0]}


def test_merge_collection_with_synapse_model():
    data = [
        {"synapse_model": "static_synapse", "source": [1], "weight": 1.0},
        {"synapse_model": "static_synapse", "source": [2, 3], "weight": 2.0},
    ]
    assert merge_dicts(data) == {
        "synapse_model": ["static_synapse", "static_synapse"],
        "source": [1, 2, 3],
        "weight": [1.0, 2.0],
    }


def test_merge_collection_key_only_in_one_dict():
    data = [{"model": "a", "x": 1}, {"model": "b"}]
    assert merge_dicts(data) == {"model": ["a", "b"], "x": [1]}


def test_merge_collection_with_dict_values_raises():
    # The dict branch tries to merge a dict into the list collected so far.
    data = [{"model": "a", "p": {"x": 1}}, {"model": "b", "p": {"y": 2}}]
    with pytest.raises(TypeError):
        merge_dicts(data)
