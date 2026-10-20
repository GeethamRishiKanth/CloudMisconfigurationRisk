import os
from pathlib import Path

import pandas as pd

from models.rama_baseline import run_rama_baseline
from models.proposed_model import run_proposed_model
from recommendations.recommendations import add_recommendations


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "misconfigurations.csv"
)

EVALUATION_DIR = (
    PROJECT_DIR
    / "evaluation"
)

FINAL_OUTPUT = (
    EVALUATION_DIR
    / "final_risk_assessment.csv"
)

COMPARISON_OUTPUT = (
    EVALUATION_DIR
    / "model_comparisons.csv"
)


# =========================================================
# PRIORITY CLASSIFICATION
# =========================================================

def assign_priority(score):
    """
    Convert proposed-model risk score into priority.

    Thresholds:

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
# CLEAN RESOURCE DISPLAY
# =========================================================

def shorten_text(text, length=55):
    """
    Shorten long resource names for terminal display.
    """

    text = str(text)

    text = (
        text
        .replace("\n", " ")
        .replace("\r", " ")
    )

    text = " ".join(
        text.split()
    )

    if len(text) > length:
        return text[:length - 3] + "..."

    return text


# =========================================================
# PRINT FINAL TABLE
# =========================================================

def print_final_table(data):
    """
    Print a compact risk-assessment table.
    """

    print("\n")
    print("=" * 130)
    print("FINAL RISK ASSESSMENT")
    print("=" * 130)

    print(
        f"{'RESOURCE':<25}"
        f"{'PROVIDER':<10}"
        f"{'TYPE':<22}"
        f"{'RAMA':>10}"
        f"{'PROPOSED':>12}"
        f"{'CHANGE':>11}"
        f"{'PRIORITY':>12}"
    )

    print("-" * 130)

    for _, row in data.iterrows():

        resource = shorten_text(
            row["resource_id"],
            24
        )

        provider = shorten_text(
            row["provider"],
            9
        )

        resource_type = shorten_text(
            row["resource_type"],
            21
        )

        rama = float(
            row["rama_score"]
        )

        proposed = float(
            row["proposed_score"]
        )

        difference = float(
            row["score_difference"]
        )

        priority = str(
            row["priority"]
        )

        change = f"{difference:+.2f}"

        print(
            f"{resource:<25}"
            f"{provider:<10}"
            f"{resource_type:<22}"
            f"{rama:>10.2f}"
            f"{proposed:>12.2f}"
            f"{change:>11}"
            f"{priority:>12}"
        )

    print("-" * 130)

    print(
        f"Total findings: {len(data)}"
    )


# =========================================================
# MODEL SUMMARY
# =========================================================

def print_model_summary(data):

    average_rama = (
        data["rama_score"].mean()
    )

    average_proposed = (
        data["proposed_score"].mean()
    )

    average_change = (
        average_proposed
        - average_rama
    )

    increased = (
        data["score_difference"] > 0
    ).sum()

    decreased = (
        data["score_difference"] < 0
    ).sum()

    unchanged = (
        data["score_difference"] == 0
    ).sum()

    if average_rama != 0:

        percentage_change = (
            average_change
            / average_rama
        ) * 100

    else:

        percentage_change = 0

    print("\n")
    print("=" * 70)
    print("MODEL EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"{'Number of findings':<30}: "
        f"{len(data)}"
    )

    print(
        f"{'Average RAMA score':<30}: "
        f"{average_rama:.2f}"
    )

    print(
        f"{'Average Proposed score':<30}: "
        f"{average_proposed:.2f}"
    )

    print(
        f"{'Average score change':<30}: "
        f"{average_change:+.2f}"
    )

    print(
        f"{'Average percentage change':<30}: "
        f"{percentage_change:+.2f}%"
    )

    print(
        f"{'Scores increased':<30}: "
        f"{increased}"
    )

    print(
        f"{'Scores decreased':<30}: "
        f"{decreased}"
    )

    print(
        f"{'Scores unchanged':<30}: "
        f"{unchanged}"
    )


# =========================================================
# PRIORITY SUMMARY
# =========================================================

def print_priority_summary(data):

    priority_order = [
        "Critical",
        "High",
        "Medium",
        "Low"
    ]

    summary = (
        data["priority"]
        .value_counts()
        .reindex(
            priority_order,
            fill_value=0
        )
    )

    print("\n")
    print("=" * 70)
    print("PRIORITY DISTRIBUTION")
    print("=" * 70)

    for priority in priority_order:

        print(
            f"{priority:<15}: "
            f"{int(summary[priority])}"
        )


# =========================================================
# DATASET VALIDATION
# =========================================================

def validate_dataset(data):

    required_columns = [

        "resource_id",
        "provider",
        "resource_type",

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
        "overprovisioned"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "The new dataset is missing required columns:\n"
            + "\n".join(
                f" - {column}"
                for column in missing_columns
            )
        )


# =========================================================
# SAVE RESULTS
# =========================================================

def save_results(data):

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Full assessment
    # -----------------------------------------------------

    data.to_csv(
        FINAL_OUTPUT,
        index=False
    )

    # -----------------------------------------------------
    # Model comparison
    # -----------------------------------------------------

    comparison_columns = [

        "resource_id",
        "provider",
        "resource_type",
        "region",

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
        "priority",

        # Original dataset risk information
        "label",
        "is_synthetic",
        "misconfig_risk_score",

        # Recommendation
        "recommendation"
    ]

    # Keep only columns actually available
    comparison_columns = [
        column
        for column in comparison_columns
        if column in data.columns
    ]

    data[
        comparison_columns
    ].to_csv(
        COMPARISON_OUTPUT,
        index=False
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    print("\n")
    print("=" * 100)
    print(
        "INTELLIGENT CLOUD MISCONFIGURATION RISK ASSESSMENT"
    )
    print(
        "Healthcare Cloud Environment"
    )
    print("=" * 100)

    # =====================================================
    # STEP 1
    # =====================================================

    print(
        "\n[1/5] Loading new cloud security dataset..."
    )

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"\nDataset not found:\n{INPUT_FILE}\n\n"
            "Place your new dataset at:\n"
            f"{INPUT_FILE}"
        )

    data = pd.read_csv(
        INPUT_FILE,
        sep=None,
        engine="python"
    )

    # =====================================================
    # STEP 2
    # =====================================================

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
        f"      Columns available: {len(data.columns)}"
    )

    # =====================================================
    # STEP 3
    # =====================================================

    print(
        "[3/5] Running RAMA baseline..."
    )

    data = run_rama_baseline(
        data
    )

    # =====================================================
    # STEP 4
    # =====================================================

    print(
        "[4/5] Running proposed healthcare-cloud model..."
    )

    data = run_proposed_model(
        data
    )

    # =====================================================
    # STEP 5
    # =====================================================

    print(
        "[5/5] Generating priorities and recommendations..."
    )

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    data["priority"] = (
        data["proposed_score"]
        .apply(
            assign_priority
        )
    )

    # -----------------------------------------------------
    # Score difference
    # -----------------------------------------------------

    data["score_difference"] = (
        data["proposed_score"]
        - data["rama_score"]
    ).round(2)

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    data = add_recommendations(
        data
    )

    # =====================================================
    # TERMINAL OUTPUT
    # =====================================================

    print_final_table(
        data
    )

    print_model_summary(
        data
    )

    print_priority_summary(
        data
    )

    # =====================================================
    # SAVE OUTPUT
    # =====================================================

    save_results(
        data
    )

    print("\n")
    print("=" * 70)
    print("FILES GENERATED")
    print("=" * 70)

    print(
        "✓ final_risk_assessment.csv"
    )

    print(
        "✓ model_comparisons.csv"
    )

    print(
        f"\n✓ {len(data)} findings processed successfully."
    )

    print("\n")
    print("=" * 100)
    print(
        "ASSESSMENT COMPLETED SUCCESSFULLY"
    )
    print("=" * 100)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()