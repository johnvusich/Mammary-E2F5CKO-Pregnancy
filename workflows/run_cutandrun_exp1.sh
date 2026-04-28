#!/bin/bash --login
#SBATCH --job-name=mec_v_pd5_cutandrun
#SBATCH --time=12:00:00
#SBATCH --mem=4GB
#SBATCH --cpus-per-task=1
#SBATCH --output=mec_v_pd5_cutandrun-%j.out

# Load Nextflow
module purge
module load Nextflow/25.04.4

# Set paths to the genome files
GENOME_DIR="Ensembl_GRCm39_mm39"
FASTA="$GENOME_DIR/mm39.fa.gz"
GTF="$GENOME_DIR/refGene.gtf.gz"
BLACKLIST="$GENOME_DIR/mm10-blacklist.v2.Liftover.mm39.bed.txt"

# Define the samplesheet, outdir, workdir, and config
SAMPLESHEET="params/samplesheet_cutandrun_exp1.csv"
OUTDIR="mec_v_pd5_cutandrun_results"
WORKDIR="mec_v_pd5_cutandrun_work"
CONFIG="nextflow.config"

# Run the CUT&RUN analysis
nextflow run nf-core/cutandrun -r 3.2.2 -profile singularity -resume \
--input $SAMPLESHEET \
--outdir $OUTDIR \
--fasta $FASTA \
--gtf $GTF \
--seacr_stringent relaxed \
--blacklist $BLACKLIST \
--remove_mitochondrial_reads \
--mito_name "chrM" \
--dedup_target_reads \
-w $WORKDIR \
-c $CONFIG
