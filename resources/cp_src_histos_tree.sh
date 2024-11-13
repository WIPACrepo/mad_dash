#!/bin/bash

# Check for the required arguments (only source directory)
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <SOURCE_DIR>"
    exit 1
fi

# Assign the source directory and force destination to the user's home directory
SOURCE_DIR="$1"
DEST_DIR="$HOME/simprod-histograms" # Define the destination under the user's home directory

dir_sample_percentage=0.1  # 10% of directories
file_sample_percentage=0.1 # 10% of .pkl files in each selected directory

echo "Starting the sampling and copying process..."
echo "Source directory: $SOURCE_DIR"
echo "Destination directory: $DEST_DIR"
echo "Sampling $((dir_sample_percentage * 100))% of directories and $((file_sample_percentage * 100))% of .pkl files within each directory."

# Find all directories matching "*/histos" and sample 10% of them
find "$SOURCE_DIR" -type d -path "*/histos" | shuf -n $(find "$SOURCE_DIR" -type d -path "*/histos" | wc -l | awk -v pct=$dir_sample_percentage '{print int($1 * pct)}') | while read -r subdir; do
    # Define the destination subdirectory path and create it
    dst_subdir="$DEST_DIR/$subdir"
    mkdir -p "$dst_subdir"
    echo "Created directory: $dst_subdir"

    # Find and sample .pkl files, then copy each sampled file
    find "$subdir" -type f -name "*.pkl" | shuf -n $(find "$subdir" -type f -name "*.pkl" | wc -l | awk -v pct=$file_sample_percentage '{print int($1 * pct)}') | while read -r file; do
        dst_file="$dst_subdir/${file##*/}"
        echo "Copying $file to $dst_file"
        cp "$file" "$dst_file"
    done
done

# Create a high-level README.md file in the main destination directory
readme_file="$DEST_DIR/README.md"
{
    echo "# Simprod Histograms"
    echo
    echo "This directory contains a sampled subset of histogram data files."
    echo
    echo "### Source Information"
    echo "- **Source Directory**: $(realpath "$SOURCE_DIR")"
    echo "- **Sampling Parameters**: $((dir_sample_percentage * 100))% of directories and $((file_sample_percentage * 100))% of .pkl files within each selected directory."
    echo
    echo "### Destination Information"
    echo "- **Destination Directory**: $(realpath "$DEST_DIR")"
    echo "- **Total Sampled Directories**: $(find "$DEST_DIR" -type d | wc -l)"
    echo "- **Total Sampled .pkl Files**: $(find "$DEST_DIR" -type f -name "*.pkl" | wc -l)"
} >>"$readme_file"

echo "Sampling and copying process complete. Summary written to $DEST_DIR/README.md."
