# src/view/components/displays/summary_display.py
"""Summary display components for showing calculated academic data.

This module provides comprehensive summary views for both individual subjects
and semester-wide academic performance. It presents calculated statistics,
grade distributions, and performance metrics in an accessible format.

The module handles three main summary types:
    1. Subject Summary - Detailed breakdown of subject marks and weights
    2. Semester Summary - Overview of all subjects with grade distribution
    3. Quick Stats - Essential metrics for rapid assessment

Key Features:
    - Real-time calculation of academic metrics
    - Visual grade distribution charts and statistics
    - Responsive layout with metric cards and progress indicators
    - Error handling for incomplete or missing data
    - Professional formatting with clear visual hierarchy

Example:
    >>> from controller.app_controller import AppController
    >>> controller = AppController()
    >>> display = SummaryDisplay(controller)
    >>> display.render_subject_summary("CSCI251", subject)
"""

from typing import Dict, Tuple

import streamlit as st

from controller import get_summary
from controller.app_controller import AppController
from model import Subject


class SummaryDisplay:
    """Handles summary information display logic for academic data.

    This class provides comprehensive summary views for both individual subjects
    and semester-wide performance analysis. It integrates with the controller
    layer to retrieve calculated data and presents it in user-friendly formats.

    The class manages three distinct summary types:
        - Subject summaries: Detailed breakdown of individual subject performance
        - Semester summaries: Overview statistics across all subjects
        - Quick stats: Essential metrics for rapid performance assessment

    Attributes:
        controller: Main application controller for data access and calculations

    Design Principles:
        - Clear visual hierarchy with consistent styling
        - Responsive layout that adapts to different data sizes
        - Error handling for edge cases and missing data
        - Professional formatting with accessible color schemes

    Example:
        >>> controller = AppController()
        >>> summary = SummaryDisplay(controller)
        >>> summary.render_semester_summary()
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize summary display with application controller.

        Args:
            controller: Main application controller providing data access
        """
        self.controller: AppController = controller

    def render_subject_summary(self, subject_code: str, subject: Subject) -> None:
        """Render comprehensive summary information for a specific subject.

        Displays a detailed breakdown of subject performance including assignment
        totals, weights, exam marks, and calculated final mark. Uses compact
        inline formatting for space efficiency.

        Args:
            subject_code: Subject identifier for context (e.g., "CSCI251")
            subject: Subject entity containing assignment and exam data

        Display Components:
            - Total weighted mark from all assignments
            - Total weight percentage of completed assignments
            - Exam mark and weight (if exam is recorded)
            - Calculated total mark for the subject

        Format:
            Uses inline code styling with pipe separators for compact display:
            "Total Weighted: `45.2` | Total Weight: `60%` | Exam Mark: `42.0` | ..."

        Example:
            >>> display.render_subject_summary("CSCI251", subject_entity)
        """
        # Get calculated summary data from controller
        total_weighted_mark: float
        total_weight: float
        exam_mark: float
        exam_weight: float
        total_mark: float
        total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = get_summary(subject)

        # Display formatted summary with inline code styling
        st.markdown(
            f"**Summary:**  "
            f"Total Weighted: `{total_weighted_mark:.2f}` &nbsp; | &nbsp; "
            f"Total Weight: `{total_weight:.0f}%` &nbsp; | &nbsp; "
            f"Exam Mark: `{exam_mark:.2f}` &nbsp; | &nbsp; "
            f"Exam Weight: `{exam_weight:.0f}%` &nbsp; | &nbsp; "
            f"Total Mark: `{total_mark:.0f}`"
        )

    def render_semester_summary(self) -> None:
        """Render comprehensive semester-wide performance overview.

        Provides statistical analysis across all subjects in the current semester,
        including grade distribution visualization and performance metrics.
        Handles edge cases for empty semesters and subjects without marks.

        Display Structure:
            1. Summary metrics in 4-column layout
            2. Grade distribution chart and statistics
            3. Error handling for initialization issues

        Features:
            - Total subject count and completion statistics
            - Average, highest, and lowest mark calculations
            - Grade distribution with HD/D/C/P/F breakdown
            - Interactive bar chart for visual analysis
            - Percentage calculations for grade distribution

        Error Handling:
            - Validates semester initialization
            - Handles empty subject lists gracefully
            - Filters subjects without marks for accurate statistics

        Example:
            >>> display.render_semester_summary()
        """
        # Validate semester initialization
        if not self.controller.semester_obj:
            st.error("❌ Semester not initialized.")
            st.info("💡 Please load or create a semester to view summary statistics.")
            return

        st.subheader("📊 Semester Overview")

        subjects: Dict[str, Subject] = self.controller.semester_obj.subjects
        if not subjects:
            st.info("📋 No subjects added yet. Use the **Manage** tab to add subjects.")
            return

        # Calculate semester-wide statistics
        total_subjects: int = len(subjects)
        subjects_with_marks: int = len([s for s in subjects.values() if s.total_mark > 0])

        # Calculate performance metrics (only for subjects with marks)
        average_mark: float = 0.0
        highest_mark: float = 0.0
        lowest_mark: float = 0.0

        if subjects_with_marks > 0:
            marked_subjects = [s for s in subjects.values() if s.total_mark > 0]
            average_mark = sum(s.total_mark for s in marked_subjects) / subjects_with_marks
            highest_mark = max(s.total_mark for s in subjects.values())
            lowest_mark = min(s.total_mark for s in marked_subjects)

        # Display summary metrics in responsive columns
        total_subjects_column, average_mark_column, highest_mark_column, lowest_mark_column = st.columns(4)

        with total_subjects_column:
            completion_rate: float = (subjects_with_marks / total_subjects) * 100 if total_subjects > 0 else 0
            st.metric("Total Subjects", total_subjects, delta=f"{completion_rate:.0f}% marked")

        with average_mark_column:
            st.metric("Average Mark", f"{average_mark:.1f}")

        with highest_mark_column:
            st.metric("Highest Mark", f"{highest_mark:.1f}")

        with lowest_mark_column:
            st.metric("Lowest Mark", f"{lowest_mark:.1f}")

        # Grade distribution analysis
        if subjects_with_marks > 0:
            self._render_grade_distribution(subjects, subjects_with_marks)

    def _render_grade_distribution(self, subjects: Dict[str, Subject], subjects_with_marks: int) -> None:
        """Render grade distribution visualization and statistics.

        Creates an interactive grade distribution analysis with bar chart
        visualization and detailed percentage breakdowns. Filters out
        zero values for cleaner visual presentation.

        Args:
            subjects: Dictionary of all subjects in the semester
            subjects_with_marks: Count of subjects that have been marked

        Features:
            - HD/D/C/P/F grade classification
            - Interactive bar chart with filtered zero values
            - Percentage calculations for each grade band
            - Two-column layout: chart and statistics

        Grade Boundaries:
            - HD (High Distinction): 85+ marks
            - D (Distinction): 75-84 marks
            - C (Credit): 65-74 marks
            - P (Pass): 50-64 marks
            - F (Fail): <50 marks

        Example:
            >>> self._render_grade_distribution(subjects_dict, 5)
        """
        st.markdown("#### 📊 Grade Distribution")

        # Initialize grade counters with descriptive labels
        grade_counts: Dict[str, int] = {"HD (85+)": 0, "D (75-84)": 0, "C (65-74)": 0, "P (50-64)": 0, "F (<50)": 0}

        # Classify subjects into grade bands
        for subject in subjects.values():
            if subject.total_mark <= 0:  # Skip unmarked subjects
                continue

            mark: float = subject.total_mark
            if mark >= 85:
                grade_counts["HD (85+)"] += 1
            elif mark >= 75:
                grade_counts["D (75-84)"] += 1
            elif mark >= 65:
                grade_counts["C (65-74)"] += 1
            elif mark >= 50:
                grade_counts["P (50-64)"] += 1
            else:
                grade_counts["F (<50)"] += 1

        # Create responsive two-column layout
        grade_visualization_column, statistics_column = st.columns([2, 1])

        with grade_visualization_column:
            # Filter out zero values for cleaner chart visualization
            filtered_grades: Dict[str, int] = {k: v for k, v in grade_counts.items() if v > 0}

            if filtered_grades:
                st.bar_chart(filtered_grades)
            else:
                st.info("📊 No grade data available for visualization")

        with statistics_column:
            st.markdown("**Grade Breakdown:**")
            # Display statistics for all grades (including zeros for completeness)
            for grade, count in grade_counts.items():
                if count > 0:
                    percentage: float = (count / subjects_with_marks) * 100
                    st.write(f"**{grade}:** {count} ({percentage:.1f}%)")
                else:
                    st.write(f"{grade}: 0 (0.0%)")

    def render_quick_stats(self, subject: Subject) -> Tuple[float, float, float, float, float]:
        """Render essential subject metrics and return calculated values.

        Displays the most important metrics for rapid assessment of subject
        performance. Provides both visual display and programmatic access
        to calculated values for further processing.

        Args:
            subject: Subject entity containing assignment and exam data

        Returns:
            Tuple containing calculated summary values:
                - total_weighted_mark: Sum of all assignment marks
                - total_weight: Total percentage weight of assignments
                - exam_mark: Recorded exam mark (if available)
                - exam_weight: Exam weight percentage
                - total_mark: Calculated final subject mark

        Display Components:
            - Assignments Total: Sum of all assignment marks
            - Assignment Weight: Percentage of total grade from assignments
            - Remaining Weight: Available percentage for exam/future work

        Layout:
            Uses 3-column responsive layout with metric cards for
            clean presentation of key performance indicators.

        Example:
            >>> values = display.render_quick_stats(subject_entity)
            >>> total_weighted, total_weight, exam, exam_weight, total = values
            >>> print(f"Subject total: {total}")
        """
        # Get comprehensive summary data from controller
        summary_data: Tuple[float, float, float, float, float] = get_summary(subject)
        total_weighted_mark: float
        total_weight: float
        exam_mark: float
        exam_weight: float
        total_mark: float
        total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark = summary_data

        # Display key metrics in responsive 3-column layout
        assignments_total_column, assignment_weight_column, remaining_weight_column = st.columns(3)

        with assignments_total_column:
            st.metric("Assignments Total", f"{total_weighted_mark:.1f}", help="Sum of all assignment marks received")

        with assignment_weight_column:
            st.metric(
                "Assignment Weight", f"{total_weight:.0f}%", help="Percentage of final grade from completed assignments"
            )

        with remaining_weight_column:
            remaining_weight: float = 100.0 - total_weight
            st.metric(
                "Remaining Weight",
                f"{remaining_weight:.0f}%",
                help="Available percentage for exam or future assignments",
            )

        # Return values for programmatic use
        return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark
