"""How Tsim expresses a circuit's noise bits f as XORs of its error bits e, as collapsible HTML."""

import html

import zxparam
from IPython.display import HTML
from tsim.core.graph import transform_error_basis
from tsim.core.params import ParamLayout
from tsim.core.parse import parse_stim_circuit

STYLE = """<style>
.tsim-eb { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1b22;
  max-width: 60rem; border: 1px solid #e6e6ef; border-radius: 12px; background: #f7f7fb; padding: 0.6rem 0.9rem; }
.tsim-eb > summary { cursor: pointer; font-weight: 700; color: #4f27d6; }
.tsim-eb p { margin: 0.5rem 0; color: #55596b; font-size: 0.85rem; }
.tsim-eb .rows { max-height: 26rem; overflow-y: auto; margin-top: 0.4rem; }
.tsim-eb details.row { border-top: 1px solid #e6e6ef; padding: 0.15rem 0; }
.tsim-eb details.row > summary { cursor: pointer; font-size: 0.85rem; }
.tsim-eb .out { font-weight: 700; }
.tsim-eb .f { color: #4f27d6; font-family: ui-monospace, Menlo, monospace; }
.tsim-eb .n { color: #55596b; }
.tsim-eb .terms { font-family: ui-monospace, Menlo, monospace; font-size: 0.78rem; line-height: 1.7;
  padding: 0.25rem 0 0.4rem 1rem; color: #33364a; }
.tsim-eb .terms span[title] { padding: 0 0.15rem; border-radius: 3px; background: #efeaff; cursor: help; }
</style>"""


def _error_names(stim_circuit, builder) -> list[str]:
    """One hover label per error bit: its noise instruction, targets, tick and bit within the channel."""
    flat = stim_circuit.flattened()
    ticks, tick = [], 0
    for inst in flat:
        ticks.append(tick)
        tick += inst.name == "TICK"
    names = []
    for site, probs in zip(builder.channel_sites, builder.channel_probs, strict=True):
        inst = flat[site.instruction]
        args = ", ".join(f"{a:g}" for a in inst.gate_args_copy())
        targets = " ".join(str(t.value) for t in inst.targets_copy()[site.start:site.end])
        bits = int(probs.size).bit_length() - 1
        for bit in range(bits):
            names.append(f"{inst.name}({args}) {targets} · tick {ticks[site.instruction]} · bit {bit + 1} of {bits}")
    return names


def error_basis(circuit, open_rows: int = 0) -> HTML:
    """Show each detector and observable as one noise bit f, and each f as the XOR of error bits e.

    Follows Tsim's compilation (``tsim.core.graph.prepare_graph``): build the sampling graph,
    reduce it with ZX rewrites, then rewrite the error bits in a basis of independent noise bits.
    """
    builder = parse_stim_circuit(circuit.stim_circuit)
    graph = builder.build(closed=True, outputs="detectors")
    zxparam.full_reduce(graph)
    graph, transform = transform_error_basis(graph, builder.num_error_bits)
    layout = ParamLayout(builder.num_error_bits)
    basis_index = {layout.basis(j): j for j in range(transform.shape[0])}
    names = _error_names(circuit.stim_circuit, builder)
    num_detectors = len(builder.detectors)

    rows = []
    for v in sorted(graph.outputs(), key=graph.port):
        port = graph.port(v)
        label = f"D{port}" if port < num_detectors else f"L{port - num_detectors}"
        fs = sorted(basis_index[p] for u in graph.neighbors(v) for p in graph.phase(u).parameters if p in basis_index)
        if not fs:
            continue
        errors = sorted({e for j in fs for e in transform.rows[j]})
        terms = " ⊕ ".join(f'<span title="{html.escape(names[e])}">e{e}</span>' for e in errors)
        f_text = " ⊕ ".join(f"f{j}" for j in fs)
        rows.append(
            f'<details class="row"{" open" if len(rows) < open_rows else ""}><summary><span class="out">{label}</span>'
            f' = <span class="f">{f_text}</span> <span class="n">· XOR of {len(errors)} error bits</span></summary>'
            f'<div class="terms">{f_text} = {terms}</div></details>'
        )
    summary = (f"Noise basis: {builder.num_error_bits} error bits e → {transform.shape[0]} noise bits f"
               f" ({len(rows)} detectors and observables)")
    return HTML(
        f'{STYLE}<details class="tsim-eb"><summary>{summary}</summary>'
        "<p>Every noise channel gets error bits e (one per independent Pauli it can apply). After ZX"
        " simplification, Tsim rewrites them in a basis of independent noise bits f = T e: error patterns"
        " with the same effect on the outputs share a bit. In this Clifford circuit, every detector and"
        " observable is a single noise bit, the XOR of the error bits that flip it. Expand a row to see them;"
        " hover an e for its noise instruction.</p>"
        f'<div class="rows">{"".join(rows)}</div></details>'
    )
