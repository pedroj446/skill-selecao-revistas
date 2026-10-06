#!/usr/bin/env python3
"""Ficha completa de uma revista, por ISSN ou trecho do título (só biblioteca padrão).

Exemplos:
    python scripts/consultar.py --issn 1932-6203
    python scripts/consultar.py --titulo "virology journal"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar import BASE, carregar  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--issn")
    g.add_argument("--titulo")
    ap.add_argument("--limite", type=int, default=5)
    ap.add_argument("--base", default=str(BASE))
    a = ap.parse_args(argv)

    linhas = carregar(a.base)
    if a.issn:
        alvo = re.sub(r"[^0-9Xx]", "", a.issn).upper()
        alvo = f"{alvo[:4]}-{alvo[4:]}"
        achados = [r for r in linhas if alvo in r["issns"].split()]
    else:
        t = a.titulo.lower()
        achados = [r for r in linhas if t in r["titulo"].lower()]
        achados.sort(key=lambda r: (r["titulo"].lower() != t, len(r["titulo"])))

    if not achados:
        print("Nenhuma revista encontrada na base. Ela pode não estar no Qualis 2021–2024, "
              "no SCImago nem no DOAJ — o que, por si só, é um sinal de alerta.")
        return 1
    for r in achados[: a.limite]:
        print("=" * 70)
        for k, v in r.items():
            if v:
                print(f"{k:22} {v}")
    if len(achados) > a.limite:
        print(f"\n(+{len(achados) - a.limite} outras correspondências; refine o título)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
