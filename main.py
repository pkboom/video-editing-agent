import streamlit as st

from app_tabs.process_tab import render_process_tab
from app_tabs.split_tab import render_split_tab

# Set page config
st.set_page_config(page_title="Video Editing Agent", page_icon="🎬", layout="wide")


def main():
    st.title("🎬 Video Editing Agent")
    st.write(
        "Use the tabs below to run the automated editor or to split a video into equal parts."
    )

    edit_tab, split_tab = st.tabs(["Process Video", "Split Video"])

    with edit_tab:
        render_process_tab()

    with split_tab:
        render_split_tab()


if __name__ == "__main__":
    main()
