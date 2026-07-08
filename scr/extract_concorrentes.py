# Coleta seguidores, posts e engajamento recente de perfis concorrentes via business_discovery.
# Uso: .venv/bin/python scr/extract_concorrentes.py <ig_user_id_da_conta_propria> <user1> <user2> ...
# Requer ACCESS_TOKEN no .env. So funciona para contas business/creator.
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://graph.facebook.com/v21.0'
N_RECENTES = 25

def load_token():
    with open(os.path.join(ROOT, '.env')) as f:
        for line in f:
            if line.startswith('ACCESS_TOKEN='):
                token = line.split('=', 1)[1].strip()
                if token:
                    return token
    raise SystemExit('ACCESS_TOKEN vazio no .env')

def main():
    if len(sys.argv) < 3:
        raise SystemExit('Uso: extract_concorrentes.py <ig_user_id> <user1> <user2> ...')
    igid, users = sys.argv[1], sys.argv[2:]
    token = load_token()
    out = []
    for u in users:
        url = (f'{API}/{igid}?fields=business_discovery.username({u})'
               f'{{username,name,followers_count,media_count,media.limit({N_RECENTES}){{like_count,comments_count,media_type,timestamp}}}}'
               f'&access_token={urllib.parse.quote(token)}')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            b = json.loads(urllib.request.urlopen(req, timeout=30).read())['business_discovery']
            posts = (b.get('media') or {}).get('data', [])
            eng = [(p.get('like_count') or 0) + (p.get('comments_count') or 0) for p in posts]
            em = round(sum(eng) / len(eng), 1) if eng else 0
            out.append({'username': b['username'], 'name': b.get('name'), 'followers': b['followers_count'],
                        'media_count': b['media_count'], 'n_recentes': len(eng), 'eng_medio_recente': em,
                        'ultimo_post': posts[0]['timestamp'][:10] if posts else None})
            print(f"{b['username']:32s} {b['followers_count']:>8,} seg | {b['media_count']:>5} posts | eng medio: {em}")
        except Exception as e:
            print(f'{u:32s} FALHOU: {str(e)[:60]} (conta pessoal ou @ inexistente)')
    dest = os.path.join(ROOT, 'data/gold/concorrentes.json')
    json.dump(out, open(dest, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(out)} perfis -> {dest}')

if __name__ == '__main__':
    main()
