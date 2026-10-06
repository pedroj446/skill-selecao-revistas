# skill-selecao-revistas

Skill para o Claude que seleciona e avalia revistas científicas para submissão. Ela cruza quatro fontes por ISSN:

- **Qualis Periódicos CAPES 2021–2024**
- **SCImago Journal Rank 2025** (SJR, quartil, categorias)
- **DOAJ** (acesso aberto, APC, licença)
- **Acordos CAPES de publicação sem APC** (Springer Nature, Royal Society, ACS, Elsevier, Wiley)

A base unificada tem ~57 mil revistas, uma linha por revista, em `data/revistas.csv.gz`.

## O que a skill faz

- **Onde submeter:** a partir do tema do manuscrito, lista revistas aderentes com filtros de Qualis mínimo, quartil, modelo OA, custo zero para autor vinculado à CAPES e área de avaliação. Entrega opções em três faixas: ambiciosa, realista e segura.
- **Conferir uma revista:** mostra estrato, SJR, OA/APC, acordo CAPES e sinais de alerta de revista predatória.
- **Conferir produção:** recebe uma lista de ISSNs (Lattes, relatório do programa) e devolve a tabela artigo → estrato.

## Instalação

Baixe o repositório como `.zip`, ou empacote a skill com `package_skill.py` do *skill-creator*, e envie em **claude.ai → Configurações → Capacidades → Skills**. O arquivo `SKILL.md` na raiz é o ponto de entrada.

## Uso direto dos scripts (sem Claude)

Os scripts de consulta usam só a biblioteca padrão do Python:

```bash
python scripts/buscar.py --termos "virology; molecular biology; bioinformatics" \
    --qualis-min A2 --sem-apc --min-termos 2 --limite 20
python scripts/consultar.py --issn 1367-4803
```

`python scripts/buscar.py --help` lista todos os filtros.

## Atualizar a base

Baixe as versões novas das fontes (os links estão em `references/fontes-e-ressalvas.md`) e rode, com [uv](https://docs.astral.sh/uv/):

```bash
uv run scripts/construir_base.py \
    --qualis qualis.xlsx --doaj doaj_journalcsv.csv \
    --scimago scimagojr.csv --springer Eligiblejournals_Springer_Nature.pdf \
    --saida data/revistas.csv.gz
```

As dependências (pandas, openpyxl, pypdf) estão declaradas no próprio script (PEP 723). As fontes brutas não são versionadas, por tamanho e por licença.

Versão atual da base: veja `data/metadados.json`.

## Limitações conhecidas

- **Acordo Elsevier:** inferido por editora e modelo híbrido, porque a editora não publica a lista em arquivo. **Acordo Wiley:** não verificado. Os dois precisam ser conferidos na hora da submissão.
- **APC:** vem do DOAJ, é autodeclarada e às vezes está errada. Revistas híbridas fora do DOAJ ficam sem valor de APC.
- **Qualis:** é o do quadriênio 2021–2024. A pontuação de cada estrato no programa depende do documento de área.

Detalhes em `references/fontes-e-ressalvas.md`.

## Fontes e citação

- CAPES. *Qualis Periódicos — classificações publicadas, quadriênio 2021–2024*. Plataforma Sucupira.
- SCImago, (n.d.). *SJR — SCImago Journal & Country Rank* [Portal]. Recuperado em set./2026 de https://www.scimagojr.com
- DOAJ — Directory of Open Access Journals. *Journal CSV*, 05/09/2026. https://doaj.org — CC BY-SA 4.0.
- Springer Nature. *Open access agreement for CAPES — eligible journals*, 31/12/2025.
- Páginas dos acordos CAPES da Royal Society, ACS, Elsevier e Wiley.

## Licenças

- **Código** (`scripts/`, `SKILL.md`, `references/`): MIT, ver `LICENSE`.
- **Dados** (`data/`): ver `LICENSE-DATA.md`. Resumo: CC BY-SA 4.0, herdada do DOAJ, e as colunas derivadas do SCImago só podem ser usadas para fins **não comerciais**, com citação.

## Autor

Pedro Júlio — PPGST/UFPE · ORCID [0009-0001-8832-2084](https://orcid.org/0009-0001-8832-2084)
