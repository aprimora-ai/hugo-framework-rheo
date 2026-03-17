# -*- coding: utf-8 -*-
"""
Experimento R-3 — Validacao do Teorema R-2 (Compressao retrospectiva)
RHEO Paper 5 | David Ohio | 2026

Teorema R-2:
    Se I_eff ~= 0 e n_H1_unres = 0 para t in [t1,t2],
    entao T_rec(r1,r2) -> 0.

Paradoxo de Bergson:
    Um intervalo de 200 steps calmos e retrospectivamente percebido
    como MENOR do que um intervalo de 20 steps de trauma.

Protocolo:
    Fase 1 (trauma):  20 steps,  I_eff = 0.40, N_H1 = 2
    Fase 2 (repouso): 200 steps, I_eff = 0.02, N_H1 = 0

    Calcular:
      T_rec_trauma  = T_rec(0, 19)       [reconstrucao da fase 1]
      T_rec_repouso = T_rec(20, 219)     [reconstrucao da fase 2]

Predicao (Paradoxo de Bergson):
    T_rec_trauma >> T_rec_repouso
    apesar de T_fisico_trauma (20s) << T_fisico_repouso (200s)

Validacao:
    PASSA se T_rec_trauma > T_rec_repouso em pelo menos 4/5 seeds.
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from rheo import RHEOConfig, RHEOCore, H1Bar

N_TRAUMA  = 20
N_REPOUSO = 200
I_TRAUMA  = 0.40
I_REPOUSO = 0.02
N_H1_TRAUMA  = 2
N_H1_REPOUSO = 0
SEEDS = [42, 123, 7, 99, 31]
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def run_seed(seed: int, cfg: RHEOConfig) -> dict:
    rng  = np.random.default_rng(seed)
    rheo = RHEOCore(cfg)
    H_NOM = np.array(cfg.H_NOM)

    # -- Fase 1: trauma --
    h1_trauma = [H1Bar(bar_id=i, birth=0, pers_H1=I_TRAUMA) for i in range(N_H1_TRAUMA)]

    for t in range(N_TRAUMA):
        theta = cfg.theta_warn - I_TRAUMA * 0.3 + rng.normal(0, 0.01)
        theta = float(np.clip(theta, cfg.theta_recovered, cfg.theta_collapse))
        H = list(np.clip(H_NOM - I_TRAUMA * rng.uniform(0.1, 0.3, 5), 0.0, 1.0))
        rheo.step(t, theta, I_TRAUMA, H, h1_trauma)

    # Resolve as H1 no fim da fase de trauma
    for bar in h1_trauma:
        bar.resolved = True
        bar.death    = N_TRAUMA - 1

    # -- Fase 2: repouso --
    h1_repouso: list[H1Bar] = []

    for t in range(N_TRAUMA, N_TRAUMA + N_REPOUSO):
        theta = cfg.theta_recovered + rng.normal(0, 0.005)
        theta = float(np.clip(theta, cfg.theta_recovered, cfg.theta_warn))
        H = list(np.clip(H_NOM + rng.normal(0, 0.01, 5), 0.0, 1.0))
        rheo.step(t, theta, I_REPOUSO, H, h1_repouso)

    # -- Reconstrucao retrospectiva --
    T_rec_trauma  = rheo.T_rec(0, N_TRAUMA - 1, h1_trauma)
    T_rec_repouso = rheo.T_rec(N_TRAUMA, N_TRAUMA + N_REPOUSO - 1, h1_repouso)

    # T_vivido direto (fluxo real — nao retrospectivo)
    T_viv_trauma  = sum(s.T_vivido_step for s in rheo.history if s.t < N_TRAUMA)
    T_viv_repouso = sum(s.T_vivido_step for s in rheo.history if s.t >= N_TRAUMA)

    return {
        "seed":           seed,
        "T_rec_trauma":   round(T_rec_trauma, 5),
        "T_rec_repouso":  round(T_rec_repouso, 5),
        "T_viv_trauma":   round(T_viv_trauma, 3),
        "T_viv_repouso":  round(T_viv_repouso, 3),
        "T_fis_trauma":   N_TRAUMA  * cfg.tick_s,
        "T_fis_repouso":  N_REPOUSO * cfg.tick_s,
        "bergson_ok":     T_rec_trauma > T_rec_repouso,
        "ratio_rec":      round(T_rec_trauma / max(T_rec_repouso, 1e-9), 4),
    }


def run_exp_r3():
    cfg = RHEOConfig(tick_s=1.0)
    all_results = []

    print("=" * 70)
    print("EXPERIMENTO R-3 -- Paradoxo de Bergson (Compressao retrospectiva)")
    print(f"Trauma: {N_TRAUMA} steps (I={I_TRAUMA}) | "
          f"Repouso: {N_REPOUSO} steps (I={I_REPOUSO})")
    print("Predicao: T_rec(trauma) >> T_rec(repouso)  [apesar de 20 << 200 steps]")
    print("=" * 70)
    print(f"{'seed':>5} | {'T_rec_tr':>10} | {'T_rec_rep':>10} | "
          f"{'ratio':>7} | {'Bergson':>8} | {'T_viv_tr':>9} | {'T_viv_rep':>10}")
    print("-" * 70)

    for seed in SEEDS:
        r = run_seed(seed, cfg)
        all_results.append(r)
        tag = "OK" if r["bergson_ok"] else "FAIL"
        print(f"{r['seed']:>5} | {r['T_rec_trauma']:>10.5f} | "
              f"{r['T_rec_repouso']:>10.5f} | {r['ratio_rec']:>7.4f} | "
              f"{tag:>8} | {r['T_viv_trauma']:>9.3f} | {r['T_viv_repouso']:>10.3f}")

    # -- Sintese --
    n_pass = sum(r["bergson_ok"] for r in all_results)
    mean_rec_trauma  = np.mean([r["T_rec_trauma"]  for r in all_results])
    mean_rec_repouso = np.mean([r["T_rec_repouso"] for r in all_results])
    mean_ratio       = np.mean([r["ratio_rec"]     for r in all_results])

    passed = n_pass >= 4
    status = "PASSOU" if passed else "FALHOU"

    print("-" * 70)
    print(f"{'MEDIA':>5} | {mean_rec_trauma:>10.5f} | {mean_rec_repouso:>10.5f} | "
          f"{mean_ratio:>7.4f} | {n_pass}/{len(SEEDS)} pass")

    print(f"\nTEOREMA R-2 (Paradoxo Bergson) -- {status}")
    print(f"\nInterpretacao:")
    print(f"  T_rec medio -- trauma  ({N_TRAUMA}s fisicos) : {mean_rec_trauma:.5f}")
    print(f"  T_rec medio -- repouso ({N_REPOUSO}s fisicos): {mean_rec_repouso:.5f}")
    print(f"  O agente percebe o trauma ~{mean_ratio:.1f}x 'mais longo'")
    print(f"  apesar de ter durado {N_TRAUMA/N_REPOUSO:.0%} do tempo fisico do repouso.")

    # -- Salvar --
    output = {
        "experiment": "R-3",
        "description": "Paradoxo de Bergson -- Compressao retrospectiva",
        "config": {
            "N_TRAUMA": N_TRAUMA, "N_REPOUSO": N_REPOUSO,
            "I_TRAUMA": I_TRAUMA, "I_REPOUSO": I_REPOUSO,
            "seeds": SEEDS,
        },
        "means": {
            "T_rec_trauma": float(mean_rec_trauma),
            "T_rec_repouso": float(mean_rec_repouso),
            "ratio": float(mean_ratio),
        },
        "passed": passed,
        "n_seeds_pass": n_pass,
        "all_results": all_results,
    }
    out_path = os.path.join(RESULTS_DIR, "exp_r3_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResultados salvos em: {out_path}")
    print("=" * 70)
    return passed


if __name__ == "__main__":
    run_exp_r3()
