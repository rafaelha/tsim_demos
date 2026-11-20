"""Tsim's compilation widget from the Tsim 1.0 blog post, steps 5-8, for the notebooks.

``pauli_program.html`` is the ``TsimCompilationSteps`` widget of the bloqade-website repo
(``src/components/TsimCompilationSteps.astro``), rendered in light mode with only the
Pauli program, Scheduling, Active qubits and Trajectory sharing steps and without the
explanatory text. Its CSS and script are inlined, so the file is self-contained.
"""

import html
import pathlib
import uuid

from IPython.display import HTML

from compilation_widget.error_basis import error_basis as error_basis

_PAGE = pathlib.Path(__file__).with_name("pauli_program.html")


def pauli_program(height: int = 900) -> HTML:
    """Return the widget as an iframe that resizes to fit the current step."""
    frame = f"tcs-{uuid.uuid4().hex}"
    return HTML(
        f'<iframe id="{frame}" srcdoc="{html.escape(_PAGE.read_text())}" '
        f'style="width: 100%; height: {height}px; border: 0;"></iframe>'
        "<script>"
        "window.addEventListener('message', (event) => {"
        f"  const frame = document.getElementById('{frame}');"
        "  if (frame && event.source === frame.contentWindow && event.data?.tcsHeight)"
        "    frame.style.height = event.data.tcsHeight + 'px';"
        "});"
        "</script>"
    )
