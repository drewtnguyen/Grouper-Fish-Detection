import sys
import os
import subprocess
from pathlib import Path 
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--vidname", required = True)
ap.add_argument("--N", required = True)
ap.add_argument("--outdir", required = True)
ap.add_argument("--to_process", required = True)
args = vars(ap.parse_args())

vidname_fullpath = args['vidname']
vidname = str(Path(vidname_fullpath).stem)
N = float(args['N'])


#dest_dir = Path('processed_video_queue',vidname, 'DO_NOT_EDIT_temp_folder_for_storing_stills')
dest_dir = args['outdir']
to_process = args['to_process']

for orig_fn in os.listdir(to_process):
    if orig_fn[:8] == 'outfile_':
        fn = orig_fn[8:]
        im_num = int(Path(fn).stem)
        s = im_num*N
        hr = s//3600
        s = s - 3600*hr
        m = s//60
        s = s - 60*m
        ms = round((s - int(s))*1000)
        tstamp = '{0:02d}_{1:02d}_{2:02d}_{3:02d}'.format(int(hr),int(m),int(s),int(ms))
        fn = vidname + "_-_" + tstamp + "_-_" + fn
        fn = Path(dest_dir, fn)
        orig_fn = Path(to_process, orig_fn)
        os.rename(str(orig_fn), str(fn)) #also moves files to another directory if the new directory is different!

