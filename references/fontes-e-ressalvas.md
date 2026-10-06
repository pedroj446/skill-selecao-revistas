# Fontes, colunas e ressalvas

## Fontes (versões da base atual — confira `data/metadados.json`)

| Fonte | Arquivo | O que traz | Onde baixar |
|---|---|---|---|
| Qualis Periódicos 2021–2024 | `classificacoes_publicadas_todas_as_areas_avaliacao.xlsx` (Sucupira) | ISSN, título, área de avaliação, estrato | Plataforma Sucupira → Qualis → Classificações publicadas → todas as áreas |
| DOAJ | `doaj_journalcsv_AAAAMMDD.csv` | só revistas OA completas: APC, licença, idiomas, palavras-chave, tempo até publicação | doaj.org → Docs → Public data dump → Journal CSV (CC BY-SA 4.0) |
| SCImago Journal Rank 2025 | `scimagojr AAAA.csv` (separador `;`, decimal `,`) | SJR, melhor quartil, categorias, H-index, editora, OA | scimagojr.com/journalrank.php → Download data (uso não comercial com citação) |
| Springer Nature × CAPES | `Eligiblejournals_<data>_Springer_Nature.pdf` | revistas híbridas com APC coberta (só as linhas com "Publish"; as "Subscription … Read" são só leitura e ficam fora) | Portal de Periódicos CAPES → Acordos |
| Royal Society × CAPES | PDF do Portal de Periódicos | 10 títulos, sem APC, CC BY 4.0 | periodicos.capes.gov.br |
| ACS × CAPES | acsopenscience.org/customers/capes | todas as revistas ACS (híbridas com APC coberta; ACS Central Science e Chemical Health & Safety diamante) | — |
| Elsevier × CAPES | elsevier.com/pt-br/open-access/agreements/brazil | >1.600 híbridas, aceites de 01/01/2026 a 31/12/2028; não cobre OA completas nem taxas extras | lista só por busca em agreements.journals.elsevier.com/capes |
| Wiley × CAPES | wiley.com/en-br/publishing/article/open-access/oa-agreement | página bloqueou leitura automática; vínculo não verificado | conferir no site da Wiley |

## Colunas de `revistas.csv.gz`

- `issns`: todos os ISSNs (impresso + eletrônico) ligados entre as fontes.
- `qualis`: melhor estrato entre os ISSNs da revista. `qualis_divergente=sim` em ~20 casos em que ISSN impresso e eletrônico receberam estratos diferentes: mostre os dois.
- `qualis_areas` / `qualis_n_areas`: áreas em que programas publicaram na revista. Mediana de 3 áreas por ISSN; PLOS ONE aparece nas 50.
- `sjr`, `quartil` (melhor quartil entre as categorias), `h_index`, `categorias` (cada uma com o quartil próprio), `areas_scimago`, `scopus=sim` se está no SCImago.
- `doaj`, `oa` (`completo` | `diamante` | vazio = híbrida ou fechada), `oa_fonte` (`doaj` | `scimago`).
- `apc` (`Yes`/`No`), `apc_valor` (texto do DOAJ, pode listar várias moedas), `isencao_apc` (política de isenção para países em desenvolvimento).
- `licenca`, `idiomas`, `semanas_ate_publicar` (média autodeclarada), `palavras_doaj`, `assuntos_doaj`, `url`, `url_autores`.
- `acordo_capes`, `acordo_confianca` (ver SKILL.md).

## Ressalvas conhecidas

1. **Cobertura assimétrica.** Revistas fora do Scopus não têm SJR, e híbridas e fechadas não têm APC na base. A ausência de um dado não significa valor zero.
2. **Ligação por ISSN.** Revistas que trocaram de ISSN ou de título podem aparecer duplicadas ou sem casar. Se `consultar.py` não achar a revista pelo ISSN, tente pelo título.
3. **SCImago vs. lista de editora.** O SCImago às vezes marca como OA uma revista que a editora ainda lista como híbrida (ex.: Oncogene na lista Springer de 31/12/2025). Nesse caso a lista da editora prevalece.
4. **APC do DOAJ é autodeclarada** e às vezes está errada. Confirme no site.
5. **Qualis ≠ pontuação do programa.** O peso de cada estrato e as regras de produção qualificada vêm do documento de área. A skill não tem os pesos por área.
6. **Acordos mudam todo ano** (cotas podem esgotar, listas são atualizadas). Trate qualquer acordo como "verificar no momento da submissão".
