#!/usr/bin/env python

'''
This script extracts sequences from a FASTA file based on BLAST results. 
It reads the identifiers from a text file containing BLAST results (with --outfmt 6), compares them to the headers of a fasta file and only returns mathcing records.
'''

import argparse
import os
import pandas as pd
from Bio import SeqIO

# parse gene list (subject/target genes)
def parse_gene_list(gene_list):
    ''' Parse gene list file and return a set of gene identifiers '''
    # check, if gene_list is a file. Note: Argarse returns a list even for single entries therefore gene_list[0] even for a filename
    if len(gene_list) == 1 and os.path.isfile(gene_list[0]):
        # if true parse file
        with open(gene_list[0], 'r') as file:
            gene_ids = {line.strip() for line in file if line.strip()}
        return set(gene_ids)
    
    else:
        # if not a file make a set of list of IDs
        return set(gene_list)

# parse blast table and make enerator with query ids
def extract_blast_hits(blast_file, subject_ids):
    ''' Get genes of interest from blast results '''
     # open the connection to the interproscan results file
    with open(blast_file, "r") as file:
        # read by line
        for line in file:
            # file ist tab-separated, so split by tab
            values = line.strip().split("\t")
            # the 4th entry contains the ID of the domain (e.g., PF01397)
            if(values[1] in subject_ids):
                # append to list
                yield values[0]

# filter fasta by query gene list
def filter_fasta_by_gene_list(input_fasta, gene_ids, remove=False):
    ''' Filter fasta file based on a list of gene identifiers '''
    # parse fasta file
    for record in SeqIO.parse(input_fasta, "fasta"):
        # check if record id is in gene_ids
        if (record.id in gene_ids and not remove) or (record.id not in gene_ids and remove):
            # return record as generator, which can be read directly by SeqIO.write
            yield record

def write_outputs(sequences, output_prefix):
    """Write output file."""
    # Write full sequences
    SeqIO.write(sequences, f"{output_prefix}.fasta", "fasta")


def main():
    parser = argparse.ArgumentParser(description="Filter FASTA file based on a list of target identifiers and blast results.")
    parser.add_argument("-i", "--input_fasta", required=True, help="Input FASTA file")
    parser.add_argument("-g", "--subject_list", required=True, nargs = "+", help="Either a text file with list of subject gene identifiers or a space separated list of subject gene identifiers")
    parser.add_argument("-b", "--blast_file", required=True, help="BLAST results file in outfmt 6 format")
    parser.add_argument("-o", "--output_prefix", required=True, help="Full path and prefix for filtered FASTA file output")
    
    args = parser.parse_args()
    

    subject_ids = parse_gene_list(args.subject_list)
    query_ids = extract_blast_hits(args.blast_file, subject_ids)
    filtered_sequences = filter_fasta_by_gene_list(args.input_fasta, query_ids)
    
    write_outputs(filtered_sequences, args.output_prefix)

if __name__ == "__main__":
    main()