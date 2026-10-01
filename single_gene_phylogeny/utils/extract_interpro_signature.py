#!/usr/bin/env python


'''
This script extracts sequences from a FASTA file based on InterPro domain annotations. It can either take nucleotide (CDS) oder protein sequences.
The user provides an InterPro TSV file and a list of InterPro signatures (e.g. Pfam IDs) that will be used to filter the sequences.
The script outputs a new tsv only containing the lines of the original InterPro file that match the provided signatures, 
    a FASTA file with the full-length sequences of the matching records, 
    and separate FASTA files for each InterPro signature containing only the domain sequences.

Developer notes: Change list to yield generator for large files? Replace lists by sets for faster lookup? Make it able to read txt files instead of PFAM list?
'''

import argparse
import pandas as pd
from Bio import SeqIO

def extract_interpro_signature_tsv(interpro_file, interpro_signature):
    ''' Get genes of interest from interproscan results '''
    selected_interpro_entries = [] # create empty list to store genes of interest
    # open the connection to the interproscan results file
    with open(interpro_file, "r") as file:
        # read by line

        for line in file:
            # file ist tab-separated, so split by tab
            values = line.strip().split("\t")
            # the 4th entry contains the ID of the domain (e.g., PF01397)
            if(values[4] in interpro_signature):
                # append to list
                selected_interpro_entries.append(values)
    # generate 1 data frame from all genes of interest, a subset of the interproscan results
    selected_interpro_entries = pd.DataFrame(selected_interpro_entries)
    #
    return selected_interpro_entries


def make_names_comparable(selected_interpro_entries):
    ''' Make gene names comparable between interproscan results and fasta file '''
    selected_interpro_entries["clean_names"] = [gene.replace(".", "").removesuffix("p") for gene in selected_interpro_entries[0]]  # Remove dots from gene IDs; Interproscane sometimes does that, but make it consistent. Also remove trailing "p" if present, as some databases add that to indicate a protein sequence. This is done to make the names comparable to the ones in the fasta file, which might not have these modifications.
    return(selected_interpro_entries)  # Return unique gene IDs as a set for faster lookup



def extract_sequences(input_fasta, selected_interpro_entries, interpro_signature, seq_type):
    ''' Extract full length and domain specific sequences from a fasta file based on genes of interest '''
    
    
    # extract full length sequences from fasta file
    full_sequences = [] # empty list to store sequences
    domain_sequences = {pfam_id: [] for pfam_id in interpro_signature}  # Dictionary to store sequences per Pfam
    # for domain extraction, we need to adjust positions for nucleotide sequences
    position_multiplier = 3 if seq_type == "nucleotide" else 1

    # use Biopythen parser to read fasta file record by record
    for record in SeqIO.parse(input_fasta, "fasta"):
        # check, if record is contained in the genes of interest
        if record.id.replace(".", "").removesuffix("p") in selected_interpro_entries["clean_names"].values:

            # append to list
            full_sequences.append(record)

            # Extract domain sequences for each matching Pfam ID
            matching_rows = selected_interpro_entries[selected_interpro_entries["clean_names"] == record.id.replace(".", "").removesuffix("p")]  # Get all rows that match the current record ID
            # use iterrows to loop over each matching row (index, values)
            # this is done to account for multiple domains in one sequence
            for _, row in matching_rows.iterrows():
                # pfam_id of the current row
                pfam_id = row[4]

                # check if pfam_id is in the list of interpro_signature to extract
                # avoids extracting unwanted domains
                
                if pfam_id in interpro_signature:
                    start_pos = (int(row[6]) - 1) * position_multiplier
                    end_pos = int(row[7]) * position_multiplier
                    
                    # Create new record with domain sequence
                    domain_record = record[:]  # Copy record, [:] is a Biopython way to copy a SeqRecord
                    domain_record.seq = record.seq[start_pos:end_pos]
                    if len(domain_record.seq) > 0:
                        domain_sequences[pfam_id].append(domain_record)

    return full_sequences, domain_sequences


def write_outputs(full_sequences, domain_sequences, selected_interpro_entries, output_prefix, interpro_signatures):
    """Write all output files."""
    # Write TSV
    selected_interpro_entries.to_csv(f"{output_prefix}_selected_interpro_entries.tsv", 
                            sep="\t", index=False, header=False)
    
    # Write full sequences
    SeqIO.write(full_sequences, f"{output_prefix}.fasta", "fasta")
    
    # Write domain files
    for signature_id in interpro_signatures:
        SeqIO.write(domain_sequences[signature_id], 
                   f"{output_prefix}_{signature_id}.fasta", "fasta")



def main():
    parser = argparse.ArgumentParser(description="Extract sequences based on InterPro domains")
    parser.add_argument("-i", "--input_fasta", required=True, help="Input FASTA file. Full path.")
    parser.add_argument("-t", "--interpro_file", required=True, help="InterPro TSV file. Full path.")  
    parser.add_argument("-p", "--interpro_signature", required=True, nargs="+", help="InterPro signature IDs (space-separated). E.G. 'PF01397' 'PTHR43653'")
    parser.add_argument("-s", "--seq_type", choices=["protein", "nucleotide"], default="protein", help="Sequence type. Str")
    parser.add_argument("-o", "--output", required=True, help="Output prefix. Needs full path to an existing directory and filename prefix as single str.")
    
    args = parser.parse_args()

    selected_interpro_entries = extract_interpro_signature_tsv(args.interpro_file, args.interpro_signature)
    selected_interpro_entries = make_names_comparable(selected_interpro_entries)
    full_sequences, domain_sequences = extract_sequences(args.input_fasta, selected_interpro_entries, args.interpro_signature, args.seq_type)
    write_outputs(full_sequences, domain_sequences, selected_interpro_entries, args.output, args.interpro_signature)

if __name__ == "__main__":
    main()