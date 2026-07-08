# Coleta insights (views, reach, shares, saved) dos posts de campanha de um perfil.
# Uso: .venv/bin/python scr/extract_insights_campanhas.py <username>
# Requer: ACCESS_TOKEN no .env (permissao instagram_manage_insights) e
#         data/gold/<username>_campanhas_config.json (ver examples/campanhas_config.example.json)
import json
import os
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://graph.facebook.com/v21.0'
METRICS = 'views,reach,shares,saved,total_interactions'

def load_token():
    with open(os.path.join(ROOT, '.env')) as f:
        for line in f:
            if line.startswith('ACCESS_TOKEN='):
                token = line.split('=', 1)[1].strip()
                if token:
                    return token
    raise SystemExit('ACCESS_TOKEN vazio no .env')

def norm(s):
    return unicodedata.normalize('NFD', (s or '').lower()).encode('ascii', 'ignore').decode()

def classify(caption, campanhas):
    """Primeira campanha (na ordem do config) com keyword presente na legenda."""
    c = norm(caption)
    for camp in campanhas:
        if any(kw in c for kw in camp['keywords']):
            return camp['id']
    return None

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    if len(sys.argv) < 2:
        raise SystemExit('Uso: extract_insights_campanhas.py <username>')
    user = sys.argv[1]
    cfg = json.load(open(os.path.join(ROOT, f'data/gold/{user}_campanhas_config.json')))
    token = load_token()
    posts = json.load(open(os.path.join(ROOT, f'data/bronze/{user}_medias.json')))
    recent = [p for p in posts if p.get('timestamp', '') >= cfg['inicio_periodo']]

    results, erros = {}, []
    for p in recent:
        camp = classify(p.get('caption'), cfg['campanhas'])
        if not camp:
            continue
        url = f"{API}/{p['id']}/insights?metric={METRICS}&access_token={urllib.parse.quote(token)}"
        try:
            data = fetch(url)
            row = {d['name']: (d.get('values') or [{}])[0].get('value') for d in data.get('data', [])}
            row['campanha'] = camp
            results[p['id']] = row
            print(camp, p['id'], row)
        except Exception as e:
            erros.append((camp, p['id'], str(e)))
            print('ERRO', camp, p['id'], e)
        time.sleep(0.4)

    out = os.path.join(ROOT, f'data/bronze/{user}_insights_campanhas.json')
    json.dump({'coletado_em': time.strftime('%Y-%m-%d %H:%M'), 'insights': results, 'erros': erros},
              open(out, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(results)} posts com insights, {len(erros)} erros -> {out}')

if __name__ == '__main__':
    main()
