# d=5 cultivation circuits of Chan et al.

From Chan, Strikis, Sun and Cai, "Diagnosing and Restoring the Degraded Fault Distance of
Magic State Cultivation", [arXiv:2609.17706](https://arxiv.org/abs/2609.17706):
[timchan0/cliffordea](https://github.com/timchan0/cliffordea), `cliffordea/sim/stim_files/`
at `27385c6` (MIT license). The originals are S-state proxies of Gidney, Shutty and Jones's
d=5 cultivation (injection and cultivation, no escape). The `_T_` files are the T-state
circuits: every `S`/`S_DAG` swapped for `T`/`T_DAG`, as cliffordea's `swap_t_and_s_gates` does.

- `d5a19_S_inject+cultivate_uncorrected.stim`: the S proxy, noiseless, without the
  Bell-growth feedforward.
- `d5a19_T_inject+cultivate_uncorrected.stim`: its T-state circuit.
- `d5a19_T_inject+cultivate_p1e-3.stim`: with the feedforward, noise p = 1e-3.
- `d5a19f13_T_inject+cultivate_p1e-3.stim`: the same with 13 Z-flag qubits in the final
  double check, Chan et al.'s fix.
