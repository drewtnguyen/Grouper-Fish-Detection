#!/bin/bash
fn="$1"
fn_no_ext="$2"
metadata_dir="$3"
identify -verbose "${fn}" | grep "exif:" > "${metadata_dir}/${fn_no_ext}_metadata.txt"