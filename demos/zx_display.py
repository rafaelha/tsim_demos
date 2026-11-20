"""Workaround: draw ZX diagrams without their scalar.

zxparam 0.1.0 always prints the graph's scalar above a drawing (unsimplified, as a run of
``Node(0,∅)`` factors). zxparam PR #16 adds ``show_scalar=False`` and Tsim will hide the scalar by
default; until those are released, importing this module drops the scalar from every drawing.
The graph is not changed.
"""

import zxparam.viz.d3 as _d3

_to_json = _d3.to_json


def _to_json_without_scalar(graph, **kwargs):
    payload = _to_json(graph, **kwargs)
    payload["scalar"] = ""  # the viewer draws no scalar line for an empty scalar
    return payload


if not getattr(_d3.to_json, "__zx_display_patch__", False):
    _to_json_without_scalar.__zx_display_patch__ = True
    _d3.to_json = _to_json_without_scalar
