"""Test imports to find where it hangs."""

import streamlit as st


def main():
    st.title("Import Test")

    try:
        st.write("Testing imports step by step...")

        # Test 1: Controller (we know this works)
        st.write("1. Importing AppController...")
        from controller.app_controller import AppController

        st.success("✅ AppController imported")

        # Test 2: StreamlitView
        st.write("2. Importing StreamlitView...")
        from view.streamlit_views import StreamlitView

        st.success("✅ StreamlitView imported")

        # Test 3: Initialize controller
        st.write("3. Initializing controller...")
        controller = AppController()
        st.success("✅ Controller initialized")

        # Test 4: Initialize view (this might be where it hangs)
        st.write("4. Initializing view...")
        view = StreamlitView(controller)
        st.success("✅ View initialized")

        # Test 5: Try rendering (this is likely the problem)
        st.write("5. Testing view.render()...")
        view.render()
        st.success("✅ View rendered successfully")

    except Exception as e:
        st.error(f"❌ Error at step: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
