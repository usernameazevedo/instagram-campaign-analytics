"""Bronze: extrai dados públicos de uma conta business/creator via business_discovery.

Uso: python scr/extract_search.py [conta_alvo]
Se conta_alvo não for passada, usa TARGET_USERNAME do .env.
"""
import json
import sys

import requests

from config import BRONZE_DIR, GRAPH_URL, ensure_dirs, get_env

REQUEST_TIMEOUT = 30


def api_get(url: str, params: dict) -> dict:
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    data = response.json()
    if 'error' in data:
        raise SystemExit(f"Erro da API: {data['error'].get('message')}")
    return data


def get_own_ig_id(access_token: str, own_username: str) -> str:
    """Encontra o ID da conta IG business do próprio usuário (via páginas do Facebook)."""
    pages = api_get(f'{GRAPH_URL}/me/accounts', {'access_token': access_token})
    for page in pages.get('data', []):
        detail = api_get(
            f"{GRAPH_URL}/{page['id']}",
            {'fields': 'instagram_business_account{id,username}', 'access_token': access_token},
        )
        ig_account = detail.get('instagram_business_account')
        if ig_account and ig_account.get('username') == own_username:
            return ig_account['id']
    raise SystemExit(
        f'Conta IG business "{own_username}" não encontrada nas páginas do Facebook '
        'acessíveis por este token. Verifique se o Instagram está vinculado a uma Página.'
    )


def business_discovery(access_token: str, own_ig_id: str, target: str, fields: str) -> dict:
    return api_get(
        f'{GRAPH_URL}/{own_ig_id}',
        {
            'fields': f'business_discovery.username({target}){{{fields}}}',
            'access_token': access_token,
        },
    )['business_discovery']


def fetch_all_media(access_token: str, own_ig_id: str, target: str) -> list[dict]:
    media_fields = (
        'comments_count,like_count,media_type,media_url,caption,timestamp,'
        'permalink,media_product_type,thumbnail_url,children{media_type,media_url}'
    )
    result = business_discovery(
        access_token, own_ig_id, target, f'media{{{media_fields}}}'
    )
    media = result.get('media', {})
    items = list(media.get('data', []))

    next_cursor = media.get('paging', {}).get('cursors', {}).get('after')
    while next_cursor:
        page = business_discovery(
            access_token, own_ig_id, target,
            f'media.after({next_cursor}){{{media_fields}}}',
        )
        media = page.get('media', {})
        items.extend(media.get('data', []))
        next_cursor = media.get('paging', {}).get('cursors', {}).get('after')

    return items


def main() -> None:
    ensure_dirs()
    access_token = get_env('ACCESS_TOKEN')
    own_username = get_env('OWN_IG_USERNAME')
    target = sys.argv[1] if len(sys.argv) > 1 else get_env('TARGET_USERNAME')

    print(f'Localizando conta própria @{own_username}...')
    own_ig_id = get_own_ig_id(access_token, own_username)

    print(f'Coletando perfil de @{target}...')
    account = business_discovery(
        access_token, own_ig_id, target,
        'id,username,name,biography,followers_count,follows_count,profile_picture_url,media_count',
    )
    account_path = BRONZE_DIR / f'{target}_account.json'
    account_path.write_text(json.dumps(account, ensure_ascii=False, indent=2))
    print(f'  -> {account_path} ({account.get("followers_count")} seguidores)')

    print(f'Coletando publicações de @{target}...')
    media_items = fetch_all_media(access_token, own_ig_id, target)
    media_path = BRONZE_DIR / f'{target}_medias.json'
    media_path.write_text(json.dumps(media_items, ensure_ascii=False, indent=2))
    print(f'  -> {media_path} ({len(media_items)} publicações)')


if __name__ == '__main__':
    main()
