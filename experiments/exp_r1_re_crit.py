# -*- coding: utf-8 -*-
"""
Experimento R-1 — Calibração de Re_crit (v1.1)
RHEO Paper 5 | David Ohio | 2026

Objetivo:
    Determinar Re_crit como o valor de Re_A em que T_vivido/T_fisico supera
    o threshold de dilatação (R_DIL_THRESH = 1.5), varrendo amplitudes de
    I_eff crescentes.

Fórmula Re_A (v1.1):
    Re_A = D_H × (τ_pers / τ_ref) × n_H1
    τ_ref = 1/decay_max = 20.0  (baseline, I_eff=0)

Escala esperada (v1.1):
    I_eff=0.05 → Re_A ≈ 0.06  (laminar)
    I_eff=0.20 → Re_A ≈ 0.49  (transitional)
    I_eff=0.40 → Re_A ≈ 3.4   (turbulent)
    R_DIL_THRESH atingido em I_eff ≈ 0.20–0.30 → Re_crit ≈ 0.5–1.5

Hipótese:
    Re_crit = f(theta_warn - theta_rec) ≈ f(0.15) ≈ 1.0
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from rheo import RHEOConfig, RHEOCore, H1Bar

# ── Parâmetros do experimento ─────────────────────────────────────────────────
N_STEPS     = 100
N_H1_OPEN   = 2          # número fixo de H1 abertas durante o experimento
R_DIL_THRESH = 1.5       # threshold de dilatação para definir Re_crit
SEEDS       = [42, 123, 7, 99, 31]
I_EFF_LEVELS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def run_level(i_eff: float, seed: int, cfg: RHEOConfig) -> dict:
    """
    Simula N_STEPS steps com I_eff constante e N_H1_OPEN barras ativas.
    Retorna métricas do experimento.
    """
    rng = np.random.default_rng(seed)
    rheo = RHEOCore(cfg)

    # Campo H inicial próximo de H_NOM com perturbação proporcional a I_eff
    H_NOM = np.array(cfg.H_NOM)

    # Cria H1 bars abertas com pers_H1 = I_eff
    h1_bars = [H1Bar(bar_id=i, birth=0, pers_H1=i_eff) for i in range(N_H1_OPEN)]

    Re_A_history = []

    for t in range(N_STEPS):
        # θ oscila: perturbação proporcional a I_eff + ruído pequeno
        theta = cfg.theta_warn - i_eff * 0.3 + rng.normal(0, 0.01)
        theta = float(np.clip(theta, cfg.theta_recovered, cfg.theta_collapse))

        # H perturba proporcionalmente a I_eff
        H = H_NOM - i_eff * rng.uniform(0.1, 0.3, size=5)
        H = list(np.clip(H, 0.0, 1.0))

        state = rheo.step(t, theta, i_eff, H, h1_bars)
        Re_A_history.append(state.Re_A)

    ratio    = rheo.ratio_subj_fisico
    Re_A_mean = float(np.mean(Re_A_history))
    Re_A_max  = float(np.max(Re_A_history))
    tau_rel_sample = rheo.history[-1].tau_rel if rheo.history else 0.0

    return {
        "i_eff":      i_eff,
        "seed":       seed,
        "Re_A_mean":  round(Re_A_mean, 4),
        "Re_A_max":   round(Re_A_max, 4),
        "tau_rel":    round(tau_rel_sample, 3),
        "ratio":      round(ratio, 4),
        "T_vivido":   round(rheo.T_vivido_total, 3),
        "T_fisico":   round(rheo.T_fisico_total, 3),
        "dilated":    ratio >= R_DIL_THRESH,
    }


def run_exp_r1():
    cfg = RHEOConfig(tick_s=1.0)   # tick=1s para análise limpa de razões
    all_results = []

    print("=" * 70)
    print("EXPERIMENTO R-1 v1.1 -- Calibracao de Re_crit")
    print(f"N_STEPS={N_STEPS} | N_H1={N_H1_OPEN} | R_DIL_THRESH={R_DIL_THRESH}")
    print("Formula: Re_A = D_H x (tau_pers/tau_ref) x n_H1")
    print("=" * 70)
    print(f"{'I_eff':>6} | {'Re_A_mean':>10} | {'Re_A_max':>9} | "
          f"{'tau_rel':>7} | {'ratio':>7} | {'regime':>15}")
    print("-" * 70)

    # Tabela média por nível de I_eff
    level_summary = {}

    for i_eff in I_EFF_LEVELS:
        level_results = []
        for seed in SEEDS:
            r = run_level(i_eff, seed, cfg)
            all_results.append(r)
            level_results.append(r)

        Re_mean_avg  = np.mean([r["Re_A_mean"] for r in level_results])
        Re_max_avg   = np.mean([r["Re_A_max"]  for r in level_results])
        ratio_avg    = np.mean([r["ratio"]      for r in level_results])
        tau_rel_avg  = np.mean([r["tau_rel"]    for r in level_results])
        dilated_frac = np.mean([r["dilated"]    for r in level_results])

        level_summary[i_eff] = {
            "Re_A_mean": float(Re_mean_avg),
            "Re_A_max":  float(Re_max_avg),
            "tau_rel":   float(tau_rel_avg),
            "ratio":     float(ratio_avg),
            "dilated_frac": float(dilated_frac),
        }
        tag = "TURBULENT     " if dilated_frac >= 0.8 else (
              "transitional  " if dilated_frac > 0.2 else "laminar       ")

        print(f"{i_eff:>6.2f} | {Re_mean_avg:>10.4f} | {Re_max_avg:>9.4f} | "
              f"{tau_rel_avg:>7.3f} | {ratio_avg:>7.4f} | {tag}")

    # ── Determinar Re_crit ────────────────────────────────────────────────────
    re_crit_estimate = None
    for i_eff in I_EFF_LEVELS:
        ls = level_summary[i_eff]
        if ls["ratio"] >= R_DIL_THRESH:
            re_crit_estimate = ls["Re_A_mean"]
            print(f"\n>>> Re_crit estimado = {re_crit_estimate:.4f}  "
                  f"(I_eff={i_eff}, ratio={ls['ratio']:.4f})")
            break

    if re_crit_estimate is None:
        re_crit_estimate = level_summary[I_EFF_LEVELS[-1]]["Re_A_mean"]
        print(f"\n>>> Threshold nao atingido -- Re_crit (upper bound) "
              f"= {re_crit_estimate:.4f}")

    # Verificação da hipótese — Re_crit deve ser próximo de 1.0
    delta_theta = cfg.theta_warn - cfg.theta_recovered   # = 0.15
    tau_ref = 1.0 / cfg.decay_max   # = 20.0
    hipotese = delta_theta * tau_ref / cfg.theta_collapse  # escala natural
    print(f"\nHipotese: Re_crit ~= f(delta_theta={delta_theta}) ~= {hipotese:.4f}")
    print(f"Re_crit estimado = {re_crit_estimate:.4f}")
    print(f"Hipotese {'CONFIRMADA (Re_crit < 2.0)' if re_crit_estimate < 2.0 else 'requer revisao'}")

    # ── Salvar resultados ─────────────────────────────────────────────────────
    output = {
        "experiment": "R-1",
        "description": "Calibração de Re_crit",
        "config": {"N_STEPS": N_STEPS, "N_H1": N_H1_OPEN,
                   "R_DIL_THRESH": R_DIL_THRESH, "seeds": SEEDS},
        "re_crit_estimate": re_crit_estimate,
        "level_summary": {str(k): v for k, v in level_summary.items()},
        "all_results": all_results,
    }
    out_path = os.path.join(RESULTS_DIR, "exp_r1_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResultados salvos em: {out_path}")
    print("=" * 70)
    return re_crit_estimate


if __name__ == "__main__":
    run_exp_r1()
