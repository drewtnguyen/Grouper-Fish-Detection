import argparse
import os
import time 

ap = argparse.ArgumentParser()
ap.add_argument("--num", required = True)
ap.add_argument("--log", required = True)
ap.add_argument("--folder_name", required = True)
args = vars(ap.parse_args())

num_files = int(args['num'])
empty_file_log = args['log']
folder_name = args['folder_name']

if num_files == 0:
	print(folder_name + " is empty! logging to " + empty_file_log)
	with open(empty_file_log, 'a+') as f:
		f.write(folder_name)



