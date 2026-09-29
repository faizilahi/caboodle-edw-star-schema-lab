"""Visit-level fact helpers for reporting marts that sit on the star."""
from __future__ import annotations

import pandas as pd

from .bridge import primary_dx


def encounter_with_primary_dx(fact: pd.DataFrame, bridge: pd.DataFrame) -> pd.DataFrame:
    """Safe 1:1 enrich — primary diagnosis only, never raw bridge join."""
    return fact.merge(primary_dx(bridge), on="EncounterKey", how="left")


def los_distribution(fact: pd.DataFrame) -> pd.DataFrame:
    return (
        fact.groupby("LOSDays", as_index=False)
        .size()
        .rename(columns={"size": "encounters"})
        .sort_values("LOSDays")
    )


def med_admin_per_encounter(admin: pd.DataFrame) -> pd.DataFrame:
    return (
        admin.groupby("EncounterKey", as_index=False)
        .size()
        .rename(columns={"size": "admin_events"})
    )
