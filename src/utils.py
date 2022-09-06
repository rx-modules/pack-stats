from io import BytesIO
import re
import streamlit as st
from beet import run_beet

from mecha.contrib.statistics import Analyzer

Pack = BytesIO


@st.experimental_singleton(show_spinner=False)  # type: ignore
def get_ctx(pack: str, filter: re.Pattern | None):
    with run_beet({"data_pack": {"load": [pack]}, "require": ["plugins.grab_stats"], "pipeline": ["mecha"]}) as ctx:
        return ctx


def get_stats(pack: str, filter: re.Pattern | None):
    return get_ctx(pack, filter).meta["stats"]


def get_data(pack: str, filter: re.Pattern | None):
    ctx = get_ctx(pack, filter)

    if filter:
        for name in list(ctx.data.functions.keys()):
            if filter.search(name):
                del ctx.data.functions[name]

    return ctx.data
