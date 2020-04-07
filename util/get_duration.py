import subprocess
import re
from pymediainfo import MediaInfo
import os
import argparse
from pathlib import Path

def get_duration(filename):
    result = subprocess.Popen(["ffprobe", filename],
             stdout = subprocess.PIPE, 
             stderr = subprocess.STDOUT
             )
    stdout, stderr = result.communicate()
    dur_list = [x for x in stdout.splitlines() if b"Duration" in x]
    dur = dur_list[0].decode()
    times_str = dur.split(",")[0].split(":")
    times = {"hours" : float(times_str[1]), "minutes": float(times_str[2]), "seconds": float(times_str[3])}
    seconds = 3600*times['hours'] + 60*times['minutes'] + times['seconds']
    minutes = round(seconds/60,3)
    hours = round(seconds/3600,3)
    return {"in_hours": hours, "in_minutes": minutes, "in_seconds": seconds}

def find_tracked_dropped_videos(path):
    all_tracked = []
    all_dropped = []
    for root, dirs, files in os.walk(path):
        vids_tracked = [os.path.join(root,file) for file in files if "_tracked.mp4" in file]
        vids_dropped = [os.path.join(root,file) for file in files if "_dropped.mp4" in file]
        all_tracked = all_tracked + vids_tracked
        all_dropped = all_dropped + vids_dropped
    return all_tracked, all_dropped

def get_total_duration(media_path, mode = 'm'):
    duration_fn = str(Path(media_path, "total_duration.txt"))
    tracked, dropped = find_tracked_dropped_videos(media_path)

    if mode == 's':
        unit = 'seconds'
        ttimes = [get_duration(vid)['in_seconds'] for vid in tracked]
        dtimes = [get_duration(vid)['in_seconds'] for vid in dropped]
    elif mode == 'm':
        unit = 'minutes'
        ttimes = [get_duration(vid)['in_minutes'] for vid in tracked]
        dtimes = [get_duration(vid)['in_minutes'] for vid in dropped]
    elif mode == 'h':
        unit = 'hours'
        ttimes = [get_duration(vid)['in_hours'] for vid in tracked]
        dtimes = [get_duration(vid)['in_hours'] for vid in dropped]
    else:
        print('mode is s, or m, or h')
        return None

    result_t = sum(ttimes)
    result_d = sum(dtimes)

    tracked_str = "tracked: " + str(result_t) + " " + str(unit)
    dropped_str = "dropped: " + str(result_d) + " " + str(unit)

    with open(duration_fn, "w+") as f: 
        f.write(tracked_str + "\n")
        f.write(dropped_str + "\n")

    print("Times for ", media_path)
    print("----------------------")
    print(tracked_str)
    print(dropped_str)
    return None


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--media_folder", required = True, help = 'this folder contains only video and images')
    ap.add_argument("--mode", required = True, help = 'directory to save sorted files')
    args = vars(ap.parse_args())

    mf = args['media_folder']
    md = args['mode']

    get_total_duration(mf, md)
