#!/usr/bin/env sh

INPUT_DIR=$1


echo "Removing ansi color in log files..."

for file in $(find $INPUT_DIR -name "*.log"); do
    echo "- $file"
    mv $file "$file.bak"
    ansifilter -i "$file.bak" > $file
    rm "$file.bak"
done

echo "Done!"
