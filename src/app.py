import re
from typing import Any
import streamlit as st

from mecha.contrib.statistics import Statistics

from millify import millify

from utils import get_stats, get_data
import pack_graph


def page_config():
    st.set_page_config(page_title="Pack Stats")


def row(*args):
    assert len(args) > 0

    columns = st.columns(len(args))
    for column, (title, value) in zip(columns, args):
        value = millify(value) if type(value) in (int, float) else value
        with column:
            st.metric(title, value)


def display_stats():
    stats: Statistics = st.session_state["stats"]

    st.header("Pack Overview")
    row(
        ("Functions", stats.function_count),
        ("Commands", sum(sum(value.values()) for value in stats.command_count.values())),
        ("Selectors", sum(stats.selector_count.values())),
        ("Objectives", len(stats.scoreboard_objectives)),
        ("Fake Players", sum(len(obj.values()) for obj in stats.scoreboard_fake_player_references.values())),
    )


def get_filter():
    output = st.text_input("Filter Datapack (regex)")

    if not output:
        return None

    try:
        return re.compile(output)
    
    except re.error as err:
        st.warning(f"Filter is not valid regex: `{err}`")
        return None


def main():
    page_config()

    st.title("Pack Stats")
    filter = get_filter()
    if pack := st.file_uploader("Upload Pack (max 200mb)", key="pack"):
        with st.spinner("Loading Pack and Analyzing Stats"):
            st.session_state["data"] = get_data(pack.name, filter)
            st.session_state["stats"] = get_stats(pack.name, filter)
        
        display_stats()

        with st.spinner("Loading Pack Graph (may take a while)"):  # TODO: timeout
            pack_graph.plot(filter)

main()
