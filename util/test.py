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

video_fexts = ['.mov', '.Mov', '.MOV','.mp4', '.Mp4', '.MP4','.mts','.Mts','.MTS','.m4v','.M4v','.M4V']
image_fexts = ['.jpg','.Jpg','.JPG','.jpeg','.Jpeg','.JPEG','.png','.Png','.PNG','.cr2','.Cr2','.CR2']
raw_fexts = ['.cr2','.Cr2','.CR2','.nef','.Nef','.NEF']

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

def is_raw(fn):
    if Path(fn).suffix in raw_fexts:
        return True
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
path = '/media/piglet/GM LASER 19/drew_storage/separated media/VIDEOS_(4K)_1567814783/Grouper Moon_--_Fish faces_--_2018_fish_faces_--_fish_faces_--_013118_afternoon_--_brice_bxs_(VIDEO)_(4K)/P1311004.JPG'

print(is_raw(path))



