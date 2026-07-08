import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / '.env')

API_VERSION = 'v21.0'
GRAPH_URL = f'https://graph.facebook.com/{API_VERSION}'

DATA_DIR = PROJECT_ROOT / 'data'
BRONZE_DIR = DATA_DIR / 'bronze'
SILVER_DIR = DATA_DIR / 'silver'
GOLD_DIR = DATA_DIR / 'gold'


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(
            f'Variável {name} não encontrada. Copie .env.example para .env e preencha.'
        )
    return value


def ensure_dirs() -> None:
    for folder in (BRONZE_DIR, SILVER_DIR, GOLD_DIR):
        folder.mkdir(parents=True, exist_ok=True)
