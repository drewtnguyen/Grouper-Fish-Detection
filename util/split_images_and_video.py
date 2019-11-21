import argparse
import os
from pathlib import Path
import shutil
import time
from pymediainfo import MediaInfo
import imghdr 
import cv2
from PIL import Image

#all raw images have already been converted to png by now, or should be.

video_fexts = ['.mov', '.Mov', '.MOV','.mp4', '.Mp4', '.MP4','.mts','.Mts','.MTS','.m4v','.M4v','.M4V', '.wmv', '.Wmv', '.WMV', '.avi', '.Avi', '.AVI']
image_fexts = ['.jpg','.Jpg','.JPG','.jpeg','.Jpeg','.JPEG','.png','.Png','.PNG','.cr2','.Cr2','.CR2']

def is_video(fn):
    if Path(fn).suffix in video_fexts:
        return True
    fn_info = MediaInfo.parse(fn)
    for track in fn_info.tracks:
        if track.track_type == 'Video':
            return True 
    return False 

def is_image(fn):
    if Path(fn).suffix in image_fexts:
        return True
    if imghdr.what(fn):
        return True
    try:
        Image.open(fn)
        return True
    except:
        pass
    return False

def is_4k(fn):
    vid = cv2.VideoCapture(fn)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    if height > 2900 or width > 2900:
        vid.release()
        return True
    else:
        vid.release()
        return False



ap = argparse.ArgumentParser()
ap.add_argument("--media_folder", required = True, help = 'this folder contains only video and images')
ap.add_argument("--out_dir", required = True, help = 'directory to save sorted files')
ap.add_argument("--timestamp", required = True)

args = vars(ap.parse_args())

fold = args['media_folder']
stamp = args['timestamp']

basenm = os.path.basename(fold)

out_dir = args['out_dir']
out_dir_vid = str(Path(out_dir, 'VIDEOS_' + stamp))
out_dir_vid_4k = str(Path(out_dir, 'VIDEOS_(4K)_' + stamp))
out_dir_imgs = str(Path(out_dir, 'IMAGES_' + stamp))
fold_vids = basenm + '_(VIDEO)'
fold_vids_4k = basenm + '_(VIDEO)_(4K)'
fold_imgs = basenm + '_(IMAGES)'
full_path_fold_vids = str(Path(out_dir_vid,fold_vids))
full_path_fold_vids_4k = str(Path(out_dir_vid_4k,fold_vids_4k))
full_path_fold_imgs = str(Path(out_dir_imgs,fold_imgs))

Path(full_path_fold_vids).mkdir(parents = True, exist_ok = True)
Path(full_path_fold_vids_4k).mkdir(parents = True, exist_ok = True)
Path(full_path_fold_imgs).mkdir(parents = True, exist_ok = True)

images_and_video = os.listdir(str(fold))

for fn in images_and_video:
    if fn[0] == '.' or Path(fn).suffix == '.LRV' or Path(fn).suffix == '.THM':
        continue
    full_path = str(Path(fold, fn))
    if is_video(full_path): 
        if is_4k(full_path):
            shutil.move(src = full_path, dst = full_path_fold_vids_4k)
        else:
            shutil.move(src = full_path, dst = full_path_fold_vids)
    elif is_image(full_path):
        shutil.move(src = full_path, dst = full_path_fold_imgs)
    else:
        print("In folder " + basenm + ", ignoring file "+ "fn")

try: 
    os.rmdir(full_path_fold_vids)
    print("no videos found in folder " + basenm)
except: 
    pass

try: 
    os.rmdir(full_path_fold_vids_4k)
    print("no 4K videos found in folder " + basenm)
except: 
    pass

try: 
    os.rmdir(full_path_fold_imgs)
    print("no images found in folder " + basenm)
except: 
    pass







