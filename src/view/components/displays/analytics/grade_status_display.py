"""Grade status and overview components."""

from typing import Any, Dict, Optional, Tuple

import pandas as pd
import streamlit as st

from controller.app_controller import AppController


class GradeStatusDisplay:
    """Handles grade status display logic."""

    def __init__(self, controller: AppController) -> None:
        self.controller: AppController = controller

    def render_overview(self, analytics_data: Dict[str, Any]) -> None:
        """Render the main grade status section."""
        st.subheader(f"📊 {analytics_data['subject_code']} - Grade Status")

        basic_metrics: Dict[str, Any] = analytics_data["basic_metrics"]
        grade_status: Dict[str, Any] = analytics_data["grade_status"]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_mark: Optional[float] = basic_metrics["total_mark"]
            st.metric("Total Mark", f"{total_mark:.1f}" if total_mark is not None else "Not set")

        with col2:
            exam_mark: Optional[float] = basic_metrics["exam_mark"]
            st.metric("Exam Mark", f"{exam_mark:.1f}" if exam_mark is not None else "Not set")

        with col3:
            assignment_total: float = basic_metrics["assignment_total"]
            st.metric("Assignment Total", f"{assignment_total:.1f}")

        with col4:
            grade_level: str = grade_status["grade_level"]
            emoji: str = grade_status["emoji"]
            st.metric("Grade", grade_level, delta=emoji)

        # Progress bar
        grade_value: float = grade_status["grade_value"]
        if grade_value > 0:
            progress_percent: float = grade_status["progress_percent"]
            grade_source: str = grade_status["grade_source"]
            st.progress(
                progress_percent,
                text=f"Grade: {grade_value:.2f} marks (from {grade_source})",
            )

    def render_assignment_breakdown(self, analytics_data: Dict[str, Any]) -> None:
        """Render assignment breakdown table."""
        st.subheader("📋 Assignment Breakdown")

        assignment_analytics: Dict[str, Any] = analytics_data["assignment_analytics"]
        basic_metrics: Dict[str, Any] = analytics_data["basic_metrics"]

        if not assignment_analytics["has_data"]:
            st.info("📝 No assignments added yet. Use the **Manage** tab to add assignments.")
            return

        # Display assignment table
        assignment_data: list[Dict[str, Any]] = assignment_analytics["assignment_data"]

        df_data: list[Dict[str, str]] = []
        for assignment in assignment_data:
            assignment_name: str = assignment["name"]
            assignment_mark: float = assignment["mark"]
            assignment_weight: float = assignment["weight"]

            df_data.append(
                {
                    "Assessment": assignment_name,
                    "Mark": f"{assignment_mark:.1f}",
                    "Weight": f"{assignment_weight:.1f}%" if assignment_weight > 0 else "N/A",
                }
            )

        df: pd.DataFrame = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            assignment_total: float = basic_metrics["assignment_total"]
            st.metric("Assignment Total", f"{assignment_total:.1f}")
        with col2:
            weight_total: float = basic_metrics["weight_total"]
            st.metric("Weight Total", f"{weight_total:.1f}%")
        with col3:
            remaining_weight: float = basic_metrics["remaining_weight"]
            st.metric("Remaining Weight", f"{remaining_weight:.1f}%")

    def render_grade_charts(self, analytics_data: Dict[str, Any]) -> None:
        """Render grade overview charts."""
        col1, col2 = st.columns(2)

        grade_status: Dict[str, Any] = analytics_data["grade_status"]
        basic_metrics: Dict[str, Any] = analytics_data["basic_metrics"]

        with col1:
            self._render_current_grade_status(grade_status)

        with col2:
            self._render_mark_distribution(basic_metrics)

    def _render_current_grade_status(self, grade_status: Dict[str, Any]) -> None:
        """Render current grade status with intelligent calculation."""
        st.markdown("#### 🎯 Current Grade Status")

        grade_value: float = grade_status["grade_value"]
        has_total_mark: bool = grade_status["has_total_mark"]

        # Check if there are any marks at all (assignments or total)
        if grade_value <= 0:
            self._show_no_data_status()
            return

        if has_total_mark:
            self._show_final_grade_status(grade_status)
        else:
            self._show_assignment_grade_status(grade_status)

        # Progress bar
        progress_percent: float = grade_status["progress_percent"]
        grade_source: str = grade_status["grade_source"]
        st.progress(
            progress_percent,
            text=f"Current Grade: {grade_value:.1f}% (from {grade_source})",
        )

        # Grade boundaries
        self._show_grade_boundaries(grade_value)

    def _show_final_grade_status(self, grade_status: Dict[str, Any]) -> None:
        """Show final grade status message."""
        grade_value: float = grade_status["grade_value"]
        grade_level: str = grade_status["grade_level"]

        # If grade value is 0, it means no marks have been assigned yet
        if grade_value == 0:
            st.info("📋 **No final grade available** - Total mark not set or is zero")
            return

        status_messages: Dict[str, Tuple[str, str]] = {
            "High Distinction": ("🎉", "Excellent work!"),
            "Distinction": ("🌟", "Great performance!"),
            "Credit": ("✅", "Good work!"),
            "Pass": ("📈", "Well done!"),
            "Fail": ("⚠️", "Keep working!"),
        }

        emoji: str
        message: str
        emoji, message = status_messages.get(grade_level, ("⭕", "Unknown status"))
        st.success(f"{emoji} **{grade_level}** - {message}")

    def _show_assignment_grade_status(self, grade_status: Dict[str, Any]) -> None:
        """Show assignment-based grade status message."""
        grade_value: float = grade_status["grade_value"]

        # If grade value is 0, it means no assignments have been marked yet
        if grade_value == 0:
            st.info("📋 **No assignment grades available** - No assignments marked yet")
            return

        st.info("📊 **Assignment-based grade** (Total mark not set)")

        if grade_value >= 85:
            st.success("🎉 **Excellent assignment performance!** - On track for HD")
        elif grade_value >= 75:
            st.success("🌟 **Strong assignment performance!** - On track for Distinction")
        elif grade_value >= 65:
            st.info("✅ **Good assignment performance!** - On track for Credit")
        elif grade_value >= 50:
            st.info("📈 **Solid assignment performance!** - On track for Pass")
        else:
            st.warning("⚠️ **Assignment performance needs improvement** - Consider extra study")

    def _show_grade_boundaries(self, grade_value: float) -> None:
        """Show grade boundaries with highlighting."""
        st.markdown("**Grade Boundaries:**")
        col_hd, col_d, col_c, col_p = st.columns(4)

        boundaries: list[Tuple[Any, str, int]] = [
            (col_hd, "HD", 85),
            (col_d, "D", 75),
            (col_c, "C", 65),
            (col_p, "P", 50),
        ]

        for col, grade, threshold in boundaries:
            with col:
                if grade_value >= threshold:
                    st.markdown(f"🟢 **{grade}** ({threshold}+")
                else:
                    st.markdown(f"⚪ {grade} ({threshold}+)")

    def _show_no_data_status(self) -> None:
        """Show status when no data is available."""
        st.info("📋 **No grade data available**")
        st.info("Add assignment marks or set a total mark to see your grade status")
        st.progress(0.0, text="No data available")

        # Show empty grade boundaries
        st.markdown("**Grade Boundaries:**")
        col_hd, col_d, col_c, col_p = st.columns(4)
        with col_hd:
            st.markdown("⚪ HD (85+)")
        with col_d:
            st.markdown("⚪ D (75+)")
        with col_c:
            st.markdown("⚪ C (65+)")
        with col_p:
            st.markdown("⚪ P (50+)")

    def _render_mark_distribution(self, basic_metrics: Dict[str, Any]) -> None:
        """Render mark distribution visualization."""
        st.markdown("#### 📊 Mark Distribution")

        assignment_total: float = basic_metrics["assignment_total"]
        exam_mark: Optional[float] = basic_metrics["exam_mark"]

        if assignment_total > 0 or (exam_mark and exam_mark > 0):
            # Calculate total marks and percentages
            exam_mark_value: float = exam_mark if exam_mark else 0
            total_marks: float = assignment_total + exam_mark_value

            if total_marks > 0:
                assignment_percent: float = (assignment_total / total_marks) * 100
                exam_percent: float = (exam_mark_value / total_marks) * 100

                # Show assignment contribution
                if assignment_total > 0:
                    st.metric("📝 Assignments", f"{assignment_total:.1f}", delta="Current total")
                    st.progress(assignment_percent / 100, text=f"Assignment Contribution: {assignment_percent:.1f}%")

                # Show exam if exists
                if exam_mark and exam_mark > 0:
                    st.metric("📝 Exam", f"{exam_mark:.1f}", delta=f"{exam_percent:.1f}% of total")
                    st.progress(exam_percent / 100, text=f"Exam Contribution: {exam_percent:.1f}%")

                # Show totals for verification
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Marks", f"{total_marks:.1f}")
                with col2:
                    coverage: float = assignment_percent + exam_percent
                    st.metric("Coverage", f"{coverage:.0f}%")

            else:
                st.info("📊 No marks available to calculate distribution")
        else:
            st.info("📊 Add assignments or exam marks to see distribution")
