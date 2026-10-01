#!/bin/bash


run_sirius() {
	if [[ $# -lt 2 || $# -gt 3 || -z "$1" || -z "$2" ]]; then
		printf 'Usage: %s <in.mgf> <out_dir> [threads]\n' "${BASH_SOURCE[0]}" >&2
		return 2
	fi

	local in="$1"
	local out_dir="$2"
	local available_threads
	local threads
	if [[ ! -f "$in" ]]; then
		printf 'Error: input file does not exist or is not a regular file: %s\n' "$in" >&2
		return 2
	fi
	if [[ "$in" != *.mgf ]]; then
		printf 'Error: input file must have the .mgf extension: %s\n' "$in" >&2
		return 2
	fi

	available_threads=$(nproc)
	threads=$((available_threads - 1))
	if (( threads < 1 )); then
		threads=1
	fi
	if [[ $# -eq 3 ]]; then
		threads="$3"
	fi
	if [[ ! "$threads" =~ ^[1-9][0-9]*$ ]]; then
		printf 'Error: threads must be a positive integer.\n' >&2
		return 2
	fi

	mkdir -p "$out_dir"

	sirius\
	 --input "$in" \
	 --ignore-formula \
	 --threads "$threads" \
	 --project "$out_dir/$(basename "$in" ".mgf")/$(basename "$in" ".mgf").sirius" \
	 --mzmax=850 \
	 config \
	 --AlgorithmProfile=qtof\
	 --MS2MassDeviation.allowedMassDeviation=10.0ppm \
	 --SpectralSearchDB=METACYC,BloodExposome,CHEBI,COCONUT,FooDB,GNPS,HMDB,HSDB,KEGG,KNAPSACK,LOTUS,LIPIDMAPS,MACONDA,MESH,MiMeDB,NORMAN,PLANTCYC,PUBCHEMANNOTATIONBIO,PUBCHEMANNOTATIONDRUG,PUBCHEMANNOTATIONFOOD,PUBCHEMANNOTATIONSAFETYANDTOXIC,SUPERNATURAL,TeroMol,YMDB \
	 --AdductSettings.fallback=[[M+H]+,[M+Na]+,[M+K]+] \
	 --FormulaSettings.enforced=H,C,N,O,P \
	 --IdentitySearchSettings.precursorDeviation=20.0ppm \
	 --FormulaSearchSettings.performBottomUpAboveMz=0 \
	 formulas fingerprints classes structures write-summaries \
	 --output "$out_dir/$(basename "$in" ".mgf")"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
	run_sirius "$@"
fi
