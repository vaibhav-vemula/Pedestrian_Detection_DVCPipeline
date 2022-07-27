import os
import sys
import yaml

if len(sys.argv) != 6:
    sys.stderr.write('Arguments error. Usage:\n')
    sys.stderr.write(
        '\tpython3 src/evaluate.py data/prepared data/transformed data/predictions data/evaluated data/store\n'
    )
    sys.exit(1)

params = yaml.safe_load(open('params.yaml'))['ingest']

images = os.path.join(sys.argv[1],f"v{params['dcount']}",'images')
gt_annots = os.path.join(sys.argv[2],f"v{params['dcount']}")
pred_annots = os.path.join(sys.argv[3],f"v{params['dcount']}", 'annots')
output = os.path.join(sys.argv[4],f"v{params['dcount']}")
store = os.path.join(sys.argv[5],f"v{params['dcount']}", 'evaluated')

os.makedirs(gt_annots, exist_ok = True)
os.makedirs(pred_annots, exist_ok = True)
os.makedirs(output, exist_ok = True)
os.makedirs(store, exist_ok = True)

print("Evaluating......")
print("DONE!!")