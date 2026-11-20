"""Build demos/benchmark_widget/sim_comparison.html from the benchmark results.

    python make_widget.py

Reads ``results_linux.json`` (Ryzen 9 9900X + RTX 5090: Clifft, SymFT, xtim, Magna, Tsim CPU
and CUDA) and ``results_metal.json`` (Apple M4 Pro GPU: Tsim Metal). Cells that are missing
show as "not run".
"""

import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
OUT = HERE.parents[1] / "demos" / "benchmark_widget" / "sim_comparison.html"
REPO = "https://github.com/rafaelha/tsim-bench/blob/master/"

CIRCUITS = {
    "papers/2406.17653_transversal_algorithmic_ft/stim/s_injection_T_d5_p0.001_pinj0.1.stim":
        ("Injection, d=5", "Zhou et al. (2024), arXiv:2406.17653"),
    "papers/2409.17595_magic_state_cultivation/stim/inject_cultivate_d3_p0.001.stim":
        ("Cultivation, d=3", "Gidney, Shutty, Jones (2024), arXiv:2409.17595"),
    "papers/2409.17595_magic_state_cultivation/stim/inject_cultivate_d5_p0.001.stim":
        ("Cultivation, d=5", "Gidney, Shutty, Jones (2024), arXiv:2409.17595"),
    "papers/2409.17595_magic_state_cultivation/stim/end2end_d5_dsurface15_p0.001.stim":
        ("Cultivation end-to-end, d=5", "Gidney, Shutty, Jones (2024), arXiv:2409.17595"),
    "papers/2509.05212_fold_transversal_cultivation/stim/fold-d5_native_T_p0.001.stim":
        ("Fold-transversal cultivation, d=5", "Sahay et al. (2025), arXiv:2509.05212"),
    "papers/2503.18657_rp2_cultivation/stim/rp_3_rp_5_T_cult.stim":
        ("RP² cultivation, d=3→5", "Chen et al. (2025), arXiv:2503.18657"),
    "papers/2505.13587_correlated_decoding_distillation/stim/distillation_15to1_T_d5_p0.001.stim":
        ("15-to-1 distillation, d=5", "Cain et al. (2025), arXiv:2505.13587"),
    "papers/2610.06811_merlin/stim/distillation_bh10_p0.001.stim":
        ("Bravyi–Haah 38-to-10", "Cercelescu, Koch, Pesah (2026), arXiv:2610.06811"),
    "papers/2610.22315_magna/stim/bh100-T.stim":
        ("Bravyi–Haah 308-to-100", "Wang, Gu (2026), arXiv:2610.22315"),
    "papers/2610.06811_merlin/stim/code_switching_bt27_p0.001.stim":
        ("Code switching, BT27", "Cercelescu, Koch, Pesah (2026), arXiv:2610.06811"),
    "papers/2610.06811_merlin/stim/code_switching_bt81_p0.001.stim":
        ("Code switching, BT81", "Cercelescu, Koch, Pesah (2026), arXiv:2610.06811"),
    "papers/2607.28600_symft/stim/coherent_surface_d5_r5_p1e-3_rz0p02.stim":
        ("Coherent R_Z noise, surface d=5", "SymFT (2026), arXiv:2607.28600"),
    "papers/2509.18294_transversal_star/stim/star_d=9.stim":
        ("Transversal STAR, d=9", "Ismail et al. (2025), arXiv:2509.18294"),
}

# id: label, color slot, marker shape, result configs (1 thread first, then all cores).
# Line style follows the device: CPU solid, Apple GPU dashed, NVIDIA GPU dotted.
ENGINES = {
    "tsim-cpu": ("Tsim CPU", 1, "circle", ["tsim-cpu-1t", "tsim-cpu-mt"]),
    "tsim-cuda": ("Tsim RTX 5090", 1, "diamond", ["tsim-cuda"]),
    "tsim-metal": ("Tsim Apple M4 Pro", 1, "triangle", ["tsim-metal"]),
    "clifft": ("Clifft", 2, "square", ["clifft-1t", "clifft-mt"]),
    "symft": ("SymFT", 3, "cross", ["symft-1t", "symft-mt"]),
    "xtim": ("xtim", 4, "circle", ["xtim-1t", "xtim-mt"]),
    "magna-cpu": ("Magna CPU (draws/s)", 5, "square", ["magna-1t", "magna-mt"]),
    "magna-cuda": ("Magna RTX 5090 (draws/s)", 5, "diamond", ["magna-cuda"]),
    # Tsim-devices view
    "tsim-1t": ("Tsim CPU, 1 thread", 0, "circle", ["tsim-cpu-1t"]),
    "tsim-mt": ("Tsim CPU, all cores", 1, "circle", ["tsim-cpu-mt"]),
}
MODES = {
    "all": ["tsim-cpu", "tsim-metal", "tsim-cuda", "clifft", "symft", "xtim", "magna-cpu", "magna-cuda"],
    "tsim": ["tsim-1t", "tsim-mt", "tsim-metal", "tsim-cuda"],
}


BENCH = pathlib.Path(__file__).resolve().parents[3] / "tsim-bench"


def recorded_k(path):
    """tsim-bench's recorded widths of ``path``: {"tsim": k, "clifft": k}, from its paper's k_max.json."""
    p = pathlib.Path(path)
    folder = p.parents[1]
    f = BENCH / folder / "k_max.json"
    if not f.exists():
        return {}
    entry = next((e for e in json.loads(f.read_text()) if e["file"] == str(p.relative_to(folder))), {})
    return {"tsim": entry.get("tsim_k"), "clifft": entry.get("clifft_k")}


def family(config):
    return "tsim" if config.startswith("tsim") else config.split("-")[0]


def infer_k(path, row):
    """Give failed cells the width their simulator reports elsewhere: another run of the same circuit,
    tsim-bench's recorded width, or the width named in the error."""
    known = {}
    for key, c in row.items():
        if c.get("k_max") is not None:
            known.setdefault(family(key.split("|")[0]), c["k_max"])
    recorded = recorded_k(path)
    for key, c in row.items():
        if "error" not in c or c.get("k_max") is not None:
            continue
        fam = family(key.split("|")[0])
        error = c["error"]
        k, source = known.get(fam), "measured in this simulator's other runs"
        if k is None and recorded.get(fam) is not None:
            k, source = recorded[fam], "recorded in tsim-bench"
        if k is None:
            m = re.search(r"needs (\d+) active qubits|k_max (\d+)|K = (\d+)", error)
            if m:
                k, source = int(next(g for g in m.groups() if g)), "from the error"
            m = re.search(r"active width would reach (\d+)", error)
            if m:
                k, source = f"≥{m.group(1)}", "from the error (planner overflow)"
        if k is not None:
            c["k_inferred"] = str(k)
            c["k_source"] = source


def read_tsim_dev(path, post):
    """Cells from a `tsim-dev bench` JSON, keyed by (circuit stem, post)."""
    if not path.exists():
        return {}
    out = {}
    for r in json.loads(path.read_text())["results"]:
        rounds = next(iter(r.get("rounds", {}).values()), [])
        first = rounds[0] if rounds else {}
        if r.get("shots_per_s") and r.get("device") not in (None, "metal"):
            out[r["circuit"], post] = {"error": f"unsupported: K = {r.get('k')} > 11, too wide for the GPU"
                                                f" (Tsim fell back to the CPU)", "tsim_version": first.get("tsim_version")}
        elif r.get("shots_per_s"):
            out[r["circuit"], post] = {
                "shots_per_s": r["shots_per_s"], "compile_s": r.get("compile_s"), "k_max": r.get("k"),
                "k_name": "active width", "kept": r.get("acceptance"), "device": r.get("device"),
                "tsim_version": first.get("tsim_version"), "threads": None,
            }
        else:
            out[r["circuit"], post] = {"error": str(r.get("error") or first.get("error") or "error")[:300],
                                       "tsim_version": first.get("tsim_version")}
    return out


def main():
    linux_path = HERE / "results_linux.json"
    linux = json.loads(linux_path.read_text()) if linux_path.exists() else {"circuits": {}, "simulators": {}}
    metal = {}
    for post, name in (("on", "metal_post_on.json"), ("off", "metal_post_off.json")):
        metal.update(read_tsim_dev(HERE / name, post))

    cells = {}
    circuits = []
    for path, (label, paper) in CIRCUITS.items():
        row = {}
        for key, c in linux["circuits"].get(path, {}).items():
            config, _, off = key.partition("|")
            sim = linux.get("simulators", {}).get(config, {})
            c = dict(c)
            c.setdefault("threads", sim.get("threads") if not config.endswith("cuda") else None)
            contract = (sim.get("output_contract") or {}).get("off" if off else "on")
            notes = []
            if config.startswith("magna"):
                notes.append("rate counts fault draws, each with its exact acceptance and error mass, not detector samples")
            if contract and not config.startswith("tsim"):
                notes.append(f"output: {contract}")
            c["note"] = " · ".join(notes) or None
            row[key] = c
        stem = path.rsplit("/", 1)[1].removesuffix(".stim")
        for post in ("on", "off"):
            if (stem, post) in metal:
                row["tsim-metal" + ("|post-off" if post == "off" else "")] = metal[stem, post]
        m = metal.get((stem, "on"))
        tsim_k = next((c.get("k_max") for c in (row.get("tsim-cpu-1t"), m) if c and c.get("k_max") is not None), None)
        name = path.rsplit("/", 1)[1].removesuffix(".stim")
        circuits.append({
            "id": path, "label": label, "paper": paper, "url": REPO + path,
            "meta": f"{name}" + (f" · K = {tsim_k}" if tsim_k is not None else ""),
        })
        infer_k(path, row)
        cells[path] = row

    machine = linux.get("machine", {})
    sims = linux.get("simulators", {})
    cores = next((s.get("threads") for k, s in sims.items() if k.endswith("-mt") and s.get("threads")), 12)
    versions = " · ".join(f"{k}: {v.get('version', '?')}" for k, v in sims.items() if not k.endswith("-mt"))
    metal_version = next((v.get("tsim_version") for v in metal.values() if v.get("tsim_version")), "?")
    specs = [
        ("Machines", f"Linux: {machine.get('cpu', 'AMD Ryzen 9 9900X (12 cores)')}, {machine.get('gpu', 'NVIDIA RTX 5090')}."
                     " Apple: M4 Pro, 20-core GPU, for Tsim's Metal backend only."),
        ("Sampling", "Attempted shots per second of the detector sampler, after a warm-up call that triggers JIT and"
                     " kernel compilation. Tsim is measured with its own harness (tsim-dev bench: bit-packed output,"
                     " calibrated calls, best of fresh-process rounds); the other simulators with their fastest"
                     " documented settings."),
        ("Postselection", "On: the detectors that each circuit's paper postselects, as recorded in tsim-bench (e.g. the"
                          " injection and cultivation detectors in cultivation). Shots discarded by postselection count"
                          " as attempted shots, so the rate is a cost per attempt; the tooltip shows the fraction kept."
                          " Off: every shot is sampled to the end."),
        ("Compilation", "Wall time from circuit text to a sampler ready to sample, excluding imports and first-call JIT."),
        ("Threads", f"1 thread: pinned to one core with every thread pool capped at 1. {cores}: each simulator's own"
                    " thread option set to all physical cores. GPU lanes do not depend on this setting."),
        ("Failures", "Each measurement has a 300 s budget (compilation, warm-up and sampling) and a memory cap."
                     " 'too wide': Tsim's GPU kernels support K ≤ 11 and its CPU statevector K ≤ 30."
                     " 'no rotations': the simulator has no arbitrary-angle rotations."),
        ("Magna", "Magna does not sample detectors: each draw of the faults gives the exact accepted probability"
                  " and the probability that an observable flips. Its rate is draws per second, a different unit of work"
                  " from the other simulators' shots per second. Magna has no thread option; its all-core lane is 12"
                  " processes. Circuits are converted to Magna's format by a script; Magna's kept fraction and error rate"
                  " agree with Tsim's within 5 standard errors on every circuit."),
        ("Output", "Each simulator ran its fastest documented output contract: Tsim and xtim return bit-packed detector"
                   " and observable rows; Clifft and SymFT return survivor counts with postselection on (SymFT can only"
                   " postselect all detectors or none). Hover a lane for the contract used."),
        ("Checks", "Every simulator's detection, observable and kept rates agree with a separate Tsim run (or xtim / Magna"
                   " where Tsim cannot run) within 5 standard errors."),
        ("Views", "One row per circuit, one lane per simulator, on a shared log axis. Lines show the device: solid for"
                  " CPUs, dashed for the Apple GPU, dotted for the RTX 5090. Relative puts each row's slowest simulator at"
                  " 1× (for compilation, the slowest to compile). Compare draws each lane from its baseline (open mark:"
                  " postselection off, or 1 thread) to the selected setting (filled mark) and gives the speedup."),
        ("K", "The most qubits held in a dense statevector at once, as each simulator reports it. Sampling cost grows as 2^K. Italic: a run that failed, with the width the simulator reported in"
              " its other runs of the circuit, in tsim-bench, or in its error."),
        ("Versions", f"{versions} · tsim-metal: bloqade-tsim {metal_version}" if versions else f"tsim-metal: bloqade-tsim {metal_version}"),
        ("Circuits", "From tsim-bench (github.com/rafaelha/tsim-bench); each name links to the circuit and its paper folder."),
    ]
    data = {
        "circuits": circuits,
        "cells": cells,
        "engines": {k: {"id": k, "label": l, "slot": s, "shape": sh, "configs": c,
                        "line": "dashed" if "metal" in k else "dotted" if "cuda" in k else "solid"}
                    for k, (l, s, sh, c) in ENGINES.items()},
        "modes": MODES,
        "cores": cores,
        "specs": specs,
    }
    template = (HERE / "widget_template.html").read_text()
    css = (HERE / "TsimBenchmarks.css").read_text()
    html = (template.replace("/*__CSS__*/", css)
            .replace("/*__DATA__*/", json.dumps(data).replace("</", "<\\/"))
            .replace("__CORES__", str(cores)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"wrote {OUT} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
