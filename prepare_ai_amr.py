#!/usr/bin/env python3
"""Prepare Salmonella AMR metadata from NCBI and BV-BRC."""

from pathlib import Path
import argparse
import pandas as pd

REQUIRED_COLUMNS = [
    "BioSample",
    "Antibiotic",
    "Resistant Phenotype",
    "Species",
    "Strain",
    "Assembly",
    "Isolation source",
    "Isolation Country",
]

PHENOTYPE_MAP = {
    "S": "S",
    "SUSCEPTIBLE": "S",
    "SENSITIVE": "S",
    "I": "I",
    "INTERMEDIATE": "I",
    "R": "R",
    "RESISTANT": "R",
}


def read_input(path):
    """Read CSV/TSV/XLSX metadata."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, dtype="string")
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t", dtype="string")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype="string")

    raise ValueError(f"Unsupported input format: {suffix}")


def clean_text(series):
    """Trim whitespace and convert empty strings to missing values."""
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    )


def normalize_antibiotic(series):
    """Normalize antibiotic names without merging distinct drugs."""
    return (
        clean_text(series)
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )


def normalize_phenotype(series):
    """Standardize phenotype labels to S, I, R, or UNKNOWN."""
    normalized = clean_text(series).str.upper()
    return normalized.map(PHENOTYPE_MAP).fillna("UNKNOWN")


def load_source(path, source):
    df = read_input(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")

    df = df[REQUIRED_COLUMNS].copy()

    for col in REQUIRED_COLUMNS:
        df[col] = clean_text(df[col])

    df["Antibiotic"] = normalize_antibiotic(df["Antibiotic"])
    df["phenotype_original"] = df["Resistant Phenotype"]
    df["Resistant Phenotype"] = normalize_phenotype(df["Resistant Phenotype"])

    df["sample_id"] = df["Assembly"]
    df["source"] = source
    df["raw_row_id"] = source + ":" + (df.index + 2).astype(str)

    return df


def main():
    parser = argparse.ArgumentParser(description="Prepare AI-AMR metadata.")
    parser.add_argument("--ncbi", required=True, help="NCBI metadata file")
    parser.add_argument("--bvbrc", required=True, help="BV-BRC metadata file")
    parser.add_argument("--outdir", default="data_processed")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ncbi = load_source(args.ncbi, "NCBI")
    bvbrc = load_source(args.bvbrc, "BV-BRC")

    # Check cross-source overlap before concatenation.
    biosample_overlap = set(ncbi["BioSample"].dropna()) & set(bvbrc["BioSample"].dropna())
    assembly_overlap = set(ncbi["Assembly"].dropna()) & set(bvbrc["Assembly"].dropna())

    # Combine both sources while retaining provenance columns.
    merged = pd.concat([ncbi, bvbrc], ignore_index=True)
    merged.to_csv(outdir / "01_merged_with_provenance.csv", index=False)

    # Detect conflicting phenotypes for the same isolate-antibiotic pair.
    valid_key = merged["Assembly"].notna() & merged["Antibiotic"].notna()
    conflict_stats = (
        merged.loc[valid_key]
        .groupby(["Assembly", "Antibiotic"])["Resistant Phenotype"]
        .nunique()
        .reset_index(name="n_phenotypes")
    )

    conflict_keys = conflict_stats.loc[
        conflict_stats["n_phenotypes"] > 1,
        ["Assembly", "Antibiotic"],
    ]

    conflicts = merged.merge(
        conflict_keys,
        on=["Assembly", "Antibiotic"],
        how="inner",
    )
    conflicts.to_csv(outdir / "03_label_conflicts.csv", index=False)

    # Remove conflicted pairs from the cleaned metadata.
    clean = merged.copy()
    if not conflict_keys.empty:
        clean = clean.merge(
            conflict_keys.assign(_conflict=True),
            on=["Assembly", "Antibiotic"],
            how="left",
        )
        clean = clean[clean["_conflict"].isna()].drop(columns="_conflict")

    # Collapse repeated isolate-antibiotic records when the phenotype agrees.
    clean = (
        clean.sort_values(["Assembly", "Antibiotic", "source"], na_position="last")
        .drop_duplicates(["Assembly", "Antibiotic"], keep="first")
        .reset_index(drop=True)
    )

    clean.to_csv(outdir / "02_phenotype_clean.csv", index=False)

    # Antibiotic-level phenotype summary. Keep S/I/R at the metadata stage.
    summary = (
        clean.groupby(["Antibiotic", "Resistant Phenotype"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for label in ["S", "I", "R", "UNKNOWN"]:
        if label not in summary.columns:
            summary[label] = 0

    summary = summary.rename(
        columns={"S": "n_S", "I": "n_I", "R": "n_R", "UNKNOWN": "n_UNKNOWN"}
    )
    summary["n_total"] = summary[["n_S", "n_I", "n_R", "n_UNKNOWN"]].sum(axis=1)
    summary = summary[
        ["Antibiotic", "n_total", "n_S", "n_I", "n_R", "n_UNKNOWN"]
    ].sort_values("n_total", ascending=False)

    summary.to_csv(outdir / "04_antibiotic_summary.csv", index=False)

    print(f"NCBI rows: {len(ncbi):,}")
    print(f"BV-BRC rows: {len(bvbrc):,}")
    print(f"Combined rows: {len(merged):,}")
    print(f"BioSample overlap: {len(biosample_overlap):,}")
    print(f"Assembly overlap: {len(assembly_overlap):,}")
    print(f"Conflicting Assembly + Antibiotic pairs: {len(conflict_keys):,}")
    print(f"Clean rows: {len(clean):,}")
    print(f"Antibiotics: {clean['Antibiotic'].nunique():,}")


if __name__ == "__main__":
    main()
