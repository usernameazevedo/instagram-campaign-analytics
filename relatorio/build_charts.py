"""Gera gráficos e números para a apresentação de qualquer perfil.

Uso: python relatorio/build_charts.py <username>
Lê data/bronze|silver do perfil e escreve relatorio/charts/<username>/.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

USERNAME = sys.argv[1] if len(sys.argv) > 1 else None
if not USERNAME:
    raise SystemExit('Uso: build_charts.py <username>')

OUT = Path(__file__).resolve().parent / 'charts' / USERNAME
OUT.mkdir(parents=True, exist_ok=True)

# Paleta  para relatórios: dominante laranja queimado, neutro cinza
ACCENT = '#D94F30'
MUTED = '#B8B2AC'
INK = '#2B2620'
GRID = '#E8E4DF'

plt.rcParams.update({
    'font.family': 'Arial',
    'text.color': INK,
    'axes.edgecolor': GRID,
    'axes.labelcolor': INK,
    'xtick.color': INK,
    'ytick.color': INK,
    'axes.grid': True,
    'grid.color': GRID,
    'grid.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.size': 13,
})

account = json.loads((ROOT / f'data/bronze/{USERNAME}_account.json').read_text())
df = pd.read_csv(ROOT / f'data/silver/{USERNAME}_medias.csv', parse_dates=['timestamp'])
df['mes'] = df['timestamp'].dt.to_period('M')
df['weekday'] = df['timestamp'].dt.weekday

DIAS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
DIAS_LONGO = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira',
              'Sexta-feira', 'Sábado', 'Domingo']
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
MESES_ABREV = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set',
               'out', 'nov', 'dez']
TIPO_LABEL = {'VIDEO': 'Vídeo / Reels', 'CAROUSEL_ALBUM': 'Carrossel', 'IMAGE': 'Foto única'}


def br(n):
    return f'{n:,.0f}'.replace(',', '.')


def mes_ano(ts):
    return f'{MESES_ABREV[ts.month - 1]}/{ts.year}'


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(name)


# 1. Evolução mensal do engajamento médio (últimos 36 meses completos)
mensal = df.groupby('mes').agg(posts=('engajamento', 'count'),
                               eng_medio=('engajamento', 'mean')).reset_index()
if len(mensal) > 1:
    mensal = mensal.iloc[:-1]  # descarta o mês corrente (parcial)
mensal = mensal.tail(36)
mensal['data'] = mensal['mes'].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(9.2, 3.6))
ax.plot(mensal['data'], mensal['eng_medio'], color=ACCENT, linewidth=2)
ax.fill_between(mensal['data'], mensal['eng_medio'], color=ACCENT, alpha=0.08)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: br(v)))
ax.set_ylim(bottom=0)
ax.grid(axis='x', visible=False)
pico = mensal.loc[mensal['eng_medio'].idxmax()]
ax.annotate(f"pico: {br(pico['eng_medio'])}", (pico['data'], pico['eng_medio']),
            textcoords='offset points', xytext=(8, -2), fontsize=11, color=INK)
save(fig, 'evolucao_mensal.png')

# 2. Engajamento médio por formato (apenas formatos presentes no feed)
tipos = (df.groupby('media_type')
         .agg(eng=('engajamento', 'mean'), n=('engajamento', 'count'))
         .sort_values('eng', ascending=False))
labels = [TIPO_LABEL.get(t, t) for t in tipos.index]
fig, ax = plt.subplots(figsize=(7.6, 3.4))
colors = [ACCENT] + [MUTED] * (len(tipos) - 1)
bars = ax.barh(labels[::-1], tipos['eng'][::-1], color=colors[::-1], height=0.55)
for bar, eng in zip(bars, tipos['eng'][::-1]):
    ax.text(bar.get_width() + tipos['eng'].max() * 0.02,
            bar.get_y() + bar.get_height() / 2, br(eng),
            va='center', fontsize=13, color=INK)
ax.set_xlim(0, tipos['eng'].max() * 1.18)
ax.grid(axis='y', visible=False)
ax.xaxis.set_visible(False)
save(fig, 'por_formato.png')

# 3. Engajamento por dia da semana
dia = df.groupby('weekday').agg(eng=('engajamento', 'mean')).reindex(range(7))
best_dia = int(dia['eng'].idxmax())
fig, ax = plt.subplots(figsize=(7.6, 3.2))
colors = [ACCENT if i == best_dia else MUTED for i in range(7)]
ax.bar(DIAS, dia['eng'], color=colors, width=0.6)
for i, v in enumerate(dia['eng']):
    if pd.notna(v):
        ax.text(i, v + dia['eng'].max() * 0.02, br(v), ha='center', fontsize=11, color=INK)
ax.set_ylim(0, dia['eng'].max() * 1.2)
ax.grid(axis='x', visible=False)
ax.yaxis.set_visible(False)
save(fig, 'por_dia.png')

# 4. Frequência de postagem
fig, ax = plt.subplots(figsize=(9.2, 3.2))
ax.bar(mensal['data'], mensal['posts'], color=MUTED, width=22)
media_posts = mensal['posts'].mean()
ax.axhline(media_posts, color=ACCENT, linewidth=1.6, linestyle='--')
ax.set_ylim(0, mensal['posts'].max() * 1.25)
ax.text(0.01, 0.94, f'média: {media_posts:.0f} posts/mês',
        transform=ax.transAxes, fontsize=11, color=ACCENT)
ax.grid(axis='x', visible=False)
save(fig, 'frequencia.png')

# ---- Números e textos dinâmicos para o deck ----
rec = df[df['timestamp'] >= df['timestamp'].max() - pd.Timedelta(days=90)]
hist = df[df['timestamp'] < df['timestamp'].max() - pd.Timedelta(days=90)]
if hist.empty:
    hist = df

melhor_tipo, pior_tipo = tipos.index[0], tipos.index[-1]
ratio = tipos['eng'].iloc[0] / max(tipos['eng'].iloc[-1], 1)
dominante = tipos['n'].idxmax()
pct_dominante = round(tipos.loc[dominante, 'n'] / len(df) * 100)

anos = round((df['timestamp'].max() - df['timestamp'].min()).days / 365.25, 1)
periodo = f"{mes_ano(df['timestamp'].min())} a {mes_ano(df['timestamp'].max())}"
taxa_hist = round(hist['taxa_engajamento_pct'].mean(), 2)
taxa_90d = round(rec['taxa_engajamento_pct'].mean(), 2)
queda = taxa_90d < taxa_hist * 0.85
tendencia_titulo = ('Sinal de alerta: queda no trimestre recente' if queda
                    else 'Tendência recente: engajamento estável ou em alta')
tendencia_texto = (
    f'O engajamento por post caiu de {br(hist["like_count"].mean())} para '
    f'{br(rec["like_count"].mean())} curtidas médias nos últimos 90 dias '
    f'({len(rec)} publicações no período). Como a base de seguidores segue alta, '
    f'cada post recente conversa com uma fração cada vez menor da audiência: '
    f'é o momento certo de agir.'
    if queda else
    f'Nos últimos 90 dias ({len(rec)} publicações), o engajamento médio se manteve '
    f'em linha com o histórico do perfil. O desafio passa a ser acelerar: usar os '
    f'formatos de melhor desempenho para elevar o patamar, não apenas mantê-lo.'
)

bio_linhas = [l.strip() for l in str(account.get('biography', '')).splitlines() if l.strip()][:3]

top = df.nlargest(5, 'engajamento')
top_list = []
for r in top.itertuples():
    cap = str(r.caption).replace('\n', ' ') if pd.notna(r.caption) else ''
    if len(cap) > 90:
        cap = ' '.join(cap[:90].split(' ')[:-1]) + '…'
    top_list.append({
        'data': f'{r.timestamp:%d/%m/%Y}',
        'likes': int(r.like_count),
        'comments': int(r.comments_count),
        'caption': cap,
        'tipo': TIPO_LABEL.get(r.media_type, r.media_type).lower(),
    })
top_tipos = {t['tipo'] for t in top_list}
top_takeaway = (
    f"Os cinco maiores resultados são {'todos ' if len(top_tipos) == 1 else 'em maioria '}"
    f"{top_list[0]['tipo']}: repetir a fórmula do que já funcionou é o caminho mais curto."
)

hoje = pd.Timestamp.now()
resumo = {
    'username': account['username'],
    'nome': account.get('name', account['username']),
    'bio': '\n'.join(bio_linhas),
    'seguidores': br(account['followers_count']),
    'posts_total': br(account.get('media_count', len(df))),
    'posts_coletados': br(len(df)),
    'periodo': periodo,
    'anos': f'{anos:.0f} anos' if anos >= 2 else f'{max(round(anos * 12), 1)} meses',
    'taxa_hist': str(taxa_hist).replace('.', ','),
    'taxa_90d': str(taxa_90d).replace('.', ','),
    'likes_hist': br(hist['like_count'].mean()),
    'likes_90d': br(rec['like_count'].mean()),
    'periodo_hist': f"{mes_ano(df['timestamp'].min())} até 90 dias atrás",
    'melhor_dia': DIAS_LONGO[best_dia],
    'mes_relatorio': f'{MESES[hoje.month - 1].capitalize()} de {hoje.year}',
    'data_coleta': f'{hoje:%d/%m/%Y}',
    'formato_titulo': (
        f'{TIPO_LABEL[melhor_tipo]} engaja {ratio:.0f}x mais que '
        f'{TIPO_LABEL[pior_tipo].lower()}' if ratio >= 1.5
        else 'Desempenho equilibrado entre formatos'),
    'pct_dominante': f'{pct_dominante}%',
    'formato_texto': (
        f'do feed é {TIPO_LABEL[dominante].lower()}'
        + (f', o formato de menor retorno ({br(tipos["eng"].iloc[-1])} de engajamento '
           f'médio contra {br(tipos["eng"].iloc[0])} de {TIPO_LABEL[melhor_tipo].lower()}).'
           if dominante == pior_tipo and ratio >= 1.5
           else f'. O formato de maior retorno é {TIPO_LABEL[melhor_tipo].lower()}, com '
                f'{br(tipos["eng"].iloc[0])} de engajamento médio por post.')),
    'tendencia_titulo': tendencia_titulo,
    'tendencia_texto': tendencia_texto,
    'queda': bool(queda),
    'top': top_list,
    'top_takeaway': top_takeaway,
}
(OUT / 'numeros.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2))
print('numeros.json')
