import fitz
import sys
sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open(r'e:\Projects\Neural_Networks_Case_Study_G2\example.pdf')
print('Pages:', len(doc))
page = doc[0]
blocks = page.get_text('dict')['blocks']
for b in blocks[:15]:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                print(f"Text: '{s['text'][:30].encode('utf-8', 'ignore').decode('utf-8')}' | Font: {s['font']} | Size: {s['size']}")
