import json
from pathlib import Path
m = json.loads(Path('outputs/splits/split_manifest.json').read_text())
expected = []
for s in m['splits']:
    for model in ['word_logistic_regression', 'character_linear_svm', 'structural_logistic_regression', 'word_xgboost', 'word_noanon_logistic_regression', 'character_noanon_linear_svm']:
        sid = s['split_id']
        expected.append(f'{model}__{sid}.parquet')
existing = set(p.name for p in Path('outputs/runs/20260811T162016Z_d2881b85/predictions').glob('*.parquet'))
missing = sorted(set(expected) - existing)
print(f'expected: {len(expected)}, existing: {len(existing)}, missing: {len(missing)}')
for m in missing:
    print(' ', m)
