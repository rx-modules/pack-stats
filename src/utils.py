import re
from io import BytesIO
from typing import Callable
from zipfile import ZipFile

import streamlit as st
from beet import Context, run_beet
from beet.core.utils import get_import_string
from mecha.contrib.statistics import Analyzer

Pack = BytesIO


def beet_analyzer(ctx: Context):
    ctx.meta["stats"] = ctx.inject(Analyzer).stats


def load_pack(ctx: Context):
    ctx.data.load(st.session_state["zipped_pack"])


@st.experimental_singleton(show_spinner=False)  # type: ignore
def get_ctx(pack_name: str, filter: re.Pattern | None):
    config = {
        "require": [get_import_string(beet_analyzer)],
        "pipeline": [get_import_string(load_pack), "mecha"],
    }

    with run_beet(config) as ctx:
        return ctx


def get_stats(pack_name: str, filter: re.Pattern | None):
    return get_ctx(pack_name, filter).meta["stats"]


def get_data(pack_name: str, filter: re.Pattern | None):
    ctx = get_ctx(pack_name, filter)

    if filter:
        for name in list(ctx.data.functions.keys()):
            if filter.search(name):
                del ctx.data.functions[name]

    return ctx.data
