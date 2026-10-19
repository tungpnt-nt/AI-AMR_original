# Salmonella Metadata Preprocessing

This workflow prepares *Salmonella* genome metadata and antimicrobial resistance (AMR) phenotype data from BV-BRC for downstream analysis and machine-learning applications.

## Preprocessing workflow

1. **Download genome metadata from [BV-BRC](https://www.bv-brc.org/).**
   - Search for *Salmonella* genomes.
   - Apply the following filters:
     - Genome Status: `WGS` and `Complete`
     - Genome Quality: `Good`
   - Download the metadata in `.csv` format.

2. **Select and clean genome metadata.**
   - Retain:
     - `Genome ID`
     - `Genome Name`
     - `Genus`
     - `Species`
     - `BioSample Accession`
     - `Assembly Accession`
   - Retain records where `Genus = Salmonella`.
   - Remove records with missing `BioSample Accession` or `Assembly Accession`.

3. **Download AMR phenotype metadata from BV-BRC.**
   - Open the **AMR Phenotypes** section.
   - Apply `Laboratory Method` as the evidence filter.
   - Download the metadata in `.csv` format.

4. **Select and clean AMR phenotype data.**
   - Retain:
     - `Genome ID`
     - `Antibiotic`
     - `Resistant Phenotype`
   - Remove records with missing values in these fields.

5. **Standardize resistance phenotypes.**
   - Convert:
     - `Resistant` → `R`
     - `Susceptible` → `S`
     - `Intermediate` → `I`
   - Remove phenotype values that cannot be mapped to these three categories.

6. **Merge genome and AMR metadata.**
   - Merge both datasets using `Genome ID`.
   - Use an inner join to retain genomes present in both datasets.

7. **Perform final data cleaning and inspection.**
   - Remove completely duplicated rows.
   - Remove records missing `Genome ID`, `BioSample Accession`, or `Assembly Accession`.
   - Inspect:
     - total number of records;
     - AMR phenotype distribution;
     - number and distribution of antibiotics;
     - number of unique genomes, assemblies, and BioSamples;
     - remaining duplicated rows.

8. **Export the processed dataset.**
   - Save the final dataset as:

     `Salmonella.csv`

The resulting dataset combines genome identifiers and accessions with standardized antibiotic-resistance phenotypes for downstream exploratory analysis and machine-learning workflows.
