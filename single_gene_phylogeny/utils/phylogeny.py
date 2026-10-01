import argparse
import os
import shutil
import subprocess
from Bio import AlignIO
from Bio import SeqIO

'''
Python script to run alignment and phylogeny of a gene of interest
'''

def filter_alignment_by_gaps(alignment, max_gap_percentage=50):
    """
    Remove sequences from alignment that have a high percentage of gaps. SeqRecord cannot be parsed to set.
    """
    filtered_sequences = []
    
    for record in alignment:
        # Count gaps and calculate percentage
        gap_count = record.seq.count('-')
        total_length = len(record.seq)
        gap_percentage = (gap_count / total_length) * 100
        
        # Keep sequences below the threshold
        if gap_percentage <= max_gap_percentage:
            filtered_sequences.append(record)
    
    # Create new alignment with filtered sequences
    if filtered_sequences:
        return filtered_sequences
    else:
        print("Warning: No sequences passed the filter!")
        return None
    

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
    parser.add_argument("-o", "--out_dir", required=True, help="Full path to folder to write outputs")
    parser.add_argument("-p", "--output_prefix", required=True, help="Prefix for output files")
    parser.add_argument("-m", "--max_gap_percentage", type=float, default=50.0, help="Maximum percentage of gaps allowed in sequences, default: 50")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads to use for MAFFT (default: 1)")
    
    args = parser.parse_args()

    print("Running initial MAFFT alignment...")

    tmp_output_dir = os.path.join(args.out_dir, "tmp")
    os.makedirs(tmp_output_dir, exist_ok=True)

    mafft_cmd = f"mafft --thread {args.threads} --auto {args.input_fasta} > {os.path.join(tmp_output_dir, args.output_prefix)}_tmp.fasta"
    subprocess.run(mafft_cmd, shell=True, check=True)

    print("Initial alignment trimming...")

    trim_cmd = f"trimal -in {os.path.join(tmp_output_dir, args.output_prefix)}_tmp.fasta -out {os.path.join(tmp_output_dir, args.output_prefix)}_trimmed.fasta -automated1"
    subprocess.run(trim_cmd, shell=True, check=True)

    alignment = AlignIO.read(f"{os.path.join(tmp_output_dir, args.output_prefix)}_trimmed.fasta", "fasta")
    filtered_sequences = filter_alignment_by_gaps(alignment, max_gap_percentage=args.max_gap_percentage)

    if filtered_sequences:

        write_outputs(filtered_sequences, f"{os.path.join(tmp_output_dir, args.output_prefix)}_filtered")

        print("Running final MAFFT alignment...")

        alignment_dir = os.path.join(args.out_dir, "alignment")
        os.makedirs(alignment_dir, exist_ok=True)

        mafft_cmd = f"mafft --thread {args.threads} --localpair {f"{os.path.join(tmp_output_dir, args.output_prefix)}_filtered.fasta"} > {os.path.join(alignment_dir, args.output_prefix)}_alignment.fasta"
        subprocess.run(mafft_cmd, shell=True, check=True)
        print("Final alignment written to:", os.path.join(alignment_dir, f"{args.output_prefix}_alignment.fasta"))

        trim_cmd = f"trimal -in {os.path.join(alignment_dir, args.output_prefix)}_alignment.fasta -out {os.path.join(alignment_dir, args.output_prefix)}_trimmed.fasta -automated1"
        subprocess.run(trim_cmd, shell=True, check=True)

        print("Final trimmed alignment written to:", os.path.join(alignment_dir, f"{args.output_prefix}_trimmed.fasta"))

        tree_dir = os.path.join(args.out_dir, "trees")
        os.makedirs(tree_dir, exist_ok=True)

        #print("Running IQTree...")

        iqtree_cmd = f"iqtree2 -s {os.path.join(alignment_dir, args.output_prefix)}_alignment.fasta -redo -alrt 1000 -bb 1000 -nt AUTO -pre {os.path.join(tree_dir, args.output_prefix)}_iqtree"
        subprocess.run(iqtree_cmd, shell=True, check=True)

        shutil.rmtree(tmp_output_dir)

    else:
        print("No sequences passed the gap filtering step. No final alignment or tree generated.")

if __name__ == "__main__":
    main()


