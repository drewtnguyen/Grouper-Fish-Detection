import pandas as pd 
import argparse
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--name", required = True)
ap.add_argument("--outdir", required = True)
args = vars(ap.parse_args())

name = args['name']
fn = name + '_bboxes_to_keep.csv'
outdir = args['outdir']
fn = str(Path(outdir, fn))


df = pd.DataFrame(columns = ['best_bboxes', 'tagged', 'comments', 'same_as_other_box', 'laser','phase'])
df.to_csv(fn, index=False)

