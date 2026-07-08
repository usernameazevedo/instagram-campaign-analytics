# Exporta o deck web (HTML animado) para PDF paginado, uma tela por pagina.
# Uso: python3 tools/html_deck_to_pdf.py <deck.html> <saida.pdf>
# Gera uma variante de impressao (slides empilhados, animacoes reveladas),
# imprime via Chrome headless e remove paginas em branco no final.
import os
import shutil
import subprocess
import sys
import tempfile

CHROME_PATHS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
]

PRINT_EXTRA = '''<style>
@media print{ @page{size:338mm 190mm;margin:0} }
html,body{overflow:visible!important;height:auto!important}
#deck{display:block!important;width:auto!important;transform:none!important;transition:none!important}
.slide{width:338mm!important;height:190mm!important;page-break-after:always;break-inside:avoid}
#nav,#hint{display:none!important}
.mini,.cover,.concl li,.roadmap li,.arte,.tcard{opacity:1!important;transform:none!important;transition:none!important}
.hfill{width:var(--w)!important}.vfill{height:var(--h)!important}.tbar::after{width:var(--w)!important}
</style>
<script>document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('.slide').forEach(s=>s.classList.add('active'));document.querySelectorAll('[data-count]').forEach(e=>{e.textContent=parseInt(e.dataset.count).toLocaleString('pt-BR')})});</script>'''


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    raise SystemExit('Chrome nao encontrado; instale o Google Chrome')


def count_slides(html):
    return html.count('<section class="slide')


def trim_pages(pdf, n_keep):
    """Mantem apenas as n_keep primeiras paginas (remove sobras do page-break)."""
    tmp = pdf + '.trim.pdf'
    if shutil.which('qpdf'):
        subprocess.run(['qpdf', pdf, '--pages', '.', f'1-{n_keep}', '--', tmp], check=True)
    elif shutil.which('gs'):
        subprocess.run(['gs', '-q', '-sDEVICE=pdfwrite', '-dFirstPage=1', f'-dLastPage={n_keep}',
                        '-o', tmp, pdf], check=True)
    else:
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            print('aviso: sem qpdf/gs/pypdf, mantendo possiveis paginas em branco no final')
            return
        r = PdfReader(pdf)
        w = PdfWriter()
        for page in r.pages[:n_keep]:
            w.add_page(page)
        with open(tmp, 'wb') as f:
            w.write(f)
    shutil.move(tmp, pdf)


def main():
    if len(sys.argv) < 3:
        raise SystemExit('Uso: html_deck_to_pdf.py <deck.html> <saida.pdf>')
    src, dst = sys.argv[1], os.path.abspath(sys.argv[2])
    html = open(src).read()
    n = count_slides(html)
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(html + PRINT_EXTRA)
        tmp_html = f.name
    try:
        subprocess.run([find_chrome(), '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={dst}', '--virtual-time-budget=8000',
                        f'file://{tmp_html}'], check=True, capture_output=True)
    finally:
        os.unlink(tmp_html)
    if n:
        trim_pages(dst, n)
    print(f'PDF gerado: {dst} ({n} paginas)')


if __name__ == '__main__':
    main()
