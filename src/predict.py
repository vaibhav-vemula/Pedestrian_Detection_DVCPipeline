import torch
import sys
import os
from PIL import Image
import yaml
import glob

if len(sys.argv) != 4:
    sys.stderr.write('Arguments error. Usage:\n')
    sys.stderr.write(
        '\tpython3 src/predict.py data/prepared data/predictions data/store\n'
    )
    sys.exit(1)

params = yaml.safe_load(open('params.yaml'))['ingest']


data_path = os.path.join(sys.argv[1], f"v{params['dcount']}", 'images')
predict_path = os.path.join(sys.argv[2], f"v{params['dcount']}", 'images')
origpred = os.path.join(sys.argv[3], f"v{params['dcount']}", 'predictions')

print(predict_path)
print(data_path)

os.makedirs(predict_path, exist_ok=True)
os.makedirs(origpred, exist_ok=True)

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, _verbose =False)
model.classes = [0]
img = os.path.join(data_path, os.listdir(data_path)[0])

preds = glob.glob(f'{data_path}/*.jpg', recursive=True)
labels = os.listdir(data_path)

results = model(preds)
results.render()

for index,im in enumerate(results.imgs):
    img = Image.fromarray(im)
    img.save(f'{predict_path}/{labels[index]}')
    img.save(f'{origpred}/{labels[index]}')
