"""Baixa foto de perfil e capas das publicações para a apresentação.

Uso: python relatorio/download_assets.py <username>
Escreve em relatorio/assets/<username>/.
"""
import json
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent

USERNAME = sys.argv[1] if len(sys.argv) > 1 else None
if not USERNAME:
    raise SystemExit('Uso: download_assets.py <username>')

ASSETS = Path(__file__).resolve().parent / 'assets' / USERNAME
ASSETS.mkdir(parents=True, exist_ok=True)

TIMEOUT = 30


def download(url, dest):
    if not url or (isinstance(url, float) and pd.isna(url)):
        return False
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f'{dest.name} ({len(r.content) // 1024} KB)')
        return True
    except Exception as e:
        print(f'FALHOU {dest.name}: {e}')
        return False


def cover_url(row):
    thumb = row.get('thumbnail_url')
    if isinstance(thumb, str) and thumb:
        return thumb
    return row.get('media_url')


account = json.loads((ROOT / f'data/bronze/{USERNAME}_account.json').read_text())
download(account.get('profile_picture_url'), ASSETS / 'perfil.jpg')

df = pd.read_csv(ROOT / f'data/silver/{USERNAME}_medias.csv', parse_dates=['timestamp'])

# Top 5 por engajamento
top = df.nlargest(5, 'engajamento').reset_index()
for i, row in top.iterrows():
    download(cover_url(row), ASSETS / f'top{i + 1}.jpg')

# Mosaico: 12 posts mais recentes com capa disponível
count = 0
for _, row in df.sort_values('timestamp', ascending=False).head(30).iterrows():
    if count >= 12:
        break
    if download(cover_url(row), ASSETS / f'feed{count + 1:02d}.jpg'):
        count += 1

print(f'\nAssets em {ASSETS} | feed: {count} imagens')
