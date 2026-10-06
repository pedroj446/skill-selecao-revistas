#!/usr/bin/env python3
"""Busca revistas por escopo e filtros na base unificada (só biblioteca padrão).

Exemplos:
    python scripts/buscar.py --termos "virology; computational biology; bioinformatics" \
        --qualis-min A2 --limite 20
    python scripts/buscar.py --termos "matrix metalloproteinase; oncology" \
        --sem-apc --ordenar qualis
    python scripts/buscar.py --termos "infectious diseases" --oa completo --doaj --formato csv

Termos: separados por ';'. Cada termo é procurado (sem diferenciar maiúsculas)
no título, nas categorias e áreas do SCImago e nas palavras-chave e assuntos
do DOAJ. Use os nomes de categoria do SCImago em inglês sempre que possível
(lista em references/categorias_scimago.txt).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data" / "revistas.csv.gz"
ESTRATOS = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]
QUARTIS = ["Q1", "Q2", "Q3", "Q4"]
CAMPOS_TEXTO = ["titulo", "categorias", "areas_scimago", "palavras_doaj", "assuntos_doaj"]


def carregar(path=BASE):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sem_custo(r):
    """APC zero ou coberta por acordo CAPES com lista oficial/editora toda."""
    if r["oa"] == "diamante" or r["apc"] == "No":
        return True
    return r["acordo_confianca"] in ("lista_oficial", "editora_toda")


def casa(termo, texto):
    """Casamento por palavra inteira: 'network' não casa com 'Internet'."""
    return re.search(r"(?<![a-z0-9])" + re.escape(termo) + r"(?![a-z0-9])", texto) is not None


def pontuar(r, termos):
    texto = " | ".join(r[c] for c in CAMPOS_TEXTO).lower()
    cat = r["categorias"].lower()
    casados = [t for t in termos if casa(t, texto)]
    # Casar na categoria do SCImago vale mais que casar em palavra-chave solta.
    return sum(2 if casa(t, cat) else 1 for t in casados), len(casados)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--termos", required=True)
    ap.add_argument("--qualis-min", choices=ESTRATOS, help="estrato mínimo (A1 é o topo)")
    ap.add_argument("--quartil-max", choices=QUARTIS, help="pior quartil SJR aceito")
    ap.add_argument("--oa", choices=["completo", "diamante", "nao-oa", "qualquer"], default="qualquer")
    ap.add_argument("--sem-apc", action="store_true", help="só revistas sem custo de publicação para autor CAPES")
    ap.add_argument("--acordo", action="store_true", help="só revistas com algum acordo CAPES")
    ap.add_argument("--doaj", action="store_true", help="só revistas indexadas no DOAJ")
    ap.add_argument("--scopus", action="store_true", help="só revistas com SJR (indexadas no Scopus)")
    ap.add_argument("--area", help="só revistas onde programas desta área CAPES publicaram (ex.: 'MEDICINA II')")
    ap.add_argument("--min-termos", type=int, default=1, help="mínimo de termos que precisam casar")
    ap.add_argument("--ordenar", choices=["relevancia", "sjr", "qualis"], default="relevancia")
    ap.add_argument("--limite", type=int, default=25)
    ap.add_argument("--formato", choices=["md", "csv"], default="md")
    ap.add_argument("--base", default=str(BASE))
    a = ap.parse_args(argv)

    termos = [t.strip().lower() for t in a.termos.split(";") if t.strip()]
    linhas = carregar(a.base)
    res = []
    for r in linhas:
        if a.qualis_min and (r["qualis"] not in ESTRATOS or ESTRATOS.index(r["qualis"]) > ESTRATOS.index(a.qualis_min)):
            continue
        if a.quartil_max and (r["quartil"] not in QUARTIS or QUARTIS.index(r["quartil"]) > QUARTIS.index(a.quartil_max)):
            continue
        if a.oa == "completo" and r["oa"] not in ("completo", "diamante"):
            continue
        if a.oa == "diamante" and r["oa"] != "diamante":
            continue
        if a.oa == "nao-oa" and r["oa"]:
            continue
        if a.sem_apc and not sem_custo(r):
            continue
        if a.acordo and not r["acordo_capes"]:
            continue
        if a.area and a.area.strip().upper() not in [x.strip().upper() for x in r["qualis_areas"].split(";")]:
            continue
        if a.doaj and r["doaj"] != "sim":
            continue
        if a.scopus and r["scopus"] != "sim":
            continue
        pts, n_casados = pontuar(r, termos)
        if n_casados < a.min_termos:
            continue
        r["_pts"] = pts
        res.append(r)

    sjr = lambda r: float(r["sjr"]) if r["sjr"] else -1.0
    qual = lambda r: ESTRATOS.index(r["qualis"]) if r["qualis"] in ESTRATOS else 99
    if a.ordenar == "sjr":
        res.sort(key=lambda r: (-sjr(r), qual(r)))
    elif a.ordenar == "qualis":
        res.sort(key=lambda r: (qual(r), -sjr(r)))
    else:
        res.sort(key=lambda r: (-r["_pts"], qual(r), -sjr(r)))

    total = len(res)
    res = res[: a.limite]
    cols = ["titulo", "issns", "qualis", "sjr", "quartil", "oa", "apc", "apc_valor",
            "acordo_capes", "acordo_confianca", "doaj", "categorias"]

    if a.formato == "csv":
        w = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(res)
    else:
        print(f"{total} revistas atendem aos filtros; mostrando {len(res)}.\n")
        print("| # | Revista | ISSN | Qualis | SJR (Q) | OA | APC | Acordo CAPES |")
        print("|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(res, 1):
            apc = {"No": "não", "Yes": (r["apc_valor"] or "sim")}.get(r["apc"], "?")
            if r["oa"] == "diamante":
                apc = "não"
            acordo = f"{r['acordo_capes']} [{r['acordo_confianca']}]" if r["acordo_capes"] else "—"
            sj = f"{r['sjr']} ({r['quartil']})" if r["sjr"] else "—"
            print(f"| {i} | {r['titulo']} | {r['issns']} | {r['qualis'] or '—'} | {sj} | "
                  f"{r['oa'] or 'híbrida/fechada'} | {apc} | {acordo} |")
        print("\nQualis 2021–2024 · SJR/quartil SCImago · APC autodeclarada no DOAJ ('?' = fora do DOAJ; "
              "confirmar no site) · acordo vale só com autor correspondente de instituição participante.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
