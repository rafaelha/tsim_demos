"""Workaround: show simplified scalars in zxparam's ZX drawings.

zxparam 0.1.0 draws ``graph.scalar`` unsimplified, so constant node terms show as a run of
``Node(0,∅)`` factors (each is 1 + e^0 = 2) instead of being folded into the power of 2.
Importing this module makes the drawings show ``Scalar.simplified()``; the graph is not changed.
"""

import zxparam.viz.d3 as _d3

_to_json = _d3.to_json


def _to_json_simplified(graph, *, param_names=None, **kwargs):
    payload = _to_json(graph, param_names=param_names, **kwargs)
    payload["scalar"] = graph.scalar.simplified().format(param_names)
    return payload


if not getattr(_d3.to_json, "__zx_display_patch__", False):
    _to_json_simplified.__zx_display_patch__ = True
    _d3.to_json = _to_json_simplified
