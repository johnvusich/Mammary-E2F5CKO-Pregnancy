#!/bin/bash --login
#SBATCH --job-name=mec_e2f5_cko_wt_rnaseq
#SBATCH --time=24:00:00
#SBATCH --mem=4GB
#SBATCH --cpus-per-task=1
#SBATCH --output=mec_e2f5_cko_wt_rnaseq-%j.out

# Load Nextflow
module purge
module load Nextflow/24.10.2

# Set the relative paths to the genome files
GENOME_DIR="Ensembl_GRCm39_mm39"
FASTA="$GENOME_DIR/genome_plus_cre.fa"
GTF="$GENOME_DIR/genes_plus_cre.gtf"

# Define the samplesheet, outdir, workdir, and config
SAMPLESHEET="samplesheet_rnaseq.csv"
OUTDIR="rnaseq_results"
WORKDIR="rnaseq_work"
CONFIG="nextflow.config"

# Run the rna-seq analysis
nextflow run nf-core/rnaseq -r 3.18.0 -profile singularity -work-dir $WORKDIR -resume \
--input $SAMPLESHEET \
--outdir $OUTDIR \
--fasta $FASTA \
--gtf $GTF \
-c $CONFIG
