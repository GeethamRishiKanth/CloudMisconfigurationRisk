import pandas as pd


# =========================================================
# RECOMMENDATION ENGINE
# =========================================================
#
# Designed for the new 10,000-row multi-cloud dataset.
#
# The new dataset does not contain a remediation/
# recommendation column, so recommendations are generated
# from the security configuration fields.
# =========================================================


# =========================================================
# GENERIC RECOMMENDATIONS
# =========================================================

RECOMMENDATIONS = {

    "public_access": (
        "Restrict public access to the affected resource and "
        "allow access only from trusted networks, identities, "
        "or private connectivity."
    ),

    "encryption": (
        "Enable encryption at rest and encryption in transit "
        "for the affected resource and use appropriate key "
        "management controls."
    ),

    "logging": (
        "Enable security and diagnostic logging and retain logs "
        "for monitoring, detection, and incident investigation."
    ),

    "monitoring": (
        "Enable continuous security monitoring and configure "
        "appropriate alerts for suspicious activity."
    ),

    "backup": (
        "Enable regular backups and verify that backup and "
        "recovery procedures are configured and tested."
    ),

    "mfa": (
        "Enable multi-factor authentication for privileged and "
        "sensitive accounts."
    ),

    "least_privilege": (
        "Apply the principle of least privilege and remove "
        "unnecessary permissions or excessive access."
    ),

    "network": (
        "Restrict unnecessary network exposure, close unused "
        "ports, and use network segmentation, private links, "
        "VPNs, or firewall controls where appropriate."
    ),

    "credentials": (
        "Remove exposed credentials immediately, rotate affected "
        "secrets, and store credentials using a secure secrets "
        "management mechanism."
    ),

    "waf": (
        "Enable and properly configure a Web Application Firewall "
        "for internet-facing web applications."
    ),

    "password": (
        "Enforce a strong password policy including appropriate "
        "complexity, length, and account protection requirements."
    ),

    "updates": (
        "Enable automatic security updates and upgrade outdated "
        "runtime components to supported versions."
    ),

    "resource_waste": (
        "Review unused or overprovisioned resources and remove "
        "or right-size resources that are no longer required."
    ),

    "default": (
        "Review the resource configuration and apply appropriate "
        "cloud security controls following the principle of least "
        "privilege and defense in depth."
    )
}


# =========================================================
# SAFE BINARY VALUE
# =========================================================

def get_binary(row, column):
    """
    Convert a dataset value into 0 or 1.
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

def get_numeric(row, column, default=0):
    """
    Safely read a numeric value.
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

def get_resource_text(row):
    """
    Combine resource metadata for keyword matching.
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
# GENERATE RECOMMENDATION
# =========================================================

def get_recommendation(row):
    """
    Generate a recommendation based on the resource's
    security configuration.

    Multiple relevant recommendations may be combined.
    """

    recommendations = []

    # -----------------------------------------------------
    # Public exposure
    # -----------------------------------------------------

    is_public = get_binary(
        row,
        "is_public"
    )

    public_ip = get_binary(
        row,
        "public_ip_attached"
    )

    any_public = get_binary(
        row,
        "any_public"
    )

    if (
        is_public
        or public_ip
        or any_public
    ):
        recommendations.append(
            RECOMMENDATIONS["public_access"]
        )

    # -----------------------------------------------------
    # Encryption
    # -----------------------------------------------------

    has_encryption = get_binary(
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

    if (
        not has_encryption
        or not encryption_at_rest
        or not encryption_in_transit
    ):
        recommendations.append(
            RECOMMENDATIONS["encryption"]
        )

    # -----------------------------------------------------
    # Logging
    # -----------------------------------------------------

    if not get_binary(
        row,
        "has_logging"
    ):
        recommendations.append(
            RECOMMENDATIONS["logging"]
        )

    # -----------------------------------------------------
    # Monitoring
    # -----------------------------------------------------

    if not get_binary(
        row,
        "has_monitoring"
    ):
        recommendations.append(
            RECOMMENDATIONS["monitoring"]
        )

    # -----------------------------------------------------
    # Backup
    # -----------------------------------------------------

    if not get_binary(
        row,
        "has_backup"
    ):
        recommendations.append(
            RECOMMENDATIONS["backup"]
        )

    # -----------------------------------------------------
    # MFA
    # -----------------------------------------------------

    if not get_binary(
        row,
        "mfa_enabled"
    ):
        recommendations.append(
            RECOMMENDATIONS["mfa"]
        )

    # -----------------------------------------------------
    # Least privilege
    # -----------------------------------------------------

    if not get_binary(
        row,
        "least_privilege"
    ):
        recommendations.append(
            RECOMMENDATIONS["least_privilege"]
        )

    # -----------------------------------------------------
    # Network security
    # -----------------------------------------------------

    open_ports = get_numeric(
        row,
        "open_ports_count"
    )

    has_open_ports = get_binary(
        row,
        "has_open_ports"
    )

    network_segmentation = get_binary(
        row,
        "network_segmentation"
    )

    if (
        open_ports > 0
        or has_open_ports
        or not network_segmentation
    ):
        recommendations.append(
            RECOMMENDATIONS["network"]
        )

    # -----------------------------------------------------
    # Exposed credentials
    # -----------------------------------------------------

    if get_binary(
        row,
        "exposed_credentials"
    ):
        recommendations.append(
            RECOMMENDATIONS["credentials"]
        )

    # -----------------------------------------------------
    # WAF
    # -----------------------------------------------------

    resource_text = get_resource_text(
        row
    )

    if (
        not get_binary(row, "has_waf")
        and any(
            keyword in resource_text
            for keyword in [
                "web",
                "application",
                "load balancer",
                "gateway",
                "api"
            ]
        )
    ):
        recommendations.append(
            RECOMMENDATIONS["waf"]
        )

    # -----------------------------------------------------
    # Password policy
    # -----------------------------------------------------

    if not get_binary(
        row,
        "password_policy_strong"
    ):
        recommendations.append(
            RECOMMENDATIONS["password"]
        )

    # -----------------------------------------------------
    # Updates
    # -----------------------------------------------------

    if get_binary(
        row,
        "outdated_runtime"
    ):

        recommendations.append(
            RECOMMENDATIONS["updates"]
        )

    elif not get_binary(
        row,
        "auto_updates"
    ):

        recommendations.append(
            RECOMMENDATIONS["updates"]
        )

    # -----------------------------------------------------
    # Resource waste
    # -----------------------------------------------------

    if (
        get_binary(
            row,
            "overprovisioned"
        )
        or get_binary(
            row,
            "has_unused"
        )
        or get_binary(
            row,
            "high_unused"
        )
    ):
        recommendations.append(
            RECOMMENDATIONS["resource_waste"]
        )

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    unique_recommendations = []

    for recommendation in recommendations:

        if recommendation not in unique_recommendations:

            unique_recommendations.append(
                recommendation
            )

    # -----------------------------------------------------
    # Default recommendation
    # -----------------------------------------------------

    if not unique_recommendations:

        return RECOMMENDATIONS[
            "default"
        ]

    # -----------------------------------------------------
    # Combine recommendations
    # -----------------------------------------------------

    return " ".join(
        unique_recommendations
    )


# =========================================================
# ADD RECOMMENDATIONS
# =========================================================

def add_recommendations(data):
    """
    Add generated recommendations to every resource.
    """

    data = data.copy()

    data["recommendation"] = data.apply(
        get_recommendation,
        axis=1
    )

    return data


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "Recommendation engine loaded successfully."
    )