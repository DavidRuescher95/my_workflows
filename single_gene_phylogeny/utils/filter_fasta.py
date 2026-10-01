#!/usr/bin/env python

'''
This script extracts sequences from a FASTA file based on a list of identifiers. 
It reads the identifiers from a text file, compares them to the headers of a fasta file and only returns matching records or deletes them.
'''

import argparse
import os
import pandas as pd
from Bio import SeqIO

def parse_gene_list(gene_list):
    ''' Parse gene list file and return a set of gene identifiers '''
    # check, if gene_list is a file. Note: Argarse returns a list even for single entries therefore gene_list[0] even for a filename
    if len(gene_list) == 1 and os.path.isfile(gene_list[0]):

        with open(gene_list[0], 'r') as file:
            gene_ids = {line.strip() for line in file if line.strip()}
        return set(gene_ids)
    
    else:

        return set(gene_list)

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
    parser = argparse.ArgumentParser(description="Filter FASTA file based on a list of gene identifiers.")
    parser.add_argument("-i", "--input_fasta", required=True, help="Input FASTA file")
    parser.add_argument("-g", "--gene_list", required=True, nargs = "+", help="Either a text file with list of gene identifiers or a space separated list of gene identifiers")
    parser.add_argument("-r", "--remove", action="store_true", help="If specified, removes sequences in the gene list instead of keeping them")
    parser.add_argument("-o", "--output_prefix", required=True, help="Full path and prefix for filtered FASTA file output")
    
    args = parser.parse_args()
    

    gene_ids = parse_gene_list(args.gene_list)
    filtered_sequences = filter_fasta_by_gene_list(args.input_fasta, gene_ids, remove=args.remove)
    
    write_outputs(filtered_sequences, args.output_prefix)

if __name__ == "__main__":
    main()