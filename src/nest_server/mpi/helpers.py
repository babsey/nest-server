# helpers.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

from nest_server.logger import log


def combine(response: list | None) -> dict | list | None:
    """Combine responses from different MPI processes.

    In a distributed scenario, each MPI process creates its own share
    of the response from the data available locally. To present a
    coherent view on the reponse data for the caller, this data has to
    be combined.

    If this function is run serially (i.e., without MPI), it just
    returns the response data from the only process immediately.

    The type of the returned result can vary depending on the call
    that produced it.

    The combination of results is based on a cascade of heuristics
    based on the call that was issued and individual repsonse data:
      * if all responses are None, the combined response will also just
        be None
      * for some specific calls, the responses are known to be the
        same from the master and all workers. In this case, the
        combined response is just the master response
      * if the response list contains only a single actual response and
        None otherwise, the combined response will be that one actual
        response
      * for calls to GetStatus on recording devices, the combined
        response will be a merged dictionary in the sense that all
        fields that contain a single value in the individual responsed
        are kept as a single values, while lists will be appended in
        order of appearance; dictionaries in the response are
        recursively treated in the same way
      * for calls to GetStatus on neurons, the combined response is just
        the single dictionary returned by the process on which the
        neuron is actually allocated
      * if the response contains one list per process, the combined
        response will be those lists concatenated and flattened.

    """
    log("combine", f"{response}")

    if response is None:
        return None

    # Filter out None values from the list
    if isinstance(response, list):
        response = [r for r in response if r is not None]

    # Return None if response is None or all items of the list are None.
    if len(response) == 0 or all(v is None for v in response):
        return None

    if len(response) == 1 or response[0] == response[1]:
        return response[0]

    # return the master response if all responses are known to be the same
    if all(isinstance(v, (list, tuple)) for v in response):
        # return combine([v[0] for v in response])
        return [v_j for v_i in list(zip(*response, strict=True)) for v_j in v_i if v_j is not None]

    # return a single merged dictionary if there are many of them
    if all(isinstance(v, dict) for v in response):
        return merge_dicts(response)

    return response

    # log("combine()", f"ERROR: cannot combine response={response}")
    # msg = "Cannot combine data because of unknown reason"
    # raise Exception(msg)  # pylint: disable=W0719


def merge_dicts(data: list[dict]) -> dict:
    """Merge dictionaries of the data.

    This function merged list of dictionaries.

    Parameters
    ----------
    data: list of dicts
        merged dict

    """

    # Merge status of recorder
    if all("n_events" in d for d in data):
        new_data = {k: [] for k in data[0]}
        for d in data:
            for k, v in d.items():
                if isinstance(v, list):
                    for idx, i in enumerate(v):
                        if d["n_events"][idx] > 0:
                            new_data[k].append(i)
                elif d["n_events"] > 0:
                    new_data[k].append(v)

        if len(new_data["n_events"]) == 1:
            new_data = {k: v[0] for k, v in new_data.items()}
        return new_data

    data = [d for d in data if d != {}]

    if len(data) == 1:
        return data[0]

    merged = {}

    keys = [k for d in data for k in list(d.keys())]
    value_types = {k: [] for k in keys}
    for d in data:
        for k, v in d.items():
            value_types[k].append(type(v))

    is_collection = "model" in keys or "synapse_model" in keys

    for d in data:
        for k, v in d.items():
            if k not in merged:
                value_type = value_types.get(k, [])
                if list in value_type or is_collection:
                    if isinstance(v, list):
                        merged[k] = v

                    else:
                        merged[k] = [v]

                else:
                    merged[k] = v

            elif not isinstance(merged[k], list):
                continue

            elif isinstance(v, list):
                merged[k].extend(v)

            elif isinstance(v, dict):
                merged[k] = {**merged[k], **v}

            else:
                merged[k].append(v)

    return merged
