#!/bin/bash

# Define the list of filenames
files=(
    "brain/c1/planner/plan.py"
    "brain/c2/orchestrator.py"
    "brain/c2/executor/executor.py"
    "brain/c5/reflection_types.py"
    "brain/c5/reflection_engine.py"
    "brain/c5/integration/c2_hooks.py"
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