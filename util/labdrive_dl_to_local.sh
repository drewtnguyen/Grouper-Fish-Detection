#!/bin/bash
#example usage: ./download_folders.sh --src "labdrive:Grouper Moon/Video and Photos/2013/Brice's 60D/1-28-13/Evening" --dest "~/Documents/labdrive_downloads" 
#TODO. allow reading from a text file a list of folders?

mkdir -p "$HOME/Grouper Moon Image Dataset/labdrive_downloads"

if [ ! $# -eq 2 ]
  then
    echo "Syntax error; the format is download_folders.sh --src SOURCE_PATH"
    exit 2
fi


while [ -n "$1" ]; do # while loop starts
 
    case "$1" in
 
    --src) src_fn="$2"
        shift
        ;;
 
    # --dest)
    #     dest_fn="$2" 
    #     shift
    #     ;;
  
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

stripped_src_fn="${src_fn#'labdrive:'}"
dest_fn="$HOME/Grouper Moon Image Dataset/labdrive_downloads"
folder_name=$(echo "${stripped_src_fn}" | sed 's/[\/]/_--_/g')
echo $folder_name
echo "Copying Google Drive directory \"${src_fn}\" to \"${dest_fn}/${folder_name}\"..."
rclone copyto "${src_fn}" "${dest_fn}/${folder_name}" 
