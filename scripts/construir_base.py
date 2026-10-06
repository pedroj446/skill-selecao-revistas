# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "openpyxl", "pypdf"]
# ///
"""Reconstrói data/revistas.csv.gz a partir das fontes brutas.

Uso (gerenciado com uv):
    uv run scripts/construir_base.py \
        --qualis qualis_2021_2024.xlsx \
        --doaj doaj_AAAAMMDD.csv \
        --scimago scimago_AAAA.csv \
        --springer springer_capes_AAAAMMDD.pdf \
        --saida data/revistas.csv.gz

Cada revista vira uma linha. As fontes são ligadas por ISSN (impresso e
eletrônico) com union-find, porque nenhuma fonte tem todos os ISSNs de uma
mesma revista.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import pypdf

ISSN_RE = re.compile(r"(\d{4})-?(\d{3}[\dXx])")
ESTRATOS = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]
QUARTIS = ["Q1", "Q2", "Q3", "Q4"]

# Títulos cobertos pelo acordo CAPES–Royal Society (PDF do Portal de Periódicos).
ROYAL_SOCIETY = [
    r"^Philosophical Transactions of the Royal Society A",
    r"^Philosophical Transactions of the Royal Society B",
    r"^Proceedings of the Royal Society A",
    r"^Proceedings of the Royal Society B",
    r"^Biology Letters$",
    r"^Journal of the Royal Society Interface$",
    r"^Interface Focus$",
    r"^Open Biology$",
    r"^Royal Society Open Science$",
    r"^Notes and Records",
]


def norm_issns(texto) -> list[str]:
    if not isinstance(texto, str):
        return []
    return [f"{a}-{b.upper()}" for a, b in ISSN_RE.findall(texto)]


class UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, issns):
        issns = list(issns)
        for i in issns:
            self.find(i)
        for i in issns[1:]:
            ra, rb = self.find(issns[0]), self.find(i)
            if ra != rb:
                self.p[rb] = ra


def ler_qualis(path):
    q = pd.read_excel(path, dtype=str)
    q.columns = ["issn", "titulo", "area", "estrato"]
    q["area"] = q["area"].str.strip()
    q["issn"] = q["issn"].map(lambda s: (norm_issns(s) or [None])[0])
    return q.dropna(subset=["issn"])


def ler_doaj(path):
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    d = d.rename(columns={
        "Journal title": "titulo",
        "Journal URL": "url",
        "Journal ISSN (print version)": "pissn",
        "Journal EISSN (online version)": "eissn",
        "Keywords": "palavras",
        "Languages in which the journal accepts manuscripts": "idiomas",
        "Publisher": "editora",
        "Country of publisher": "pais",
        "Journal license": "licenca",
        "Review process": "revisao",
        "Average number of weeks between article submission and publication": "semanas",
        "APC": "apc",
        "APC amount": "apc_valor",
        "Journal waiver policy (for developing country authors etc)": "isencao",
        "Subjects": "assuntos",
        "URL for journal's instructions for authors": "url_autores",
    })
    d["issns"] = (d["pissn"] + " " + d["eissn"]).map(norm_issns)
    return d


def ler_scimago(path):
    s = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False)
    s.columns = [
        "rank", "sourceid", "titulo", "tipo", "issn", "editora", "oa", "oa_diamante",
        "sjr", "quartil", "h", "docs_ano", "docs_3a", "refs", "cit_3a", "citaveis_3a",
        "cit_doc_2a", "ref_doc", "pct_fem", "overton", "pais", "regiao", "editora2",
        "cobertura", "categorias", "areas",
    ]
    s = s[s["tipo"].isin(["journal", "trade journal"])].copy()
    s["sjr_num"] = pd.to_numeric(s["sjr"].str.replace(",", "."), errors="coerce")
    s["issns"] = s["issn"].map(norm_issns)
    return s


def ler_springer(path):
    texto = "\n".join(p.extract_text() for p in pypdf.PdfReader(path).pages)
    issns = []
    for linha in texto.splitlines():
        if re.match(r"^\d+ \d+ ", linha) and "springer.com/" in linha:
            m = ISSN_RE.findall(linha)
            if m:
                a, b = m[0]
                issns.append(f"{a}-{b.upper()}")
    return set(issns)


def melhor(valores, ordem):
    vals = [v for v in valores if v in ordem]
    return min(vals, key=ordem.index) if vals else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qualis", required=True)
    ap.add_argument("--doaj", required=True)
    ap.add_argument("--scimago", required=True)
    ap.add_argument("--springer", required=True)
    ap.add_argument("--saida", default="data/revistas.csv.gz")
    a = ap.parse_args()

    q, d, s = ler_qualis(a.qualis), ler_doaj(a.doaj), ler_scimago(a.scimago)
    springer = ler_springer(a.springer)

    uf = UF()
    for issns in s["issns"]:
        if issns:
            uf.union(issns)
    for issns in d["issns"]:
        if issns:
            uf.union(issns)
    for i in q["issn"]:
        uf.union([i])

    reg: dict[str, dict] = {}

    def r(issn):
        k = uf.find(issn)
        return reg.setdefault(k, {"issns": set(), "qualis": [], "titulos_q": [],
                                  "areas_q": set(), "doaj": None, "sci": None})

    for row in q.itertuples():
        e = r(row.issn)
        e["issns"].add(row.issn)
        e["qualis"].append(row.estrato)
        e["titulos_q"].append(row.titulo)
        e["areas_q"].add(row.area)
    for row in d.itertuples():
        if row.issns:
            e = r(row.issns[0])
            e["issns"].update(row.issns)
            e["doaj"] = row
    # Se dois registros SCImago caírem no mesmo grupo, fica o de maior SJR.
    for row in s.sort_values("sjr_num", na_position="first").itertuples():
        if row.issns:
            e = r(row.issns[0])
            e["issns"].update(row.issns)
            e["sci"] = row

    rs_re = [re.compile(p, re.I) for p in ROYAL_SOCIETY]
    linhas = []
    for e in reg.values():
        sci, dj = e["sci"], e["doaj"]
        editora = (sci.editora if sci is not None else "") or (dj.editora if dj is not None else "")
        titulo = (sci.titulo if sci is not None else "") or (dj.titulo if dj is not None else "") \
            or (e["titulos_q"][0] if e["titulos_q"] else "")
        no_springer = bool(e["issns"] & springer)  # a lista Springer só traz híbridas
        oa_fonte = "doaj" if dj is not None else (
            "scimago" if sci is not None and sci.oa == "Yes" and not no_springer else "")
        oa_completo = bool(oa_fonte)

        # Acordos CAPES — o nível de confiança vai junto do nome do acordo.
        acordo, conf = "", ""
        if no_springer:
            acordo, conf = "Springer Nature", "lista_oficial"
        elif sci is not None and re.search(r"Royal Society Publishing|^The Royal Society$", sci.editora) \
                and any(p.search(sci.titulo) for p in rs_re):
            acordo, conf = "Royal Society", "lista_oficial"
        elif re.fullmatch(r"American Chemical Society", editora or ""):
            acordo, conf = "ACS", "editora_toda"
        elif re.match(r"Elsevier", editora or "") and not oa_completo:
            acordo, conf = "Elsevier (híbridas)", "inferido_editora"
        elif re.search(r"Wiley", editora or "") and not oa_completo:
            acordo, conf = "Wiley", "nao_verificado"

        estrato = melhor(e["qualis"], ESTRATOS)
        linhas.append({
            "titulo": titulo,
            "issns": " ".join(sorted(e["issns"])),
            "editora": editora,
            "pais": (sci.pais if sci is not None else "") or (dj.pais if dj is not None else ""),
            "qualis": estrato,
            "qualis_divergente": "sim" if len(set(e["qualis"])) > 1 else "",
            "qualis_n_areas": len(e["areas_q"]),
            "qualis_areas": "; ".join(sorted(e["areas_q"])),
            "sjr": "" if sci is None or pd.isna(sci.sjr_num) else f"{sci.sjr_num:.3f}",
            "quartil": sci.quartil if sci is not None and sci.quartil in QUARTIS else "",
            "h_index": sci.h if sci is not None else "",
            "categorias": sci.categorias if sci is not None else "",
            "areas_scimago": sci.areas if sci is not None else "",
            "scopus": "sim" if sci is not None else "",
            "doaj": "sim" if dj is not None else "",
            "oa": "completo" if oa_completo else ("diamante" if sci is not None and sci.oa_diamante == "Yes" else ""),
            "oa_fonte": oa_fonte,
            "oa_diamante": "sim" if sci is not None and sci.oa_diamante == "Yes" else "",
            "apc": (dj.apc if dj is not None else ""),
            "apc_valor": (dj.apc_valor if dj is not None else ""),
            "isencao_apc": (dj.isencao if dj is not None else ""),
            "licenca": (dj.licenca if dj is not None else ""),
            "idiomas": (dj.idiomas if dj is not None else ""),
            "semanas_ate_publicar": (dj.semanas if dj is not None else ""),
            "palavras_doaj": (dj.palavras if dj is not None else ""),
            "assuntos_doaj": (dj.assuntos if dj is not None else ""),
            "url": (dj.url if dj is not None else ""),
            "url_autores": (dj.url_autores if dj is not None else ""),
            "acordo_capes": acordo,
            "acordo_confianca": conf,
        })

    out = pd.DataFrame(linhas)
    out["oa"] = out.apply(lambda x: "diamante" if x.oa_diamante == "sim" else x.oa, axis=1)
    out = out.drop(columns=["oa_diamante"])
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.saida, index=False, compression="gzip")

    meta = {
        "gerado_em": date.today().isoformat(),
        "fontes": {
            "qualis": Path(a.qualis).name, "doaj": Path(a.doaj).name,
            "scimago": Path(a.scimago).name, "springer": Path(a.springer).name,
        },
        "n_revistas": len(out),
        "n_com_qualis": int((out.qualis != "").sum()),
        "n_com_sjr": int((out.sjr != "").sum()),
        "n_doaj": int((out.doaj == "sim").sum()),
        "acordos": out.acordo_capes.value_counts().to_dict(),
        "n_springer_lista": len(springer),
    }
    Path(a.saida).with_name("metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
