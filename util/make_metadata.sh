#!/bin/bash
fn="$1"
fn_no_ext="$2"
vid_dir="$3"
ffprobe -hide_banner -loglevel panic -i "${fn}" -show_format -show_streams > "${vid_dir}/${fn_no_ext}_metadata.txt"