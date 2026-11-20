# d=5 cultivation circuits of Chan et al.

From Chan, Strikis, Sun and Cai, "Diagnosing and Restoring the Degraded Fault Distance of
Magic State Cultivation", [arXiv:2609.17706](https://arxiv.org/abs/2609.17706):
[timchan0/cliffordea](https://github.com/timchan0/cliffordea), `cliffordea/sim/stim_files/`
at `27385c6` (MIT license). They are S-state proxies of Gidney, Shutty and Jones's d=5
cultivation (injection and cultivation, no escape); swapping every `S`/`S_DAG` for
`T`/`T_DAG` gives the T-state circuit.

- `d5a19_inject+cultivate_uncorrected.stim`: noiseless, without the Bell-growth feedforward.
- `d5a19_inject+cultivate_p1e-3.stim`: with the feedforward, noise p = 1e-3.
- `d5a19f13_inject+cultivate_p1e-3.stim`: the same with 13 Z-flag qubits in the final
  double check, Chan et al.'s fix.
