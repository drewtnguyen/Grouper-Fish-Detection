#!/bin/bash
#example usage: ./download_folders.sh --src "labdrive:Grouper Moon/Video and Photos/2013/Brice's 60D/1-28-13/Evening" --dest "~/Documents/labdrive_downloads" 
#TODO. allow reading from a text file a list of folders?

if [ ! $# -eq 4 ]
  then
    echo "Syntax error; the format is download_folders.sh --src SOURCE_PATH --dest DEST_PATH"
    exit 2
fi


while [ -n "$1" ]; do # while loop starts
 
    case "$1" in
 
    --src) src_fn="$2"
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
 
    *) echo "Error; option $1 not recognized. The format is download_folders.sh --src SOURCE_PATH --dest DEST_PATH"
        exit 2 
        ;;
 
    esac
 
    shift
 
done

mkdir -p "${dest_fn}"
stripped_src_fn="${src_fn#'labdrive:'}"
folder_name=$(echo "${stripped_src_fn}" | sed 's/[\/]/_--_/g')
echo $folder_name
echo "Copying Google Drive directory \"${src_fn}\" to \"${dest_fn}/${folder_name}\"..."
timestamp=$(date +%s)
rclone copyto "${src_fn}" "${dest_fn}/${folder_name}" --verbose --log-file="download_logs/dl_log_${timestamp}.txt" 
#count if there are any empty files
num_files=$(ls "${dest_fn}/${folder_name}" -1 | wc -l)
touch "${dest_fn}/empty_files_log.txt" #count in case any files turn up empty
python util/note_empty_files.py --num "${num_files}" --log "${dest_fn}/empty_files_log.txt" --folder_name "${folder_name}"

