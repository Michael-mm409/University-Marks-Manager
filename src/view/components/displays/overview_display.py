"""Overview tab display components."""

import streamlit as st

from application.queries.summary_queries import build_assignment_table_rows
from controller import AppController, get_all_subjects, get_summary
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
        # Add null check before accessing semester_obj Args
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.subheader(
            f"{subject.subject_name} ({subject_code})"
            f"{' - Synced' if getattr(subject, 'sync_subject', False) else ''} "
            f"in {self.controller.semester_obj.name} {self.controller.semester_obj.year}"
        )

        # Build rows via DuckDB helper (list of dicts) and display directly
        rows = build_assignment_table_rows(subject)
        st.dataframe(rows, use_container_width=True, hide_index=True, key=f"summary_editor_{subject_code}")

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
