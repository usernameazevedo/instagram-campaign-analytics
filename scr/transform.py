"""Silver/Gold: transforma os JSONs bronze em CSVs analíticos.

Uso: python scr/transform.py [conta_alvo]
Gera:
  silver/<conta>_medias.csv   - uma linha por publicação, com taxa de engajamento
  gold/<conta>_resumo.csv     - resumo geral da conta
  gold/<conta>_por_tipo.csv   - engajamento médio por tipo de mídia
  gold/<conta>_top10.csv      - top 10 publicações por engajamento
"""
import json
import sys

import pandas as pd

from config import BRONZE_DIR, GOLD_DIR, SILVER_DIR, ensure_dirs, get_env


def build_media_table(media_items: list[dict], followers: int) -> pd.DataFrame:
    df = pd.DataFrame(media_items)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['data'] = df['timestamp'].dt.date
    df['like_count'] = df.get('like_count', 0)
    df[['like_count', 'comments_count']] = (
        df[['like_count', 'comments_count']].fillna(0).astype(int)
    )
    df['engajamento'] = df['like_count'] + df['comments_count']
    df['taxa_engajamento_pct'] = (df['engajamento'] / followers * 100).round(3)
    df['caption'] = df.get('caption', '').fillna('').str.slice(0, 200)
    return df.sort_values('timestamp', ascending=False)


def main() -> None:
    ensure_dirs()
    target = sys.argv[1] if len(sys.argv) > 1 else get_env('TARGET_USERNAME')

    account = json.loads((BRONZE_DIR / f'{target}_account.json').read_text())
    media_items = json.loads((BRONZE_DIR / f'{target}_medias.json').read_text())
    followers = account['followers_count']

    df = build_media_table(media_items, followers)
    silver_path = SILVER_DIR / f'{target}_medias.csv'
    df.to_csv(silver_path, index=False)

    resumo = pd.DataFrame([{
        'username': account['username'],
        'nome': account.get('name'),
        'seguidores': followers,
        'seguindo': account.get('follows_count'),
        'total_publicacoes': account.get('media_count'),
        'publicacoes_coletadas': len(df),
        'media_likes': round(df['like_count'].mean(), 1),
        'media_comentarios': round(df['comments_count'].mean(), 1),
        'taxa_engajamento_media_pct': round(df['taxa_engajamento_pct'].mean(), 3),
        'primeira_publicacao': df['data'].min(),
        'ultima_publicacao': df['data'].max(),
    }])
    resumo.to_csv(GOLD_DIR / f'{target}_resumo.csv', index=False)

    por_tipo = (
        df.groupby('media_type')
        .agg(
            publicacoes=('id', 'count') if 'id' in df else ('media_type', 'count'),
            media_likes=('like_count', 'mean'),
            media_comentarios=('comments_count', 'mean'),
            taxa_engajamento_media_pct=('taxa_engajamento_pct', 'mean'),
        )
        .round(2)
        .reset_index()
    )
    por_tipo.to_csv(GOLD_DIR / f'{target}_por_tipo.csv', index=False)

    top10_cols = [
        'data', 'media_type', 'like_count', 'comments_count',
        'taxa_engajamento_pct', 'permalink', 'caption',
    ]
    top10 = df.nlargest(10, 'engajamento')[top10_cols]
    top10.to_csv(GOLD_DIR / f'{target}_top10.csv', index=False)

    print(f'Silver: {silver_path} ({len(df)} publicações)')
    print(f'Gold: resumo, por_tipo e top10 em {GOLD_DIR}')
    print()
    print(resumo.T.to_string(header=False))


if __name__ == '__main__':
    main()
