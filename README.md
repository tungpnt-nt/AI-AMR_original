Module 1: Metadata Preparation for AI-AMR

Learning outcomes

By the end of this practical, you should be able to:





prepare genome and phenotypic AST metadata for downstream analysis;



standardize AMR phenotype labels;



identify missing, duplicated, and conflicting records;



merge datasets using a common genome identifier; and



export an analysis-ready cohort table.



Workflow

Genome metadata + Phenotypic AST metadata
                ↓
        Inspect and select fields
                ↓
         Clean and standardize
                ↓
       Validate IDs and records
                ↓
        Merge by Genome ID
                ↓
            Final QC
                ↓
      Analysis-ready cohort table





1. Input data

Two BV-BRC tables are used.

Genome metadata







Field



Use





Genome ID



Common identifier





Genome Name



Genome/isolate description





Genus, Species



Taxonomy





BioSample Accession



Link to sample record





Assembly Accession



Link to genome assembly



Phenotypic AST metadata







Field



Use





Genome ID



Common identifier





Antibiotic



Antimicrobial tested





Resistant Phenotype



Phenotypic AST result



Genome ID is the key used to link the two datasets.





2. Inspect and select required fields

Before modifying the data, check:





dataset dimensions;



expected columns;



missing values in key fields; and



duplicated identifiers.

Retain only fields required for sample identification, genome retrieval, and phenotype definition.

genome_cols = [
    "Genome ID", "Genome Name", "Genus", "Species",
    "BioSample Accession", "Assembly Accession"
]

amr_cols = [
    "Genome ID", "Antibiotic", "Resistant Phenotype"
]

genome = genome_df[genome_cols].copy()
amr = amr_df[amr_cols].copy()





3. Clean and standardize



Genome metadata





retain Salmonella records;



remove records without Genome ID;



quantify missing BioSample and Assembly accessions;



remove records lacking required accessions only if they are needed downstream.

genome = genome[genome["Genus"] == "Salmonella"].copy()
genome = genome.dropna(subset=["Genome ID"])



AST metadata

Remove records missing any essential AST field:

amr = amr.dropna(
    subset=["Genome ID", "Antibiotic", "Resistant Phenotype"]
)

Standardize phenotype labels:







Original



Standardized





Resistant



R





Intermediate



I





Susceptible



S

phenotype_map = {
    "Resistant": "R",
    "Intermediate": "I",
    "Susceptible": "S"
}

amr["Resistant Phenotype"] = (
    amr["Resistant Phenotype"].map(phenotype_map)
)

Checkpoint: only R, I, and S should remain.





4. Validate identifiers and phenotype records

Check that genome metadata contain one record per Genome ID.

For AST data, use the pair:

Genome ID + Antibiotic

as the unit of observation.

Distinguish between:

G001 | Ampicillin | R
G001 | Ampicillin | R   → repeated result

and:

G001 | Ampicillin | R
G001 | Ampicillin | S   → conflicting result

Conflicting phenotypes should be flagged and resolved explicitly rather than removed with drop_duplicates().

A simple conflict check is:

conflicts = (
    amr.groupby(["Genome ID", "Antibiotic"])["Resistant Phenotype"]
       .nunique()
       .reset_index(name="n_phenotypes")
       .query("n_phenotypes > 1")
)

Checkpoint: record the number of duplicate and conflicting genome-antibiotic pairs.





5. Merge genome and AST metadata

Merge using Genome ID:

cohort = amr.merge(
    genome,
    on="Genome ID",
    how="inner",
    validate="many_to_one"
)

many_to_one is expected because one genome can have AST results for multiple antibiotics, while each genome should have one genome metadata record.

Checkpoint: report matched and unmatched Genome IDs before accepting the merge.





6. Final quality control

Before export, confirm:





no missing Genome ID values;



no unresolved phenotype conflicts;



phenotype values are restricted to R, I, and S;



no unexpected duplicate genome-antibiotic observations remain; and



required accessions are available for downstream genomic processing.

Record a short cohort summary:





number of genome-antibiotic observations;



number of unique genomes;



number of unique antibiotics;



number of BioSample accessions; and



number of Assembly accessions.





7. Export

cohort.to_csv(
    "salmonella_genome_amr_metadata.csv",
    index=False
)



Output

salmonella_genome_amr_metadata.csv

Each row represents one genome-antibiotic observation containing genome identifiers, public accessions, taxonomic information, antibiotic, and standardized phenotypic AMR label.

This table is the metadata input for downstream genomic feature extraction and AI-AMR modelling.





Minimum processing record

Keep a simple record of sample/data attrition:







Step



Records retained





Raw genome metadata



—





Salmonella genomes



—





AST records with complete key fields



—





Conflicting phenotype pairs



—





Matched genomes



—





Final genome-antibiotic observations



—





Reference style

This practical follows the concise training structure used in the Wellcome Connecting Science AMR course: learning outcomes → dataset → practical steps → checkpoints/output.





Wellcome Connecting Science AMR 2026: https://github.com/WCSCourses/AMR_2026

