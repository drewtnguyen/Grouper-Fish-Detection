import pandas as pd 
import argparse
from pathlib import Path
import re
from datetime import date

today = str(date.today())

ap = argparse.ArgumentParser()
ap.add_argument("--data", required = True)
ap.add_argument("--processing", required = True)
ap.add_argument("--your_folder", required = True)
args = vars(ap.parse_args())

cols = ['image_name_(auto)', 'date_enrolled_(auto)', 'image_created_date_(auto)', 'parent_folders_(auto)', 'omitted', 'location', 'diver', 'year', 'month', 'day', 'rough_time_of_day', 'image_comments']

fn = args['data']
processing = args['processing']
your_folder = args['your_folder'] #doubles as parent folders, just need to change _--_ to /
parent_folders = your_folder.replace("_--_", "/")

with open(processing) as f:
	rows_list = []
	for line in f:
		img_name = line.strip('\n')
		img_name_no_ext = str(Path(img_name).stem)
		metadat_fn = img_name_no_ext + '_metadata.txt'
		metadat_path = str(Path('enrolled_image_folders', your_folder, 'metadata', metadat_fn))
		with open(metadat_path) as mf:
			time_match = None
			time_info = None
			for mf_line in mf:
				time_match = re.search("exif:DateTime: ", mf_line)
				if time_match:
					time_info = mf_line.strip("exif:DateTime: ")
					time_info = time_info.strip('\n')
					break
		img_dict = {}
		img_dict['image_name_(auto)'] = img_name
		img_dict['date_enrolled_(auto)'] = today
		if time_match:
			img_dict['image_created_date_(auto)'] = time_info
		img_dict['parent_folders_(auto)'] = parent_folders
		rows_list.append(img_dict)

df = pd.DataFrame(rows_list, columns = cols)
df.to_csv(fn, index=False)
