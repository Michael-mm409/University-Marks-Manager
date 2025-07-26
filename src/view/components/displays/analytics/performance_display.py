"""Performance analysis and trends display components.

This module provides comprehensive performance analysis capabilities for the
University Marks Manager, including trend analysis, progress tracking, and
statistical performance metrics. It creates interactive visualizations and
provides actionable insights about academic performance patterns.

Key Features:
    - Progress tracking towards grade targets (HD/D/C/P)
    - Performance trend analysis with visual line charts
    - Comprehensive statistical metrics and distributions
    - Scale detection for different marking schemes
    - Personalized performance feedback and suggestions
    - Consistency analysis and improvement recommendations

The module automatically adapts to different marking scales and provides
context-aware analysis based on assignment characteristics and performance
patterns.

Example:
    >>> from controller.app_controller import AppController
    >>> controller = AppController()
    >>> display = PerformanceDisplay(controller)
    >>> display.render(analytics_data)
"""

from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from controller import AppController


class PerformanceDisplay:
    """Handles comprehensive performance analysis display and visualization.

    This class provides detailed performance analysis through multiple visualization
    types and statistical analysis. It automatically adapts to different marking
    scales and provides personalized feedback based on performance patterns.

    The class generates several analysis components:
        - Progress tracking towards academic grade targets
        - Performance trend visualization with line charts
        - Statistical metrics including averages and consistency
        - Grade distribution analysis with visual breakdowns
        - Personalized feedback and improvement suggestions

    Attributes:
        controller: Main application controller for data access

    Design Principles:
        - Adaptive scaling based on marking scheme detection
        - Context-aware feedback and suggestions
        - Clear visual hierarchy with consistent styling
        - Interactive elements for detailed exploration

    Example:
        >>> controller = AppController()
        >>> display = PerformanceDisplay(controller)
        >>> display.render(analytics_data)
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize performance display with application controller.

        Args:
            controller: Main application controller providing data access
        """
        self.controller: AppController = controller

    def render(self, analytics_data: Dict[str, Any]) -> None:
        """Render comprehensive performance analysis interface.

        Creates a complete performance analysis display with progress tracking,
        trend analysis, and detailed statistics. Uses responsive layout to
        present multiple analysis components effectively.

        Args:
            analytics_data: Complete analytics dataset containing:
                - performance_analytics: Progress and trend analysis data
                - assignment_analytics: Assignment-specific metrics and statistics

        Layout Structure:
            - Top row: Two-column layout with progress targets and trend analysis
            - Bottom section: Comprehensive performance statistics and feedback

        Features:
            - Progress bars towards grade targets (HD/D/C/P)
            - Interactive trend line charts
            - Statistical metrics with consistency analysis
            - Personalized performance feedback

        Example:
            >>> display.render(analytics_data)
        """
        performance_analytics: Dict[str, Any] = analytics_data["performance_analytics"]
        assignment_analytics: Dict[str, Any] = analytics_data["assignment_analytics"]

        # Two-column layout for main analysis components
        col1, col2 = st.columns(2)

        with col1:
            self._render_progress_targets(performance_analytics)

        with col2:
            self._render_trend_analysis(performance_analytics, assignment_analytics)

        # Comprehensive statistics section
        if assignment_analytics["has_data"]:
            self._render_performance_statistics(assignment_analytics)

    def _render_progress_targets(self, performance_analytics: Dict[str, Any]) -> None:
        """Render progress tracking towards academic grade targets.

        Displays visual progress bars showing advancement towards standard
        academic grade boundaries (Pass, Credit, Distinction, High Distinction).
        Adapts display based on whether total marks are available.

        Args:
            performance_analytics: Performance data containing target progress

        Features:
            - Color-coded progress bars for each grade target
            - Achievement indicators with emoji feedback
            - Percentage progress with descriptive status messages
            - Adaptive messaging based on achievement level

        Target Categories:
            - Pass (50%): Basic achievement threshold
            - Credit (65%): Good performance level
            - Distinction (75%): Strong performance level
            - High Distinction (85%): Excellent performance level

        Progress Status Types:
            - Achieved: Target reached (green success message)
            - Almost there: 80%+ progress (blue info message)
            - Needs work: <80% progress (yellow warning message)

        Example:
            >>> self._render_progress_targets(performance_data)
        """
        st.markdown("#### 🎯 Progress to Grade Targets")

        if performance_analytics["has_total_mark"]:
            progress_data: Dict[str, Dict[str, Any]] = performance_analytics["progress_to_targets"]

            for target_name, target_info in progress_data.items():
                emoji: str = target_info["emoji"]
                progress: float = target_info["progress_percent"]
                status: str = target_info["status"]

                # Display achievement status with appropriate styling
                if target_info["achieved"]:
                    st.success(f"{emoji} **{target_name}** - Achieved!")
                    st.progress(1.0, text=f"✅ {progress:.1f}%")
                elif status == "Almost there":
                    st.info(f"{emoji} **{target_name}** - {status}!")
                    st.progress(progress / 100, text=f"📈 {progress:.1f}%")
                else:
                    st.warning(f"{emoji} **{target_name}** - {status}")
                    st.progress(progress / 100, text=f"📉 {progress:.1f}%")
        else:
            st.info("📈 Set a total mark to see progress analysis")

    def _render_trend_analysis(
        self, performance_analytics: Dict[str, Any], assignment_analytics: Dict[str, Any]
    ) -> None:
        """Render performance trend analysis with interactive line chart.

        Creates a comprehensive trend analysis showing performance patterns
        over time. Includes visual line chart and descriptive trend analysis
        with actionable feedback about performance direction.

        Args:
            performance_analytics: Trend analysis data and calculations
            assignment_analytics: Assignment data for chart generation

        Features:
            - Interactive line chart showing assignment performance over time
            - Trend direction analysis (improving/declining/stable)
            - Quantitative change measurement between first and last assignments
            - Color-coded feedback based on trend direction

        Chart Components:
            - X-axis: Assignment sequence (A1, A2, A3, etc.)
            - Y-axis: Assignment marks/scores
            - Hover details: Full assignment names and marks

        Trend Categories:
            - Improving: >5 point increase (green success message)
            - Declining: >5 point decrease (yellow warning message)
            - Stable: ±5 point variation (blue info message)

        Example:
            >>> self._render_trend_analysis(performance_data, assignment_data)
        """
        st.markdown("#### 📈 Performance Trends")

        trend_data: Dict[str, Any] = performance_analytics["trend_analysis"]

        if not trend_data["has_trend"]:
            st.info("📄 Add more assignments to see performance trends")
            return

        if assignment_analytics["has_data"]:
            # Build interactive trend chart
            assignment_data: List[Dict[str, Any]] = assignment_analytics["assignment_data"]

            # Create chart data with abbreviated labels and full names for hover
            trend_chart_data: List[Dict[str, Any]] = []
            for i, assignment in enumerate(assignment_data):
                trend_chart_data.append(
                    {"Assignment": f"A{i + 1}", "Mark": assignment["mark"], "Full_Name": assignment["name"]}
                )

            if len(trend_chart_data) > 1:
                df_trend: pd.DataFrame = pd.DataFrame(trend_chart_data)

                # Create streamlined chart data
                chart_df: pd.DataFrame = df_trend[["Assignment", "Mark"]].copy()
                chart_df = chart_df.set_index("Assignment")

                st.line_chart(chart_df, height=300)

        # Display trend analysis with color-coded feedback
        trend_change: float = trend_data["trend_change"]
        direction: str = trend_data["trend_direction"]

        if direction == "improving":
            st.success(f"📈 **Improving trend!** +{trend_change:.1f} points")
        elif direction == "declining":
            st.warning(f"📉 **Declining trend.** -{abs(trend_change):.1f} points")
        else:
            st.info(f"📊 **Stable performance** (±{abs(trend_change):.1f} points)")

    def _render_performance_statistics(self, assignment_analytics: Dict[str, Any]) -> None:
        """Render comprehensive performance statistics and metrics.

        Displays detailed statistical analysis of assignment performance including
        basic metrics, grade distribution, and performance feedback. Provides
        both quantitative analysis and qualitative insights.

        Args:
            assignment_analytics: Assignment data containing performance metrics

        Statistics Components:
            - Basic metrics: Average, highest, lowest, standard deviation
            - Grade distribution: Count of assignments in each grade band
            - Performance feedback: Scale-aware analysis and suggestions

        Layout Structure:
            - Four-column metrics layout for basic statistics
            - Five-column grade distribution display
            - Comprehensive performance analysis section

        Example:
            >>> self._render_performance_statistics(assignment_data)
        """
        st.divider()
        st.markdown("#### 📊 Performance Statistics")

        metrics: Dict[str, float] = assignment_analytics["performance_metrics"]
        grade_dist: Dict[str, int] = assignment_analytics["grade_distribution"]

        # Basic performance metrics in responsive layout
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Average", f"{metrics['average']:.1f}")
        with col2:
            st.metric("Highest", f"{metrics['highest']:.1f}")
        with col3:
            st.metric("Lowest", f"{metrics['lowest']:.1f}")
        with col4:
            if metrics["std_dev"] > 0:
                st.metric(
                    "Std Dev", f"{metrics['std_dev']:.1f}", help="Lower values indicate more consistent performance"
                )
            else:
                st.metric("Std Dev", "N/A")

        # Grade distribution visualization
        st.markdown("**Grade Distribution:**")
        col1, col2, col3, col4, col5 = st.columns(5)

        grade_cols: List[Tuple[Any, str]] = [(col1, "HD"), (col2, "D"), (col3, "C"), (col4, "P"), (col5, "F")]

        for col, grade in grade_cols:
            with col:
                count: int = grade_dist[grade]
                delta_color: str = "inverse" if grade == "F" and count > 0 else "normal"
                st.metric(grade, count, delta_color=delta_color)

        # Detailed performance analysis
        self._render_performance_feedback(assignment_analytics, metrics)

    def _render_performance_feedback(self, assignment_analytics: Dict[str, Any], metrics: Dict[str, float]) -> None:
        """Render personalized performance feedback and improvement suggestions.

        Provides context-aware analysis based on detected marking scales and
        performance patterns. Offers specific feedback about grade achievements
        and consistency patterns with actionable improvement suggestions.

        Args:
            assignment_analytics: Assignment data with scale detection
            metrics: Calculated performance metrics including consistency

        Feedback Categories:
            - Scale detection: Automatic marking scheme identification
            - Grade achievement: Specific feedback about grade level performance
            - Consistency analysis: Performance stability assessment

        Scale Detection:
            - Small scale: ≤20 marks (provides percentage conversion)
            - Standard scale: 100-point marking (direct percentage analysis)

        Consistency Levels:
            - Very consistent: >90% consistency score
            - Reasonably consistent: 75-90% consistency
            - Variable: <75% consistency (improvement suggestions)

        Example:
            >>> self._render_performance_feedback(assignment_data, metrics_data)
        """
        st.markdown("**Performance Analysis:**")

        if assignment_analytics["is_small_scale"]:
            # Small-scale marking analysis (e.g., out of 15, 20 marks)
            max_mark: float = assignment_analytics["max_mark"]
            scale_factor: float = assignment_analytics["scale_factor"]
            avg_percentage: float = (metrics["average"] / max_mark) * 100 if max_mark > 0 else 0.0

            st.info(f"📊 **Scale Detection:** Marks appear to be out of ~{max_mark:.0f}")
            st.success(f"📊 **Average Performance:** {avg_percentage:.1f}% on detected scale")

            # Scale-aware grade feedback
            hd_count: int = assignment_analytics["grade_distribution"]["HD"]
            d_count: int = assignment_analytics["grade_distribution"]["D"]
            f_count: int = assignment_analytics["grade_distribution"]["F"]

            if hd_count > 0:
                st.success(f"🌟 {hd_count} assignment(s) at HD level ({85 * scale_factor:.1f}+")
            if d_count > 0:
                st.info(f"📈 {d_count} assignment(s) at Distinction level")
            if f_count > 0:
                st.warning(f"⚠️ {f_count} assignment(s) below pass level")
        else:
            # Standard 100-point scale analysis
            avg_mark: float = metrics["average"]
            st.info(f"📊 **Average Performance:** {avg_mark:.1f} points (assuming 100-point scale)")

            hd_count: int = assignment_analytics["grade_distribution"]["HD"]
            d_count: int = assignment_analytics["grade_distribution"]["D"]
            f_count: int = assignment_analytics["grade_distribution"]["F"]

            if f_count > 0:
                st.warning(f"⚠️ {f_count} assignment(s) below 50 (pass mark)")
            elif hd_count > 0:
                st.success(f"🌟 {hd_count} assignment(s) at HD level (85+)")
            elif d_count > 0:
                st.info(f"📈 {d_count} assignment(s) at Distinction level (75-84)")

        # Performance consistency analysis
        consistency: float = metrics.get("consistency", 0)
        if consistency > 90:
            st.success("🎯 **Very consistent** performance")
        elif consistency > 75:
            st.info("📊 **Reasonably consistent** performance")
        else:
            st.warning("📉 **Variable** performance - aim for consistency")
