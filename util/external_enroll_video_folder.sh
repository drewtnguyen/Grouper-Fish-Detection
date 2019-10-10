#!/bin/bash
#run this from directory Grouper Moon Image Dataset via the line ./enroll_video_folder.sh --dir DIRECTORY
if [ ! $# -eq 4 ]
  then
    echo "Error; the format is enroll_video_folder.sh --dir DIRECTORY --enroll ENROLL_DIRECTORY"
    exit 2
fi

#########boilerplate code for args
while [ -n "$1" ]; do # while loop starts
    case "$1" in
    --dir) full_path="$2"
        your_folder=$(basename -- "${full_path}")
        shift
        ;;
    --enroll) enroll_dir="$2"
        shift
        ;;
    --)
        shift # The double dash makes them parameters
        break
        ;;
    *) echo "Error; option $1 not recognized. The format is enroll_video_folder.sh --dir DIRECTORY"
        exit 2 
        ;;
    esac
    shift
done

# ########check if there are only video files, otherwise exit
# read -p "Please confirm there are ONLY video files in your folder \"${your_folder}\". If not, and you run this script anyway, you'll enroll unnecessary files. [y/n]" -n 1 -r
# echo    
# if [[ $REPLY =~ ^[Yy]$ ]]; then
# 	true
# else 
# 	echo "Exiting..."
# 	exit 0
# fi

if [ ! -d "${full_path}" ]; then
    echo "${full_path} is a not a directory"
    exit 0
fi

echo "Please confirm there are ONLY video files in your folder \"${your_folder}\". If not, and you run this script anyway, you'll enroll unnecessary files."

#make directory for your folder in enrolled video folders
mkdir -p "${enroll_dir}/${your_folder}"

#####make a directory for each file in the specified folder and fill it with metadata
timestamp=$(date +%s)
processing_fn="processing_${timestamp}_${your_folder}.txt"
ls "${full_path}" > "util/${processing_fn}"
readarray -t files < "util/${processing_fn}"

for fn in "${files[@]}"
do 
	fn_ext=$(basename -- "$fn")
	fn_no_ext="${fn_ext%.*}"
	vid_dir="${enroll_dir}/${your_folder}/${fn_no_ext}"
	mkdir -p "${vid_dir}"
	./util/make_metadata.sh "${full_path}/${fn}" "${fn_no_ext}" "${vid_dir}"
    echo "${fn_ext} enrolled!"
done 

#generate the csv
python util/external_enroll_video_folder.py --data "${enroll_dir}/${your_folder}/${your_folder}.csv" --processing "util/${processing_fn}" --your_folder "${your_folder}" --enroll_dir "${enroll_dir}"

rm "util/${processing_fn}"

