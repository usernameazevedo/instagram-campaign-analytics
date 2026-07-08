# Injeta transicoes de slide (zoom, fade, morph, push) em um .pptx pronto.
# O pptxgenjs nao gera transicoes; este pos-processador edita o XML do arquivo.
# Uso: python3 tools/add_transitions.py <arquivo.pptx> [--morph N-M] [--push N-M] [--zoom N]
#   --zoom N    transicao de circulo no slide N (bom para capa)
#   --morph N-M transicao Morph (PowerPoint 2019+) nos slides N a M; degrada para fade
#   --push N-M  push lateral nos slides N a M
# Slides sem flag recebem fade suave.
import re
import shutil
import sys
import zipfile

def alt(ns, uri, inner, dur, fb='<p:fade/>'):
    return (f'<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
            f'<mc:Choice xmlns:{ns}="{uri}" Requires="{ns}">'
            f'<p:transition spd="slow" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" p14:dur="{dur}">{inner}</p:transition>'
            f'</mc:Choice><mc:Fallback><p:transition spd="med">{fb}</p:transition></mc:Fallback></mc:AlternateContent>')

MORPH = alt('p159', 'http://schemas.microsoft.com/office/powerpoint/2015/09/main', '<p159:morph option="byObject"/>', 1400)
FADE = alt('p14', 'http://schemas.microsoft.com/office/powerpoint/2010/main', '<p:fade/>', 700)
PUSH = alt('p14', 'http://schemas.microsoft.com/office/powerpoint/2010/main', '<p:push dir="l"/>', 600)
ZOOM = alt('p14', 'http://schemas.microsoft.com/office/powerpoint/2010/main', '<p:circle/>', 900, '<p:circle/>')

def parse_range(arg):
    a, _, b = arg.partition('-')
    return set(range(int(a), int(b or a) + 1))

def main():
    src = sys.argv[1]
    morph, push, zoom = set(), set(), set()
    args = sys.argv[2:]
    for flag, val in zip(args[::2], args[1::2]):
        if flag == '--morph':
            morph = parse_range(val)
        elif flag == '--push':
            push = parse_range(val)
        elif flag == '--zoom':
            zoom = parse_range(val)
    tmp = src + '.tmp'
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.namelist():
        data = zin.read(item)
        m = re.match(r'ppt/slides/slide(\d+)\.xml$', item)
        if m:
            n = int(m.group(1))
            t = ZOOM if n in zoom else MORPH if n in morph else PUSH if n in push else FADE
            data = data.decode('utf-8').replace('</p:sld>', t + '</p:sld>').encode('utf-8')
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(tmp, src)
    print(f'transicoes aplicadas em {src} (zoom={sorted(zoom)}, morph={sorted(morph)}, push={sorted(push)}, resto=fade)')

if __name__ == '__main__':
    main()
