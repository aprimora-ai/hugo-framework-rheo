# RHEO — Flow-Based Temporal Dynamics for Artificial Agents

**Paper V of the HUGO AGI Framework**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> *"Time is not what the clock says. Time is what the field does."*

## Overview

RHEO (from Greek *rheo*, to flow) introduces a fluid-dynamics formalism for subjective temporal experience in artificial agents. Using an Affective Reynolds Number Re_A(t), RHEO governs a time dilation factor Φ(t) that produces a subjective clock running faster under emotional intensity and compressing during monotony.

**Key results:**
- **Time dilation validated:** 2.17x under trauma (I_eff = 0.40), 5/5 seeds
- **Bergson paradox emerges:** 20 steps of trauma perceived 4.4x longer than 200 steps of rest
- **Re_crit ~ 1.16** separates laminar (calm) from turbulent (intense) temporal flow

## Quick Start

```bash
cd C:\Users\ohiod\Projects\RHEO
python run_all_rheo.py
```

## Formalism

```
Re_A(t) = D_H(t) × tau_rel(t) × n_H1(t)    — Affective Reynolds Number
Φ(t)    = 1 + α·Re_A(t) + β·ω_A(t)          — Time dilation factor
C_subj  = Σ Φ(t) · tick_s                     — Subjective clock

Where:
  D_H      = ||H(t) - H_NOM||₂               — homeostatic displacement
  tau_rel  = tau_pers / tau_ref                — relative persistence
  n_H1     = unresolved topological features   — structural complexity
  ω_A      = Σ pers_H1_i / age_i              — vorticity (unresolved tensions)
```

## Experiments

| Exp | Validates | Result |
|-----|-----------|--------|
| R-1 | Re_crit calibration | Re_crit ~ 1.16, laminar/turbulent transition confirmed |
| R-2 | Theorem R-1 (dilation) | ratio = 2.17x at I=0.40, 5/5 seeds PASS |
| R-3 | Theorem R-2 (Bergson) | T_rec(trauma) = 4.4x T_rec(rest), 5/5 seeds PASS |

## HUGO Ecosystem

| Paper | Module | Function | DOI |
|-------|--------|----------|-----|
| I | HUGO | Homeostatic field | [10.5281/zenodo.18947852](https://doi.org/10.5281/zenodo.18947852) |
| II | ECHO | Empathic coupling | [10.5281/zenodo.19043115](https://doi.org/10.5281/zenodo.19043115) |
| III | REMIND | Episodic memory | [10.5281/zenodo.19054013](https://doi.org/10.5281/zenodo.19054013) |
| IV | Radiante | Structural navigation | [10.5281/zenodo.18940478](https://doi.org/10.5281/zenodo.18940478) |
| **V** | **RHEO** | **Temporal dynamics** | **This paper** |

## Structure

```
RHEO/
├── paper_rheo_v1.md          # Paper source
├── run_all_rheo.py           # Run all experiments
├── requirements.txt
├── src/
│   └── rheo/
│       ├── rheo_core.py      # Core engine (343 lines)
│       └── __init__.py
└── experiments/
    ├── exp_r1_re_crit.py     # Re_crit calibration
    ├── exp_r2_dilatacao.py   # Time dilation validation
    ├── exp_r3_compressao.py  # Bergson paradox validation
    └── results/              # JSON outputs
```

## Author

**David Ohio** — Independent Researcher
- Email: odavidohio@gmail.com
- GitHub: [@aprimora-ai](https://github.com/aprimora-ai)

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

## Citation

```bibtex
@software{ohio2026rheo,
  author    = {Ohio, David},
  title     = {RHEO: Flow-Based Temporal Dynamics for Artificial Agents},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.PENDING},
  url       = {https://github.com/aprimora-ai/hugo-framework-rheo}
}
```
