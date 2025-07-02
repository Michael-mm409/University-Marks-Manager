# src/view/components/displays/summary_display.py
"""Summary display components for showing calculated data."""

from typing import Tuple

import streamlit as st

from controller import get_summary
from controller.app_controller import AppController
from model import Subject


class SummaryDisplay:
    """Handles summary information display logic."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render_subject_summary(self, subject_code: str, subject: Subject) -> None:
        """Render summary information for a specific subject."""
        total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = get_summary(subject)

        st.markdown(
            f"**Summary:**  "
            f"Total Weighted: `{total_weighted_mark:.2f}` &nbsp; | &nbsp; "
            f"Total Weight: `{total_weight:.0f}%` &nbsp; | &nbsp; "
            f"Exam Mark: `{exam_mark:.2f}` &nbsp; | &nbsp; "
            f"Exam Weight: `{exam_weight:.0f}%` &nbsp; | &nbsp; "
            f"Total Mark: `{total_mark:.0f}`"
        )

    def render_semester_summary(self) -> None:
        """Render overall semester summary."""
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.subheader("📊 Semester Overview")

        subjects = self.controller.semester_obj.subjects
        if not subjects:
            st.info("No subjects added yet.")
            return

        # Calculate semester-wide statistics
        total_subjects = len(subjects)
        subjects_with_marks = len([s for s in subjects.values() if s.total_mark > 0])

        if subjects_with_marks > 0:
            average_mark = sum(s.total_mark for s in subjects.values()) / subjects_with_marks
            highest_mark = max(s.total_mark for s in subjects.values())
            lowest_mark = min(s.total_mark for s in subjects.values() if s.total_mark > 0)
        else:
            average_mark = highest_mark = lowest_mark = 0

        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Subjects", total_subjects)
        with col2:
            st.metric("Average Mark", f"{average_mark:.1f}")
        with col3:
            st.metric("Highest Mark", f"{highest_mark:.1f}")
        with col4:
            st.metric("Lowest Mark", f"{lowest_mark:.1f}")

        # Grade distribution
        if subjects_with_marks > 0:
            grade_counts = {"HD (85+)": 0, "D (75-84)": 0, "C (65-74)": 0, "P (50-64)": 0, "F (<50)": 0}

            for subject in subjects.values():
                if subject.total_mark >= 85:
                    grade_counts["HD (85+)"] += 1
                elif subject.total_mark >= 75:
                    grade_counts["D (75-84)"] += 1
                elif subject.total_mark >= 65:
                    grade_counts["C (65-74)"] += 1
                elif subject.total_mark >= 50:
                    grade_counts["P (50-64)"] += 1
                else:
                    grade_counts["F (<50)"] += 1

            st.markdown("#### Grade Distribution")
            col1, col2 = st.columns([2, 1])

            with col1:
                # Filter out zero values for cleaner chart
                filtered_grades = {k: v for k, v in grade_counts.items() if v > 0}
                if filtered_grades:
                    st.bar_chart(filtered_grades)

            with col2:
                for grade, count in grade_counts.items():
                    if count > 0:
                        percentage = (count / subjects_with_marks) * 100
                        st.write(f"**{grade}:** {count} ({percentage:.1f}%)")

    def render_quick_stats(self, subject: Subject) -> Tuple[float, float, float, float, float]:
        """Render quick statistics and return calculated values."""
        total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = get_summary(subject)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Assignments Total", f"{total_weighted_mark:.1f}")
        with col2:
            st.metric("Assignment Weight", f"{total_weight:.0f}%")
        with col3:
            st.metric("Remaining Weight", f"{exam_weight:.0f}%")

        return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark
