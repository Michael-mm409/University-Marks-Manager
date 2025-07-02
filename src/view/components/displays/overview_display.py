"""Overview tab display components."""

from typing import List, Union

import pandas as pd
import streamlit as st

from controller import get_all_subjects, get_summary
from controller.app_controller import AppController
from model import Subject


class OverviewDisplay:
    """Handles overview tab display logic."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        """Render overview tab with subject tables."""
        if not self.controller.semester_obj or not self.controller.data_persistence:
            st.error("Controller not properly initialized.")
            return

        subjects = get_all_subjects(self.controller.semester_obj, self.controller.data_persistence)

        for subject_code in sorted(subjects.keys()):
            self._render_subject_table(subject_code, subjects[subject_code])

    def _render_subject_table(self, subject_code: str, subject: Subject) -> None:
        """Render individual subject table."""
        # Add null check before accessing semester_obj attributes
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.subheader(
            f"{subject.subject_name} ({subject_code})"
            f"{' - Synced' if getattr(subject, 'sync_subject', False) else ''} "
            f"in {self.controller.semester_obj.name} {self.controller.semester_obj.year}"
        )

        # Create assignment rows
        rows: List[List[Union[str, float, None]]] = []
        for assignment in subject.assignments:
            rows.append(
                [
                    assignment.subject_assessment,
                    assignment.unweighted_mark,
                    assignment.weighted_mark,
                    assignment.mark_weight,
                ]
            )

        df = pd.DataFrame(
            rows,
            columns=["Assessment", "Unweighted Mark", "Weighted Mark", "Mark Weight"],
        ).astype(str)

        st.dataframe(df.reset_index(drop=True), use_container_width=True, key=f"summary_editor_{subject_code}")

        # Summary
        total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = get_summary(subject)
        st.markdown(
            f"**Summary:**  "
            f"Total Weighted: `{total_weighted_mark:.2f}` &nbsp; | &nbsp; "
            f"Total Weight: `{total_weight:.0f}%` &nbsp; | &nbsp; "
            f"Exam Mark: `{exam_mark:.2f}` &nbsp; | &nbsp; "
            f"Exam Weight: `{exam_weight:.0f}%` &nbsp; | &nbsp; "
            f"Total Mark: `{total_mark:.0f}`"
        )
        st.markdown("---")
