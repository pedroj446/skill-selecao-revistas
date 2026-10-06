# Licença dos dados (`data/`)

`data/revistas.csv.gz` é uma obra derivada de várias fontes, cada uma com seus próprios termos:

| Colunas | Fonte | Termos |
|---|---|---|
| `doaj`, `oa`, `apc`, `apc_valor`, `isencao_apc`, `licenca`, `idiomas`, `semanas_ate_publicar`, `palavras_doaj`, `assuntos_doaj`, `url`, `url_autores` | DOAJ (journal CSV) | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): atribuição + compartilhamento pelos mesmos termos |
| `sjr`, `quartil`, `h_index`, `categorias`, `areas_scimago`, `scopus` | SCImago Journal & Country Rank | uso **não comercial** com citação ("All the information shown in the SCImago Journal & Country Rank website can be used for non-commercial purposes as long as it is cited") |
| `qualis`, `qualis_areas`, `qualis_n_areas`, `qualis_divergente` | CAPES — Plataforma Sucupira | dado público governamental |
| `acordo_capes`, `acordo_confianca` | listas e páginas públicas das editoras | fatos (ISSN ∈ lista) |

O arquivo como um todo é distribuído sob **CC BY-SA 4.0**. As colunas derivadas do SCImago estão sujeitas, além disso, à condição de uso não comercial do SCImago. Ao reutilizar, cite as fontes conforme o `README.md`.

Os dados são fornecidos "como estão", sem garantia de exatidão. Confira sempre na fonte original antes de decisões de submissão ou de avaliação.
