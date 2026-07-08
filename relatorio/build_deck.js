// Gera a apresentação padrão de análise de Instagram para qualquer perfil.
// Defina BRAND com o nome da sua marca/agência.
// Uso: node build_deck.js <username> <arquivo_saida.pptx>
// Lê charts/<username>/numeros.json (+ PNGs) e assets/<username>/*.jpg.
const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const USERNAME = process.argv[2];
const OUTFILE = process.argv[3];
if (!USERNAME || !OUTFILE) {
  console.error('Uso: node build_deck.js <username> <arquivo_saida.pptx>');
  process.exit(1);
}

const CHARTS = path.join(__dirname, 'charts', USERNAME);
const ASSETS = path.join(__dirname, 'assets', USERNAME);
const N = JSON.parse(fs.readFileSync(path.join(CHARTS, 'numeros.json'), 'utf8'));

const INK = '2B2620';
const ACCENT = 'D94F30';
const MUTED = '8A837C';
const LIGHT = 'F4F1EE';
const WHITE = 'FFFFFF';
const SOFT = 'C9C2BA';
const FONT = 'Arial';
const BRAND = process.env.BRAND || 'SUA MARCA';

const asset = (name) => {
  const p = path.join(ASSETS, name);
  return fs.existsSync(p) ? p : null;
};

const pptx = new pptxgen();
pptx.defineLayout({ name: 'WIDE', width: 13.33, height: 7.5 });
pptx.layout = 'WIDE';

let pageNum = 0;
const footer = (s) => {
  pageNum += 1;
  if (pageNum === 1) return;
  s.addText(`${BRAND}  |  Análise de Instagram: @${N.username}`, {
    x: 0.6, y: 7.05, w: 6, h: 0.3, fontFace: FONT, fontSize: 9, color: MUTED, margin: 0,
  });
  s.addText(String(pageNum), { x: 12.5, y: 7.05, w: 0.4, h: 0.3, fontFace: FONT, fontSize: 9, color: MUTED, align: 'right', margin: 0 });
};

const title = (s, txt) => {
  s.addText(txt, { x: 0.6, y: 0.45, w: 12.1, h: 0.75, fontFace: FONT, fontSize: 30, bold: true, color: INK, margin: 0 });
};

// ---------- 1. Capa ----------
let s = pptx.addSlide();
s.background = { color: INK };
if (asset('perfil.jpg')) {
  s.addImage({ path: asset('perfil.jpg'), x: 0.9, y: 1.55, w: 1.5, h: 1.5, rounding: true });
}
s.addText('ANÁLISE DE INSTAGRAM', { x: 0.9, y: 3.35, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 20, color: SOFT, charSpacing: 6, margin: 0 });
s.addText(`@${N.username}`, { x: 0.9, y: 3.85, w: 11.5, h: 1.1, fontFace: FONT, fontSize: 54, bold: true, color: WHITE, margin: 0 });
s.addText('Diagnóstico de desempenho e recomendações de conteúdo', { x: 0.9, y: 5.05, w: 9, h: 0.45, fontFace: FONT, fontSize: 17, color: SOFT, margin: 0 });
s.addShape('ellipse', { x: 0.9, y: 6.05, w: 0.14, h: 0.14, fill: { color: ACCENT } });
s.addText(`${BRAND}  |  ${N.mes_relatorio}`, { x: 1.2, y: 5.92, w: 6, h: 0.4, fontFace: FONT, fontSize: 13, color: WHITE, margin: 0 });
['feed01', 'feed02', 'feed03', 'feed04', 'feed05', 'feed06'].forEach((f, i) => {
  if (!asset(f + '.jpg')) return;
  const col = i % 2, row = Math.floor(i / 2);
  s.addImage({ path: asset(f + '.jpg'), x: 9.5 + col * 1.78, y: 1.15 + row * 1.78,
    w: 1.68, h: 1.68, sizing: { type: 'cover', w: 1.68, h: 1.68 } });
});
footer(s);

// ---------- 2. Visão geral (perfil + stats) ----------
s = pptx.addSlide();
title(s, 'Visão geral da conta');
s.addShape('roundRect', { x: 0.6, y: 1.55, w: 4.0, h: 4.5, rectRadius: 0.1, fill: { color: LIGHT } });
if (asset('perfil.jpg')) {
  s.addImage({ path: asset('perfil.jpg'), x: 1.9, y: 1.9, w: 1.4, h: 1.4, rounding: true });
}
s.addText(N.nome, { x: 0.85, y: 3.45, w: 3.5, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: INK, align: 'center', margin: 0 });
s.addText(`@${N.username}`, { x: 0.85, y: 3.85, w: 3.5, h: 0.35, fontFace: FONT, fontSize: 13, color: ACCENT, align: 'center', margin: 0 });
s.addText(N.bio, { x: 0.85, y: 4.35, w: 3.5, h: 1.5, fontFace: FONT, fontSize: 11.5, color: MUTED, align: 'center', valign: 'top', margin: 0 });
const stats = [
  { v: N.seguidores, l: 'seguidores' },
  { v: N.posts_total, l: 'publicações no perfil' },
  { v: `${N.taxa_hist}%`, l: 'taxa de engajamento média histórica' },
  { v: N.anos, l: `de conteúdo analisado (${N.periodo})` },
];
stats.forEach((st, i) => {
  const x = 4.95 + (i % 2) * 3.95;
  const y = 1.55 + Math.floor(i / 2) * 2.32;
  s.addShape('roundRect', { x, y, w: 3.75, h: 2.18, rectRadius: 0.08, fill: { color: LIGHT } });
  s.addText(st.v, { x, y: y + 0.32, w: 3.75, h: 0.85, fontFace: FONT, fontSize: 38, bold: true, color: ACCENT, align: 'center', margin: 0 });
  s.addText(st.l, { x: x + 0.3, y: y + 1.2, w: 3.15, h: 0.85, fontFace: FONT, fontSize: 13, color: INK, align: 'center', valign: 'top', margin: 0 });
});
s.addText([
  { text: 'Fonte e método: ', options: { bold: true } },
  { text: `dados públicos coletados via API oficial da Meta (Graph API, business discovery) em ${N.data_coleta}. Foram analisadas ${N.posts_coletados} publicações do feed. A taxa de engajamento considera curtidas + comentários sobre a base atual de seguidores. Stories, alcance e impressões não são disponibilizados pela API para contas de terceiros.`, options: {} },
], { x: 0.6, y: 6.25, w: 12.1, h: 0.75, fontFace: FONT, fontSize: 11, color: MUTED, margin: 0, valign: 'top' });
footer(s);

// ---------- 3. O feed hoje (mosaico) ----------
s = pptx.addSlide();
title(s, 'O feed hoje');
for (let i = 0; i < 12; i++) {
  const f = `feed${String(i + 1).padStart(2, '0')}.jpg`;
  if (!asset(f)) continue;
  const col = i % 6, row = Math.floor(i / 6);
  s.addImage({ path: asset(f), x: 0.6 + col * 2.06, y: 1.5 + row * 2.06,
    w: 1.96, h: 1.96, sizing: { type: 'cover', w: 1.96, h: 1.96 } });
}
s.addText(`As 12 publicações mais recentes do feed de @${N.username}, como o público as encontra hoje. É a matéria-prima do diagnóstico dos próximos slides: formatos, temas e ritmo.`, { x: 0.6, y: 5.85, w: 12.1, h: 0.8, fontFace: FONT, fontSize: 13.5, color: INK, margin: 0, valign: 'top' });
footer(s);

// ---------- 4. Evolução mensal ----------
s = pptx.addSlide();
title(s, 'Evolução do engajamento por publicação');
s.addImage({ path: path.join(CHARTS, 'evolucao_mensal.png'), x: 0.6, y: 1.45, w: 9.0, h: 3.55 });
s.addText('Engajamento médio (curtidas + comentários) por publicação, mês a mês, últimos 36 meses.', { x: 0.6, y: 5.15, w: 9.0, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, margin: 0 });
s.addShape('roundRect', { x: 9.9, y: 1.45, w: 2.85, h: 3.55, rectRadius: 0.08, fill: { color: LIGHT } });
s.addText('Leitura', { x: 10.15, y: 1.7, w: 2.35, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: ACCENT, margin: 0 });
s.addText('Os picos indicam o potencial real da audiência: o que o perfil alcança quando o conteúdo certo encontra o público. A distância entre o pico e a média é a oportunidade.', { x: 10.15, y: 2.15, w: 2.4, h: 2.7, fontFace: FONT, fontSize: 12.5, color: INK, margin: 0, valign: 'top' });
footer(s);

// ---------- 5. Formato ----------
s = pptx.addSlide();
title(s, N.formato_titulo);
s.addImage({ path: path.join(CHARTS, 'por_formato.png'), x: 0.6, y: 1.6, w: 7.6, h: 3.4 });
s.addText('Engajamento médio (curtidas + comentários) por publicação, por formato.', { x: 0.6, y: 5.15, w: 7.6, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, margin: 0 });
s.addText(N.pct_dominante, { x: 8.7, y: 1.75, w: 4.0, h: 0.95, fontFace: FONT, fontSize: 60, bold: true, color: ACCENT, margin: 0 });
s.addText(N.formato_texto, { x: 8.7, y: 2.75, w: 3.9, h: 1.35, fontFace: FONT, fontSize: 14, color: INK, margin: 0, valign: 'top' });
s.addText('Oportunidade: redistribuir o mix de formatos sem aumentar o volume de produção.', { x: 8.7, y: 4.2, w: 3.9, h: 0.95, fontFace: FONT, fontSize: 14, bold: true, color: INK, margin: 0, valign: 'top' });
footer(s);

// ---------- 6. Frequência ----------
s = pptx.addSlide();
title(s, 'Ritmo de publicação');
s.addImage({ path: path.join(CHARTS, 'frequencia.png'), x: 0.6, y: 1.5, w: 9.0, h: 3.15 });
s.addText('Publicações no feed por mês, últimos 36 meses.', { x: 0.6, y: 4.8, w: 9.0, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, margin: 0 });
s.addShape('roundRect', { x: 9.9, y: 1.5, w: 2.85, h: 3.15, rectRadius: 0.08, fill: { color: LIGHT } });
s.addText('Leitura', { x: 10.15, y: 1.75, w: 2.35, h: 0.4, fontFace: FONT, fontSize: 14, bold: true, color: ACCENT, margin: 0 });
s.addText('Constância importa mais que volume. A linha tracejada marca a média do período: quedas prolongadas abaixo dela costumam preceder perda de alcance.', { x: 10.15, y: 2.2, w: 2.4, h: 2.3, fontFace: FONT, fontSize: 12.5, color: INK, margin: 0, valign: 'top' });
footer(s);

// ---------- 7. Dia da semana ----------
s = pptx.addSlide();
title(s, 'Desempenho por dia da semana');
s.addImage({ path: path.join(CHARTS, 'por_dia.png'), x: 0.6, y: 1.6, w: 7.6, h: 3.2 });
s.addText('Engajamento médio por publicação, por dia da semana em que foi postada.', { x: 0.6, y: 4.95, w: 7.6, h: 0.4, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, margin: 0 });
s.addText(N.melhor_dia, { x: 8.7, y: 1.9, w: 4.0, h: 0.7, fontFace: FONT, fontSize: 34, bold: true, color: ACCENT, margin: 0 });
s.addText('é o dia com melhor engajamento médio histórico.', { x: 8.7, y: 2.6, w: 3.9, h: 0.7, fontFace: FONT, fontSize: 14, color: INK, margin: 0 });
s.addText('Vale usar como referência de calendário, priorizando os conteúdos de maior aposta nos dias de melhor resposta.', { x: 8.7, y: 3.5, w: 3.9, h: 1.2, fontFace: FONT, fontSize: 14, color: INK, margin: 0 });
footer(s);

// ---------- 8. Tendência recente ----------
s = pptx.addSlide();
title(s, N.tendencia_titulo);
const cols = [
  { t: `Histórico (${N.periodo_hist})`, likes: N.likes_hist, taxa: `${N.taxa_hist}%`, bg: LIGHT, c: INK },
  { t: 'Últimos 90 dias', likes: N.likes_90d, taxa: `${N.taxa_90d}%`, bg: INK, c: WHITE },
];
cols.forEach((col, i) => {
  const x = 0.6 + i * 6.35;
  s.addShape('roundRect', { x, y: 1.65, w: 6.0, h: 3.3, rectRadius: 0.1, fill: { color: col.bg } });
  s.addText(col.t, { x: x + 0.4, y: 1.95, w: 5.2, h: 0.45, fontFace: FONT, fontSize: 16, bold: true, color: col.c, margin: 0 });
  s.addText(col.likes, { x: x + 0.4, y: 2.5, w: 2.5, h: 0.85, fontFace: FONT, fontSize: 48, bold: true, color: ACCENT, margin: 0 });
  s.addText('curtidas médias por post', { x: x + 0.4, y: 3.4, w: 2.5, h: 0.6, fontFace: FONT, fontSize: 12, color: col.c, margin: 0 });
  s.addText(col.taxa, { x: x + 3.1, y: 2.5, w: 2.5, h: 0.85, fontFace: FONT, fontSize: 48, bold: true, color: ACCENT, margin: 0 });
  s.addText('taxa de engajamento média', { x: x + 3.1, y: 3.4, w: 2.5, h: 0.6, fontFace: FONT, fontSize: 12, color: col.c, margin: 0 });
});
s.addText(N.tendencia_texto, { x: 0.6, y: 5.3, w: 12.1, h: 1.0, fontFace: FONT, fontSize: 14, color: INK, margin: 0, valign: 'top' });
footer(s);

// ---------- 9. Top 5 (cards visuais com capas) ----------
s = pptx.addSlide();
title(s, 'O que já funcionou: top 5 publicações');
const CARD_W = 2.35, GAP = 0.16;
N.top.forEach((t, i) => {
  const x = 0.6 + i * (CARD_W + GAP);
  const y = 1.45;
  if (asset(`top${i + 1}.jpg`)) {
    s.addImage({ path: asset(`top${i + 1}.jpg`), x, y, w: CARD_W, h: 2.94,
      sizing: { type: 'cover', w: CARD_W, h: 2.94 } });
  } else {
    s.addShape('roundRect', { x, y, w: CARD_W, h: 2.94, rectRadius: 0.06, fill: { color: LIGHT } });
  }
  s.addShape('ellipse', { x: x + 0.12, y: y + 0.12, w: 0.46, h: 0.46, fill: { color: i === 0 ? ACCENT : INK } });
  s.addText(String(i + 1), { x: x + 0.12, y: y + 0.12, w: 0.46, h: 0.46, fontFace: FONT, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle', margin: 0 });
  s.addText(`${t.likes.toLocaleString('pt-BR')} curtidas`, { x, y: y + 3.04, w: CARD_W, h: 0.34, fontFace: FONT, fontSize: 14, bold: true, color: ACCENT, margin: 0 });
  s.addText(`${t.comments.toLocaleString('pt-BR')} comentários  |  ${t.data}`, { x, y: y + 3.38, w: CARD_W, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0 });
  const flat = t.caption.replace(/\n+/g, ' ');
  const legenda = flat.length > 75
    ? flat.slice(0, 75).split(' ').slice(0, -1).join(' ') + '…'
    : flat;
  s.addText(legenda, { x, y: y + 3.72, w: CARD_W, h: 0.85, fontFace: FONT, fontSize: 10, color: INK, margin: 0, valign: 'top' });
});
s.addText(N.top_takeaway, { x: 0.6, y: 6.45, w: 12.1, h: 0.4, fontFace: FONT, fontSize: 13, bold: true, color: INK, margin: 0 });
footer(s);

// ---------- 10. Recomendações ----------
s = pptx.addSlide();
title(s, 'Recomendações');
const recs = [
  ['Concentrar no formato vencedor', `${N.formato_titulo}. Redistribuir o mix de formatos é o ganho mais rápido disponível, sem aumentar produção.`],
  ['Repetir a fórmula dos maiores sucessos', N.top_takeaway],
  [N.queda ? 'Reagir à queda do trimestre' : 'Elevar o patamar recente',
    N.queda
      ? 'Plano de recuperação de 30 dias com conteúdo de alta aposta, aproveitando a base de seguidores já construída.'
      : 'Aproveitar a estabilidade para testar novos formatos e elevar a taxa média de engajamento.'],
  ['Medir todo mês', 'Acompanhamento mensal com esta mesma metodologia para validar o efeito das mudanças e comparar com concorrentes.'],
];
recs.forEach((r, i) => {
  const y = 1.55 + i * 1.28;
  s.addShape('ellipse', { x: 0.6, y: y + 0.08, w: 0.55, h: 0.55, fill: { color: ACCENT } });
  s.addText(String(i + 1), { x: 0.6, y: y + 0.08, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 18, bold: true, color: WHITE, align: 'center', valign: 'middle', margin: 0 });
  s.addText(r[0], { x: 1.45, y, w: 11.2, h: 0.42, fontFace: FONT, fontSize: 17, bold: true, color: INK, margin: 0 });
  s.addText(r[1], { x: 1.45, y: y + 0.44, w: 11.2, h: 0.8, fontFace: FONT, fontSize: 13.5, color: INK, margin: 0, valign: 'top' });
});
footer(s);

// ---------- 11. Encerramento ----------
s = pptx.addSlide();
s.background = { color: INK };
s.addText('Próximo passo', { x: 0.9, y: 2.5, w: 11.5, h: 0.5, fontFace: FONT, fontSize: 18, color: SOFT, charSpacing: 4, margin: 0 });
s.addText('Transformar diagnóstico em resultado', { x: 0.9, y: 3.0, w: 11.5, h: 1.5, fontFace: FONT, fontSize: 40, bold: true, color: WHITE, margin: 0 });
s.addText(`Relatório gerado por ${BRAND} com dados públicos da API oficial da Meta.`, { x: 0.9, y: 4.6, w: 10, h: 0.4, fontFace: FONT, fontSize: 13, color: SOFT, margin: 0 });
s.addShape('ellipse', { x: 0.9, y: 5.5, w: 0.14, h: 0.14, fill: { color: ACCENT } });
s.addText(`${BRAND}  |  ${N.mes_relatorio}`, { x: 1.2, y: 5.37, w: 6, h: 0.4, fontFace: FONT, fontSize: 13, color: WHITE, margin: 0 });
footer(s);

pptx.writeFile({ fileName: OUTFILE }).then(() => console.log('OK ' + OUTFILE));
