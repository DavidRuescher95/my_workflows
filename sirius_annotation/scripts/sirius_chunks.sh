#!/bin/bash

run_sirius_chunks() {
    if [[ $# -lt 2 || $# -gt 3 || -z "$1" || -z "$2" ]]; then
        printf 'Usage: %s <in.mgf> <out_dir> [threshold]\n' "${BASH_SOURCE[0]}" >&2
        return 2
    fi

    local input_mgf="$1"
    local out_dir="$2"
    local threshold="${3:-10000}"
    if [[ ! "$threshold" =~ ^[1-9][0-9]{0,4}$ ]] || (( threshold > 20000 )); then
        printf 'Error: threshold must be an integer between 1 and 20000.\n' >&2
        return 2
    fi

    local script_dir
    local feature_count
    local chunk_dir
    local chunk
    local input_out_dir
    local status

    if [[ ! -f "$input_mgf" ]]; then
        printf 'Error: input file does not exist or is not a regular file: %s\n' "$input_mgf" >&2
        return 2
    fi
    if [[ "$input_mgf" != *.mgf ]]; then
        printf 'Error: input file must have the .mgf extension: %s\n' "$input_mgf" >&2
        return 2
    fi

    script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || return 1
    source "$script_dir/sirius.sh" || return 1
    source "$script_dir/merge_sirius_output.sh" || return 1
    printf 'Processing %s with feature threshold %s\n' "$input_mgf" "$threshold"

    feature_count=$(grep '^FEATURE_ID=' "$input_mgf" | sort -u | wc -l)
    if (( feature_count > threshold )); then
        printf 'Splitting %s (%s features)\n' "$input_mgf" "$feature_count"
        chunk_dir=$(mktemp -d) || return 1
        python3 "$script_dir/../utils/split_mgf.py" "$input_mgf" "$chunk_dir" "$threshold" || {
            status=$?
            rm -rf -- "$chunk_dir"
            return "$status"
        }

        input_out_dir="$out_dir/$(basename "$input_mgf" ".mgf")"
        for chunk in "$chunk_dir"/*.mgf; do
            [[ -f "$chunk" ]] || continue
            run_sirius "$chunk" "$input_out_dir" || {
                status=$?
                rm -rf -- "$chunk_dir"
                return "$status"
            }
        done
        merge_sirius_output "$input_out_dir" || {
            status=$?
            rm -rf -- "$chunk_dir"
            return "$status"
        }
        rm -rf -- "$chunk_dir"
    else
        printf 'Running %s directly (%s features)\n' "$input_mgf" "$feature_count"
        run_sirius "$input_mgf" "$out_dir" || return $?
    fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    run_sirius_chunks "$@"
fi