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
ap.add_argument("--enroll_dir", required = True)
args = vars(ap.parse_args())

cols = ['video_name_(auto)', 'date_enrolled_(auto)', 'video_created_date_(auto)', 'parent_folders_(auto)', 'omitted', 'location', 'diver', 'year', 'month', 'day', 'rough_time_of_day', 'video_comments']

fn = args['data']
processing = args['processing']
your_folder = args['your_folder'] #doubles as parent folders, just need to change _--_ to /
enroll_dir = args['enroll_dir']
parent_folders = your_folder.replace("_--_", "/")

with open(processing) as f:
	rows_list = []
	for line in f:
		vid_name = line.strip('\n')
		vid_name_no_ext = str(Path(vid_name).stem)
		metadat_fn = vid_name_no_ext + '_metadata.txt'
		metadat_path = str(Path(enroll_dir, your_folder, vid_name_no_ext, metadat_fn))
		with open(metadat_path) as mf:
			time_match = None
			time_info = None
			for mf_line in mf:
				time_match = re.search("TAG:creation_time=", mf_line)
				if time_match:
					time_info = mf_line.strip("TAG:creation_time=")
					time_info = time_info.strip('\n')
					break
		vid_dict = {}
		vid_dict['video_name_(auto)'] = vid_name
		vid_dict['date_enrolled_(auto)'] = today
		if time_match:
			vid_dict['video_created_date_(auto)'] = time_info
		vid_dict['parent_folders_(auto)'] = parent_folders
		rows_list.append(vid_dict)

df = pd.DataFrame(rows_list, columns = cols)
df.to_csv(fn, index=False)
