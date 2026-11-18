import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'pdf-tools'))
import pymupdf as fitz

document = fitz.open(r'C:\Users\raiha\Downloads\Landingpage.pdf')
output = Path(__file__).parent / 'pdf-reference'
output.mkdir(exist_ok=True)
print('Pages:', len(document))
for index, page in enumerate(document):
    blocks = page.get_text('dict', flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)
    (output / f'page-{index+1}.json').write_text(json.dumps(blocks), encoding='utf-8')
    (output / f'page-{index+1}.txt').write_text(page.get_text(), encoding='utf-8')
    spans = [span for block in blocks['blocks'] if 'lines' in block for line in block['lines'] for span in line['spans']]
    bottom = max((span['bbox'][3] for span in spans), default=page.rect.height)
    print('Page:', index+1, 'Size:', page.rect, 'Content bottom:', bottom)
    clip = fitz.Rect(0, 0, page.rect.width, min(page.rect.height, bottom + 100))
    page.get_pixmap(matrix=fitz.Matrix(.5, .5), clip=clip, alpha=False).save(str(output / f'page-{index+1}.png'))
    if index == 0:
        page.get_pixmap(matrix=fitz.Matrix(1, 1), clip=fitz.Rect(0, 0, page.rect.width, min(1150, page.rect.height)), alpha=False).save(str(output / 'hero.png'))
        print(page.get_text()[:14000])
