"""Simulator benchmark widget for the notebooks (built by benchmarks/sim_comparison/make_widget.py)."""

import html
import pathlib
import uuid

from IPython.display import HTML

_PAGE = pathlib.Path(__file__).with_name("sim_comparison.html")


def simulator_comparison(height: int = 900) -> HTML:
    """Return the widget as an iframe that resizes to fit its content."""
    frame = f"tsb-{uuid.uuid4().hex}"
    return HTML(
        f'<iframe id="{frame}" srcdoc="{html.escape(_PAGE.read_text())}" '
        f'style="width: 100%; height: {height}px; border: 0;"></iframe>'
        "<script>"
        "window.addEventListener('message', (event) => {"
        f"  const frame = document.getElementById('{frame}');"
        "  if (frame && event.source === frame.contentWindow && event.data?.tsbHeight)"
        "    frame.style.height = event.data.tsbHeight + 'px';"
        "});"
        "</script>"
    )
