"""Build star schema in DuckDB and compute KPIs."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def load_dims_facts(con: duckdb.DuckDBPyConnection, data_dir: Path) -> None:
    for name in (
        "dim_patient",
        "dim_facility",
        "dim_date",
        "dim_encounter_type",
        "fact_encounter",
    ):
        path = (data_dir / f"{name}.csv").as_posix()
        con.execute(
            f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')"
        )


def kpi_alos(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    sql = """
    SELECT
        f.facility_name,
        ROUND(AVG(fact.length_of_stay_days), 2) AS avg_los,
        COUNT(*) AS inpatient_count
    FROM fact_encounter fact
    JOIN dim_facility f ON fact.facility_key = f.facility_key
    JOIN dim_encounter_type t ON fact.encounter_type_key = t.encounter_type_key
    WHERE t.encounter_type = 'Inpatient'
      AND fact.length_of_stay_days IS NOT NULL
    GROUP BY 1
    ORDER BY inpatient_count DESC
    """
    return con.execute(sql).df()


def kpi_readmission_proxy(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """30-day readmission proxy: second inpatient within 30 days for same patient."""
    sql = """
    WITH inp AS (
        SELECT
            fact.patient_key,
            CAST(d.full_date AS DATE) AS admit_date,
            fact.length_of_stay_days,
            fact.encounter_id
        FROM fact_encounter fact
        JOIN dim_date d ON fact.admit_date_key = d.date_key
        JOIN dim_encounter_type t ON fact.encounter_type_key = t.encounter_type_key
        WHERE t.encounter_type = 'Inpatient'
    ),
    index_total AS (
        SELECT COUNT(DISTINCT encounter_id) AS total_index FROM inp
    ),
    pairs AS (
        SELECT
            a.patient_key,
            a.encounter_id AS index_encounter,
            MIN(b.encounter_id) AS readmit_encounter
        FROM inp a
        JOIN inp b
          ON a.patient_key = b.patient_key
         AND b.admit_date > a.admit_date
         AND b.admit_date <= a.admit_date + INTERVAL 30 DAY
        GROUP BY 1, 2
    )
    SELECT
        (SELECT total_index FROM index_total) AS index_inpatient_encounters,
        COUNT(*) AS readmit_pairs,
        ROUND(
            COUNT(*)::DOUBLE / NULLIF((SELECT total_index FROM index_total), 0),
            4
        ) AS readmit_proxy_rate
    FROM pairs
    """
    return con.execute(sql).df()


def run_analytics(db_path: Path, data_dir: Path) -> dict[str, pd.DataFrame]:
    con = duckdb.connect(str(db_path))
    load_dims_facts(con, data_dir)
    return {
        "alos_by_facility": kpi_alos(con),
        "readmission_proxy": kpi_readmission_proxy(con),
    }
