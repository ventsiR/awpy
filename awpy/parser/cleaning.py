"""Data cleaning functions."""

import difflib
from collections.abc import Sequence
from typing import Any, Literal, Protocol

import numpy as np
import pandas as pd
import textdistance


class DistMetricCallable(Protocol):
    """Class to define valid FOM callables."""

    def __call__(self, *sequences: Sequence[object]) -> float:
        """Protocol for dist metric callables.

        Take a sequence of objects and return a distance.

        Returns:
            float: Distance between object.
        """


def _set_distance_metric(metric: str) -> DistMetricCallable:
    if metric== "lcss":
        return textdistance.lcsseq.distance
    if metric == "hamming":
        return textdistance.hamming.distance
    if metric == "levenshtein":
        return textdistance.levenshtein.distance
    if metric == "jaro":
        return textdistance.jaro.distance
    raise ValueError(
            "Metric can only be lcss, hamming, levenshtein, jaro or difflib."
        )


def associate_entities(
    game_names: list[str | None] | None = None,
    entity_names: list[str] | None = None,
    metric: Literal["lcss", "hamming", "levenshtein", "jaro", "difflib"] = "lcss",
) -> dict:
    """A function to return a dict of associated entities. Accepts.

    Args:
        game_names (list, optional): A list of names generated by the demofile.
            Defaults to []
        entity_names (list, optional): A list of names: Defaults to []
        metric (string, optional): A string indicating distance metric,
            one of lcss, hamming, levenshtein, jaro, difflib.
            Defaults to 'lcss'

    Returns:
        A dictionary where the keys are entries in game_names,
        values are the matched entity names.

    Raises:
        ValueError: If metric is not in:
            ["lcss", "hamming", "levenshtein", "jaro", "difflib"]
    """
    if game_names is None:
        game_names = []
    if entity_names is None:
        entity_names = []
    entities: dict[str | None, Any] = {}
    if metric.lower() == "difflib":
        for gn in game_names:
            if gn is not None and gn is not np.nan:
                closest_name = difflib.get_close_matches(
                    gn, entity_names, n=1, cutoff=0.0
                )
                if len(closest_name) > 0:
                    entities[gn] = closest_name[0]
                else:
                    entities[gn] = None
        entities[None] = None
        return entities

    dist_metric = _set_distance_metric(metric.lower())
    for gn in game_names:
        if gn is not None and gn is not np.nan and gn != "":
            name_distances = []
            names = []
            if len(entity_names) > 0:
                for p in entity_names:
                    name_distances.append(dist_metric(gn.lower(), p.lower()))
                    names.append(p)
                entities[gn] = names[np.argmin(name_distances)]
                entity_names.pop(np.argmin(name_distances))
        if gn == "":
            entities[gn] = None
    entities[None] = None
    return entities


def replace_entities(
    df: pd.DataFrame, col_name: str, entity_dict: dict
) -> pd.DataFrame:
    """A function to replace values in a Pandas df column given an entity dict.

    entitiy_dict as created in associate_entities().

    Args:
        df (DataFrame)     : A Pandas DataFrame
        col_name (string)  : A column in the Pandas DataFrame
        entity_dict (dict) : A dictionary as created in associate_entities()

    Returns:
        A dataframe with replaced names.
    """
    if col_name not in df.columns:
        raise ValueError("Column does not exist!")
    df[col_name] = df[col_name].replace(entity_dict)
    return df
