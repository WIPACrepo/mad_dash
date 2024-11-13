#!/bin/bash

# Check for the required arguments (only source directory)
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <SOURCE_DIR>"
    exit 1
fi

# Assign the source directory and force destination to the user's home directory
SOURCE_DIR=$(realpath "$1")
DEST_DIR=$(realpath "$HOME/simprod-histograms") # Define the destination under the user's home directory

dir_sample_percentage=0.1  # 10% of directories
file_sample_percentage=0.1 # 10% of .pkl files in each selected directory

echo "Starting the sampling and copying process for Simprod Histograms..."
echo "Source directory: $SOURCE_DIR"
echo "Destination directory: $DEST_DIR"
echo "Sampling $(echo "$dir_sample_percentage * 100" | bc)% of directories and $(echo "$file_sample_percentage * 100" | bc)% of .pkl files within each directory."

# Prepare the destination directory
mkdir -p "$DEST_DIR"

# Find all directories matching "*/histos" and sample 10% of them
total_dirs=$(find "$SOURCE_DIR" -type d -path "*/histos" | wc -l)
sampled_dirs=$(echo "$total_dirs * $dir_sample_percentage" | bc | awk '{print int($1+0.5)}')

find "$SOURCE_DIR" -type d -path "*/histos" | shuf -n "$sampled_dirs" | while read -r subdir; do
    # Define the destination subdirectory path, clean up with realpath, and create it
    dst_subdir=$(realpath "$DEST_DIR/$subdir")
    mkdir -p "$dst_subdir"
    echo "Created directory: $dst_subdir"

    # Find and sample .pkl files, then copy each sampled file
    total_files=$(find "$subdir" -type f -name "*.pkl" | wc -l)
    sampled_files=$(echo "$total_files * $file_sample_percentage" | bc | awk '{print int($1+0.5)}')

    find "$subdir" -type f -name "*.pkl" | shuf -n "$sampled_files" | while read -r file; do
        # Define the destination file path with realpath for clean path
        dst_file=$(realpath "$dst_subdir/${file##*/}")
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
    echo "- **Source Directory**: $SOURCE_DIR"
    echo "- **Sampling Parameters**: $(echo "$dir_sample_percentage * 100" | bc)% of directories and $(echo "$file_sample_percentage * 100" | bc)% of .pkl files within each selected directory."
    echo
    echo "### Destination Information"
    echo "- **Destination Directory**: $DEST_DIR"
    echo "- **Total Sampled Directories**: $(find "$DEST_DIR" -type d | wc -l)"
    echo "- **Total Sampled .pkl Files**: $(find "$DEST_DIR" -type f -name "*.pkl" | wc -l)"
} >>"$readme_file"

echo "Sampling and copying process complete. Summary written to $DEST_DIR/README.md."
