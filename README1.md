#### Step 1: Metadata Preparation

- Metadata were collected from two sources: **[NCBI](www.ncbi.nlm.nih.gov)** and **[BV-BRC](https://www.bv-brc.org/)** for *Salmonella enterica*.
- The raw input files are:
  - `Salmonella_NCBI.csv`
  - `Salmonella_BVBRC.csv`
- Both files contain the following metadata fields: `BioSample`, `Antibiotic`, `Resistant Phenotype`, `Species`, `Strain`, `Assembly`, `Isolation source`, and `Isolation Country`.

- Run the metadata preparation script to validate, standardize, and combine the two datasets:
  ```bash
  python prepare_ai_amr.py \
      --ncbi "Salmonella_NCBI.csv" \
      --bvbrc "Salmonella_BVBRC.csv" \
      --outdir data_processed
  ```
- The preprocessing step performs the following operations:
  - Standardizes antibiotic names and phenotype labels.
  - Adds source information (`NCBI` or `BV-BRC`) for provenance tracking.
  - Uses `Assembly` as the isolate identifier.
  - Checks duplicate records using the `Assembly + Antibiotic` combination.
  - Detects conflicting phenotype labels for the same isolate-antibiotic pair.
  - Removes `Intermediate (I)` records from the binary classification dataset.
  - Encodes `Susceptible (S)` as `0` and `Resistant (R)` as `1`.
  - Retains missing values in non-essential metadata fields such as `Strain`, `Isolation source`, and `Isolation Country`.

- No overlapping `BioSample` or `Assembly` identifiers were found between the current NCBI and BV-BRC datasets; therefore, the two datasets are concatenated after preprocessing.

- The main output files are:
  - `01_merged_with_provenance.csv`: combined metadata before binary phenotype filtering.
  - `02_binary_sr_clean.csv`: cleaned metadata containing only `S` and `R` phenotypes.
  - `03_label_conflicts.csv`: isolate-antibiotic pairs with conflicting phenotype labels.
  - `04_excluded_rows.csv`: records excluded during preprocessing, including `Intermediate` phenotypes.
  - `05_antibiotic_summary.csv`: number of susceptible and resistant samples for each antibiotic.

The cleaned metadata are used as input for the subsequent genome preparation and model development steps.
