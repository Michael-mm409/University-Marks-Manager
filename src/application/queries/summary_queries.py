"""DuckDB-backed query helpers for tables and summaries.

These helpers centralize SQL/data logic so views can call simple functions
and keep pandas usage to display-only when needed.
"""

from __future__ import annotations

from typing import Any, Dict, List

import duckdb
import pandas as pd

from model import Subject


def build_assignment_table_rows(subject: Subject | Any) -> List[Dict[str, str]]:
    """Return assignment rows for a subject using DuckDB transformations.

    Output rows are ready for Streamlit's st.dataframe (list of dicts).
    Columns: Assessment, Unweighted Mark, Weighted Mark, Mark Weight
    """
    # Convert assignments to list of dicts
    raw: List[Dict[str, Any]] = []
    for a in getattr(subject, "assignments", []) or []:
        raw.append(
            {
                "Assessment": getattr(a, "subject_assessment", ""),
                "Unweighted": getattr(a, "unweighted_mark", None),
                "Weighted": getattr(a, "weighted_mark", None),
                "Weight": getattr(a, "mark_weight", None),
            }
        )

    if not raw:
        return []

    con = duckdb.connect()
    # Register a DataFrame to ensure compatibility across DuckDB versions
    df = pd.DataFrame(raw)
    con.register("input", df)
    # Format and coalesce via SQL
    rows = con.execute(
        """
        SELECT
            Assessment,
            coalesce(cast(Unweighted as double), 0) as Unweighted_Mark,
            CASE
                WHEN typeof(Weighted) = 'VARCHAR' THEN cast(Weighted as varchar)
                WHEN Weighted IS NULL THEN ''
                ELSE cast(cast(Weighted as double) as varchar)
            END AS Weighted_Mark,
            CASE
                WHEN Weight IS NULL THEN 'N/A'
                WHEN cast(Weight as double) = 0 THEN '0%'
                ELSE concat(cast(cast(Weight as double) as varchar), '%')
            END AS Mark_Weight
        FROM input
        """
    ).fetchall()
    con.close()

    # Map to list of dicts for Streamlit display
    out: List[Dict[str, str]] = []
    for assessment, unweighted, weighted_str, weight_str in rows:
        out.append(
            {
                "Assessment": str(assessment) if assessment is not None else "",
                "Unweighted Mark": f"{float(unweighted):.1f}",
                "Weighted Mark": weighted_str if weighted_str is not None else "",
                "Mark Weight": weight_str,
            }
        )
    return out


def select_name_mark_ordered(assignment_data: List[Dict[str, Any]]) -> tuple[list[str], list[float]]:
    """Return (names, marks) ordered by original sequence using DuckDB.

    Useful for charts that previously used pandas DataFrame columns.
    """
    if not assignment_data:
        return [], []

    indexed = [dict(idx=i, **row) for i, row in enumerate(assignment_data)]
    con = duckdb.connect()
    con.register("input", pd.DataFrame(indexed))
    result = con.execute(
        """
        select name, cast(mark as double) as mark
        from input
        order by idx
        """
    ).fetchall()
    con.close()

    names = [r[0] for r in result]
    marks = [float(r[1]) for r in result]
    return names, marks


def build_assignment_breakdown_rows(assignment_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format assignment breakdown rows (name, mark, weight) via DuckDB.

    Returns list of dicts with string-formatted values for clean display.
    """
    if not assignment_data:
        return []

    con = duckdb.connect()
    con.register("input", pd.DataFrame(assignment_data))
    rows = con.execute(
        """
        select
            cast(name as varchar) as Assessment,
            case
                when mark is null then '' else printf('%.1f', cast(mark as double))
            end as Mark,
            case
                when weight is null or cast(weight as double) <= 0 then 'N/A'
                else printf('%.1f%%', cast(weight as double))
            end as Weight
        from input
        """
    ).fetchall()
    con.close()

    return [{"Assessment": assessment, "Mark": mark, "Weight": weight} for (assessment, mark, weight) in rows]
