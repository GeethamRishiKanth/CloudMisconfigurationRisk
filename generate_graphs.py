import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "model_comparisons.csv"
)


# =========================================================
# LOAD MODEL COMPARISON DATA
# =========================================================

print("\n")
print("=" * 70)
print("GENERATING RISK ASSESSMENT GRAPHS")
print("=" * 70)

print("\n[1/4] Loading model comparison data...")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nModel comparison file not found:\n{INPUT_FILE}"
    )


data = pd.read_csv(
    INPUT_FILE
)


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

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


print(
    f"      Loaded {len(data)} findings."
)


# =========================================================
# VALIDATE REQUIRED COLUMNS
# =========================================================

required_columns = [
    "resource_id",
    "rama_score",
    "proposed_score",
    "score_difference",
    "priority"
]


missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]


if missing_columns:

    raise ValueError(
        "Missing required columns: "
        + str(missing_columns)
    )


# =========================================================
# GRAPH 1
# RAMA VS PROPOSED
# =========================================================

print(
    "\n[2/4] Generating RAMA vs Proposed model graph..."
)


# ---------------------------------------------------------
# IMPORTANT
# ---------------------------------------------------------
# Plotting all 10,000 resources with readable labels makes
# the graph extremely crowded.
#
# Therefore:
#
#   - all 10,000 findings are used for calculations
#   - only the first 100 resource IDs are displayed
#
# This keeps the graph readable without changing the data.
# ---------------------------------------------------------

plot_data = data.head(100).copy()

x = range(
    len(plot_data)
)

width = 0.4


plt.figure(
    figsize=(18, 7)
)


plt.bar(
    [
        i - width / 2
        for i in x
    ],
    plot_data["rama_score"],
    width=width,
    label="RAMA Baseline"
)


plt.bar(
    [
        i + width / 2
        for i in x
    ],
    plot_data["proposed_score"],
    width=width,
    label="Proposed Model"
)


plt.xlabel(
    "Resource"
)

plt.ylabel(
    "Risk Score"
)

plt.title(
    "RAMA Baseline vs Proposed Model "
    "(First 100 Resources)"
)


plt.xticks(
    list(x),
    plot_data["resource_id"],
    rotation=90,
    fontsize=7
)


plt.legend()


plt.tight_layout()


output_file = (
    BASE_DIR
    / "rama_vs_proposed.png"
)


plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"      Saved: {output_file}"
)


# =========================================================
# GRAPH 2
# SCORE DIFFERENCE
# =========================================================

print(
    "\n[3/4] Generating score difference graph..."
)


plt.figure(
    figsize=(18, 7)
)


plt.bar(
    plot_data["resource_id"],
    plot_data["score_difference"]
)


plt.axhline(
    0,
    linewidth=1
)


plt.xlabel(
    "Resource"
)

plt.ylabel(
    "Proposed Score - RAMA Score"
)

plt.title(
    "Risk Score Difference: "
    "Proposed Model vs RAMA "
    "(First 100 Resources)"
)


plt.xticks(
    rotation=90,
    fontsize=7
)


plt.tight_layout()


output_file = (
    BASE_DIR
    / "score_difference.png"
)


plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"      Saved: {output_file}"
)


# =========================================================
# GRAPH 3
# PRIORITY DISTRIBUTION
# =========================================================

print(
    "\n[4/4] Generating priority distribution graph..."
)


priority_counts = (
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


plt.figure(
    figsize=(8, 6)
)


bars = plt.bar(
    priority_counts.index,
    priority_counts.values
)


plt.xlabel(
    "Priority Level"
)

plt.ylabel(
    "Number of Findings"
)

plt.title(
    "Proposed Model Risk Priority Distribution"
)


# ---------------------------------------------------------
# Add values above bars
# ---------------------------------------------------------

for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,

        height + max(
            priority_counts.values
        ) * 0.01,

        str(
            int(height)
        ),

        ha="center"
    )


plt.tight_layout()


output_file = (
    BASE_DIR
    / "priority_distribution.png"
)


plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"      Saved: {output_file}"
)


# =========================================================
# GRAPH 4
# TOP 10 RISKS
# =========================================================

print(
    "\nGenerating top 10 risk findings graph..."
)


top_10 = (
    data
    .sort_values(
        by="proposed_score",
        ascending=False
    )
    .head(10)
    .copy()
)


plt.figure(
    figsize=(12, 7)
)


bars = plt.bar(
    top_10["resource_id"].astype(str),
    top_10["proposed_score"]
)


plt.xlabel(
    "Resource"
)

plt.ylabel(
    "Proposed Risk Score"
)

plt.title(
    "Top 10 Highest-Risk Resources"
)


plt.xticks(
    rotation=45,
    ha="right"
)


# ---------------------------------------------------------
# Add score values
# ---------------------------------------------------------

for bar, score in zip(
    bars,
    top_10["proposed_score"]
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,

        bar.get_height()
        + 0.5,

        f"{score:.2f}",

        ha="center"
    )


plt.tight_layout()


output_file = (
    BASE_DIR
    / "top_10_risks.png"
)


plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"Saved: {output_file}"
)


# =========================================================
# SUMMARY
# =========================================================

print("\n")
print("=" * 70)
print("GRAPH GENERATION COMPLETED")
print("=" * 70)

print(
    f"\nFindings processed       : {len(data)}"
)

print(
    f"Average RAMA score       : "
    f"{data['rama_score'].mean():.2f}"
)

print(
    f"Average Proposed score   : "
    f"{data['proposed_score'].mean():.2f}"
)


print(
    f"\nCritical findings        : "
    f"{int(priority_counts['Critical'])}"
)

print(
    f"High findings            : "
    f"{int(priority_counts['High'])}"
)

print(
    f"Medium findings          : "
    f"{int(priority_counts['Medium'])}"
)

print(
    f"Low findings             : "
    f"{int(priority_counts['Low'])}"
)


print("\nGenerated files:")

print(
    "  ✓ rama_vs_proposed.png"
)

print(
    "  ✓ score_difference.png"
)

print(
    "  ✓ priority_distribution.png"
)

print(
    "  ✓ top_10_risks.png"
)

print("\n")
print("=" * 70)