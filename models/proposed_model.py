import pandas as pd


# =========================================================
# PROPOSED HEALTHCARE-CLOUD MODEL
# =========================================================
#
# Designed for the new 10,000-row multi-cloud dataset.
#
# The model combines:
#
#   40% RAMA baseline
#   25% Cloud exposure
#   20% Healthcare/data sensitivity
#   15% Healthcare impact
#
# Final score:
#   0 - 100
#
# IMPORTANT:
#   label
#   misconfig_risk_score
#
# are NOT used as model inputs.
# =========================================================


# =========================================================
# CLOUD EXPOSURE SCORES
# =========================================================

EXPOSURE_SCORES = {
    "internal": 25,
    "restricted": 50,
    "internet": 75,
    "public": 100
}


# =========================================================
# HEALTHCARE SENSITIVITY SCORES
# =========================================================

SENSITIVITY_SCORES = {
    "operational data": 40,
    "medical data": 70,
    "sensitive patient data": 100
}


# =========================================================
# HEALTHCARE IMPACT SCORES
# =========================================================

HEALTHCARE_IMPACT_SCORES = {
    "low": 25,
    "medium": 50,
    "high": 75,
    "critical": 100
}


# =========================================================
# SAFE BINARY VALUE
# =========================================================

def get_binary(row, column):
    """
    Convert a dataset field into 0 or 1.
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
        "enabled"
    ]:
        return 1

    return 0


# =========================================================
# SAFE NUMERIC VALUE
# =========================================================

def get_numeric(row, column, default=0.0):
    """
    Safely read a numeric field.
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
# RESOURCE TEXT
# =========================================================

def get_text(row):
    """
    Combine useful resource information.
    """

    fields = [
        row.get("resource_id", ""),
        row.get("provider", ""),
        row.get("resource_type", "")
    ]

    return " ".join(
        str(value)
        for value in fields
        if pd.notna(value)
    ).lower()


# =========================================================
# CLOUD EXPOSURE
# =========================================================

def derive_cloud_exposure(row):
    """
    Derive exposure from the new dataset's network fields.
    """

    is_public = get_binary(
        row,
        "is_public"
    )

    public_ip = get_binary(
        row,
        "public_ip_attached"
    )

    has_private_link = get_binary(
        row,
        "has_private_link"
    )

    has_vpn = get_binary(
        row,
        "has_vpn"
    )

    open_ports = get_numeric(
        row,
        "open_ports_count"
    )

    any_public = get_binary(
        row,
        "any_public"
    )

    # -----------------------------------------------------
    # Public
    # -----------------------------------------------------

    if (
        is_public
        or public_ip
        or any_public
    ):
        return "public"

    # -----------------------------------------------------
    # Internet exposed
    # -----------------------------------------------------

    if open_ports > 0:
        return "internet"

    # -----------------------------------------------------
    # Restricted
    # -----------------------------------------------------

    if (
        has_private_link
        or has_vpn
    ):
        return "restricted"

    # -----------------------------------------------------
    # Internal
    # -----------------------------------------------------

    return "internal"


# =========================================================
# HEALTHCARE SENSITIVITY
# =========================================================

def derive_healthcare_sensitivity(row):
    """
    Estimate data sensitivity from resource type.

    This dataset does not contain an explicit healthcare-data
    classification field, so sensitivity is inferred from
    resource type only.
    """

    text = get_text(row)

    # -----------------------------------------------------
    # Highly sensitive resources
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "patient",
            "medical",
            "health",
            "clinical",
            "healthcare",
            "phi",
            "ehr",
            "emr"
        ]
    ):
        return "sensitive patient data"

    # -----------------------------------------------------
    # Medical/data resources
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "database",
            "rds",
            "sql",
            "mysql",
            "postgres",
            "dynamodb",
            "cosmos",
            "storage",
            "bucket",
            "blob",
            "data",
            "iam",
            "identity"
        ]
    ):
        return "medical data"

    # -----------------------------------------------------
    # Other cloud resources
    # -----------------------------------------------------

    return "operational data"


# =========================================================
# HEALTHCARE IMPACT
# =========================================================

def derive_healthcare_impact(row):
    """
    Estimate healthcare impact from the security posture.

    This dataset does not contain an explicit healthcare
    impact column, so impact is derived from security
    characteristics.
    """

    text = get_text(row)

    is_public = get_binary(
        row,
        "is_public"
    )

    public_ip = get_binary(
        row,
        "public_ip_attached"
    )

    exposed_credentials = get_binary(
        row,
        "exposed_credentials"
    )

    encryption = get_binary(
        row,
        "has_encryption"
    )

    backup = get_binary(
        row,
        "has_backup"
    )

    mfa = get_binary(
        row,
        "mfa_enabled"
    )

    least_privilege = get_binary(
        row,
        "least_privilege"
    )

    open_ports = get_numeric(
        row,
        "open_ports_count"
    )

    # -----------------------------------------------------
    # Critical conditions
    # -----------------------------------------------------

    if exposed_credentials:
        return "critical"

    if (
        is_public
        and not encryption
    ):
        return "critical"

    if (
        public_ip
        and exposed_credentials
    ):
        return "critical"

    # -----------------------------------------------------
    # High impact
    # -----------------------------------------------------

    high_risk_conditions = 0

    if is_public:
        high_risk_conditions += 1

    if public_ip:
        high_risk_conditions += 1

    if not encryption:
        high_risk_conditions += 1

    if not backup:
        high_risk_conditions += 1

    if not mfa:
        high_risk_conditions += 1

    if not least_privilege:
        high_risk_conditions += 1

    if open_ports >= 5:
        high_risk_conditions += 1

    if any(
        keyword in text
        for keyword in [
            "database",
            "storage",
            "iam"
        ]
    ):
        high_risk_conditions += 1

    if high_risk_conditions >= 3:
        return "high"

    # -----------------------------------------------------
    # Medium impact
    # -----------------------------------------------------

    if high_risk_conditions >= 1:
        return "medium"

    # -----------------------------------------------------
    # Low impact
    # -----------------------------------------------------

    return "low"


# =========================================================
# PROPOSED SCORE
# =========================================================

def calculate_proposed_score(row):
    """
    Calculate proposed healthcare-cloud risk score.

    Weighting:

        40% RAMA
        25% Cloud exposure
        20% Healthcare sensitivity
        15% Healthcare impact
    """

    rama_score = float(
        row["rama_score"]
    )

    exposure = EXPOSURE_SCORES[
        row["cloud_exposure"]
    ]

    sensitivity = SENSITIVITY_SCORES[
        row["healthcare_sensitivity"]
    ]

    impact = HEALTHCARE_IMPACT_SCORES[
        row["healthcare_impact"]
    ]

    proposed_score = (
        rama_score * 0.40
        + exposure * 0.25
        + sensitivity * 0.20
        + impact * 0.15
    )

    return round(
        min(
            proposed_score,
            100
        ),
        2
    )


# =========================================================
# RUN PROPOSED MODEL
# =========================================================

def run_proposed_model(data):
    """
    Run proposed healthcare-cloud model.
    """

    data = data.copy()

    # -----------------------------------------------------
    # Validate required columns
    # -----------------------------------------------------

    required_columns = [
        "resource_id",
        "provider",
        "resource_type",
        "is_public",
        "public_ip_attached",
        "open_ports_count",
        "has_private_link",
        "has_vpn",
        "exposed_credentials",
        "has_encryption",
        "has_backup",
        "mfa_enabled",
        "least_privilege"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "Dataset is missing required proposed-model "
            "columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # Derive cloud exposure
    # -----------------------------------------------------

    data["cloud_exposure"] = data.apply(
        derive_cloud_exposure,
        axis=1
    )

    # -----------------------------------------------------
    # Derive healthcare sensitivity
    # -----------------------------------------------------

    data["healthcare_sensitivity"] = data.apply(
        derive_healthcare_sensitivity,
        axis=1
    )

    # -----------------------------------------------------
    # Derive healthcare impact
    # -----------------------------------------------------

    data["healthcare_impact"] = data.apply(
        derive_healthcare_impact,
        axis=1
    )

    # -----------------------------------------------------
    # Calculate proposed score
    # -----------------------------------------------------

    data["proposed_score"] = data.apply(
        calculate_proposed_score,
        axis=1
    )

    return data


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "Proposed healthcare-cloud model "
        "loaded successfully."
    )