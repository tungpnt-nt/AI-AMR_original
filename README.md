## Step 1: Metadata preprocessing
- Download **genome metadata** and **AMR phenotype metadata** for the target organism from BV-BRC.
- Retain the variables required for downstream analysis:
  - Genome metadata: `Genome ID`, `Genome Name`, `Genus`, `Species`, `BioSample Accession`, `Assembly Accession`
  - AMR metadata: `Genome ID`, `Antibiotic`, `Resistant Phenotype`
- Clean the datasets:
  - retain *Salmonella* records;
  - remove records missing key identifiers or required accessions;
  - remove incomplete AMR records.
- Standardize AMR phenotypes:
  - `Resistant` → `R`
  - `Intermediate` → `I`
  - `Susceptible` → `S`
- Validate the data:
  - check duplicate `Genome ID` values;
  - identify repeated `Genome ID + Antibiotic` records;
  - review conflicting phenotype records.
- Merge genome and AMR metadata using `Genome ID`.
- Perform final QC and export the analysis-ready dataset as:
  `salmonella_genome_amr_metadata.csv`
Each row represents one **genome–antibiotic observation** for downstream AI-AMR analysis.
