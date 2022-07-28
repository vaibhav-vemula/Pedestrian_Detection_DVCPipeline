import os
import sys
import yaml
import pickle
from tqdm import tqdm
import cv2

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

with open(os.path.join(gt_annots,'v{}.pkl'.format(params['dcount'])),'rb') as f:
    transformed_data = pickle.load(f)

with open(os.path.join(sys.argv[3],'v{}'.format(params['dcount']),'v{}.pkl'.format(params['dcount'])),'rb') as f:
    predicted_data = pickle.load(f)

print("-------------------------------")
print("Evaluating.....")
print("-------------------------------")

def get_iou(bb1, bb2):
	"""
	Calculate the Intersection over Union (IoU) of two bounding boxes.
	Parameters
	----------
	bb1 : dict
		Keys: {'xmin', 'xmax', 'ymin', 'ymax'}
		The (xmin, ymin) position is at the top left corner,
		the (xmax, ymax) position is at the bottom right corner
	bb2 : dict
		Keys: {'xmin', 'xmax', 'ymin', 'ymax'}
		The (x, y) position is at the top left corner,
		the (xmax, ymax) position is at the bottom right corner
	Returns
	-------
	float
		in [0, 1]
	"""
	assert bb1['xmin'] < bb1['xmax']
	assert bb1['ymin'] < bb1['ymax']
	assert bb2['xmin'] < bb2['xmax']
	assert bb2['ymin'] < bb2['ymax']

	# determine the coordinates of the intersection rectangle
	x_left = max(bb1['xmin'], bb2['xmin'])
	y_top = max(bb1['ymin'], bb2['ymin'])
	x_right = min(bb1['xmax'], bb2['xmax'])
	y_bottom = min(bb1['ymax'], bb2['ymax'])

	if x_right < x_left or y_bottom < y_top:
		return 0.0

	# The intersection of two axis-aligned bounding boxes is always an
	# axis-aligned bounding box
	intersection_area = (x_right - x_left) * (y_bottom - y_top)

	# compute the area of both AABBs
	bb1_area = (bb1['xmax'] - bb1['xmin']) * (bb1['ymax'] - bb1['ymin'])
	bb2_area = (bb2['xmax'] - bb2['xmin']) * (bb2['ymax'] - bb2['ymin'])

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
	assert iou >= 0.0
	assert iou <= 1.0
	return iou


image_names_list = transformed_data["name"].unique()
iou_list = []
iou_thresh = 0.5
yolo_metrics = {
			'tp':0, 	# iou>thresh
			'fp': 0, 	# 0<iou<thresh
			'fn':0		# iou==0	
}

for image_name in tqdm(image_names_list, file=sys.__stdout__):
	iou_list = []
	labels = transformed_data[transformed_data["name"]==image_name]
	detections = predicted_data[predicted_data["name"]==image_name]  
	for index1, lab in labels.iterrows():
		largest_iou = 0.0
		for index2, yolo_bb in detections.iterrows():
			iou = get_iou(lab, yolo_bb)
			if iou > largest_iou:
				largest_iou = iou
			if largest_iou==0:
				yolo_metrics['fn'] += 1
			else:
				if largest_iou>iou_thresh:
					yolo_metrics['tp'] += 1
				else:
					yolo_metrics['fp'] += 1
		iou_list.append(largest_iou)
	image_path = labels["image"].iloc[0]
	img = cv2.imread(image_path)
	for index1, lab in labels.iterrows():
		img = cv2.rectangle(img, (round(lab['xmin']), round(lab['ymin'])), (round(lab['xmax']), round(lab['ymax'])), (255,255,0),2)
	for index2, lab in detections.iterrows():
		img = cv2.rectangle(img, (round(lab['xmin']), round(lab['ymin'])), (round(lab['xmax']), round(lab['ymax'])), (0,255,0),2)
	
	
	min_iou = min(iou_list)
	max_iou = max(iou_list)
	avg_iou = sum(iou_list) / len(iou_list)
	img = cv2.putText(img, 'min_iou='+str(round(min_iou,4)), (25,25), 
				cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
				(255, 0, 0), 
				1, cv2.LINE_AA)
	img = cv2.putText(img, 'max_iou='+str(round(max_iou,4)), (25,45), 
				cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
				(255, 0, 0), 
				1, cv2.LINE_AA)
	img = cv2.putText(img, 'avg_iou='+str(round(avg_iou,4)), (25,65), 
				cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
				(255, 0, 0), 
				1, cv2.LINE_AA)

	
	save_path = os.path.join(output, image_name)
	store_path = os.path.join(store, image_name)
	cv2.imwrite(save_path,img)
	cv2.imwrite(store_path,img)

print("Evaluating......")
print("DONE!!")	