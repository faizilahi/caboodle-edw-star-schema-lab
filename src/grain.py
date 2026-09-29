"""Grain violation detectors."""
from __future__ import annotations

import pandas as pd


def duplicate_keys(df: pd.DataFrame, key: str) -> pd.DataFrame:
    return df[df.duplicated(key, keep=False)].sort_values(key)


def orphan_bridge(bridge: pd.DataFrame, fact: pd.DataFrame, key: str = "EncounterKey") -> pd.DataFrame:
    parents = set(fact[key])
    return bridge[~bridge[key].isin(parents)]


def bridge_explodes_fact(
    fact: pd.DataFrame, bridge: pd.DataFrame, key: str = "EncounterKey"
) -> bool:
    """True if someone incorrectly left-joined bridge onto fact without aggregating."""
    joined = fact.merge(bridge, on=key, how="left")
    return len(joined) > len(fact) and bridge[key].duplicated().any()
