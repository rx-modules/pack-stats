import math
from typing import Mapping
import re

from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st

from beet import Function

from utils import get_data

function_pattern = re.compile(r'(?:(?:schedule )?function(?![^{]*})) (#?[a-z0-9.-_+:]+)(?: \d+.)?')


def generate(functions: Mapping[str, Function], filter: re.Pattern | None):
    cached_ids = set()
    for source_name, function in functions.items():
        if filter and filter.search(source_name):
            continue

        if source_name not in cached_ids:
            yield Node(
                id=source_name,
                title=source_name,
                size=int(math.log(len(function.to_str(function.lines)))),
            )
            cached_ids.add(source_name)

        for line in function.lines:
            if line.startswith("#"):
                continue
            
            if match := function_pattern.match(line):
                target_name = match.groups()[0]
                
                if target_name not in cached_ids:
                    yield Node(
                        id=target_name,
                    )
                    cached_ids.add(target_name)
                
                yield Edge(
                    source=source_name,
                    target=target_name,
                )


def config():
    return Config(
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
        node={'labelProperty': 'label', 'renderLabel': True},
    )


def plot(filter: re.Pattern | None):
    st.header("Pack Graph")

    data = st.session_state["data"]

    nodes, edges = [], []

    for graph_obj in generate(data.functions, filter):
        match graph_obj:
            case Node():
                nodes.append(graph_obj)
            case Edge():
                edges.append(graph_obj)
            case _:
                print("???", graph_obj)
    
    if nodes:
        agraph(nodes=nodes, edges=edges, config=config())
    else:
        st.warning("No functions matching filter found, please adjust filter")
