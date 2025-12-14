#!/usr/bin/env bash
file=$1; seal=$2
leaf=$(sha256sum "$file" | cut -d' ' -f1)
root=$(printf '\x00%s' "$(cat "$file")" | sha256sum | cut -d' ' -f1)
geo="35.4689,-97.5211,2025-12-09T23:44:12Z"
name=$(basename "$file")
test "$(echo -n "${root}|${geo}|${name}" | sha256sum | cut -d' ' -f1)" = "$seal" && echo "SEAL VALID" || echo "SEAL BROKEN"
