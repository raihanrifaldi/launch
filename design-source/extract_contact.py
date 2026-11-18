import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'pdf-tools'))
import pymupdf

root = Path(__file__).parent
document = json.loads((root / 'contact-document.json').read_text(encoding='utf-8'))
nodes = document['nodeChanges']
key = lambda guid: f"{guid.get('sessionID')}:{guid.get('localID')}"
by_id = {key(node['guid']): node for node in nodes}
children = defaultdict(list)
for node in nodes:
    children[key(node.get('parentIndex', {}).get('guid', {}))].append(node)


def path_data(index):
    values = document['blobs'][index]['bytes']
    data = bytes(values[str(i)] for i in range(len(values)))
    offset = 0
    commands = []
    started = False
    while offset < len(data):
        operation = data[offset]
        offset += 1
        if operation == 0:
            if started:
                commands.append('Z')
            continue
        assert operation in (1, 2, 3, 4), (index, operation, offset)
        count = {1: 2, 2: 2, 3: 4, 4: 6}[operation]
        values = struct.unpack_from('<' + 'f' * count, data, offset)
        offset += count * 4
        assert all(math.isfinite(value) for value in values)
        commands.append({1: 'M', 2: 'L', 3: 'Q', 4: 'C'}[operation] + ' '.join(f'{value:.8g}' for value in values))
        started = True
    assert offset == len(data)
    return ' '.join(commands)


def text_paths(node):
    paths = []
    for glyph in node.get('derivedTextData', {}).get('glyphs', []):
        position = glyph['position']
        paths.append(f'<path d="{path_data(glyph["commandsBlob"])}" transform="translate({position["x"]} {position["y"]}) scale({glyph["fontSize"]} {-glyph["fontSize"]})"/>')
    return ''.join(paths)


assets = root.parent / 'portfolio' / 'dist' / 'assets'
for local_id, name in [(670, 'phone'), (678, 'email'), (686, 'location'), (701, 'chevron')]:
    node = by_id[f'900:{local_id}']
    width, height = node['size']['x'], node['size']['y']
    color = '#fff' if name == 'chevron' else '#000'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><g fill="{color}">{text_paths(node)}</g></svg>'
    (assets / f'contact-{name}.svg').write_text(svg, encoding='utf-8')
    print(f'contact-{name}.svg', width, height)


def solid(paint):
    color = paint.get('color', {})
    rgb = [round(255 * color.get(channel, 0)) for channel in ('r', 'g', 'b')]
    return f'rgb({rgb[0]},{rgb[1]},{rgb[2]})', paint.get('opacity', 1) * color.get('a', 1)


def render(node):
    if node.get('visible') is False:
        return ''
    matrix = node.get('transform', {})
    if any(matrix.get(name) is None for name in ('m00', 'm10', 'm01', 'm11', 'm02', 'm12')):
        return ''
    transform = ' '.join(str(matrix[name]) for name in ('m00', 'm10', 'm01', 'm11', 'm02', 'm12'))
    fill = next((paint for paint in node.get('fillPaints', []) if paint.get('visible', True) and paint['type'] == 'SOLID'), None)
    content = ''
    if node['type'] == 'TEXT':
        color, opacity = solid(fill) if fill else ('#fff', 1)
        content = f'<g fill="{color}" opacity="{opacity}">{text_paths(node)}</g>'
    elif fill and node.get('size', {}).get('x') is not None:
        width, height = node['size']['x'], node['size']['y']
        color, opacity = solid(fill)
        if node['type'] == 'ELLIPSE':
            content = f'<ellipse cx="{width/2}" cy="{height/2}" rx="{width/2}" ry="{height/2}" fill="{color}" opacity="{opacity}"/>'
        else:
            content = f'<rect width="{width}" height="{height}" rx="{node.get("cornerRadius", 0)}" fill="{color}" opacity="{opacity}"/>'
    return f'<g transform="matrix({transform})">{content}{"".join(render(child) for child in children[key(node["guid"])])}</g>'


central = ''.join(render(by_id[f'900:{local_id}']) for local_id in (664, 687, 702))
reference = f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1000" viewBox="0 532 1920 1000"><rect x="0" y="532" width="1920" height="1000" fill="#0e0e0e"/>{central}</svg>'
(root / 'contact-source-reference.svg').write_text(reference, encoding='utf-8')
svg_document = pymupdf.open(stream=reference.encode(), filetype='svg')
pdf_document = pymupdf.open('pdf', svg_document.convert_to_pdf())
pdf_document[0].get_pixmap(matrix=pymupdf.Matrix(.7, .7), alpha=False).save(root / 'contact-source-reference.png')
print('Rendered contact-source-reference.png from original layout and glyph outlines.')
