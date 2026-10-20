import pandas as pd
from pathlib import Path
import sys


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

PROJECT_DIR = BASE_DIR.parent

DATA_DIR = PROJECT_DIR / "data"

MODELS_DIR = PROJECT_DIR / "models"

OUTPUT_DIR = BASE_DIR


# =========================================================
# IMPORT MODEL FILES
# =========================================================

sys.path.insert(
    0,
    str(MODELS_DIR)
)

from rama_baseline import run_rama_baseline
from proposed_model import run_proposed_model


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_FILE = (
    DATA_DIR
    / "misconfigurations.csv"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "model_comparisons.csv"
)


# =========================================================
# PRIORITY CLASSIFICATION
# =========================================================

def assign_priority(score):
    """
    Convert proposed-model risk score into priority.

    Score thresholds:

        >= 90 : Critical
        >= 70 : High
        >= 40 : Medium
        <  40 : Low
    """

    score = float(score)

    if score >= 90:
        return "Critical"

    elif score >= 70:
        return "High"

    elif score >= 40:
        return "Medium"

    else:
        return "Low"


# =========================================================
# VALIDATE DATASET
# =========================================================

def validate_dataset(data):

    required_columns = [

        "resource_id",
        "provider",
        "resource_type",
        "region",

        "is_public",

        "has_encryption",
        "encryption_at_rest",
        "encryption_in_transit",

        "has_logging",
        "has_monitoring",
        "has_backup",

        "mfa_enabled",
        "has_waf",
        "least_privilege",
        "has_dlp",

        "password_policy_strong",
        "network_segmentation",

        "open_ports_count",
        "exposed_credentials",

        "outdated_runtime",

        "has_vpn",
        "has_private_link",
        "public_ip_attached",

        "auto_updates",

        "unused_resources",
        "overprovisioned",

        "label",
        "misconfig_risk_score"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nDataset is missing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
        )


# =========================================================
# LOAD DATASET
# =========================================================

print("\n")
print("=" * 100)
print(
    "INTELLIGENT CLOUD MISCONFIGURATION RISK ASSESSMENT"
)
print(
    "Healthcare Cloud Environment"
)
print("=" * 100)


print(
    "\n[1/5] Loading cloud misconfiguration dataset..."
)


if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nDataset not found:\n{INPUT_FILE}"
    )


data = pd.read_csv(
    INPUT_FILE,
    sep=None,
    engine="python"
)


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

print(
    "[2/5] Preparing dataset..."
)


data.columns = (
    data.columns
    .str.strip()
    .str.lower()
    .str.replace(
        "\ufeff",
        "",
        regex=False
    )
)


validate_dataset(
    data
)


print(
    f"      Loaded {len(data)} findings."
)


print(
    f"      Dataset columns: {len(data.columns)}"
)


# =========================================================
# RUN RAMA
# =========================================================

print(
    "[3/5] Running RAMA baseline..."
)


data = run_rama_baseline(
    data
)


# =========================================================
# RUN PROPOSED MODEL
# =========================================================

print(
    "[4/5] Running proposed healthcare-cloud model..."
)


data = run_proposed_model(
    data
)


# =========================================================
# PRIORITY
# =========================================================

print(
    "[5/5] Generating model comparison..."
)


data["priority"] = (
    data["proposed_score"]
    .apply(
        assign_priority
    )
)


# =========================================================
# SCORE DIFFERENCE
# =========================================================

data["score_difference"] = (
    data["proposed_score"]
    - data["rama_score"]
).round(2)


# =========================================================
# DISPLAY FINAL ASSESSMENT
# =========================================================

print("\n")
print("=" * 120)
print(
    "MODEL COMPARISON"
)
print("=" * 120)


display_columns = [

    "resource_id",

    "provider",

    "resource_type",

    "region",

    "rama_score",

    "proposed_score",

    "score_difference",

    "priority"
]


print(
    data[
        display_columns
    ].to_string(
        index=False
    )
)


# =========================================================
# MODEL EVALUATION
# =========================================================

average_rama = round(
    data["rama_score"].mean(),
    2
)


average_proposed = round(
    data["proposed_score"].mean(),
    2
)


average_change = round(
    average_proposed
    - average_rama,
    2
)


increased = int(
    (
        data["score_difference"]
        > 0
    ).sum()
)


decreased = int(
    (
        data["score_difference"]
        < 0
    ).sum()
)


unchanged = int(
    (
        data["score_difference"]
        == 0
    ).sum()
)


# =========================================================
# PERCENTAGE CHANGE
# =========================================================

if average_rama != 0:

    average_percentage_change = round(
        (
            (
                average_proposed
                - average_rama
            )
            / average_rama
        )
        * 100,
        2
    )

else:

    average_percentage_change = 0


# =========================================================
# MODEL EVALUATION SUMMARY
# =========================================================

print("\n")
print("=" * 70)
print(
    "MODEL EVALUATION SUMMARY"
)
print("=" * 70)


print(
    f"Number of findings            : "
    f"{len(data)}"
)


print(
    f"Average RAMA score            : "
    f"{average_rama:.2f}"
)


print(
    f"Average Proposed score        : "
    f"{average_proposed:.2f}"
)


print(
    f"Average score change          : "
    f"{average_change:+.2f}"
)


print(
    f"Average percentage change     : "
    f"{average_percentage_change:+.2f}%"
)


print(
    f"Scores increased              : "
    f"{increased}"
)


print(
    f"Scores decreased              : "
    f"{decreased}"
)


print(
    f"Scores unchanged              : "
    f"{unchanged}"
)


# =========================================================
# PRIORITY DISTRIBUTION
# =========================================================

print("\n")
print("=" * 70)
print(
    "PRIORITY DISTRIBUTION"
)
print("=" * 70)


priority_summary = (
    data["priority"]
    .value_counts()
    .reindex(
        [
            "Critical",
            "High",
            "Medium",
            "Low"
        ],
        fill_value=0
    )
)


for priority, count in (
    priority_summary.items()
):

    print(
        f"{priority:<15}: "
        f"{int(count)}"
    )


# =========================================================
# SAVE MODEL COMPARISON
# =========================================================

comparison_columns = [

    # Resource information
    "resource_id",
    "provider",
    "resource_type",
    "region",

    # Original risk information
    "label",
    "is_synthetic",
    "misconfig_risk_score",

    # RAMA
    "confidentiality_score",
    "integrity_score",
    "availability_score",
    "rama_score",

    # Proposed model
    "cloud_exposure",
    "healthcare_sensitivity",
    "healthcare_impact",
    "proposed_score",

    # Comparison
    "score_difference",
    "priority"
]


# Keep only columns that exist

comparison_columns = [
    column
    for column in comparison_columns
    if column in data.columns
]


data[
    comparison_columns
].to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# COMPLETION
# =========================================================

print("\n")
print("=" * 70)
print(
    "FILES GENERATED"
)
print("=" * 70)


print(
    f"✓ {OUTPUT_FILE.name}"
)


print(
    f"\n✓ {len(data)} findings processed successfully."
)


print("\n")
print("=" * 100)
print(
    "MODEL COMPARISON COMPLETED SUCCESSFULLY"
)
print("=" * 100)