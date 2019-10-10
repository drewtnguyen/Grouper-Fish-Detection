import pandas as pd 
import argparse
import os
from os import listdir
from pathlib import Path
import shutil
import time

ap = argparse.ArgumentParser()
ap.add_argument("--your_folder", required = True)
args = vars(ap.parse_args())

yf = args['your_folder']
yf_stem = os.path.basename(yf)
#files_all= listdir(yf) #video directories and a csv
#files_dirs = [f in files_all if f[-4:] != ".csv"]
yf_csv =  yf_stem + ".csv"
yf_csv = str(Path(yf, yf_csv))
df_yf = pd.read_csv(yf_csv) #has columns video_name_(auto)  date_enrolled_(auto)    video_created_date_(auto)   parent_folders_(auto)   omitted    location    diver   year    month   day rough_time_of_day   video_comments

bbox_cols = ['bbox_name_(auto)', 'date_enrolled_(auto)', 'created_date_(auto)', 'parent_folders_(auto)', 'location', 'diver', 'year', 'month', 'day', 'rough_time_of_day', 'video_comments', 'bbox_comments', 'tagged', 'same_as_other_box', 'laser','phase','xmin', 'ymin', 'xmax', 'ymax', 'score', 'obj_id']

now = str(int(time.time()))
all_bboxes_path = str(Path('extracted_bboxes', yf_stem + '_--_' + now, 'all_boxes')) 
all_bboxes_bboxes = str(Path('extracted_bboxes', yf_stem + '_--_' + now, 'all_boxes', 'bboxes')) 
Path.mkdir(Path(all_bboxes_bboxes), parents = True)

final_dfs = [] 

# folder structure:

# extracted bboxes >>> subdirs yf >>>> all_bboxes and also by video. each all bboxes and video has a folder of bboxes and a csv

for _, yf_row in df_yf.iterrows(): #i.e., for a given video

    if pd.isnull(yf_row['omitted']): #if video is not omitted
        #define some filenames
        #fn_all is the auto-generated csv of detections
        #fn_keep is the user-generated csv of bboxes to keep for this video
        #bboxes folder is the directory containing all the bboxes for this video
        vid_fn = yf_row['video_name_(auto)']
        video_folder = str(Path(vid_fn).stem)
        fn_keep = video_folder + "_bboxes_to_keep.csv"
        fn_all = video_folder + "_detections_output_with_obj_id.csv"
        fn_keep = str(Path(yf, video_folder, fn_keep)) 
        fn_all = str(Path(yf, video_folder, fn_all)) #a csv with columns xmin  ymin    xmax    ymax    score   xmean   ymean   obj_id
        bboxes_folder = str(Path(yf, video_folder, "bboxes"))
        #load the data
        df_keep = pd.read_csv(fn_keep)
        df_all = pd.read_csv(fn_all)
        #load all bboxes into memory as a dict
        bboxes = listdir(bboxes_folder)
        bbox_nums = [int(bbox.rsplit(sep = "_box")[1][:-4]) for bbox in bboxes]
        bboxes_dict = dict(zip(bbox_nums, bboxes))    
        #make some empty lists
        df_finals_rows_list = [] #gonna be a list of dicts, then convert to a df of bboxes with cols bbox_cols
        for _, row_keep in df_keep.iterrows():
            box_num = int(row_keep['best_bboxes'])
            next_row = {}
            next_row['bbox_name_(auto)'] = bboxes_dict[box_num]
            next_row['date_enrolled_(auto)'] = yf_row['date_enrolled_(auto)']
            next_row['created_date_(auto)'] = yf_row['video_created_date_(auto)']
            next_row['parent_folders_(auto)'] = yf_row['parent_folders_(auto)']
            next_row['location'] = yf_row['location']
            next_row['diver']  = yf_row['diver']
            next_row['year'] = yf_row['year']
            next_row['month'] = yf_row['month']
            next_row['day'] = yf_row['day']
            next_row['rough_time_of_day'] = yf_row['rough_time_of_day']
            next_row['video_comments'] = yf_row['video_comments']
            next_row['bbox_comments'] = row_keep['comments']
            try: #i forgot to add the tagged ones in!
                next_row['tagged'] = row_keep['tagged']
            except:
                pass
            try: #i forgot to add the tagged ones in!
                next_row['same_as_other_box'] = row_keep['same_as_other_box']
            except:
                pass
            try: #i forgot to add the tagged ones in!
                next_row['laser'] = row_keep['laser']
            except:
                pass
            try: #i forgot to add the tagged ones in!
                next_row['phase'] = row_keep['phase']
            except:
                pass
            next_row['xmin'] = df_all.iloc[box_num]['xmin']
            next_row['ymin'] = df_all.iloc[box_num]['ymin']
            next_row['xmax'] = df_all.iloc[box_num]['xmax']
            next_row['ymax'] = df_all.iloc[box_num]['ymax']
            next_row['score'] = df_all.iloc[box_num]['score']
            next_row['xmean'] = df_all.iloc[box_num]['ymean']
            next_row['obj_id'] = df_all.iloc[box_num]['obj_id']
            df_finals_rows_list.append(next_row)
        #make the final dataframe for this video
        df_final = pd.DataFrame(df_finals_rows_list, columns = bbox_cols)
        final_dfs.append(df_final)
        #create the directories we're going to save this csv to
        video_bboxes_path = str(Path('extracted_bboxes', yf_stem + '_--_' + now, video_folder))
        video_bboxes_bboxes = str(Path('extracted_bboxes', yf_stem + '_--_' + now, video_folder, 'bboxes'))
        Path.mkdir(Path(video_bboxes_bboxes), parents = True)
        #save the csv 
        vid_csv_fn = str(Path(video_bboxes_path, video_folder + '_kept_bboxes.csv'))
        df_final.to_csv(vid_csv_fn, index=False)
        #now copy the bboxes into video_bboxes_bboxes, AND into all_bboxes_bboxes
        bboxes_to_keep = df_final['bbox_name_(auto)'].to_list()
        bboxes_to_keep_paths = [str(Path(bboxes_folder, bbox)) for bbox in bboxes_to_keep]

        for bbox_path in bboxes_to_keep_paths:
            shutil.copy(src = bbox_path, dst = video_bboxes_bboxes)
            shutil.copy(src = bbox_path, dst = all_bboxes_bboxes)

#finally, make the final combined df

combined_csv_fn = str(Path(all_bboxes_path, yf_stem + '_all_kept_bboxes.csv'))
combined_df = pd.concat(final_dfs)
combined_df.to_csv(combined_csv_fn, index = False)

print("finished! bboxes are in extracted_bboxes directory!")







