# Simulator comparison for the Rutgers talk

Shots per second, compile time and active width K of 13 tsim-bench circuits
(https://github.com/rafaelha/tsim-bench) in Tsim (CPU, Apple GPU, RTX 5090), Clifft, SymFT, xtim
and Magna (CPU, RTX 5090), with the paper's postselection on and off. Measured 2026-11-20.

- `circuits.txt`: the circuits, as paths in tsim-bench.
- `results_linux.json`: Ryzen 9 9900X (1 and 12 threads) and RTX 5090. Tsim ran under
  `tsim-dev bench` (bloqade-tsim 1.1.0 at `feat/determined-measurements` 0e95b9a3, CUDA at
  `cuda-statevector-executor` d140f3d9); the other simulators with the harness in
  `~/sim-comparison/` on that machine (worker, runner, Magna converter, `results_full.json` with
  standard errors and raw errors).
- `metal_post_on.json`, `metal_post_off.json`: Apple M4 Pro GPU, `tsim-dev bench --device gpu`
  (with `--no-postselect` for off), from a worktree of `feat/determined-measurements` 0e95b9a3.
- `make_widget.py`: builds `demos/benchmark_widget/sim_comparison.html` from these files, with
  `widget_template.html` and bloqade-website's `TsimBenchmarks.css`.
