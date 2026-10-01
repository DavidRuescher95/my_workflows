## Summary
This repository contains different sets of utility functions, shell executables and python classes that are used as helper functions in the analysis of biological data. It aims to provide reusable and well-structured code to streamline common bioinformatics tasks with the goal to write efficient, maintainable, and reliable analysis pipelines, ultimately with the goal to establish snakemake workflows.

## Terminology
- RNA-seq: RNA sequencing, a technique used to quantify the experession of genes in a biological sample.
- phylogeny: the evolutionary history and relationships among a group of organisms or genes, often represented as a phylogenetic tree. Phylogenies are built upon sequence similarity and other evolutionary information.
- msa: multiple sequence alignment, a method used to align three or more biological sequences (protein or nucleic acid) to identify regions of similarity that may indicate functional, structural, or evolutionary relationships.
- sequence alignment: alignment of biological sequences (i.e. RNA, DNA or protein/amino acid) to infer homology and evolutionary relationships.
- STAR: a common splice-aware RNA-seq aligner used to map RNA sequencing reads to a reference genome.
- Snakemake: a workflow management system that allows the definition of complex bioinformatics pipelines in a readable and maintainable manner, automating the execution of tasks and handling dependencies between them.
- mass spectrometry: an analytical technique used to measure the mass-to-charge ratio of ions, commonly used in proteomics and metabolomics to identify and quantify molecules in a sample.
- MGF: Mascot Generic Format, a file format commonly used to store mass spectrometry data, developed for proteomics applications but also used for GNPS or SIRIUS analyses.
- GNPS: Global Natural Products Social Molecular Networking, an online platform for sharing, analyzing, and annotating mass spectrometry data, particularly in the context of natural products research.
- SIRIUS: a software tool for the analysis of mass spectrometry data, used to predict molecular formulas and annotate metabolites based on fragmentation patterns.


## Architecture
Each workflow lives in its own directory.
Scripts of Python or R are saved to the utils directory. Bash scripts are saved to the scripts directory.

## Task planning and problem-solving
- Before each task, you must first complete the following steps:
  1. Provide a full plan of your changes.
  2. Provide a list of behaviors that you'll change.
  3. Provide a list of test cases to add.
- Before you add any code, always check if you can re-use or re-configure any existing code to achieve the result.
- Use existing utility functions whenever possible to avoid code duplication and maintain consistency across the project.

## Coding guidelines
- Always write clear and concise code that is easy to understand and maintain.
- Follow consistent naming conventions for variables, functions, and files across the repository.
- Document all functions with meaningful comments and usage examples.
- Avoid code duplication by reusing existing functions and utilities.
- Write unit tests for all new functionality to ensure correctness and reliability.
- Ensure that the code adheres to the overall architecture and design principles of the project.
- add error handling to ensure that the code gracefully handles unexpected inputs and edge cases.

## Tooling
- use the conda environment workflow-dev for all Python scripts to ensure consistent dependencies and reproducibility.
