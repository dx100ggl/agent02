#!/usr/bin/env bash
set -euo pipefail

ROOT="docs/brain-24"

echo "Renaming chapter folders from C# → Ch# under: $ROOT"
echo

for n in {1..20}; do
    old="$ROOT/C$n"
    new="$ROOT/Ch$n"

    if [ -d "$old" ]; then
        echo "Renaming folder: $old → $new"
        mv "$old" "$new"

        # Rename files inside the folder
        for f in "$new"/C$n*; do
            if [ -e "$f" ]; then
                base=$(basename "$f")
                newfile="${base/C$n/Ch$n}"
                echo "  Renaming file: $f → $new/$newfile"
                mv "$f" "$new/$newfile"
            fi
        done
    fi
done

echo
echo "Done."
