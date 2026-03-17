# -*- coding: utf-8 -*-
"""
Experimento R-2 — Validação do Teorema R-1 (Dilatação sob trauma)
RHEO Paper 5 | David Ohio | 2026

Teorema R-1:
    Se I_eff(t) >= I_crit para t in [t1,t2],
    entao T_vivido(t1,t2) > T_fisico(t1,t2).

Protocolo:
    Tres condicoes x 5 seeds x 1 episodio de N_STEPS steps:
      A: I_eff = 0.05  (controle)
      B: I_eff = 0.15  (no limiar de I_crit)
      C: I_eff = 0.40  (acima de I_crit — vivid, trauma)

Predicao:
    R_dil(C) > R_dil(B) > R_dil(A) ~= 1.0

Validacao:
    PASSA se R_dil(C) > R_dil(B) > R_dil(A) em pelo menos 4/5 seeds.
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from rheo import RHEOConfig, RHEOCore, H1Bar

N_STEPS  = 50
N_H1     = 2
SEEDS    = [42, 123, 7, 99, 31]
CONDITIONS = {
    "A_control": 0.05,
    "B_limiar":  0.15,
    "C_trauma":  0.40,
}
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def run_condition(label: str, i_eff: float, seed: int, cfg: RHEOConfig) -> dict:
    rng  = np.random.default_rng(seed)
    rheo = RHEOCore(cfg)
    H_NOM = np.array(cfg.H_NOM)

    h1_bars = [H1Bar(bar_id=i, birth=0, pers_H1=i_eff) for i in range(N_H1)]

    for t in range(N_STEPS):
        theta = cfg.theta_warn - i_eff * 0.3 + rng.normal(0, 0.01)
        theta = float(np.clip(theta, cfg.theta_recovered, cfg.theta_collapse))
        H = list(np.clip(H_NOM - i_eff * rng.uniform(0.05, 0.25, 5), 0.0, 1.0))
        rheo.step(t, theta, i_eff, H, h1_bars)

    ratio = rheo.ratio_subj_fisico
    return {
        "condition": label,
        "i_eff":     i_eff,
        "seed":      seed,
        "ratio":     round(ratio, 5),
        "T_vivido":  round(rheo.T_vivido_total, 3),
        "T_fisico":  round(rheo.T_fisico_total, 3),
    }


def run_exp_r2():
    cfg = RHEOConfig(tick_s=1.0)
    all_results = []

    print("=" * 65)
    print("EXPERIMENTO R-2 -- Validacao Teorema R-1 (Dilatacao sob trauma)")
    print(f"N_STEPS={N_STEPS} | N_H1={N_H1}")
    print("Predicao: R_dil(C) > R_dil(B) > R_dil(A)")
    print("=" * 65)

    # Coletar resultados por condicao
    cond_ratios = {label: [] for label in CONDITIONS}
    for label, i_eff in CONDITIONS.items():
        for seed in SEEDS:
            r = run_condition(label, i_eff, seed, cfg)
            all_results.append(r)
            cond_ratios[label].append(r["ratio"])

    # Medias
    means = {label: float(np.mean(ratios)) for label, ratios in cond_ratios.items()}

    print(f"\n{'Condicao':>14} | {'I_eff':>6} | {'ratio medio':>12} | {'ratio (seeds)':>35}")
    print("-" * 75)
    for label, i_eff in CONDITIONS.items():
        ratios_str = "  ".join(f"{r:.3f}" for r in cond_ratios[label])
        print(f"{label:>14} | {i_eff:>6.2f} | {means[label]:>12.5f} | {ratios_str}")

    # -- Validacao da predicao --
    labels = list(CONDITIONS.keys())
    ordem_correta_media = means[labels[2]] > means[labels[1]] > means[labels[0]]

    # Por seed: contar quantas vezes C > B > A
    n_pass = 0
    for i, seed in enumerate(SEEDS):
        r_A = cond_ratios[labels[0]][i]
        r_B = cond_ratios[labels[1]][i]
        r_C = cond_ratios[labels[2]][i]
        if r_C > r_B > r_A:
            n_pass += 1

    print(f"\nOrdem correta (medias): {ordem_correta_media}")
    print(f"Seeds com C>B>A: {n_pass}/{len(SEEDS)}")

    # Passa se a ordem e correta em pelo menos 4/5 seeds E nas medias
    passed = ordem_correta_media and n_pass >= 4
    status = "PASSOU" if passed else "FALHOU"
    print(f"\nTEOREMA R-1 -- {status}")

    # Verificacao qualitativa
    print(f"\nInterpretacao:")
    print(f"  Controle (I=0.05): ratio={means[labels[0]]:.4f} ~= 1.0 "
          f"({'OK' if abs(means[labels[0]]-1.0) < 0.5 else 'DIVERGE'})")
    print(f"  Trauma   (I=0.40): ratio={means[labels[2]]:.4f} >> 1.0 "
          f"({'DILATA' if means[labels[2]] > 1.2 else 'insuficiente'})")

    # -- Salvar --
    output = {
        "experiment": "R-2",
        "description": "Validacao Teorema R-1 -- Dilatacao sob trauma",
        "config": {"N_STEPS": N_STEPS, "N_H1": N_H1, "seeds": SEEDS},
        "means": means,
        "passed": passed,
        "n_seeds_pass": n_pass,
        "all_results": all_results,
    }
    out_path = os.path.join(RESULTS_DIR, "exp_r2_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResultados salvos em: {out_path}")
    print("=" * 65)
    return passed


if __name__ == "__main__":
    run_exp_r2()
