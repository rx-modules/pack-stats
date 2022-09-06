import re
from typing import Any
from zipfile import ZipFile

import streamlit as st
from beet import DataPack
from mecha.contrib.statistics import Statistics
from millify import millify
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers.mcfunction import MCFunctionLexer

import pack_graph
from utils import get_data, get_stats

REPO_LINK = "https://github.com/rx-modules/pack-stats"
BUG_REPORT_URL = "https://github.com/rx-modules/pack-stats/issues/new?assignees=&labels=bug&template=bug-report.md&title=%5BBug%5D"
DISCORD_LINK = "https://discord.gg/nfwsJ3XeDT"

def page_config():
    st.set_page_config(
        page_title="Pack Stats",
        page_icon=":package:",
        layout="wide",
        menu_items={
            "Report a bug": BUG_REPORT_URL,
            "Get help": DISCORD_LINK,
            "About": (
                "# Pack Stats\n"
                "A cool way to visualize your Minecraft Data Pack Stats\n"
                "\n"
                f"[Github]({REPO_LINK})"
            )
        }
    )


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
        (
            "Commands",
            sum(sum(value.values()) for value in stats.command_count.values()),
        ),
        ("Selectors", sum(stats.selector_count.values())),
        ("Objectives", len(stats.scoreboard_objectives)),
        (
            "Fake Players",
            sum(
                len(obj.values())
                for obj in stats.scoreboard_fake_player_references.values()
            ),
        ),
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
    if pack := st.file_uploader("Upload Pack (zip only)"):
        st.session_state["zipped_pack"] = ZipFile(pack)

        with st.spinner("Loading Pack and Analyzing Stats"):
            st.session_state["data"] = get_data(pack.name, filter)
            st.session_state["stats"] = get_stats(pack.name, filter)

        display_stats()

        graph_col, code_col = st.columns(2)
        with (
            st.spinner("Loading Pack Graph (may take a while)"),
            graph_col,
        ):  # TODO: timeout
            highlighted_node = pack_graph.plot(filter)

        with code_col:
            data: DataPack = st.session_state["data"]
            if highlighted_node:
                st.header(f"Function: `{highlighted_node}`")
                content = "\n".join(data.functions[highlighted_node].lines)
                st.markdown(
                    highlight(
                        content,
                        MCFunctionLexer(),
                        HtmlFormatter(
                            style="material",
                            noclasses=True,
                            nobackground=True,
                            lineseparator="<br>",
                            cssstyles="font-family: 'Source Code Pro';",
                        ),
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.header("No function selected")


main()
