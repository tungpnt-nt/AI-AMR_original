### Step 1: Metadata Preparation

- Metadata for *Salmonella enterica* were collected from [**NCBI**](https://www.ncbi.nlm.nih.gov) and [**BV-BRC**](https://www.bv-brc.org/).
- Raw input files:
  - `Salmonella_NCBI.csv`
  - `Salmonella_BVBRC.csv`
- Both files contain the following fields: `BioSample`, `Antibiotic`, `Resistant Phenotype`, `Species`, `Strain`, `Assembly`, `Isolation source`, and `Isolation Country`.
- Run the preprocessing script:
```bash
python prepare_ai_amr.py \
    --ncbi "Salmonella_NCBI.csv" \
    --bvbrc "Salmonella_BVBRC.csv" \
    --outdir data_processed
```

- The script:
  - standardizes antibiotic names and phenotype labels;
  - combines the NCBI and BV-BRC datasets;
  - uses `Assembly` as the isolate ID;
  - checks duplicated or conflicting `Assembly + Antibiotic` records;

- No overlapping `BioSample` or `Assembly` IDs were found between the two datasets, so they are concatenated after preprocessing.
- Main outputs:
  - `01_merged_with_provenance.csv`
  - `02_phenotype_clean.csv`
  - `03_label_conflicts.csv`
  - `04_antibiotic_summary.csv`

`02_phenotype_clean.csv` is used as the cleaned metadata file for the next steps.
