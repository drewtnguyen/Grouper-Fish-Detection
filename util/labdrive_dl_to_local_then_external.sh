#!/bin/bash
#example usage: ./download_folders.sh --src "labdrive:Grouper Moon/Video and Photos/2013/Brice's 60D/1-28-13/Evening" --local "~/Documents/labdrive_downloads" --dest "~/media/semmenslab/drew_storage" 
#TODO. allow reading from a text file a list of folders?

if [ ! $# -eq 6 ]
  then
    echo "Syntax error; the format is download_folders.sh --src SOURCE_PATH --local LOCAL --dest DEST_PATH"
    exit 2
fi


while [ -n "$1" ]; do # while loop starts
 
    case "$1" in
 
    --src) src_fn="$2"
        shift
        ;;
        
    --local)
        local_fn="$2" 
        shift
        ;;
 
    --dest)
        dest_fn="$2" 
        shift
        ;;
  
    --)
        shift # The double dash makes them parameters
 
        break
        ;;
 
    *) echo "Error; option $1 not recognized. The format is download_folders.sh --src SOURCE_PATH --local LOCAL --dest DEST_PATH"
        exit 2 
        ;;
 
    esac
 
    shift
 
done

mkdir -p "${dest_fn}"
stripped_src_fn="${src_fn#'labdrive:'}"
folder_name=$(echo "${stripped_src_fn}" | sed 's/[\/]/_--_/g')
echo $folder_name
echo "Copying Google Drive directory \"${src_fn}\" to local directory \"${local_fn}/${folder_name}\"..."
timestamp=$(date +%s)
rclone copyto "${src_fn}" "${local_fn}/${folder_name}" --verbose --log-file="download_logs/dl_log_${timestamp}.txt" 
echo "Copying downloaded file to external directory \"${dest_fn}\"..."
rsync -v -r --stats --progress "${local_fn}/${folder_name}" "${dest_fn}" --log-file="download_logs/rsync_log_${timestamp}.txt" && echo "Deleting file from local..." && rm -r "${local_fn}/${folder_name}"