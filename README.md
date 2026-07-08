# Instagram Campaign Analytics

Pipeline completo para analisar perfis de Instagram (business/creator) via Graph API da Meta e gerar relatórios de resultados: apresentação PPTX com transições, análise de campanhas com métricas privadas (Insights), benchmark de concorrentes e exportação em PDF.

Adaptado do projeto [Analise_instagram](https://github.com/GabrielGalani/Analise_instagram), estendido com análise de campanhas, insights por post, comparativo de concorrentes e geração de decks.

## O que ele faz

- **Coleta** posts, curtidas e comentários de qualquer conta business/creator (Graph API v21)
- **Classifica posts por campanha** via keywords configuráveis nas legendas
- **Coleta Insights privados** por post: visualizações, alcance, compartilhamentos, salvamentos (para contas que você administra)
- **Benchmark de concorrentes** via business_discovery: seguidores, volume de posts e engajamento médio de qualquer conta business, sem acesso à conta
- **Gera apresentação PPTX** (pptxgenjs) com gráficos, capas reais dos posts nos formatos originais (1:1, 4:5, 9:16) e insights automáticos
- **Injeta transições de slide** (fade, morph, push, zoom) no PPTX pronto, algo que o pptxgenjs não suporta
- **Exporta PDF** de decks HTML via Chrome headless

## Uso rápido

```bash
# 1. Configure o .env (copie de .env.example) com seu ACCESS_TOKEN da Meta
# 2. Pipeline completo: coleta -> análise -> gráficos -> deck PPTX
./gerar_relatorio.sh <username> "Nome do Cliente"
```

### Análise de campanhas

```bash
# defina as campanhas em data/gold/<username>_campanhas_config.json
# (modelo em examples/campanhas_config.example.json)
python3 scr/extract_insights_campanhas.py <username>
```

### Concorrentes

```bash
python3 scr/extract_concorrentes.py <seu_ig_user_id> perfil1 perfil2 perfil3
```

### Transições no PPTX

```bash
python3 tools/add_transitions.py apresentacao.pptx --zoom 1 --morph 9-12
```

Morph exige PowerPoint 2019+; degrada para fade em versões antigas.

### PDF de deck HTML

```bash
python3 tools/html_deck_to_pdf.py deck.html saida.pdf
```

## Pré-requisitos

1. Conta Instagram **Business ou Creator** vinculada a uma Página do Facebook
2. App em [developers.facebook.com](https://developers.facebook.com) com token contendo: `instagram_basic`, `business_management`, `pages_show_list`, `pages_read_engagement` (+ `instagram_manage_insights` para views/shares/saved)
3. `pip install -r requirements.txt` e `npm install -g pptxgenjs`
4. O token de teste do Graph API Explorer expira em 1-2h; gere um novo quando a coleta falhar com erro 190

## Estrutura

| Arquivo | Função |
|---|---|
| `scr/extract_search.py` | coleta bruta (posts, curtidas, comentários) |
| `scr/transform.py` | métricas de engajamento (CSVs silver/gold) |
| `scr/extract_insights_campanhas.py` | insights privados por post, classificados por campanha |
| `scr/extract_concorrentes.py` | benchmark de concorrentes (business_discovery) |
| `relatorio/build_charts.py` | gráficos PNG + números do relatório |
| `relatorio/download_assets.py` | foto de perfil e capas dos posts |
| `relatorio/build_deck.js` | apresentação PPTX (defina `BRAND` no ambiente) |
| `tools/add_transitions.py` | transições de slide no XML do PPTX |
| `tools/html_deck_to_pdf.py` | deck HTML → PDF paginado |

## Limitações da API

- Contas de terceiros: apenas curtidas e comentários públicos (sem alcance/impressões)
- Insights (views, shares, saved) exigem que você administre a conta
- business_discovery não enxerga contas pessoais

## Author

Built by **Luis Azevedo** — available for freelance / consulting work on video, short-form content, and automation.
📬 [username.azevedo@gmail.com](mailto:username.azevedo@gmail.com)

## Licença

MIT
