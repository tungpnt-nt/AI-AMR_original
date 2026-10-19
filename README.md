Module 1: Metadata Preparation for AI-AMR
Overview
This module describes the first stage of the AI-AMR data preparation workflow: building a clean and traceable cohort by integrating bacterial genome metadata with phenotypic antimicrobial susceptibility data.

The goal is to produce an analysis-ready metadata table that can later be linked to genomic features for machine-learning analysis.
Workflow
Genome metadata + Phenotypic AST metadata
                ↓
        Inspect input data
                ↓
      Select required variables
                ↓
      Clean and standardize
                ↓
         Validate records
                ↓
 Resolve duplicates / conflicts
                ↓
      Merge using Genome ID
                ↓
          Final quality check
                ↓
      Analysis-ready cohort table
Learning objectives
By the end of this practical, you should be able to:
- identify the metadata required for an AI-AMR cohort;
- inspect genome and phenotypic AST datasets before processing;
- select variables required for downstream analysis;
- standardize antimicrobial resistance phenotype labels;
- validate sample identifiers and duplicated records;
- identify conflicting phenotype records;
- merge genome and phenotype metadata using a common identifier; and
- export a curated cohort table for downstream genomic and machine-learning analyses.
1. Input data
Two metadata tables are used in this workflow.
1.1 Genome metadata
Genome metadata are obtained from BV-BRC after selecting Salmonella genomes that meet the project inclusion criteria.

The fields retained in this practical are:
Variable	Purpose
Genome ID	Primary identifier used to link datasets
Genome Name	Genome or isolate description
Genus	Taxonomic information
Species	Species-level taxonomic information
BioSample Accession	Link to the corresponding biological sample record
Assembly Accession	Link to the corresponding genome assembly


1.2 Phenotypic AST metadata
Phenotypic antimicrobial susceptibility data are also obtained from BV-BRC.

The fields retained are:
Variable	Purpose
Genome ID	Identifier used to link phenotype and genome metadata
Antibiotic	Antimicrobial tested
Resistant Phenotype	Reported susceptibility phenotype


Key point: Genome ID is the common identifier used to connect genome records with phenotypic AST records.

2. Inspect the input datasets
Before cleaning or filtering, inspect both datasets to understand their structure.

Check:
- number of rows and columns;
- available column names;
- data types;
- first few records; and
- missing values in key variables.
Example:
print(genome_df.shape)
display(genome_df.head())
genome_df.info()

print(amr_df.shape)
display(amr_df.head())
amr_df.info()
Checkpoint
Confirm that the expected identifier and phenotype fields are present before continuing.
3. Select variables required for downstream analysis
Retain only variables required for sample identification, genome retrieval and phenotype definition.
genome_features = [
    "Genome ID",
    "Genome Name",
    "Genus",
    "Species",
    "BioSample Accession",
    "Assembly Accession"
]

genome_clean = genome_df[genome_features].copy()
For phenotype data:
amr_features = [
    "Genome ID",
    "Antibiotic",
    "Resistant Phenotype"
]

amr_clean = amr_df[amr_features].copy()
Keeping only relevant fields makes subsequent validation easier to interpret and reduces unnecessary complexity.
4. Clean and standardize metadata
4.1 Genome metadata
For the genome table:
1. retain records belonging to Salmonella;
2. check that Genome ID is present;
3. quantify missing BioSample Accession and Assembly Accession values;
4. remove records lacking accessions only when those accessions are required for downstream genome retrieval; and
5. remove exact duplicate records.
Example:
genome_clean = genome_clean[
    genome_clean["Genus"] == "Salmonella"
].copy()
Before removing missing values, report how many records would be excluded:
print(genome_clean[[
    "Genome ID",
    "BioSample Accession",
    "Assembly Accession"
]].isna().sum())
If both accessions are required downstream:
genome_clean = genome_clean.dropna(
    subset=[
        "Genome ID",
        "BioSample Accession",
        "Assembly Accession"
    ]
)
Checkpoint
Record the number of genomes before and after each filtering step. This provides a simple audit trail of dataset attrition.
4.2 Phenotypic AST metadata
Remove records lacking one of the key fields:
- Genome ID;
- Antibiotic; or
- Resistant Phenotype.
amr_clean = amr_clean.dropna(
    subset=[
        "Genome ID",
        "Antibiotic",
        "Resistant Phenotype"
    ]
)
Next, standardize phenotype labels.
Original value	Standardized value
Resistant	R
Intermediate	I
Susceptible	S


phenotype_mapping = {
    "Resistant": "R",
    "Intermediate": "I",
    "Susceptible": "S"
}

amr_clean["Resistant Phenotype"] = (
    amr_clean["Resistant Phenotype"]
    .map(phenotype_mapping)
)
Remove or review values that cannot be mapped:
amr_clean = amr_clean.dropna(
    subset=["Resistant Phenotype"]
)
Checkpoint
Confirm that no unexpected phenotype categories remain:
amr_clean["Resistant Phenotype"].value_counts(dropna=False)
Expected categories:
R
I
S
5. Validate identifiers and phenotype records
Validation should be performed before merging the two datasets.
5.1 Check genome identifiers
A genome metadata table should normally contain one metadata record per Genome ID.
genome_id_duplicates = genome_clean[
    genome_clean.duplicated("Genome ID", keep=False)
]
Review duplicated identifiers rather than removing them automatically.
5.2 Check genome–antibiotic duplicates
The biological observation of interest in the phenotype table is:
Genome ID + Antibiotic → phenotype
Check whether the same genome–antibiotic pair occurs more than once:
pair_duplicates = amr_clean[
    amr_clean.duplicated(
        subset=["Genome ID", "Antibiotic"],
        keep=False
    )
].sort_values(["Genome ID", "Antibiotic"])
Two situations should be distinguished.
Exact repeated result
Genome ID    Antibiotic    Phenotype
G001         Ampicillin    R
G001         Ampicillin    R
These records carry the same information and may be collapsed according to a predefined rule.
Conflicting result
Genome ID    Antibiotic    Phenotype
G001         Ampicillin    R
G001         Ampicillin    S
This is a phenotype conflict and should not be removed silently.

Identify conflicting genome–antibiotic pairs:
conflicts = (
    amr_clean
    .groupby(["Genome ID", "Antibiotic"])["Resistant Phenotype"]
    .nunique()
    .reset_index(name="n_phenotypes")
    .query("n_phenotypes > 1")
)
Checkpoint
Before merging, report:
- number of duplicated genome identifiers;
- number of duplicated genome–antibiotic pairs; and
- number of conflicting phenotype pairs.
Important: Conflict-resolution rules should be defined explicitly and documented. Do not rely on drop_duplicates() to resolve biologically inconsistent records.

6. Merge genome and phenotype metadata
Merge the cleaned datasets using Genome ID.
merged_df = amr_clean.merge(
    genome_clean,
    how="inner",
    on="Genome ID",
    validate="many_to_one"
)
many_to_one is expected because one genome may have phenotypes for multiple antibiotics, while each genome should have one corresponding genome metadata record.
Why use an inner join?
For this cohort, only records with both:
- genome metadata; and
- a phenotypic AST result
are retained for downstream analysis.
Merge diagnostics
Do not assess a merge only from the final number of rows. Record:
- unique genomes in the genome metadata;
- unique genomes in the AST metadata;
- matched Genome IDs;
- unmatched Genome IDs; and
- unique genomes in the final cohort.
Example:
genome_ids = set(genome_clean["Genome ID"])
amr_ids = set(amr_clean["Genome ID"])

matched_ids = genome_ids & amr_ids
only_genome = genome_ids - amr_ids
only_amr = amr_ids - genome_ids

print("Matched Genome IDs:", len(matched_ids))
print("Genome metadata only:", len(only_genome))
print("AMR metadata only:", len(only_amr))
7. Final quality control
Before exporting the cohort, perform a final validation.

Confirm:
- no missing Genome ID values;
- no unresolved phenotype conflicts;
- phenotype values are restricted to R, I, and S;
- no unexpected duplicated genome–antibiotic observations remain;
- the number of unique genomes is plausible;
- the number of unique antibiotics is plausible; and
- required accessions are present for downstream genomic processing.
A concise cohort summary can be generated as follows:
summary = pd.DataFrame({
    "Metric": [
        "Genome–antibiotic records",
        "Unique genomes",
        "Unique antibiotics",
        "Unique BioSamples",
        "Unique assemblies"
    ],
    "Value": [
        len(merged_df),
        merged_df["Genome ID"].nunique(),
        merged_df["Antibiotic"].nunique(),
        merged_df["BioSample Accession"].nunique(),
        merged_df["Assembly Accession"].nunique()
    ]
})

summary
Also inspect the final phenotype distribution:
merged_df["Resistant Phenotype"].value_counts()
At this stage, extensive exploratory plots are not required. Detailed EDA should be performed in a separate downstream analysis notebook.
8. Export the analysis-ready cohort
Save the curated table using a descriptive filename:
output_file = "salmonella_genome_amr_metadata.csv"

merged_df.to_csv(
    output_file,
    index=False
)
Final output
salmonella_genome_amr_metadata.csv

Each row represents one genome–antibiotic observation.

The final table contains:
- genome identifiers;
- BioSample and Assembly accessions;
- taxonomic information;
- antibiotic tested; and
- standardized phenotypic AMR label (R, I, or S).
This table forms the phenotype/cohort metadata input for downstream genomic feature extraction and AI-AMR modelling.
9. Recommended processing record
For reproducibility, keep a short record of dataset attrition during preprocessing.
Processing step	Records / genomes retained
Raw genome metadata	To report
Salmonella records	To report
Records with required accessions	To report
Raw AST records	To report
AST records with complete key fields	To report
AST records after phenotype standardization	To report
Conflicting phenotype pairs	To report
Matched genomes	To report
Final genome–antibiotic observations	To report


This table provides a transparent summary of how the final analysis cohort was constructed.
Take-home messages
1. Inspect before filtering. Understand the input tables before modifying them.
2. Standardize before merging. Consistent identifiers and phenotype labels reduce downstream errors.
3. Validate biological records, not only rows. A duplicated row and a conflicting genome–antibiotic phenotype are different problems.
4. Document dataset attrition. Record how many samples are retained at each stage.
5. Validate the merge. Always quantify matched and unmatched identifiers.
6. Keep preprocessing separate from EDA and modelling. The output of this module should be a clean, traceable cohort table.
Next step
The next phase of the AI-AMR workflow links this cohort table to genomic data and derived genomic features for machine-learning analysis.
Analysis-ready cohort table
            +
       genomic data
            ↓
   genomic feature extraction
            ↓
       AI-ready dataset
