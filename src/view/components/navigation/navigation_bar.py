"""Navigation bar component.

Provides year, semester, and subject selection controls. Includes semester
initialization UI when a year has no configured semesters.
"""

import streamlit as st

from controller import AppController


class NavigationBar:
    """Handles navigation controls (year, semester, subject)."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        year_col, sem_col, subj_col = st.columns(3)
        with year_col:
            self._render_year_selector()
        with sem_col:
            self._render_semester_selector()
        with subj_col:
            self._render_subject_selector()

    def _render_year_selector(self) -> None:
        selected_year = st.selectbox(
            "Select Year",
            options=self.controller.available_years,
            index=self.controller.available_years.index(self.controller.current_year),
            key="year_select",
        )
        if self.controller.year != selected_year:
            self.controller.set_year(selected_year)
        semesters = self.controller.available_semesters
        needs_init = (not semesters) or (len(semesters) == 1 and semesters[0] == "Semester 1")
        if needs_init:
            with st.expander("Initialize Semesters", expanded=True):
                st.caption("Choose preset or enter custom comma-separated list.")
                presets = {
                    "Autumn/Spring/Summer": ["Autumn", "Spring", "Summer"],
                    "Autumn/Spring/Annual": ["Autumn", "Spring", "Annual"],
                    "Autumn & Spring": ["Autumn", "Spring"],
                    "Session 1 & 2": ["Session 1", "Session 2"],
                    "Annual Only": ["Annual"],
                }
                preset_choice = st.selectbox("Preset", options=list(presets.keys()), key="preset_semesters_choice")
                custom = st.text_input(
                    "Custom (comma separated)",
                    placeholder="Autumn, Spring, Summer",
                    key="custom_semesters_input",
                )
                if st.button("Create Semesters", key="create_semesters_btn"):
                    names = [s.strip() for s in custom.split(",") if s.strip()] or presets[preset_choice]
                    dp = self.controller.data_persistence
                    if dp and hasattr(dp, "add_semesters"):
                        try:
                            dp.add_semesters(names)  # type: ignore[attr-defined]
                            if "Semester 1" not in names and hasattr(dp, "remove_semester"):
                                try:
                                    dp.remove_semester("Semester 1")  # type: ignore[attr-defined]
                                except Exception:
                                    pass
                            self.controller.set_year(selected_year)
                            first = names[0]
                            self.controller.set_semester(first)
                            st.session_state["semester_select"] = first
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add semesters: {e}")
                    else:
                        st.error("Persistence does not support adding semesters.")

    def _render_semester_selector(self) -> None:
        if not self.controller.year:
            return
        semesters = self.controller.available_semesters
        if not semesters:
            return
        prev = st.session_state.get("semester_select")
        index = 0
        if prev in semesters:  # type: ignore[arg-type]
            index = semesters.index(prev)  # type: ignore[arg-type]
        selected = st.selectbox("Select Semester", options=semesters, index=index, key="semester_select")
        self.controller.set_semester(selected)

    def _render_subject_selector(self) -> None:
        subs = self.controller.available_subjects
        if not subs:
            return
        selected_subject = st.selectbox("Select Subject", options=subs, key="subject_select")
        st.session_state["selected_subject"] = selected_subject
