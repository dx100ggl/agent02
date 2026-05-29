#!/bin/bash

# Define the list of filenames
files=(
    "brain/c3/memory/store.py"
    "brain/c3/memory/base.py"
    "brain/c3/memory/retriever.py"
    "brain/c3/memory/__init__.py"
    "tests/test_c3_memory_store.py"
    "tests/test_c1_memory_guided_planner.py"
)

# Loop through each filename in the list
for fn in "${files[@]}"; do
    # Check if the file actually exists before trying to read it
    if [ -f "$fn" ]; then
        echo "=== $fn ==="
        cat "$fn"
        echo "" # Adds a blank line for cleaner spacing
    else
        echo "=== $fn (File not found) ==="
    fi
done