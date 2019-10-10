#!/bin/bash

#run this from directory fishface_tool via the line ./process_one_video.sh VIDEONAME 

#This script takes in a video name, and then in ${vid_dir} creates a folder of the same name minus the extension. In this folder is also placed:
#1. a folder of bboxes
#2. a csv of where the bboxes are, and an id of which fish they correspond to
#3. the metadata of the video file
#4. the original video, suffixed by _original on it. THe original video is DELETED, so be sure you have a backup!
#5. a second copy of the video at a lower framerate, with bbox annotations, suffixed by _tracked

#use ctrl-z to pause process; you can then kill it with "kill -9 pid"

#. ~/anaconda3/etc/profile.d/conda.sh #enables conda command
#conda activate fishface
#########boilerplate code for args
if [ ! $# -eq 12 ]
  then
    echo "Error; the format is process_one_video.sh --input_file FILE --output_dir DIRECTORY --stills STILLS_DIR --period N --batch_size B --cuda_visible G"
    exit 2
fi

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    --input_file) fn="$2"
        fn_ext=$(basename -- "$fn")
        fn_no_ext="${fn_ext%.*}"
        ext="${fn_ext##*.}"
        fn_orig="${fn_no_ext}_original.${ext}"
        shift
        ;;
    --output_dir) vid_dir="$2" #should be the folder corresponding to the specific video
        temp_dir="${vid_dir}/DO_NOT_EDIT_temp_folder_for_storing_stills"
        mkdir -p "${vid_dir}"
        mkdir -p "${temp_dir}"
        shift
        ;;
    --stills) stills="$2" #should be the folder corresponding to the specific video
        shift
        ;;
    --period) N="$2"
        shift
        ;;
    --batch_size) B="$2"
        shift
        ;;
    --cuda_visible) G="$2"
        shift
        ;;
    --)
        shift # The double dash makes them parameters
        break
        ;;
    *) echo "Error; option $1 not recognized. The format is process_one_video.sh --input_file FILE --output_dir DIRECTORY --period N --batch_size B"
        exit 2 
        ;;
    esac
    shift
done


start=`date +%s`

echo "Beginning processing for ${fn_ext}..."

###make the stills
echo "[1/5] Making stills for processing..."
#N=0.25 #period to sample pictures, in seconds. typically N=0.25, which means 4 frames per second

mkdir -p "${stills}/gpu_${G}"

if [ "$ext" = "MTS" ] || [ "$ext" = "mts" ] ; then
    echo "Deinterlacing MTS file..." 
    ffmpeg -hide_banner -noautorotate -loglevel panic -i "${fn}" -vf "fps=1/${N},yadif=0:-1:1" -q:v 1 "${stills}/gpu_${G}/outfile_%d.jpg"
    #currently this deinterlaces IF it's an MTS container and IF it says the frame is interlaced. this may not work in general, but i guess we can watch out for that. 
else 
    ffmpeg -hide_banner -noautorotate -loglevel panic -i "${fn}" -vf fps=1/${N} -q:v 1 "${stills}/gpu_${G}/outfile_%d.jpg"
fi 

echo "stills generated. now renaming stills..."

#now process the stills we've made
python util/process_stills.py --N "${N}" --vidname "${fn}" --to_process "${stills}/gpu_${G}" --outdir "${temp_dir}"

###now run the detection network, and save results to a csv
echo "[2/5] Processing stills with detection neural net..."
path_to_frozen_graph="lib/tf_scripts/exported_models/faster_rcnn_resnet101_joe_data_fgvc/frozen_inference_graph.pb"
path_to_labels="lib/tf_scripts/data/grouper_label_map.pbtxt"
PYTHONPATH=`pwd`/lib/tf_scripts/models/research:`pwd`/lib/tf_scripts/models/research/slim \
    python lib/tf_scripts/detect_folder.py --batch_size "${B}" --graph "${path_to_frozen_graph}" --labels "${path_to_labels}" --imgs_dir "${temp_dir}" --csv_dir "${vid_dir}" --cuda_visible "${G}" #makes a csv of bboxes 

######at this stage we have a csv of bboxes, and a folder of images in temp dir. let's make the annotated video and bboxes as images
echo "[3/5] Using detection results to get bboxes..."
dat_no_id="${vid_dir}/${fn_no_ext}_detections_output.csv"
mkdir -p "${vid_dir}/tracked_frames"
mkdir -p "${vid_dir}/imgs_to_stitch"
mkdir -p "${vid_dir}/bboxes"
rm -rf "${vid_dir}/tracked_frames/*"
rm -rf "${vid_dir}/imgs_to_stitch/*"
rm -rf "${vid_dir}/bboxes/*"

python lib/simple-object-tracking/object_tracker_imgs.py -md 4 -dat "${dat_no_id}" -outdir "${vid_dir}" #makes the bboxes and does some initial tracking
dat_id="${vid_dir}/${fn_no_ext}_detections_output_with_obj_id.csv"
python lib/simple-object-tracking/visualize_tracking.py -dat "${dat_id}" -imgfold "${temp_dir}" -outdir "${vid_dir}/tracked_frames" -outtemp "${vid_dir}/imgs_to_stitch"\
    -boxesdir "${vid_dir}/bboxes"  #makes bboxes and annotated images
echo "[4/5] Using detection results to get annotated video..."
ffmpeg -hide_banner -loglevel panic -framerate 1/${N} -i "${vid_dir}/imgs_to_stitch/img_%d.jpg" -pix_fmt yuv420p -c:v libx264 "${vid_dir}/${fn_no_ext}_tracked.mp4" #stitches images to make annotated video

####do some clean up
echo "[5/5] Cleaning up..."
#mv "${fn}" "${vid_dir}/${fn_orig}"
#cp "${fn}" "${vid_dir}/${fn_orig}"
rm -rf "${vid_dir}/imgs_to_stitch"
rm -rf "${temp_dir}"
rm "$dat_no_id"
rm -rf "${stills}/gpu_${G}"/*
python util/make_blank_annotation_csv.py --name "${fn_no_ext}" --outdir "${vid_dir}"

end=`date +%s`
runtime=$((end-start))
framerate=$(bc <<< "scale=3;1/${N}")
echo "Completed processing video ${fn_ext} in ${runtime} seconds; output at ${framerate} fps"
echo "Completed processing video ${fn_ext} in ${runtime} seconds; output at ${framerate} fps" > "${vid_dir}/${fn_no_ext}_time_taken"

