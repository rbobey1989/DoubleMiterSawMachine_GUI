#!/bin/bash

# Define the source and destination paths
src_path1_with_ext="DoubleMitreSawMachine.py"
src_path1_without_ext="DoubleMitreSawMachine"
src_path2="ProfileWidgets"
src_path3="ActionBtnsWidgets"
src_path8="CSVViewerWidget"
src_path9="DxfViewer"
src_path10="DxfExplorer"
src_path11="DxfDataBase"
dest_path_src="/usr/bin/DoubleMitreSawMachine/"

dest_path_config="/home/rbobey1989/linuxcnc/configs/DoubleMitreSawMachine/"
src_path4="icons"
src_path5="images"
src_path6="splash_screen"
src_path7="css_styles_sheets"

# Create the destination directory if it does not exist
mkdir -p "$dest_path_src"
echo "Creating directory: $dest_path_config"
mkdir -p "$dest_path_config"

# Remove the existing destination files and directories, if they exist
if [ -f "${dest_path_src}${src_path1_without_ext}" ]; then
    rm "${dest_path_src}${src_path1_without_ext}"
fi

if [ -d "${dest_path_src}${src_path2}" ]; then
    rm -r "${dest_path_src}${src_path2}"
fi

if [ -d "${dest_path_src}${src_path3}" ]; then
    rm -r "${dest_path_src}${src_path3}"
fi

if [ -d "${dest_path_src}${src_path8}" ]; then
    rm -r "${dest_path_src}${src_path8}"
fi

if [ -d "${dest_path_config}${src_path9}" ]; then
    rm -r "${dest_path_config}${src_path9}"
fi

if [ -d "${dest_path_config}${src_path10}" ]; then
    rm -r "${dest_path_config}${src_path10}"
fi

if [ -d "${dest_path_config}${src_path11}" ]; then
    rm -r "${dest_path_config}${src_path11}"
fi

if [ -d "${dest_path_config}${src_path4}" ]; then
    rm -r "${dest_path_config}${src_path4}"
fi

if [ -d "${dest_path_config}${src_path5}" ]; then
    rm -r "${dest_path_config}${src_path5}"
fi

if [ -d "${dest_path_config}${src_path6}" ]; then
    rm -r "${dest_path_config}${src_path6}"
fi

if [ -d "${dest_path_config}${src_path7}" ]; then
    rm -r "${dest_path_config}${src_path7}"
fi



# Copy the source files and directories to the destination
cp "$src_path1_with_ext" "${dest_path_src}${src_path1_without_ext}"
cp -r "$src_path2" "${dest_path_src}"
cp -r "$src_path3" "${dest_path_src}"
cp -r "$src_path8" "${dest_path_src}"
cp -r "$src_path9" "${dest_path_src}"
cp -r "$src_path10" "${dest_path_src}"
cp -r "$src_path11" "${dest_path_src}"

cp -r "$src_path4" "${dest_path_config}"
cp -r "$src_path5" "${dest_path_config}"
cp -r "$src_path6" "${dest_path_config}"
cp -r "$src_path7" "${dest_path_config}"


# Change the permissions of the destination files to make them executable
chmod +x "${dest_path_src}${src_path1_without_ext}"
