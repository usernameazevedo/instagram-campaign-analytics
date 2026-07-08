#!/bin/bash
# Pipeline completo: coleta -> análise -> gráficos -> imagens -> apresentação.
#
# Uso: ./gerar_relatorio.sh <username_instagram> ["Nome do Cliente"]
#   username_instagram : conta business/creator a analisar (ex: umaburgueria)
#   Nome do Cliente    : nome da pasta de saída (padrão: username)
#
# Pré-requisito: .env preenchido com ACCESS_TOKEN e OWN_IG_USERNAME.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
USERNAME="${1:?Uso: ./gerar_relatorio.sh <username_instagram> [\"Nome do Cliente\"]}"
CLIENTE="${2:-$USERNAME}"
PY="$DIR/.venv/bin/python"
DEST_DIR="${OUTPUT_DIR:-./output}/$CLIENTE"

echo "==> [1/5] Coleta (bronze)"
"$PY" "$DIR/scr/extract_search.py" "$USERNAME"

echo "==> [2/5] Transformação (silver/gold)"
"$PY" "$DIR/scr/transform.py" "$USERNAME"

echo "==> [3/5] Gráficos e números"
"$PY" "$DIR/relatorio/build_charts.py" "$USERNAME"

echo "==> [4/5] Imagens (perfil e capas)"
"$PY" "$DIR/relatorio/download_assets.py" "$USERNAME"

echo "==> [5/5] Apresentação"
mkdir -p "$DEST_DIR"
V=1
while [ -e "$DEST_DIR/Analise Instagram $CLIENTE V$V.pptx" ]; do V=$((V + 1)); done
OUTFILE="$DEST_DIR/Analise Instagram $CLIENTE V$V.pptx"
NODE_PATH="$(npm root -g)" node "$DIR/relatorio/build_deck.js" "$USERNAME" "$OUTFILE"

echo ""
echo "Pronto: $OUTFILE"
echo "CSVs analíticos em: $DIR/data/gold/"
