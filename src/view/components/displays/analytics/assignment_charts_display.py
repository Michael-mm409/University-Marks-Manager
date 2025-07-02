"""Assignment visualization components."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from controller.app_controller import AppController


class AssignmentChartsDisplay:
    """Handles assignment charts and analysis."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self, analytics_data: dict) -> None:
        """Render assignment charts and analysis."""
        assignment_analytics = analytics_data["assignment_analytics"]

        if not assignment_analytics["has_data"]:
            st.info("📝 No assignments to display. Add assignments in the Manage tab.")
            return

        # Create charts using the processed data
        assignment_data = assignment_analytics["assignment_data"]
        df = pd.DataFrame(assignment_data)

        col1, col2 = st.columns(2)

        with col1:
            self._render_performance_chart(df, assignment_analytics)

        with col2:
            self._render_weight_distribution(assignment_analytics, analytics_data["basic_metrics"])

    def _get_chart_height(self, df: pd.DataFrame) -> int:
        """Calculate optimal chart height based on data."""
        num_assignments = len(df)
        max_label_length = max(len(str(name)) for name in df["name"]) if len(df) > 0 else 0

        # Base height
        base_height = 500

        # Add height for long labels or many assignments
        if max_label_length > 15 or num_assignments > 6:
            return base_height + 50
        elif max_label_length > 10 or num_assignments > 4:
            return base_height + 25
        else:
            return base_height

    def _get_tick_angle(self, df: pd.DataFrame) -> int:
        """Determine optimal tick angle based on label lengths."""
        if len(df) == 0:
            return 0

        max_label_length = max(len(str(name)) for name in df["name"])
        num_assignments = len(df)

        # Smart angle calculation
        if max_label_length > 20 or num_assignments > 8:
            return 45
        elif max_label_length > 15 or num_assignments > 5:
            return 30
        elif max_label_length > 10 or num_assignments > 3:
            return 15
        else:
            return 0

    def _render_performance_chart(self, df: pd.DataFrame, assignment_analytics: dict) -> None:
        """Render assignment performance chart using Plotly."""
        st.markdown("#### 📊 Assignment Performance")

        # Calculate optimal settings
        chart_height = self._get_chart_height(df)
        tick_angle = self._get_tick_angle(df)

        # Create Plotly bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df["name"],
                    y=df["mark"],
                    text=df["mark"].round(1),
                    textposition="outside",
                    textfont=dict(size=11, family="Arial"),
                    marker=dict(color="steelblue", opacity=0.8, line=dict(color="navy", width=1)),
                    hovertemplate="<b>%{x}</b><br>Mark: %{y:.1f}<extra></extra>",
                    name="Assignment Marks",
                )
            ]
        )

        # Update layout for better appearance - FIXED VERSION
        fig.update_layout(
            height=chart_height,
            title=dict(text="Assignment Performance", font=dict(size=16, family="Arial"), x=0.5),
            xaxis=dict(
                title=dict(text="Assignment", font=dict(size=12, family="Arial")),
                tickangle=tick_angle,
                tickfont=dict(size=12, family="Arial"),
                showgrid=False,
                automargin=True,  # Auto-adjust margins for long labels
            ),
            yaxis=dict(
                title=dict(text="Mark", font=dict(size=12, family="Arial")),
                tickfont=dict(size=12, family="Arial"),
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128, 128, 128, 0.2)",
            ),
            # MOVED THESE PROPERTIES TO LAYOUT LEVEL:
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper background
            margin=dict(l=60, r=20, t=60, b=100),  # Increased bottom margin for angled labels
            showlegend=False,
            font=dict(family="Arial", size=14),  # Global font setting
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial", bordercolor="black"),
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Grade reference and performance summary
        self._render_grade_reference(assignment_analytics)
        self._render_performance_summary(assignment_analytics)

    def _render_weight_chart(self, assignment_data: list) -> None:
        """Render weight distribution as a pie chart."""
        # Filter assignments with weights
        weighted_assignments = [a for a in assignment_data if a["weight"] > 0]

        if not weighted_assignments:
            st.info("No weight information available")
            return

        # Create pie chart data
        names = [a["name"][:15] + "..." if len(a["name"]) > 15 else a["name"] for a in weighted_assignments]
        weights = [a["weight"] for a in weighted_assignments]

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

    def _render_grade_reference(self, assignment_analytics: dict) -> None:
        """Render grade reference based on individual assignment calculations."""
        st.markdown("**Grade Reference:**")
        col_ref1, col_ref2, col_ref3, col_ref4 = st.columns(4)

        # Show that grades are calculated per assignment
        st.info("📊 **Grades calculated individually for each assignment based on its maximum mark**")

        references = [
            (col_ref1, "🟢", "HD", 85),
            (col_ref2, "🔵", "D", 75),
            (col_ref3, "🟠", "C", 65),
            (col_ref4, "🔴", "P", 50),
        ]

        for col, emoji, grade, threshold in references:
            with col:
                st.markdown(f"{emoji} {grade}: {threshold}%+")

    def _render_performance_summary(self, assignment_analytics: dict) -> None:
        """Render performance summary."""
        metrics = assignment_analytics["performance_metrics"]
        grade_dist = assignment_analytics["grade_distribution"]  # Now this should be correct!

        st.markdown("**Performance Summary:**")

        # Use smaller metrics layout
        col_avg, col_pct = st.columns(2)
        with col_avg:
            st.metric("Average", f"{metrics['average']:.1f}")

        if assignment_analytics["is_small_scale"]:
            max_mark = assignment_analytics["max_mark"]
            avg_percentage = (metrics["average"] / max_mark) * 100
            with col_pct:
                st.metric("Average %", f"{avg_percentage:.1f}%")
            st.info(f"📊 **Scale:** ~{max_mark:.0f} marks")

        # Compact grade distribution - now using the corrected data
        st.markdown("**Grade Distribution:**")
        col1, col2, col3, col4, col5 = st.columns(5)

        grade_cols = [(col1, "HD"), (col2, "D"), (col3, "C"), (col4, "P"), (col5, "F")]
        for col, grade in grade_cols:
            with col:
                count = grade_dist[grade]  # This now comes from the corrected calculation
                delta_color = "inverse" if grade == "F" and count > 0 else "normal"
                st.metric(grade, count, delta_color=delta_color)

    def _render_weight_distribution(self, assignment_analytics: dict, basic_metrics: dict) -> None:
        """Render weight distribution analysis."""
        st.markdown("#### ⚖️ Weight Distribution")

        assignment_data = assignment_analytics["assignment_data"]

        # Option 1: Progress bars (current approach)
        for assignment in assignment_data:
            if assignment["weight"] > 0:
                weight_percent = assignment["weight"] / 100
                name = assignment["name"][:15] + ("..." if len(assignment["name"]) > 15 else "")
                st.write(f"**{name}**")
                st.progress(weight_percent, text=f"{assignment['weight']:.1f}%")

        # Option 2: Plotly pie chart (alternative - uncomment to use)
        # self._render_weight_chart(assignment_data)

        # Weight summary
        st.divider()
        col_w1, col_w2 = st.columns(2)

        with col_w1:
            st.metric("Total", f"{basic_metrics['weight_total']:.1f}%")
        with col_w2:
            st.metric("Remaining", f"{basic_metrics['remaining_weight']:.1f}%")

        # Validation
        remaining = basic_metrics["remaining_weight"]
        if remaining < 0:
            st.error("⚠️ Weight exceeds 100%!")
        elif remaining > 50:
            st.warning(f"⚠️ {remaining:.1f}% remaining")
        else:
            st.success("✅ Good distribution")
