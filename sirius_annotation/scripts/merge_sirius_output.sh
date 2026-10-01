#!/bin/bash

merge_sirius_output() {
    if [[ $# -lt 1 || $# -gt 2 || -z "$1" ]]; then
        printf 'Usage: %s <chunks_dir> [merged_dir]\n' "${BASH_SOURCE[0]}" >&2
        return 2
    fi

    local chunks_dir="$1"
    local merged_dir="${2:-$1}"
    local first_chunk
    local chunk
    local file
    local file_basename
    local -a files

    if [[ ! -d "$chunks_dir" ]]; then
        printf 'Error: chunk output directory does not exist: %s\n' "$chunks_dir" >&2
        return 2
    fi
    mkdir -p "$merged_dir" || return 1

    first_chunk=""
    for chunk in "$chunks_dir"/chunk_*; do
        if [[ -d "$chunk" ]]; then
            first_chunk="$chunk"
            break
        fi
    done
    if [[ -z "$first_chunk" ]]; then
        printf 'Error: no chunk output directories found in %s\n' "$chunks_dir" >&2
        return 1
    fi

    for file in "$first_chunk"/*; do
        [[ -f "$file" ]] || continue
        file_basename=$(basename "$file")
        files=()
        for chunk in "$chunks_dir"/chunk_*; do
            [[ -d "$chunk" && -f "$chunk/$file_basename" ]] || continue
            files+=("$chunk/$file_basename")
        done

        {
            head -n 1 -- "${files[0]}"
            tail -n +2 -q -- "${files[@]}"
        } > "$merged_dir/$file_basename" || return 1
    done
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    merge_sirius_output "$@"
fi

