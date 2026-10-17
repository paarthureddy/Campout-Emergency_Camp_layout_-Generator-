import os
file='generate_paper_pdf.py'
content=open(file, encoding='utf-8').read()
replacements = {'—': '--', '×': 'x', '∈': 'in', 'ℝ': 'R', '‖': '||', '·': '*', '⌈': 'ceil(', '⌉': ')', '⌊': 'floor(', '⌋': ')', 'Σ': 'Sum', '≥': '>=', '≤': '<=', '–': '-', '”': '"', '“': '"', '’': "'", '‘': "'", '⁻': '^-', '³': '^3', '⁴': '^4'}
for k, v in replacements.items():
    content = content.replace(k, v)
open(file, 'w', encoding='utf-8').write(content)
print('Done')
