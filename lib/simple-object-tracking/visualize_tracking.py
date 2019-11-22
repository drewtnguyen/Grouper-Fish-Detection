import numpy as np
import pandas as pd
import argparse
import imutils
import time
import cv2
import shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("-dat", "--detectionsdatawithids", required=True,
	help="csv with bounding boxes and object ids")
ap.add_argument("-imgfold", "--folderwithimgs", required=True,
	help="folder of images")
ap.add_argument("-outdir", "--output_directory", required = False, help = 'output directory to save images')
ap.add_argument("-outtempdir", "--output_temp_directory", required = True, help = 'output directory to save temp images')
ap.add_argument("-boxesdir", "--bboxes_directory", required = True, help = "directory for bboxes")
args = vars(ap.parse_args())


df = pd.read_csv(args['detectionsdatawithids'], index_col = [0,1])
imgfold = args['folderwithimgs']
frames = set(df.index.get_level_values(0))
frames = list(frames)
frames.sort()
for frame_num, frame in enumerate(frames):
	#print(frame)
	fn = str(Path(imgfold, str(frame) + '.jpg'))
	img = cv2.imread(fn)
	img_copy = cv2.imread(fn)
	if img is None:
		sys.exit('failed to load image: %s' % image_path)
	#img = img[..., ::-1]  # BGR to RGB

	frame_detects = df.loc[frame]

	# loop over the tracked objects
	for detect_num, row in frame_detects.iterrows():
		if detect_num == 0:
			continue
		boxID = df.index.get_loc((frame,detect_num))
		objectID = int(row['obj_id'])
		ymin = int(row['ymin'])
		ymax = int(row['ymax'])
		xmin = int(row['xmin'])
		xmax = int(row['xmax'])
		centroid = (int(row['xmean']), int(row['ymean']))
		top_left = (xmin, ymin)
		bottom_right = (xmax, ymax)
		box_fn = str(Path(args['bboxes_directory'], str(frame) + "_ID" + str(objectID) + "_box" + str(boxID) + ".jpg"))
		box_img = img[ymin:ymax, xmin:xmax]
		cv2.imwrite(box_fn, box_img)
		#import pdb; pdb.set_trace()
		# draw both the ID of the object and the centroid of the
		# object on the output frame
		fish_id_text = "ID {}".format(objectID)
		box_id_text = "BB {}".format(boxID)
		cv2.putText(img_copy, fish_id_text, (centroid[0] - 10, centroid[1] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
		cv2.putText(img_copy, box_id_text, (centroid[0] - 20, centroid[1] + 20),
			cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
		cv2.circle(img_copy, center = (centroid[0], centroid[1]), radius = 4, color = (0, 255, 0), thickness = -1)
		cv2.rectangle(img_copy, top_left, bottom_right, color = (0, 255, 0), thickness = 1)
	out_fn_temp = str(Path(args['output_temp_directory'], "img_" + str(frame_num) + ".jpg"))
	cv2.imwrite(out_fn_temp, img_copy)

bboxes_to_zip = args['bboxes_directory']
bboxes_zip_fn = bboxes_to_zip

try: 
	shutil.make_archive(bboxes_zip_fn, 'zip', bboxes_to_zip)
	zip_success = True
except:
	zip_success = False

if zip_success:
	shutil.rmtree(bboxes_to_zip)