import pandas as pd


# =========================================================
# RAMA BASELINE
# =========================================================
#
# Adapted for the new 10,000-row multi-cloud dataset.
#
# The dataset does NOT provide direct CIA scores.
# Therefore, CIA impact is derived from the available
# security/configuration features.
#
# RAMA weighting:
#
#   Confidentiality = 40%
#   Integrity       = 30%
#   Availability    = 30%
#
# Each CIA dimension is calculated on a 0-10 scale.
# Final RAMA score is normalized to 0-100.
#
# IMPORTANT:
#   label
#   misconfig_risk_score
#
# are NOT used to calculate RAMA in order to avoid
# target/data leakage.
# =========================================================


# =========================================================
# REQUIRED DATASET COLUMNS
# =========================================================

REQUIRED_COLUMNS = [
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
    "overprovisioned",
]


# =========================================================
# SAFE NUMERIC CONVERSION
# =========================================================

def get_numeric(row, column, default=0.0):
    """
    Safely read a numeric dataset value.
    """

    try:
        value = float(
            row.get(column, default)
        )

    except (TypeError, ValueError):
        value = default

    if pd.isna(value):
        value = default

    return value


# =========================================================
# SAFE BINARY CONVERSION
# =========================================================

def get_binary(row, column):
    """
    Convert a binary feature to 0 or 1.

    Supports:
        0 / 1
        True / False
        yes / no
        true / false
    """

    value = row.get(column, 0)

    if pd.isna(value):
        return 0

    if isinstance(value, bool):
        return int(value)

    text = str(value).strip().lower()

    if text in [
        "1",
        "true",
        "yes",
        "y",
        "enabled",
        "active"
    ]:
        return 1

    return 0


# =========================================================
# TEXT INFORMATION
# =========================================================

def get_resource_text(row):
    """
    Combine resource information for resource-type checks.
    """

    values = [
        row.get("provider", ""),
        row.get("resource_type", "")
    ]

    return " ".join(
        str(value)
        for value in values
        if pd.notna(value)
    ).lower()


# =========================================================
# CONFIDENTIALITY
# =========================================================

def calculate_confidentiality(row):
    """
    Calculate confidentiality impact on a 0-10 scale.

    Higher confidentiality risk is associated with:
        - public resources
        - public IP exposure
        - exposed credentials
        - missing encryption
        - missing encryption at rest
        - missing encryption in transit
        - missing DLP
        - database/storage resources
    """

    score = 2.0

    text = get_resource_text(row)

    is_public = get_binary(
        row,
        "is_public"
    )

    public_ip = get_binary(
        row,
        "public_ip_attached"
    )

    encryption = get_binary(
        row,
        "has_encryption"
    )

    encryption_at_rest = get_binary(
        row,
        "encryption_at_rest"
    )

    encryption_in_transit = get_binary(
        row,
        "encryption_in_transit"
    )

    exposed_credentials = get_binary(
        row,
        "exposed_credentials"
    )

    dlp = get_binary(
        row,
        "has_dlp"
    )

    # -----------------------------------------------------
    # Exposure
    # -----------------------------------------------------

    if is_public:
        score += 2.0

    if public_ip:
        score += 1.0

    # -----------------------------------------------------
    # Encryption
    # -----------------------------------------------------

    if not encryption:
        score += 1.0

    if not encryption_at_rest:
        score += 0.75

    if not encryption_in_transit:
        score += 0.75

    # -----------------------------------------------------
    # Credential exposure
    # -----------------------------------------------------

    if exposed_credentials:
        score += 1.5

    # -----------------------------------------------------
    # Data-loss prevention
    # -----------------------------------------------------

    if not dlp:
        score += 0.25

    # -----------------------------------------------------
    # Sensitive resource types
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "database",
            "rds",
            "sql",
            "mysql",
            "postgres",
            "storage",
            "bucket",
            "blob",
            "cosmos",
            "dynamodb"
        ]
    ):
        score += 0.75

    return min(
        round(score, 2),
        10.0
    )


# =========================================================
# INTEGRITY
# =========================================================

def calculate_integrity(row):
    """
    Calculate integrity impact on a 0-10 scale.

    Higher integrity risk is associated with:
        - weak access control
        - missing MFA
        - exposed credentials
        - lack of network segmentation
        - weak password policies
        - outdated runtimes
        - excessive privileges
    """

    score = 2.0

    text = get_resource_text(row)

    mfa = get_binary(
        row,
        "mfa_enabled"
    )

    least_privilege = get_binary(
        row,
        "least_privilege"
    )

    password_policy = get_binary(
        row,
        "password_policy_strong"
    )

    segmentation = get_binary(
        row,
        "network_segmentation"
    )

    exposed_credentials = get_binary(
        row,
        "exposed_credentials"
    )

    outdated_runtime = get_binary(
        row,
        "outdated_runtime"
    )

    # -----------------------------------------------------
    # Identity and access control
    # -----------------------------------------------------

    if not mfa:
        score += 1.25

    if not least_privilege:
        score += 1.5

    if not password_policy:
        score += 0.75

    # -----------------------------------------------------
    # Credential exposure
    # -----------------------------------------------------

    if exposed_credentials:
        score += 1.5

    # -----------------------------------------------------
    # Network segmentation
    # -----------------------------------------------------

    if not segmentation:
        score += 0.75

    # -----------------------------------------------------
    # Outdated software
    # -----------------------------------------------------

    if outdated_runtime:
        score += 0.75

    # -----------------------------------------------------
    # IAM resources
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "iam",
            "identity",
            "role",
            "permission",
            "user"
        ]
    ):
        score += 0.75

    return min(
        round(score, 2),
        10.0
    )


# =========================================================
# AVAILABILITY
# =========================================================

def calculate_availability(row):
    """
    Calculate availability impact on a 0-10 scale.

    Higher availability risk is associated with:
        - missing backups
        - open ports
        - lack of monitoring
        - weak network controls
        - missing VPN/private connectivity
        - outdated runtimes
        - lack of automatic updates
        - excessive resource waste
    """

    score = 2.0

    open_ports = get_numeric(
        row,
        "open_ports_count"
    )

    backup = get_binary(
        row,
        "has_backup"
    )

    monitoring = get_binary(
        row,
        "has_monitoring"
    )

    segmentation = get_binary(
        row,
        "network_segmentation"
    )

    vpn = get_binary(
        row,
        "has_vpn"
    )

    private_link = get_binary(
        row,
        "has_private_link"
    )

    outdated_runtime = get_binary(
        row,
        "outdated_runtime"
    )

    auto_updates = get_binary(
        row,
        "auto_updates"
    )

    overprovisioned = get_binary(
        row,
        "overprovisioned"
    )

    unused_resources = get_numeric(
        row,
        "unused_resources"
    )

    # -----------------------------------------------------
    # Backup
    # -----------------------------------------------------

    if not backup:
        score += 1.75

    # -----------------------------------------------------
    # Open ports
    # -----------------------------------------------------

    if open_ports > 0:
        score += 0.75

    if open_ports >= 5:
        score += 0.75

    # -----------------------------------------------------
    # Monitoring
    # -----------------------------------------------------

    if not monitoring:
        score += 0.75

    # -----------------------------------------------------
    # Network resilience
    # -----------------------------------------------------

    if not segmentation:
        score += 0.5

    if not vpn and not private_link:
        score += 0.5

    # -----------------------------------------------------
    # Maintenance
    # -----------------------------------------------------

    if outdated_runtime:
        score += 0.5

    if not auto_updates:
        score += 0.5

    # -----------------------------------------------------
    # Resource condition
    # -----------------------------------------------------

    if overprovisioned:
        score += 0.25

    if unused_resources >= 5:
        score += 0.25

    return min(
        round(score, 2),
        10.0
    )


# =========================================================
# CALCULATE CIA VALUES
# =========================================================

def calculate_cia_values(row):
    """
    Calculate CIA values for one finding/resource.
    """

    confidentiality = calculate_confidentiality(
        row
    )

    integrity = calculate_integrity(
        row
    )

    availability = calculate_availability(
        row
    )

    return (
        confidentiality,
        integrity,
        availability
    )


# =========================================================
# RAMA SCORE
# =========================================================

def calculate_rama_score(row):
    """
    Calculate normalized RAMA score.

    Weighting:

        Confidentiality = 40%
        Integrity       = 30%
        Availability    = 30%

    CIA scale:
        0 - 10

    RAMA scale:
        0 - 100
    """

    confidentiality = get_numeric(
        row,
        "confidentiality_score"
    )

    integrity = get_numeric(
        row,
        "integrity_score"
    )

    availability = get_numeric(
        row,
        "availability_score"
    )

    score = (
        confidentiality * 0.40
        + integrity * 0.30
        + availability * 0.30
    )

    return round(
        (score / 10.0) * 100.0,
        2
    )


# =========================================================
# RUN RAMA BASELINE
# =========================================================

def run_rama_baseline(data):
    """
    Run RAMA baseline on the new multi-cloud dataset.
    """

    data = data.copy()

    # -----------------------------------------------------
    # Validate dataset
    # -----------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "Dataset is missing required RAMA columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # Calculate CIA values
    # -----------------------------------------------------

    cia_values = data.apply(
        calculate_cia_values,
        axis=1
    )

    data["confidentiality_score"] = (
        cia_values.apply(
            lambda x: x[0]
        )
    )

    data["integrity_score"] = (
        cia_values.apply(
            lambda x: x[1]
        )
    )

    data["availability_score"] = (
        cia_values.apply(
            lambda x: x[2]
        )
    )

    # -----------------------------------------------------
    # Calculate RAMA score
    # -----------------------------------------------------

    data["rama_score"] = data.apply(
        calculate_rama_score,
        axis=1
    )

    return data


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "RAMA baseline module loaded successfully."
    )