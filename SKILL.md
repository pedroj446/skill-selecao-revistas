---
name: selecao-revistas
description: Seleciona e avalia revistas científicas para submissão cruzando Qualis CAPES 2021–2024, SJR/quartil (SCImago), DOAJ e acordos CAPES de APC (Springer Nature, Elsevier, Wiley, ACS, Royal Society). Use sempre que o usuário perguntar onde submeter um artigo, qual revista escolher, pedir revistas A1/A2 ou Q1 sobre um tema, quiser saber o Qualis, o SJR, a APC ou se uma revista tem acordo CAPES, quiser publicar sem pagar, desconfiar de revista predatória, ou precisar conferir como as publicações dele ou do programa pontuam na avaliação CAPES — mesmo que fale só "qual revista?", "isso é A1?" ou "essa revista presta?".
---

# Seleção de revistas e avaliação CAPES

A base local (`data/revistas.csv.gz`, ~57 mil revistas, uma linha por revista) une quatro fontes por ISSN. Os scripts usam só a biblioteca padrão do Python e rodam em menos de 1 s. **Nunca carregue o CSV inteiro no contexto**: chame os scripts.

```
python scripts/buscar.py   --termos "virology; oncology" [filtros]   # lista ranqueada
python scripts/consultar.py --issn 1234-5678 | --titulo "trecho"     # ficha completa
```

Antes de responder, leia `data/metadados.json` para saber a data de cada fonte. Se alguma tiver mais de 12 meses, avise o usuário e mostre como atualizar (seção "Atualizar a base").

## Modo 1 — Onde submeter um manuscrito

1. **Montar o perfil do manuscrito.** Extraia do texto ou da conversa: tema central, tipo de artigo (original, revisão, short communication, data/software paper), abordagem (experimental, computacional, clínica) e restrições do usuário: orçamento para APC, Qualis ou quartil mínimo, prazo, idioma, área CAPES do programa. Pergunte só o que mudar o resultado e não puder ser inferido. O orçamento costuma ser a pergunta que mais importa.

2. **Traduzir o tema em termos de busca.** Use nomes de categoria do SCImago em inglês (`references/categorias_scimago.txt`, 310 categorias) mais 2–4 palavras-chave livres, que casam com as palavras-chave do DOAJ. Não existe categoria "Bioinformatics" no SCImago: para trabalho computacional em biologia combine `Molecular Biology`, `Genetics`, `Computer Science Applications`, `Health Informatics`, e o termo livre `bioinformatics`.

3. **Buscar em duas passadas.**
   - Ampla: termos + filtro de qualidade mínima (`--qualis-min` ou `--quartil-max`), `--limite 30`.
   - Restrita: a ampla + as restrições do usuário (`--sem-apc`, `--oa completo`, `--area "MEDICINA II"`) e `--min-termos 2` para exigir aderência a mais de um aspecto do tema.
   Se uma passada retornar menos de 5 revistas, afrouxe um filtro por vez e diga qual afrouxou.

4. **Filtrar por escopo, não por métrica.** Para os 8–12 melhores, rode `consultar.py` e leia categorias e palavras-chave do DOAJ. Descarte as revistas em que o tema do manuscrito seria periférico. Uma A1 fora do escopo vira desk reject e custa semanas. Se houver acesso à web, abra a página de *Aims & Scope* e o guia do autor das finalistas (`url`, `url_autores`) para confirmar escopo, tipo de artigo aceito e APC.

5. **Entregar 4–6 revistas em três faixas.** A **ambiciosa** tem a maior métrica com escopo plausível. A **realista** tem escopo forte e métrica boa. A **segura** tem escopo exato, decisão rápida e custo baixo. Para cada uma informe Qualis, SJR (quartil), modelo OA, APC e acordo CAPES com o nível de confiança, mais uma linha dizendo por que o manuscrito cabe ali. Termine com o que o usuário precisa conferir antes de submeter.

## Modo 2 — Conferir uma revista ou a produção para a CAPES

- **Uma revista:** `consultar.py --issn` (preferível) ou `--titulo`. Responda direto: estrato, SJR/quartil, OA/APC, acordo e alertas.
- **Lista de publicações** (Lattes, relatório do programa): rode `consultar.py --issn` para cada ISSN e monte uma tabela artigo → estrato. Conte quantos são A1–A4. Revistas sem Qualis precisam ser apontadas, não omitidas.
- **Suspeita de predatória:** a revista ausente de Qualis, SCImago e DOAJ ao mesmo tempo é sinal de alerta, não prova. Combine com os sinais clássicos: promessa de revisão em dias, e-mail de convite em massa, conselho editorial não verificável, APC cobrada só depois do aceite.

## Regras de interpretação — leia antes de afirmar qualquer coisa

Os detalhes estão em `references/fontes-e-ressalvas.md`. O essencial:

- **Qualis é o do quadriênio 2021–2024.** Cada revista tem estrato único (A1 > A2 > A3 > A4 > B1 > … > C). A coluna `qualis_areas` lista as áreas de avaliação em que programas publicaram naquela revista. Não é a área "dona" da revista e não restringe onde ela vale. Não afirme como as publicações serão pontuadas em 2025–2028: as regras do próximo quadriênio vêm do documento de área vigente, e o usuário deve conferi-lo.
- **Acordos CAPES têm níveis de confiança diferentes.** Mostre sempre o nível:
  - `lista_oficial`: o ISSN está na lista da editora (Springer Nature, Royal Society). É confiável.
  - `editora_toda`: o acordo cobre todas as revistas da editora (ACS). É confiável.
  - `inferido_editora`: Elsevier. O acordo cobre "mais de 1.600 híbridas", mas a editora não publica a lista em CSV, então o vínculo foi inferido por editora e modelo híbrido. Mande conferir em agreements.journals.elsevier.com/capes.
  - `nao_verificado`: Wiley. A página do acordo não pôde ser lida, então o vínculo é só um candidato a confirmar com a Wiley.
  - Todo acordo exige que o **autor correspondente** seja de instituição participante, com ORCID vinculado ao cadastro CAPES, e vale pela data de aceite. Diga isso sempre que o acordo pesar na escolha.
- **A APC vem do DOAJ, que é autodeclarado.** Confirme no site da revista antes de dizer que é gratuita. Há casos conhecidos de divergência. Para híbridas fora do DOAJ a APC fica "?": não invente valor.
- **O modelo OA** vem do DOAJ (`oa_fonte=doaj`, mais confiável) ou só do SCImago (`oa_fonte=scimago`). Quando os dois discordam de uma lista oficial de editora, vale a lista.
- **Métricas não são escopo.** Nunca recomende uma revista só pelo SJR ou pelo Qualis.
- Expresse a confiança: dado da base = certeza **sobre o que a fonte diz**; aderência de escopo = julgamento seu, apresente como tal.

## Atualizar a base

As fontes brutas não vão na skill porque são grandes demais. Para atualizar, baixe as versões novas e rode no computador do usuário:

```
uv run scripts/construir_base.py --qualis <qualis.xlsx> --doaj <doaj.csv> \
    --scimago <scimago.csv> --springer <springer_capes.pdf> --saida data/revistas.csv.gz
```

As origens de cada arquivo estão em `references/fontes-e-ressalvas.md`. Depois de reconstruir, reempacote a skill.
