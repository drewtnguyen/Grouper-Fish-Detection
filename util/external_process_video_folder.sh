#!/bin/bash
#run this from directory Grouper Moon Image Dataset via the line ./process_video_folder.sh --dir DIRECTORY --period N --batch_size B --cuda_visible G

#########boilerplate code for args
if [ ! $# -eq 12 ]
  then
    echo "Error; the format is process_video_folder.sh --dir DIRECTORY --enroll ENROLL_DIR --stills STILLS_DIR --period N --batch_size B --cuda_visible G"
    exit 2
fi

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    --dir) full_path="$2"
        media_folder=$(basename -- "${full_path}")
        shift
        ;;
    --enroll) enroll_dir="$2"
        shift
        ;;
    --stills) stills_dir="$2"
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
    *) echo "Error; option $1 not recognized. The format is process_video_folder.sh --dir DIRECTORY --period N --batch_size B"
        exit 2 
        ;;
    esac
    shift
done

# ########check if there are only video files, otherwise exit
# read -p "Please confirm there are ONLY video files in your folder \"${media_folder}\". If not, and you run this script anyway, you'll get an error. [y/n]" -n 1 -r
# echo    
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#   true
# else 
#     echo "Exiting..."
#     exit 0
# fi   

echo "Please confirm there are ONLY video files in your folder \"${media_folder}\". If not, and you run this script anyway, weird stuff might happen."

######check for enrollment of folder, otherwise exit 
if [[ ! -d "${enroll_dir}/${media_folder}" ]]; then
    echo "###########"
    echo "Directory ${enroll_dir}/${media_folder} doesn't exist. Did you enroll your video?"
    echo "Exiting..."
    echo "############"
    exit 0
fi

if [[ ! -f "${enroll_dir}/${media_folder}/${media_folder}.csv" ]]; then
    echo "###########"
    echo "The csv file ${enroll_dir}/${media_folder}/${media_folder}.csv doesn't exist. Did you enroll your video?"
    echo "Exiting..."
    echo "############"
    exit 0
fi


#####run the processing on each file in the specified folder
echo "Starting processing job for ${media_folder}..."

timestamp=$(date +%s)
processing_fn="processing_${timestamp}_${media_folder}.txt"
ls "${full_path}" > "util/${processing_fn}"
readarray -t files < "util/${processing_fn}"
for fn in "${files[@]}"
do 
    fn_ext=$(basename -- "$fn")
    fn_no_ext="${fn_ext%.*}"
    vid_dir="${enroll_dir}/${media_folder}/${fn_no_ext}"
    ./util/external_process_one_video.sh --input_file "${full_path}/${fn}" --output_dir "${vid_dir}" --stills "${stills_dir}" --period "${N}" --batch_size "${B}" --cuda_visible "${G}"
done 

rm "util/${processing_fn}"

python util/get_duration.py --media_folder "${enroll_dir}/${media_folder}" --mode "m" #in minutes

echo "Finished processing job for ${media_folder}"