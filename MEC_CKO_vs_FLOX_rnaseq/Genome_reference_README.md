## Custom Reference Genome Preparation with Cre Recombinase

This project involves bulk RNA-seq analysis of mammary epithelial cells from a Cre-driven conditional knockout mouse model (MMTV-Cre; E2F5^fl/fl). To detect and quantify Cre recombinase expression from the RNA-seq data, I modified the GRCm39 reference genome and annotation to include the Cre coding sequence as an additional "gene" on a dummy chromosome.

### Reference Sources

* **Genome FASTA**: [`Mus_musculus.GRCm39.dna.primary_assembly.fa`](https://ftp.ensembl.org/pub/release-112/fasta/mus_musculus/dna/)
* **Gene Annotation (GTF)**: [`Mus_musculus.GRCm39.112.gtf`](https://ftp.ensembl.org/pub/release-112/gtf/mus_musculus/)
* **Cre Recombinase CDS**: Manually copied the coding sequence from the NCBI GenBank entry [X03453.1](https://www.ncbi.nlm.nih.gov/nuccore/X03453.1?report=fasta&format=text) and saved it to `cre_cds.fa`.

---

### Step-by-Step Instructions

1. **Modify the Cre FASTA header to use a dummy chromosome name**:

   ```bash
   sed -i '1s/.*/>chrCre Cre CDS/' cre_cds.fa
   ```

2. **Append Cre to the Ensembl primary genome FASTA**:

   ```bash
   cat Mus_musculus.GRCm39.dna.primary_assembly.fa cre_cds.fa > genome_plus_cre.fa
   ```

3. **Create a minimal GTF for the Cre gene**:

   ```bash
   cre_len=$(grep -v ">" cre_cds.fa | tr -d '\n' | wc -c)

   cat <<EOF > cre.gtf
   chrCre	Cregene	exon	1	$cre_len	.	+	.	gene_id "Cre"; transcript_id "Cre"; gene_biotype "protein_coding";
   EOF
   ```

4. **Append the Cre GTF entry to the Ensembl annotation**:

   ```bash
   cat Mus_musculus.GRCm39.112.gtf cre.gtf > genes_plus_cre.gtf
   ```

---

### Result

The final modified reference files:

* `genome_plus_cre.fa`
* `genes_plus_cre.gtf`

These can be used with `nf-core/rnaseq` to quantify Cre recombinase expression alongside endogenous mouse genes.

---

### Notes

* The dummy chromosome `chrCre` ensures no conflicts with real chromosomes.
* This method is compatible with both STAR and Salmon alignment modes in `nf-core/rnaseq`.
