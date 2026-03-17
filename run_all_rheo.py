# -*- coding: utf-8 -*-
"""
run_all_rheo.py — Runner unificado dos experimentos RHEO
David Ohio | 2026

Executa R-1, R-2 e R-3 em sequência e imprime sumário de validação.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from experiments.exp_r1_re_crit  import run_exp_r1
from experiments.exp_r2_dilatacao import run_exp_r2
from experiments.exp_r3_compressao import run_exp_r3


def main():
    print("\n" + "=" * 65)
    print("  RHEO -- Validacao Completa dos Experimentos")
    print("  HUGO AGI Framework -- Paper 5")
    print("  David Ohio | odavidohio@gmail.com | 2026")
    print("=" * 65 + "\n")

    re_crit = run_exp_r1()
    print()
    r2_ok = run_exp_r2()
    print()
    r3_ok = run_exp_r3()

    print("\n" + "=" * 65)
    print("SUMÁRIO DE VALIDAÇÃO RHEO v1.0")
    print("=" * 65)
    print(f"  Exp R-1 (Calibracao Re_crit)   : Re_crit ~= {re_crit:.5f}")
    print(f"  Exp R-2 (Teorema R-1 Dilatacao): {'PASSOU' if r2_ok else 'FALHOU'}")
    print(f"  Exp R-3 (Teorema R-2 Bergson)  : {'PASSOU' if r3_ok else 'FALHOU'}")

    all_pass = r2_ok and r3_ok
    print(f"\n  STATUS GERAL: {'TODOS OS TEOREMAS VALIDADOS' if all_pass else 'REVISAR PARAMETROS'}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
