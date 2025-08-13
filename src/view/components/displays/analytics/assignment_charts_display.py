"""Assignment visualization components.

This module provides comprehensive assignment analysis and visualization capabilities
for the University Marks Manager. It generates interactive charts, performance metrics,
and weight distribution analysis to help students understand their assignment performance.

The module uses Plotly for interactive visualizations and Streamlit for the interface,
providing responsive charts that adapt to different data sizes and label lengths.

Key Features:
    - Assignment performance bar charts with adaptive sizing
    - Weight distribution visualization (progress bars and pie charts)
    - Grade distribution analysis with HD/D/C/P/F breakdown
    - Performance metrics including averages and consistency
    - Smart chart formatting based on data characteristics

Example:
    >>> from controller.app_controller import AppController
    >>> controller = AppController()
    >>> charts = AssignmentChartsDisplay(controller)
    >>> charts.render(analytics_data)
"""

from typing import Any, Dict, List, Tuple

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from application.queries.summary_queries import select_name_mark_ordered
from controller import AppController


class AssignmentChartsDisplay:
    """Handles assignment charts and analysis visualization."""

    def __init__(self, controller: AppController) -> None:
        self.controller: AppController = controller

    def render(self, analytics_data: Dict[str, Any]) -> None:
        assignment_analytics: Dict[str, Any] = analytics_data["assignment_analytics"]

        if not assignment_analytics.get("has_data", False):
            st.info("📝 No assignments to display. Add assignments in the Manage tab.")
            return

        assignment_data: List[Dict[str, Any]] = assignment_analytics["assignment_data"]
        names, marks = select_name_mark_ordered(assignment_data)

        col1, col2 = st.columns(2)

        with col1:
            self._render_performance_chart(names, marks, assignment_analytics)

        with col2:
            self._render_weight_distribution(assignment_analytics, analytics_data["basic_metrics"])

    def _get_chart_height(self, names: List[str]) -> int:
        num_assignments: int = len(names)
        max_label_length: int = max((len(str(n)) for n in names), default=0)

        base_height: int = 500
        if max_label_length > 15 or num_assignments > 6:
            return base_height + 50
        elif max_label_length > 10 or num_assignments > 4:
            return base_height + 25
        else:
            return base_height

    def _get_tick_angle(self, names: List[str]) -> int:
        if len(names) == 0:
            return 0

        max_label_length: int = max((len(str(n)) for n in names), default=0)
        num_assignments: int = len(names)

        if max_label_length > 20 or num_assignments > 8:
            return 45
        elif max_label_length > 15 or num_assignments > 5:
            return 30
        elif max_label_length > 10 or num_assignments > 3:
            return 15
        else:
            return 0

    def _render_performance_chart(
        self, names: List[str], marks: List[float], assignment_analytics: Dict[str, Any]
    ) -> None:
        st.markdown("#### 📊 Assignment Performance")

        chart_height: int = self._get_chart_height(names)
        tick_angle: int = self._get_tick_angle(names)

        fig = go.Figure(
            data=[
                go.Bar(
                    x=names,
                    y=marks,
                    text=[f"{m:.1f}" for m in marks],
                    textposition="outside",
                    textfont=dict(size=11, family="Arial"),
                    marker=dict(color="steelblue", opacity=0.8, line=dict(color="navy", width=1)),
                    hovertemplate="<b>%{x}</b><br>Mark: %{y:.1f}<extra></extra>",
                    name="Assignment Marks",
                )
            ]
        )

        fig.update_layout(
            height=chart_height,
            title=dict(text="Assignment Performance", font=dict(size=16, family="Arial"), x=0.5),
            xaxis=dict(
                title=dict(text="Assignment", font=dict(size=12, family="Arial")),
                tickangle=tick_angle,
                tickfont=dict(size=12, family="Arial"),
                showgrid=False,
                automargin=True,
            ),
            yaxis=dict(
                title=dict(text="Mark", font=dict(size=12, family="Arial")),
                tickfont=dict(size=12, family="Arial"),
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128, 128, 128, 0.2)",
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=60, r=20, t=60, b=100),
            showlegend=False,
            font=dict(family="Arial", size=14),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", bordercolor="black"),
        )

        st.plotly_chart(fig, use_container_width=True)

        self._render_grade_reference(assignment_analytics)
        self._render_performance_summary(assignment_analytics)

    def _render_weight_chart(self, assignment_data: List[Dict[str, Any]]) -> None:
        """Render weight distribution as an interactive pie chart.

        Creates a donut chart showing the relative weights of assignments.
        Handles cases where assignments have no weight information gracefully.

        Args:
            assignment_data: List of assignment dictionaries containing:
                - name: Assignment name
                - weight: Assignment weight percentage

        Chart Features:
            - Donut chart design with center hole
            - Color-coded segments with Set3 palette
            - Interactive hover with percentage details
            - Truncated labels for long assignment names
            - Responsive legend positioning

        Example:
            >>> self._render_weight_chart(assignment_data)
        """
        # Filter assignments with weights
        weighted_assignments: List[Dict[str, Any]] = [a for a in assignment_data if a["weight"] > 0]

        if not weighted_assignments:
            st.info("No weight information available")
            return

        # Create pie chart data
        names: List[str] = [a["name"][:15] + "..." if len(a["name"]) > 15 else a["name"] for a in weighted_assignments]
        weights: List[float] = [a["weight"] for a in weighted_assignments]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=names,
                    values=weights,
                    hole=0.3,  # Donut chart
                    textinfo="label+percent",
                    textposition="auto",
                    hovertemplate="<b>%{label}</b><br>Weight: %{value}%<br>Percent: %{percent}<extra></extra>",
                    marker=dict(colors=px.colors.qualitative.Set3, line=dict(color="white", width=2)),
                )
            ]
        )

        fig.update_layout(
            height=350,
            title=dict(text="Weight Distribution", font=dict(size=16), x=0.5),
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10)),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_grade_reference(self, assignment_analytics: Dict[str, Any]) -> None:
        """Render grade reference guide for assignment performance.

        Displays a visual reference showing grade boundaries (HD/D/C/P) with
        explanation that grades are calculated per individual assignment.

        Args:
            assignment_analytics: Analytics data (used for context)

        Display Elements:
            - Color-coded grade indicators
            - Percentage thresholds for each grade
            - Explanation of individual assignment grading
            - Four-column layout for compact display
        """
        st.markdown("**Grade Reference:**")
        col_ref1, col_ref2, col_ref3, col_ref4 = st.columns(4)

        # Show that grades are calculated per assignment
        st.info("📊 **Grades calculated individually for each assignment based on its maximum mark**")

        references: List[Tuple[Any, str, str, int]] = [
            (col_ref1, "🟢", "HD", 85),
            (col_ref2, "🔵", "D", 75),
            (col_ref3, "🟡", "C", 65),
            (col_ref4, "🔴", "P", 50),
        ]

        for col, emoji, grade, threshold in references:
            with col:
                st.markdown(f"{emoji} {grade}: {threshold}%+")

    def _render_performance_summary(self, assignment_analytics: Dict[str, Any]) -> None:
        """Render comprehensive performance summary with metrics and grade distribution.

        Displays key performance metrics including averages, grade distribution,
        and scale information. Adapts display based on whether assignments use
        small-scale marking (≤20 marks) or percentage-based marking.

        Args:
            assignment_analytics: Analytics data containing:
                - performance_metrics: Statistical metrics (average, etc.)
                - grade_distribution: Count of assignments in each grade band
                - is_small_scale: Whether assignments use small-scale marking
                - max_mark: Maximum mark for scale reference

        Display Components:
            - Average mark and percentage metrics
            - Scale information for small-scale assignments
            - Grade distribution breakdown (HD/D/C/P/F counts)
            - Color-coded metrics with delta indicators

        Example:
            >>> self._render_performance_summary(analytics_data)
        """
        metrics: Dict[str, float] = assignment_analytics["performance_metrics"]
        grade_dist: Dict[str, int] = assignment_analytics["grade_distribution"]

        st.markdown("**Performance Summary:**")

        # Use smaller metrics layout
        col_avg, col_pct = st.columns(2)
        with col_avg:
            st.metric("Average", f"{metrics['average']:.1f}")

        if assignment_analytics["is_small_scale"]:
            max_mark: float = assignment_analytics["max_mark"]
            if max_mark == 0:
                avg_percentage: float = 0.0
            else:
                avg_percentage: float = (metrics["average"] / max_mark) * 100
            with col_pct:
                st.metric("Average %", f"{avg_percentage:.1f}%")
            st.info(f"📊 **Scale:** ~{max_mark:.0f} marks")

        # Compact grade distribution
        st.markdown("**Grade Distribution:**")
        col1, col2, col3, col4, col5 = st.columns(5)

        grade_cols: List[Tuple[Any, str]] = [(col1, "HD"), (col2, "D"), (col3, "C"), (col4, "P"), (col5, "F")]

        for col, grade in grade_cols:
            with col:
                count: int = grade_dist[grade]
                delta_color: str = "inverse" if grade == "F" and count > 0 else "normal"
                st.metric(grade, count, delta_color=delta_color)

    def _render_weight_distribution(self, assignment_analytics: Dict[str, Any], basic_metrics: Dict[str, Any]) -> None:
        """Render weight distribution analysis with progress bars and summary.

        Displays assignment weight distribution using progress bars, weight
        summary metrics, and validation indicators. Provides clear visual
        feedback about weight allocation and remaining capacity.

        Args:
            assignment_analytics: Assignment data containing weight information
            basic_metrics: Summary metrics including:
                - weight_total: Total allocated weight percentage
                - remaining_weight: Remaining weight capacity

        Display Components:
            - Individual assignment weight progress bars
            - Total and remaining weight metrics
            - Weight validation with color-coded feedback
            - Truncated assignment names for compact display

        Validation Logic:
            - Error: Weight exceeds 100%
            - Warning: More than 50% remaining weight
            - Success: Good distribution (0-50% remaining)

        Example:
            >>> self._render_weight_distribution(assignment_analytics, basic_metrics)
        """
        st.markdown("#### ⚖️ Weight Distribution")

        assignment_data: List[Dict[str, Any]] = assignment_analytics["assignment_data"]

        # Progress bars for individual assignments
        for assignment in assignment_data:
            if assignment["weight"] > 0:
                weight_percent: float = assignment["weight"] / 100
                name: str = assignment["name"][:15] + ("..." if len(assignment["name"]) > 15 else "")
                st.write(f"**{name}**")
                st.progress(weight_percent, text=f"{assignment['weight']:.1f}%")

        # Weight summary
        st.divider()
        col_w1, col_w2 = st.columns(2)

        with col_w1:
            st.metric("Total", f"{basic_metrics['weight_total']:.1f}%")
        with col_w2:
            st.metric("Remaining", f"{basic_metrics['remaining_weight']:.1f}%")

        # Validation with color-coded feedback
        remaining: float = basic_metrics["remaining_weight"]
        if remaining < 0:
            st.error("⚠️ Weight exceeds 100%!")
        elif remaining > 50:
            st.warning(f"⚠️ {remaining:.1f}% remaining")
        else:
            st.success("✅ Good distribution")
