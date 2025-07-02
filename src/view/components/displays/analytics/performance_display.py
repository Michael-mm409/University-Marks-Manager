"""Performance analysis and trends display."""

import pandas as pd
import streamlit as st

from controller.app_controller import AppController


class PerformanceDisplay:
    """Handles performance analysis display."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self, analytics_data: dict) -> None:
        """Render performance analysis charts."""
        performance_analytics = analytics_data["performance_analytics"]
        assignment_analytics = analytics_data["assignment_analytics"]

        col1, col2 = st.columns(2)

        with col1:
            self._render_progress_targets(performance_analytics)

        with col2:
            self._render_trend_analysis(performance_analytics, assignment_analytics)

        # Summary statistics section
        if assignment_analytics["has_data"]:
            self._render_performance_statistics(assignment_analytics)

    def _render_progress_targets(self, performance_analytics: dict) -> None:
        """Render progress to grade targets."""
        st.markdown("#### 🎯 Progress to Grade Targets")

        if performance_analytics["has_total_mark"]:
            progress_data = performance_analytics["progress_to_targets"]

            for target_name, target_info in progress_data.items():
                emoji = target_info["emoji"]
                progress = target_info["progress_percent"]
                status = target_info["status"]

                if target_info["achieved"]:
                    st.success(f"{emoji} **{target_name}** - Achieved!")
                    st.progress(1.0, text=f"✅ {progress:.1f}%")
                elif status == "Almost there":
                    st.info(f"{emoji} **{target_name}** - {status}!")
                    st.progress(progress / 100, text=f"📈 {progress:.1f}%")
                else:
                    st.warning(f"{emoji} **{target_name}** - {status}")
                    st.progress(progress / 100, text=f"📊 {progress:.1f}%")
        else:
            st.info("📋 Set a total mark to see progress analysis")

    def _render_trend_analysis(self, performance_analytics: dict, assignment_analytics: dict) -> None:
        """Render performance trends."""
        st.markdown("#### 📈 Performance Trends")

        trend_data = performance_analytics["trend_analysis"]

        if not trend_data["has_trend"]:
            st.info("📝 Add more assignments to see performance trends")
            return

        if assignment_analytics["has_data"]:
            # Create trend chart
            assignment_data = assignment_analytics["assignment_data"]

            # Build trend data for chart
            trend_chart_data = []
            for i, assignment in enumerate(assignment_data):
                trend_chart_data.append(
                    {"Assignment": f"A{i + 1}", "Mark": assignment["mark"], "Full_Name": assignment["name"]}
                )

            if len(trend_chart_data) > 1:
                df_trend = pd.DataFrame(trend_chart_data)

                # Create line chart
                chart_df = df_trend[["Assignment", "Mark"]].copy()
                chart_df = chart_df.set_index("Assignment")

                st.line_chart(chart_df, height=300)

        # Show trend analysis
        trend_change = trend_data["trend_change"]
        direction = trend_data["trend_direction"]

        if direction == "improving":
            st.success(f"📈 **Improving trend!** +{trend_change:.1f} points")
        elif direction == "declining":
            st.warning(f"📉 **Declining trend.** -{abs(trend_change):.1f} points")
        else:
            st.info(f"📊 **Stable performance** (±{abs(trend_change):.1f} points)")

    def _render_performance_statistics(self, assignment_analytics: dict) -> None:
        """Render detailed performance statistics."""
        st.divider()
        st.markdown("#### 📊 Performance Statistics")

        metrics = assignment_analytics["performance_metrics"]
        grade_dist = assignment_analytics["grade_distribution"]

        # Basic metrics
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

        # Grade distribution
        st.markdown("**Grade Distribution:**")
        col1, col2, col3, col4, col5 = st.columns(5)

        grade_cols = [(col1, "HD"), (col2, "D"), (col3, "C"), (col4, "P"), (col5, "F")]
        for col, grade in grade_cols:
            with col:
                count = grade_dist[grade]
                delta_color = "inverse" if grade == "F" and count > 0 else "normal"
                st.metric(grade, count, delta_color=delta_color)

        # Performance feedback
        self._render_performance_feedback(assignment_analytics, metrics)

    def _render_performance_feedback(self, assignment_analytics: dict, metrics: dict) -> None:
        """Render performance feedback and suggestions."""
        st.markdown("**Performance Analysis:**")

        if assignment_analytics["is_small_scale"]:
            max_mark = assignment_analytics["max_mark"]
            scale_factor = assignment_analytics["scale_factor"]
            avg_percentage = (metrics["average"] / max_mark) * 100

            st.info(f"📊 **Scale Detection:** Marks appear to be out of ~{max_mark:.0f}")
            st.success(f"📊 **Average Performance:** {avg_percentage:.1f}% on detected scale")

            # Performance feedback based on scaled results
            hd_count = assignment_analytics["grade_distribution"]["HD"]
            d_count = assignment_analytics["grade_distribution"]["D"]
            f_count = assignment_analytics["grade_distribution"]["F"]

            if hd_count > 0:
                st.success(f"🌟 {hd_count} assignment(s) at HD level ({85 * scale_factor:.1f}+)")
            if d_count > 0:
                st.info(f"📈 {d_count} assignment(s) at Distinction level")
            if f_count > 0:
                st.warning(f"⚠️ {f_count} assignment(s) below pass level")
        else:
            # Standard scale feedback
            avg_mark = metrics["average"]
            st.info(f"📊 **Average Performance:** {avg_mark:.1f} points (assuming 100-point scale)")

            hd_count = assignment_analytics["grade_distribution"]["HD"]
            d_count = assignment_analytics["grade_distribution"]["D"]
            f_count = assignment_analytics["grade_distribution"]["F"]

            if f_count > 0:
                st.warning(f"⚠️ {f_count} assignment(s) below 50 (pass mark)")
            elif hd_count > 0:
                st.success(f"🌟 {hd_count} assignment(s) at HD level (85+)")
            elif d_count > 0:
                st.info(f"📈 {d_count} assignment(s) at Distinction level (75-84)")

        # Consistency feedback
        consistency = metrics.get("consistency", 0)
        if consistency > 90:
            st.success("🎯 **Very consistent** performance")
        elif consistency > 75:
            st.info("📊 **Reasonably consistent** performance")
        else:
            st.warning("📈 **Variable** performance - aim for consistency")
