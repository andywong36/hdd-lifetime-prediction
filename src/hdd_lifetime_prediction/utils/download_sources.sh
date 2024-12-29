#! /bin/bash

# This script does the follwoing:
# - Download the detail interactive graphs from https://ars.els-cdn.com/content/image/1-s2.0-S2666827021000219-mmc1.zip into a temporary folder
# - Unzip the file
# Pull out src/hdd_lifetime_prediction/utils/Fig3. Optimal Survival Tree for predicting long-term health.html
# Pull out src/hdd_lifetime_prediction/utils/Fig6. Optimal Survival Tree predicting short-term health.html:Zone.Identifier
# Delete the zip and the temporary folder

# The script is intended to be run from the root of the repository

temp_dir=$(mktemp -d)
echo "Downloading files"
wget https://ars.els-cdn.com/content/image/1-s2.0-S2666827021000219-mmc1.zip -P $temp_dir
unzip $temp_dir/1-s2.0-S2666827021000219-mmc1.zip -d $temp_dir
echo "Moving files"
mv $temp_dir/Supplementary/Fig3.\ Optimal\ Survival\ Tree\ for\ predicting\ long-term\ health.html\
    src/hdd_lifetime_prediction/utils/
mv $temp_dir/Supplementary/Fig6.\ Optimal\ Survival\ Tree\ predicting\ short-term\ health.html\
    src/hdd_lifetime_prediction/utils/
echo "Cleaning up"
rm -rf $temp_dir
