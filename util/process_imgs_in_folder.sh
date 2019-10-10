#!/bin/bash

#run this from directory fishface_tool via the line ./process_one_video.sh VIDEONAME 

#This script takes in a image folder name, and then in ${enroll_dir} creates a folder of the same name minus the extension. In this folder is also placed:
#1. a folder of bboxes
#2. a csv of where the bboxes are, and an id of which fish they correspond to
#3. the metadata of the video file
#4. the original video, suffixed by _original on it. THe original video is DELETED, so be sure you have a backup!
#5. a second copy of the video at a lower framerate, with bbox annotations, suffixed by _tracked

#use ctrl-z to pause process; you can then kill it with "kill -9 pid"


#. ~/anaconda3/etc/profile.d/conda.sh #enables conda command
#conda activate fishface
#########boilerplate code for args
if [ ! $# -eq 4 ]
  then
    echo "Error; the format is process_one_video.sh --input_dir DIRECTORY --output_dir DIRECTORY"
    exit 2
fi

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    --input_dir) input_dir="$2"
        your_folder=$(basename -- "${input_dir}")
        shift
        ;;
    --output_dir) enroll_dir="$2" #should be the folder corresponding to the specific video
        mkdir -p "${enroll_dir}"
        shift
        ;;
    --)
        shift # The double dash makes them parameters
        break
        ;;
    *) echo "Error; option $1 not recognized. The format is process_one_video.sh --input_file FILE --output_dir DIRECTORY"
        exit 2 
        ;;
    esac
    shift
done

start=`date +%s`
echo "[1/3] Processing image folder ${input_dir}..."
path_to_frozen_graph="lib/tf_scripts/exported_models/faster_rcnn_resnet101_joe_data_fgvc/frozen_inference_graph.pb"
path_to_labels="lib/tf_scripts/data/grouper_label_map.pbtxt"
PYTHONPATH=`pwd`/lib/tf_scripts/models/research:`pwd`/lib/tf_scripts/models/research/slim \
    python lib/tf_scripts/detect_folder_imgs.py --graph "${path_to_frozen_graph}" --labels "${path_to_labels}" --imgs_dir "${input_dir}" --csv_dir "${enroll_dir}" #makes a csv of bboxes in enroll_dir

######at this stage we have a csv of bboxes, and a folder of images in temp dir. let's make the annotated video and bboxes as images
echo "[2/3] Using processing results to get bboxes..."
dat="${enroll_dir}/${your_folder}_detections_output.csv"
mkdir -p "${enroll_dir}/bboxes"
rm -rf "${enroll_dir}/bboxes/*"
python lib/simple-object-tracking/visualize_tracking_imgs.py -dat "${dat}" -imgfold "${input_dir}" -outdir "${enroll_dir}/tracked_images" \
    -boxesdir "${enroll_dir}/bboxes" #makes bboxes and annotated images

echo "[3/3] Cleaning up..."
python util/make_blank_annotation_csv.py --name "${your_folder}" --outdir "${enroll_dir}"


end=`date +%s`
runtime=$((end-start))
echo "Completed processing image folder ${your_folder} in ${runtime} seconds"
echo "Completed processing image folder ${your_folder} in ${runtime} seconds" > "${enroll_dir}/${your_folder}_time_taken.txt"