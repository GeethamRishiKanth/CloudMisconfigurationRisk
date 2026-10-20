from pathlib import Path
from datetime import datetime
import subprocess
import sys

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DASHBOARD_DIR.parent

DATA_DIR = PROJECT_DIR / "data"
EVALUATION_DIR = PROJECT_DIR / "evaluation"

DATASET = DATA_DIR / "misconfigurations.csv"

FINAL_REPORT = (
    EVALUATION_DIR / "final_risk_assessment.csv"
)

COMPARISON_REPORT = (
    EVALUATION_DIR / "model_comparisons.csv"
)

AZURE_SCRIPT = (
    PROJECT_DIR / "azure_storage.py"
)

MAIN_SCRIPT = (
    PROJECT_DIR / "main.py"
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CloudRisk Healthcare",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# NAVY / BLACK CYBERSECURITY THEME
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

.stApp {
    background:
        radial-gradient(
            circle at 85% 0%,
            rgba(10, 55, 105, 0.22),
            transparent 32%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(5, 30, 70, 0.18),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #010308 0%,
            #030811 45%,
            #061326 100%
        );

    color: #f4f8fd;
}

.main .block-container {
    max-width: 1550px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #010308 0%,
            #030914 50%,
            #050d1c 100%
        );

    border-right: 1px solid #102542;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f4f8ff !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #879db5 !important;
}


/* =========================================================
   HEADINGS
   ========================================================= */

h1 {
    color: #f7faff !important;
    font-weight: 850 !important;
    letter-spacing: -1.5px;
}

h2 {
    color: #edf5ff !important;
    font-weight: 800 !important;
}

h3 {
    color: #dceafa !important;
    font-weight: 750 !important;
}

p {
    color: #9aafc4;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
    min-height: 46px !important;

    border-radius: 12px !important;

    background:
        linear-gradient(
            135deg,
            #06172d,
            #0a3157
        ) !important;

    color: #edf8ff !important;

    border: 1px solid #164c78 !important;

    font-weight: 750 !important;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.45);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease,
        background 0.25s ease !important;
}


/* Clearly visible hover */

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: scale(1.08) !important;

    background:
        linear-gradient(
            135deg,
            #0c3158,
            #145f99
        ) !important;

    border-color: #42b8f5 !important;

    color: #ffffff !important;

    box-shadow:
        0 0 8px rgba(50, 175, 240, 0.45),
        0 0 25px rgba(50, 175, 240, 0.25),
        0 12px 35px rgba(0, 0, 0, 0.65);
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform: scale(1.02) !important;
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

div[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            #071426,
            #020810
        );

    border: 1px solid #112e4b;

    border-radius: 16px;

    padding: 18px;

    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.48);

    transition:
        transform 0.22s ease,
        border-color 0.22s ease,
        box-shadow 0.22s ease;
}

div[data-testid="stMetric"]:hover {
    transform:
        translateY(-5px)
        scale(1.015);

    border-color: #21618f;

    box-shadow:
        0 15px 40px rgba(0, 0, 0, 0.65);
}

div[data-testid="stMetricLabel"] {
    color: #6885a1 !important;

    font-size: 0.72rem !important;

    font-weight: 800 !important;

    letter-spacing: 0.7px;
}

div[data-testid="stMetricValue"] {
    color: #f5faff !important;

    font-weight: 850 !important;
}


/* =========================================================
   SELECT BOXES
   ========================================================= */

div[data-baseweb="select"] > div {
    background: #040a13 !important;

    border: 1px solid #142e49 !important;

    border-radius: 10px !important;

    color: #e6f3ff !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #286b9d !important;
}


/* =========================================================
   TEXT INPUT
   ========================================================= */

div[data-testid="stTextInput"] input {
    background: #030911 !important;

    color: #eef7ff !important;

    border: 1px solid #142e49 !important;

    border-radius: 10px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #2484bd !important;

    box-shadow:
        0 0 0 1px #2484bd !important;
}


/* =========================================================
   SLIDERS
   ========================================================= */

div[data-testid="stSlider"] {
    color: #55bdf5 !important;
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {
    color: #617b97 !important;

    font-weight: 750 !important;
}

button[data-baseweb="tab"]:hover {
    color: #a8dafa !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #4bb9f4 !important;
}


/* =========================================================
   EXPANDERS
   ========================================================= */

div[data-testid="stExpander"] {
    background:
        linear-gradient(
            145deg,
            #071526,
            #020911
        ) !important;

    border: 1px solid #112e4b !important;

    border-radius: 14px !important;
}

div[data-testid="stExpander"]:hover {
    border-color: #225e8d !important;
}


/* =========================================================
   DATAFRAME
   ========================================================= */

div[data-testid="stDataFrame"] {
    border: 1px solid #102d48;

    border-radius: 14px;

    overflow: hidden;

    box-shadow:
        0 10px 35px rgba(0, 0, 0, 0.45);
}


/* =========================================================
   ALERTS
   ========================================================= */

div[data-testid="stAlert"] {
    background: #040d19 !important;

    border: 1px solid #143653 !important;

    border-radius: 12px !important;
}


/* =========================================================
   STATUS
   ========================================================= */

div[data-testid="stStatusWidget"] {
    background: #030914 !important;

    border: 1px solid #143653 !important;

    border-radius: 14px !important;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: #0d2238 !important;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "selected_resource" not in st.session_state:
    st.session_state.selected_resource = None

if "priority_filter" not in st.session_state:
    st.session_state.priority_filter = "All"

if "search_results" not in st.session_state:
    st.session_state.search_results = None


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data(file_path, modified_time):
    return pd.read_csv(file_path)


# ============================================================
# NAVIGATION HELPERS
# ============================================================

def go_to_page(page_name):
    st.session_state.page = page_name


def select_resource(resource_id):
    st.session_state.selected_resource = resource_id
    st.session_state.page = "Resource Details"


def clear_selected_resource():
    st.session_state.selected_resource = None


def show_score(value):
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "N/A"


def format_bool(value):

    if pd.isna(value):
        return "Unknown"

    if isinstance(value, bool):
        return "Enabled" if value else "Disabled"

    text = str(value).strip().lower()

    if text in [
        "true",
        "1",
        "yes",
        "y",
        "enabled"
    ]:
        return "Enabled"

    if text in [
        "false",
        "0",
        "no",
        "n",
        "disabled"
    ]:
        return "Disabled"

    return str(value)


# ============================================================
# AZURE REFRESH
# ============================================================

def refresh_from_azure():

    if not AZURE_SCRIPT.exists():

        st.error(
            "azure_storage.py was not found."
        )

        st.code(
            str(AZURE_SCRIPT)
        )

        return

    if not MAIN_SCRIPT.exists():

        st.error(
            "main.py was not found."
        )

        st.code(
            str(MAIN_SCRIPT)
        )

        return

    try:

        with st.status(
            "Refreshing CloudRisk from Azure...",
            expanded=True
        ) as status:

            # ------------------------------------------------
            # STEP 1 — AZURE
            # ------------------------------------------------

            st.write(
                "☁️ Connecting to Azure Blob Storage..."
            )

            azure_result = subprocess.run(
                [
                    sys.executable,
                    str(AZURE_SCRIPT)
                ],
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True
            )

            if azure_result.stdout:

                st.code(
                    azure_result.stdout,
                    language="text"
                )

            if azure_result.stderr:

                st.code(
                    azure_result.stderr,
                    language="text"
                )

            if azure_result.returncode != 0:

                status.update(
                    label="Azure download failed",
                    state="error"
                )

                st.error(
                    "Azure dataset download failed."
                )

                return

            # ------------------------------------------------
            # STEP 2 — VERIFY DATASET
            # ------------------------------------------------

            if not DATASET.exists():

                status.update(
                    label="Dataset not found",
                    state="error"
                )

                st.error(
                    "misconfigurations.csv was not found."
                )

                return

            downloaded_data = pd.read_csv(
                DATASET,
                sep=None,
                engine="python"
            )

            downloaded_rows = len(
                downloaded_data
            )

            st.success(
                f"✓ Dataset verified: "
                f"{downloaded_rows:,} rows"
            )

            # ------------------------------------------------
            # STEP 3 — MAIN ASSESSMENT
            # ------------------------------------------------

            st.write(
                "🧠 Running risk assessment pipeline..."
            )

            main_result = subprocess.run(
                [
                    sys.executable,
                    str(MAIN_SCRIPT)
                ],
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True
            )

            if main_result.stdout:

                st.code(
                    main_result.stdout,
                    language="text"
                )

            if main_result.stderr:

                st.code(
                    main_result.stderr,
                    language="text"
                )

            # ------------------------------------------------
            # STEP 4 — FINAL REPORT
            # ------------------------------------------------

            st.write(
                "📊 Checking generated risk assessment..."
            )

            if not FINAL_REPORT.exists():

                status.update(
                    label="Assessment output missing",
                    state="error"
                )

                st.error(
                    "final_risk_assessment.csv "
                    "was not generated."
                )

                return

            final_data = pd.read_csv(
                FINAL_REPORT
            )

            final_rows = len(
                final_data
            )

            if final_rows == 0:

                status.update(
                    label="Assessment contains no findings",
                    state="error"
                )

                st.error(
                    "The final assessment contains "
                    "zero findings."
                )

                return

            st.success(
                f"✓ Assessment generated: "
                f"{final_rows:,} findings"
            )

            # ------------------------------------------------
            # STEP 5 — MODEL COMPARISON
            # ------------------------------------------------

            comparison_rows = 0

            if COMPARISON_REPORT.exists():

                comparison_data = pd.read_csv(
                    COMPARISON_REPORT
                )

                comparison_rows = len(
                    comparison_data
                )

                st.success(
                    f"✓ Model comparison generated: "
                    f"{comparison_rows:,} findings"
                )

            else:

                st.warning(
                    "model_comparisons.csv was not found."
                )

            status.update(
                label=(
                    f"CloudRisk refresh complete — "
                    f"{final_rows:,} findings"
                ),
                state="complete"
            )

        # ----------------------------------------------------
        # CLEAR CACHE
        # ----------------------------------------------------

        st.cache_data.clear()

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        st.success(
            f"☁️ CloudRisk refreshed successfully! "
            f"{final_rows:,} findings are now loaded."
        )

        st.session_state.page = "Dashboard"

        st.rerun()

    except Exception as error:

        st.error(
            "Unexpected error during Azure refresh."
        )

        st.exception(error)


# ============================================================
# CHECK FINAL REPORT
# ============================================================

if not FINAL_REPORT.exists():

    st.title(
        "☁️ CloudRisk Healthcare"
    )

    st.subheader(
        "Healthcare Cloud Security Intelligence"
    )

    st.warning(
        "No risk assessment is currently available."
    )

    if st.button(
        "☁️ Load Dataset from Azure",
        type="primary",
        use_container_width=True
    ):

        refresh_from_azure()

    st.stop()


# ============================================================
# LOAD FINAL DATA
# ============================================================

data = load_data(
    str(FINAL_REPORT),
    FINAL_REPORT.stat().st_mtime
)


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

data.columns = (
    data.columns
    .str.strip()
    .str.lower()
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = {
    "resource_id",
    "rama_score",
    "proposed_score",
    "score_difference",
    "priority",
    "recommendation"
}

missing_columns = (
    required_columns
    - set(data.columns)
)

if missing_columns:

    st.error(
        "The final assessment is missing "
        "required columns."
    )

    st.write(
        sorted(missing_columns)
    )

    st.stop()


# ============================================================
# STATISTICS
# ============================================================

priority_order = [
    "Critical",
    "High",
    "Medium",
    "Low"
]

priority_counts = (
    data["priority"]
    .value_counts()
    .reindex(
        priority_order,
        fill_value=0
    )
)

average_rama = data[
    "rama_score"
].mean()

average_proposed = data[
    "proposed_score"
].mean()

average_change = data[
    "score_difference"
].mean()

scores_increased = int(
    (
        data["score_difference"] > 0
    ).sum()
)

scores_decreased = int(
    (
        data["score_difference"] < 0
    ).sum()
)

scores_unchanged = int(
    (
        data["score_difference"] == 0
    ).sum()
)

if average_rama != 0:

    percentage_change = (
        average_change
        / average_rama
        * 100
    )

else:

    percentage_change = 0


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.title(
        "☁️ CloudRisk"
    )

    st.caption(
        "Healthcare Security Intelligence"
    )

    st.divider()

    st.subheader(
        "Navigation"
    )

    if st.button(
        "🏠 Executive Dashboard",
        use_container_width=True
    ):

        go_to_page("Dashboard")
        st.rerun()

    if st.button(
        "🔎 Resource Explorer",
        use_container_width=True
    ):

        go_to_page("Resource Explorer")
        st.rerun()

    if st.button(
        "🚨 Risk Center",
        use_container_width=True
    ):

        go_to_page("Risk Center")
        st.rerun()

    if st.button(
        "🛡 Security Posture",
        use_container_width=True
    ):

        go_to_page("Security Posture")
        st.rerun()

    if st.button(
        "🤖 Model Analysis",
        use_container_width=True
    ):

        go_to_page("Model Analysis")
        st.rerun()

    if st.button(
        "💡 Recommendations",
        use_container_width=True
    ):

        go_to_page("Recommendations")
        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # AZURE
    # --------------------------------------------------------

    st.subheader(
        "☁️ Azure"
    )

    st.success(
        "Connected"
    )

    st.caption(
        "Blob: misconfigurations.csv"
    )

    st.caption(
        f"{len(data):,} findings loaded"
    )

    if st.button(
        "🔄 Refresh Azure Data",
        type="primary",
        use_container_width=True
    ):

        refresh_from_azure()

    st.divider()

    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------

    st.subheader(
        "📥 Reports"
    )

    if FINAL_REPORT.exists():

        with open(
            FINAL_REPORT,
            "rb"
        ) as file:

            st.download_button(
                "Download Assessment",
                data=file,
                file_name="final_risk_assessment.csv",
                mime="text/csv",
                use_container_width=True
            )

    if COMPARISON_REPORT.exists():

        with open(
            COMPARISON_REPORT,
            "rb"
        ) as file:

            st.download_button(
                "Download Comparison",
                data=file,
                file_name="model_comparisons.csv",
                mime="text/csv",
                use_container_width=True
            )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "☁️ CloudRisk Healthcare"
)

st.write(
    "Intelligent Cloud Misconfiguration Risk Assessment"
)

st.caption(
    "Healthcare Cloud Security Intelligence Platform"
)


# ============================================================
# GLOBAL RESOURCE SEARCH
# ============================================================

search_col, search_button_col = st.columns(
    [5, 1]
)

with search_col:

    global_search = st.text_input(
        "🔎 Search Resource",
        placeholder="Enter Resource ID, e.g. RES10490",
        key="global_resource_search"
    )

with search_button_col:

    st.write("")

    search_clicked = st.button(
        "Search",
        type="primary",
        use_container_width=True
    )


if search_clicked:

    search_value = global_search.strip()

    if not search_value:

        st.warning(
            "Please enter a resource ID."
        )

    else:

        # Exact match

        exact = data[
            data[
                "resource_id"
            ]
            .astype(str)
            .str.lower()
            ==
            search_value.lower()
        ]

        if len(exact) == 1:

            found_resource = exact.iloc[0][
                "resource_id"
            ]

            select_resource(
                found_resource
            )

            st.rerun()

        else:

            # Partial match

            partial = data[
                data[
                    "resource_id"
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_value.lower(),
                    na=False
                )
            ]

            if partial.empty:

                st.error(
                    f"🔴 Resource '{search_value}' "
                    f"doesn't exist in the current "
                    f"{len(data):,}-resource dataset."
                )

            else:

                st.info(
                    f"Found {len(partial):,} "
                    f"matching resources."
                )

                st.session_state.search_results = (
                    partial[
                        "resource_id"
                    ]
                    .astype(str)
                    .tolist()
                )

                st.session_state.page = (
                    "Resource Explorer"
                )

                st.rerun()


# ============================================================
# STATUS BAR
# ============================================================

st.divider()

status1, status2, status3, status4 = st.columns(
    4
)

with status1:

    st.success(
        "● Azure Connected"
    )

with status2:

    st.info(
        f"● {len(data):,} Resources"
    )

with status3:

    st.info(
        "● Assessment Complete"
    )

with status4:

    modified = datetime.fromtimestamp(
        FINAL_REPORT.stat().st_mtime
    )

    st.info(
        "● Updated "
        + modified.strftime(
            "%d %b %H:%M"
        )
    )


# ============================================================
# RESOURCE DETAILS
# ============================================================

if st.session_state.page == "Resource Details":

    resource_id = (
        st.session_state.selected_resource
    )

    if resource_id is None:

        st.session_state.page = (
            "Resource Explorer"
        )

        st.rerun()

    resource_matches = data[
        data[
            "resource_id"
        ]
        .astype(str)
        ==
        str(resource_id)
    ]

    if resource_matches.empty:

        st.error(
            f"🔴 Resource '{resource_id}' "
            "doesn't exist."
        )

        if st.button(
            "← Back to Resource Explorer"
        ):

            clear_selected_resource()

            go_to_page(
                "Resource Explorer"
            )

            st.rerun()

        st.stop()

    resource = resource_matches.iloc[0]

    st.header(
        f"🔎 {resource_id}"
    )

    st.caption(
        "Complete cloud resource risk profile"
    )

    if st.button(
        "← Back to Resource Explorer"
    ):

        clear_selected_resource()

        go_to_page(
            "Resource Explorer"
        )

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # RESOURCE INFORMATION
    # --------------------------------------------------------

    st.subheader(
        "Resource Information"
    )

    info1, info2, info3, info4 = st.columns(
        4
    )

    with info1:

        st.metric(
            "Resource ID",
            str(
                resource.get(
                    "resource_id",
                    "N/A"
                )
            )
        )

    with info2:

        st.metric(
            "Provider",
            str(
                resource.get(
                    "provider",
                    "N/A"
                )
            )
        )

    with info3:

        st.metric(
            "Resource Type",
            str(
                resource.get(
                    "resource_type",
                    "N/A"
                )
            )
        )

    with info4:

        st.metric(
            "Region",
            str(
                resource.get(
                    "region",
                    "N/A"
                )
            )
        )

    # --------------------------------------------------------
    # RISK ASSESSMENT
    # --------------------------------------------------------

    st.subheader(
        "🚨 Risk Assessment"
    )

    r1, r2, r3, r4 = st.columns(
        4
    )

    with r1:

        st.metric(
            "RAMA Score",
            show_score(
                resource["rama_score"]
            )
        )

    with r2:

        st.metric(
            "Proposed Score",
            show_score(
                resource["proposed_score"]
            )
        )

    with r3:

        st.metric(
            "Score Difference",
            show_score(
                resource["score_difference"]
            )
        )

    with r4:

        st.metric(
            "Priority",
            str(
                resource["priority"]
            )
        )

    # --------------------------------------------------------
    # SECURITY CONTROLS
    # --------------------------------------------------------

    st.subheader(
        "🛡 Security Controls"
    )

    security_columns = [

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
        "has_vpn",
        "has_private_link",
        "public_ip_attached",
        "auto_updates",
        "unused_resources",
        "overprovisioned",
        "exposed_credentials",
        "outdated_runtime"
    ]

    available_security = [
        column
        for column in security_columns
        if column in data.columns
    ]

    if not available_security:

        st.info(
            "Detailed security-control fields "
            "are not available in the final report."
        )

    else:

        security_cols = st.columns(
            3
        )

        for index, column in enumerate(
            available_security
        ):

            with security_cols[
                index % 3
            ]:

                value = format_bool(
                    resource[column]
                )

                label = (
                    column
                    .replace("_", " ")
                    .title()
                )

                if value == "Enabled":

                    st.success(
                        f"✓ {label}"
                    )

                elif value == "Disabled":

                    st.error(
                        f"✗ {label}"
                    )

                else:

                    st.info(
                        f"• {label}: {value}"
                    )

    # --------------------------------------------------------
    # SECURITY SCORES
    # --------------------------------------------------------

    score_columns = [

        "observability_score",
        "exposure_score",
        "defense_score",
        "hygiene_score",
        "misconfig_risk_score"
    ]

    available_scores = [
        column
        for column in score_columns
        if column in data.columns
    ]

    if available_scores:

        st.subheader(
            "📊 Security Scores"
        )

        score_cols = st.columns(
            len(
                available_scores
            )
        )

        for index, column in enumerate(
            available_scores
        ):

            with score_cols[index]:

                st.metric(
                    column.replace(
                        "_",
                        " "
                    ).title(),
                    show_score(
                        resource[column]
                    )
                )

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    st.subheader(
        "💡 Recommended Action"
    )

    st.info(
        str(
            resource["recommendation"]
        )
    )

    st.stop()


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.header(
        "🏠 Executive Security Dashboard"
    )

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    st.subheader(
        "Risk Overview"
    )

    k1, k2, k3, k4, k5 = st.columns(
        5
    )

    # TOTAL

    with k1:

        st.metric(
            "TOTAL",
            f"{len(data):,}"
        )

        if st.button(
            "View All Resources",
            key="view_all_resources",
            use_container_width=True
        ):

            st.session_state.priority_filter = (
                "All"
            )

            go_to_page(
                "Resource Explorer"
            )

            st.rerun()

    # CRITICAL

    with k2:

        st.metric(
            "CRITICAL",
            f"{int(priority_counts['Critical']):,}"
        )

        if st.button(
            "View Critical",
            key="view_critical",
            use_container_width=True
        ):

            st.session_state.priority_filter = (
                "Critical"
            )

            go_to_page(
                "Risk Center"
            )

            st.rerun()

    # HIGH

    with k3:

        st.metric(
            "HIGH",
            f"{int(priority_counts['High']):,}"
        )

        if st.button(
            "View High",
            key="view_high",
            use_container_width=True
        ):

            st.session_state.priority_filter = (
                "High"
            )

            go_to_page(
                "Risk Center"
            )

            st.rerun()

    # MEDIUM

    with k4:

        st.metric(
            "MEDIUM",
            f"{int(priority_counts['Medium']):,}"
        )

        if st.button(
            "View Medium",
            key="view_medium",
            use_container_width=True
        ):

            st.session_state.priority_filter = (
                "Medium"
            )

            go_to_page(
                "Risk Center"
            )

            st.rerun()

    # LOW

    with k5:

        st.metric(
            "LOW",
            f"{int(priority_counts['Low']):,}"
        )

        if st.button(
            "View Low",
            key="view_low",
            use_container_width=True
        ):

            st.session_state.priority_filter = (
                "Low"
            )

            go_to_page(
                "Risk Center"
            )

            st.rerun()

    # --------------------------------------------------------
    # MODEL SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🤖 Model Performance"
    )

    m1, m2, m3, m4 = st.columns(
        4
    )

    with m1:

        st.metric(
            "RAMA Average",
            f"{average_rama:.2f}"
        )

    with m2:

        st.metric(
            "Proposed Average",
            f"{average_proposed:.2f}"
        )

    with m3:

        st.metric(
            "Average Change",
            f"{average_change:+.2f}"
        )

    with m4:

        st.metric(
            "Percentage Change",
            f"{percentage_change:+.2f}%"
        )

    if st.button(
        "🤖 Open Model Analysis",
        use_container_width=True
    ):

        go_to_page(
            "Model Analysis"
        )

        st.rerun()

    # ========================================================
    # HEALTHCARE SECURITY INSIGHTS
    # ========================================================

    st.divider()

    st.subheader(
        "🏥 Healthcare Security Insights"
    )

    st.caption(
        "Healthcare-focused security posture indicators "
        "from the current assessment."
    )

    total_resources = len(data)

    # --------------------------------------------------------
    # HEALTHCARE-SENSITIVE RESOURCES
    # --------------------------------------------------------

    healthcare_sensitive = int(
        data["healthcare_sensitivity"]
        .astype(str)
        .str.lower()
        .isin([
            "medical data",
            "sensitive patient data"
        ])
        .sum()
    )

    # --------------------------------------------------------
    # PUBLIC / INTERNET EXPOSURE
    # --------------------------------------------------------

    public_exposed = int(
        data["cloud_exposure"]
        .astype(str)
        .str.lower()
        .isin([
            "public",
            "internet"
        ])
        .sum()
    )

    # --------------------------------------------------------
    # ENCRYPTION
    # --------------------------------------------------------

    encryption_enabled = int(
        pd.to_numeric(
            data["has_encryption"],
            errors="coerce"
        )
        .fillna(0)
        .eq(1)
        .sum()
    )

    # --------------------------------------------------------
    # MFA
    # --------------------------------------------------------

    mfa_enabled = int(
        pd.to_numeric(
            data["mfa_enabled"],
            errors="coerce"
        )
        .fillna(0)
        .eq(1)
        .sum()
    )

    # --------------------------------------------------------
    # LOGGING
    # --------------------------------------------------------

    logging_enabled = int(
        pd.to_numeric(
            data["has_logging"],
            errors="coerce"
        )
        .fillna(0)
        .eq(1)
        .sum()
    )

    # --------------------------------------------------------
    # BACKUP
    # --------------------------------------------------------

    backup_enabled = int(
        pd.to_numeric(
            data["has_backup"],
            errors="coerce"
        )
        .fillna(0)
        .eq(1)
        .sum()
    )

    # --------------------------------------------------------
    # FIRST ROW
    # --------------------------------------------------------

    h1, h2, h3 = st.columns(3)

    with h1:

        st.metric(
            "Healthcare-Sensitive",
            f"{healthcare_sensitive:,}",
            (
                f"{healthcare_sensitive / total_resources * 100:.1f}%"
                if total_resources
                else None
            )
        )

    with h2:

        st.metric(
            "Public / Internet Exposed",
            f"{public_exposed:,}",
            (
                f"{public_exposed / total_resources * 100:.1f}%"
                if total_resources
                else None
            )
        )

    with h3:

        st.metric(
            "Encryption Enabled",
            f"{encryption_enabled:,}",
            (
                f"{encryption_enabled / total_resources * 100:.1f}% coverage"
                if total_resources
                else None
            )
        )

    # --------------------------------------------------------
    # SECOND ROW
    # --------------------------------------------------------

    h4, h5, h6 = st.columns(3)

    with h4:

        st.metric(
            "MFA Enabled",
            f"{mfa_enabled:,}",
            (
                f"{mfa_enabled / total_resources * 100:.1f}% coverage"
                if total_resources
                else None
            )
        )

    with h5:

        st.metric(
            "Logging Enabled",
            f"{logging_enabled:,}",
            (
                f"{logging_enabled / total_resources * 100:.1f}% coverage"
                if total_resources
                else None
            )
        )

    with h6:

        st.metric(
            "Backup Enabled",
            f"{backup_enabled:,}",
            (
                f"{backup_enabled / total_resources * 100:.1f}% coverage"
                if total_resources
                else None
            )
        )


    # ========================================================
    # CHARTS
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Risk Analytics"
    )

    chart1, chart2 = st.columns(2)

    # --------------------------------------------------------
    # PRIORITY DISTRIBUTION
    # --------------------------------------------------------

    with chart1:

        st.markdown(
            "### 🚨 Priority Distribution"
        )

        priority_chart = pd.DataFrame(
            {
                "Priority": priority_counts.index,
                "Resources": priority_counts.values
            }
        )

        fig_priority, ax_priority = plt.subplots(
            figsize=(7, 4)
        )

        ax_priority.bar(
            priority_chart["Priority"],
            priority_chart["Resources"]
        )

        ax_priority.set_ylabel(
            "Number of Resources"
        )

        ax_priority.set_xlabel(
            "Risk Priority"
        )

        ax_priority.set_title(
            "Risk Priority Distribution"
        )

        ax_priority.grid(
            axis="y",
            alpha=0.15
        )

        for index, value in enumerate(
            priority_chart["Resources"]
        ):

            ax_priority.text(
                index,
                value + max(
                    priority_chart["Resources"]
                ) * 0.02,
                f"{value:,}",
                ha="center",
                fontsize=9
            )

        fig_priority.tight_layout()

        st.pyplot(
            fig_priority,
            use_container_width=True
        )

        plt.close(fig_priority)

    # --------------------------------------------------------
    # SCORE COMPARISON
    # --------------------------------------------------------

    with chart2:

        st.markdown(
            "### 📈 Score Comparison"
        )

        score_chart = pd.DataFrame(
            {
                "Model": [
                    "RAMA",
                    "Proposed"
                ],
                "Average Score": [
                    average_rama,
                    average_proposed
                ]
            }
        )

        fig_score, ax_score = plt.subplots(
            figsize=(7, 4)
        )

        ax_score.bar(
            score_chart["Model"],
            score_chart["Average Score"]
        )

        ax_score.set_ylabel(
            "Average Risk Score"
        )

        ax_score.set_xlabel(
            "Model"
        )

        ax_score.set_title(
            "Model Average Risk Scores"
        )

        ax_score.grid(
            axis="y",
            alpha=0.15
        )

        for index, value in enumerate(
            score_chart["Average Score"]
        ):

            ax_score.text(
                index,
                value + 1,
                f"{value:.2f}",
                ha="center",
                fontsize=9
            )

        fig_score.tight_layout()

        st.pyplot(
            fig_score,
            use_container_width=True
        )

        plt.close(fig_score)


    # ========================================================
    # HIGHEST-RISK RESOURCES
    # ========================================================

    st.divider()

    st.subheader(
        "🔥 Highest-Risk Resources"
    )

    st.caption(
        "Resources with the highest proposed risk scores."
    )

    top_risks = (
        data
        .sort_values(
            "proposed_score",
            ascending=False
        )
        .head(10)
    )

    # --------------------------------------------------------
    # TABLE HEADER
    # --------------------------------------------------------

    header_cols = st.columns(
        [
            3,
            2,
            1.5,
            1.5,
            1.5
        ]
    )

    with header_cols[0]:

        st.caption(
            "RESOURCE"
        )

    with header_cols[1]:

        st.caption(
            "PROVIDER"
        )

    with header_cols[2]:

        st.caption(
            "RISK SCORE"
        )

    with header_cols[3]:

        st.caption(
            "PRIORITY"
        )

    with header_cols[4]:

        st.caption(
            "ACTION"
        )

    st.divider()

    # --------------------------------------------------------
    # TOP RISK ROWS
    # --------------------------------------------------------

    for index, (_, row) in enumerate(
        top_risks.iterrows()
    ):

        resource_id = str(
            row["resource_id"]
        )

        resource_cols = st.columns(
            [
                3,
                2,
                1.5,
                1.5,
                1.5
            ]
        )

        with resource_cols[0]:

            st.write(
                f"**{resource_id}**"
            )

        with resource_cols[1]:

            st.write(
                str(
                    row.get(
                        "provider",
                        "N/A"
                    )
                )
            )

        with resource_cols[2]:

            st.write(
                f"{float(row['proposed_score']):.2f}"
            )

        with resource_cols[3]:

            priority = str(
                row["priority"]
            )

            if priority == "Critical":

                st.error(
                    priority
                )

            elif priority == "High":

                st.warning(
                    priority
                )

            elif priority == "Medium":

                st.info(
                    priority
                )

            else:

                st.success(
                    priority
                )

        with resource_cols[4]:

            if st.button(
                "Open",
                key=f"dashboard_top_{index}",
                use_container_width=True
            ):

                select_resource(
                    resource_id
                )

                st.rerun()


    # ========================================================
    # DASHBOARD SUMMARY
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Assessment Summary"
    )

    summary1, summary2 = st.columns(2)

    with summary1:

        st.markdown(
            f"""
**Total resources assessed:** {len(data):,}

**High-risk resources:** {int(priority_counts["High"]):,}

**Medium-risk resources:** {int(priority_counts["Medium"]):,}

**Low-risk resources:** {int(priority_counts["Low"]):,}

**Critical resources:** {int(priority_counts["Critical"]):,}
"""
        )

    with summary2:

        st.markdown(
            f"""
**RAMA average score:** {average_rama:.2f}

**Proposed average score:** {average_proposed:.2f}

**Average score change:** {average_change:+.2f}

**Scores increased:** {scores_increased:,}

**Scores decreased:** {scores_decreased:,}
"""
        )


# ============================================================
# RESOURCE EXPLORER
# ============================================================

elif st.session_state.page == "Resource Explorer":

    st.header(
        "🔎 Resource Explorer"
    )

    st.caption(
        "Search, filter and inspect assessed cloud resources."
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_value = st.text_input(
        "Search resources",
        placeholder=(
            "Resource ID, provider, resource type "
            "or region..."
        ),
        key="resource_explorer_search"
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    f1, f2, f3, f4 = st.columns(4)

    with f1:

        provider_options = [
            "All"
        ]

        if "provider" in data.columns:

            provider_options += sorted(
                data["provider"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        provider_filter = st.selectbox(
            "Provider",
            provider_options
        )

    with f2:

        priority_options = [
            "All",
            "Critical",
            "High",
            "Medium",
            "Low"
        ]

        priority_filter = st.selectbox(
            "Priority",
            priority_options,
            index=(
                priority_options.index(
                    st.session_state.priority_filter
                )
                if st.session_state.priority_filter
                in priority_options
                else 0
            )
        )

        st.session_state.priority_filter = (
            priority_filter
        )

    with f3:

        if "resource_type" in data.columns:

            type_options = [
                "All"
            ] + sorted(
                data["resource_type"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        else:

            type_options = [
                "All"
            ]

        type_filter = st.selectbox(
            "Resource Type",
            type_options
        )

    with f4:

        if "region" in data.columns:

            region_options = [
                "All"
            ] + sorted(
                data["region"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        else:

            region_options = [
                "All"
            ]

        region_filter = st.selectbox(
            "Region",
            region_options
        )

    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered = data.copy()

    if search_value.strip():

        search_text = (
            search_value
            .strip()
            .lower()
        )

        searchable_columns = [
            column
            for column in [
                "resource_id",
                "provider",
                "resource_type",
                "region",
                "priority",
                "recommendation"
            ]
            if column in filtered.columns
        ]

        mask = pd.Series(
            False,
            index=filtered.index
        )

        for column in searchable_columns:

            mask |= (
                filtered[column]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
            )

        filtered = filtered[mask]

    if provider_filter != "All":

        filtered = filtered[
            filtered["provider"]
            .astype(str)
            ==
            provider_filter
        ]

    if priority_filter != "All":

        filtered = filtered[
            filtered["priority"]
            .astype(str)
            ==
            priority_filter
        ]

    if type_filter != "All":

        filtered = filtered[
            filtered["resource_type"]
            .astype(str)
            ==
            type_filter
        ]

    if region_filter != "All":

        filtered = filtered[
            filtered["region"]
            .astype(str)
            ==
            region_filter
        ]

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.divider()

    st.write(
        f"Showing **{len(filtered):,}** "
        f"of **{len(data):,}** resources"
    )

    if filtered.empty:

        st.warning(
            "No resources match the selected filters."
        )

    else:

        display_columns = [
            column
            for column in [
                "resource_id",
                "provider",
                "resource_type",
                "region",
                "rama_score",
                "proposed_score",
                "score_difference",
                "priority"
            ]
            if column in filtered.columns
        ]

        explorer_display = (
            filtered[
                display_columns
            ]
            .sort_values(
                "proposed_score",
                ascending=False
            )
            .copy()
        )

        if "rama_score" in explorer_display.columns:

            explorer_display[
                "rama_score"
            ] = explorer_display[
                "rama_score"
            ].round(2)

        if "proposed_score" in explorer_display.columns:

            explorer_display[
                "proposed_score"
            ] = explorer_display[
                "proposed_score"
            ].round(2)

        if "score_difference" in explorer_display.columns:

            explorer_display[
                "score_difference"
            ] = explorer_display[
                "score_difference"
            ].round(2)

        st.dataframe(
            explorer_display,
            use_container_width=True,
            height=520
        )

        st.divider()

        st.subheader(
            "Open Resource"
        )

        resource_options = (
            filtered[
                "resource_id"
            ]
            .astype(str)
            .tolist()
        )

        selected = st.selectbox(
            "Select a resource",
            resource_options
        )

        if st.button(
            "🔎 Open Resource Details",
            type="primary",
            use_container_width=True
        ):

            select_resource(
                selected
            )

            st.rerun()


# ============================================================
# RISK CENTER
# ============================================================

elif st.session_state.page == "Risk Center":

    st.header(
        "🚨 Risk Center"
    )

    st.caption(
        "Prioritized view of cloud security risks."
    )

    # --------------------------------------------------------
    # RISK KPIs
    # --------------------------------------------------------

    r1, r2, r3, r4 = st.columns(4)

    with r1:

        st.metric(
            "Critical",
            f"{int(priority_counts['Critical']):,}"
        )

    with r2:

        st.metric(
            "High",
            f"{int(priority_counts['High']):,}"
        )

    with r3:

        st.metric(
            "Medium",
            f"{int(priority_counts['Medium']):,}"
        )

    with r4:

        st.metric(
            "Low",
            f"{int(priority_counts['Low']):,}"
        )

    st.divider()

    # --------------------------------------------------------
    # RISK FILTER
    # --------------------------------------------------------

    selected_priority = st.selectbox(
        "Risk Priority",
        [
            "All",
            "Critical",
            "High",
            "Medium",
            "Low"
        ],
        index=(
            [
                "All",
                "Critical",
                "High",
                "Medium",
                "Low"
            ].index(
                st.session_state.priority_filter
            )
            if st.session_state.priority_filter
            in [
                "All",
                "Critical",
                "High",
                "Medium",
                "Low"
            ]
            else 0
        )
    )

    st.session_state.priority_filter = (
        selected_priority
    )

    risk_data = data.copy()

    if selected_priority != "All":

        risk_data = risk_data[
            risk_data["priority"]
            ==
            selected_priority
        ]

    risk_data = risk_data.sort_values(
        "proposed_score",
        ascending=False
    )

    st.write(
        f"**{len(risk_data):,}** findings"
    )

    # --------------------------------------------------------
    # RISK TABLE
    # --------------------------------------------------------

    risk_display_columns = [
        column
        for column in [
            "resource_id",
            "provider",
            "resource_type",
            "cloud_exposure",
            "healthcare_sensitivity",
            "healthcare_impact",
            "rama_score",
            "proposed_score",
            "priority",
            "recommendation"
        ]
        if column in risk_data.columns
    ]

    if risk_data.empty:

        st.info(
            "No findings for this priority."
        )

    else:

        risk_display = (
            risk_data[
                risk_display_columns
            ]
            .copy()
        )

        for column in [
            "rama_score",
            "proposed_score"
        ]:

            if column in risk_display.columns:

                risk_display[
                    column
                ] = risk_display[
                    column
                ].round(2)

        st.dataframe(
            risk_display,
            use_container_width=True,
            height=600
        )

        # ----------------------------------------------------
        # OPEN RESOURCE
        # ----------------------------------------------------

        st.divider()

        risk_resources = (
            risk_data[
                "resource_id"
            ]
            .astype(str)
            .tolist()
        )

        selected_risk_resource = st.selectbox(
            "Inspect a high-risk resource",
            risk_resources,
            key="risk_resource_select"
        )

        if st.button(
            "🚨 Inspect Risk",
            type="primary",
            use_container_width=True
        ):

            select_resource(
                selected_risk_resource
            )

            st.rerun()
# ============================================================
# SECURITY POSTURE
# ============================================================

elif st.session_state.page == "Security Posture":

    st.header(
        "🛡 Security Posture"
    )

    st.caption(
        "Overview of security controls across the "
        "assessed cloud environment."
    )

    # --------------------------------------------------------
    # SECURITY CONTROL CALCULATIONS
    # --------------------------------------------------------

    total_resources = len(data)

    control_columns = {
        "Encryption": "has_encryption",
        "MFA": "mfa_enabled",
        "Logging": "has_logging",
        "Monitoring": "has_monitoring",
        "Backup": "has_backup",
        "WAF": "has_waf",
        "Least Privilege": "least_privilege",
        "DLP": "has_dlp",
        "Strong Password Policy": "password_policy_strong",
        "Network Segmentation": "network_segmentation",
        "VPN": "has_vpn",
        "Private Link": "has_private_link",
        "Automatic Updates": "auto_updates"
    }

    control_results = []

    for control_name, column in control_columns.items():

        if column not in data.columns:
            continue

        enabled = int(
            pd.to_numeric(
                data[column],
                errors="coerce"
            )
            .fillna(0)
            .eq(1)
            .sum()
        )

        percentage = (
            enabled / total_resources * 100
            if total_resources
            else 0
        )

        control_results.append(
            {
                "Control": control_name,
                "Enabled": enabled,
                "Coverage": percentage
            }
        )

    controls_df = pd.DataFrame(
        control_results
    )

    # --------------------------------------------------------
    # OVERALL POSTURE
    # --------------------------------------------------------

    if not controls_df.empty:

        average_coverage = (
            controls_df["Coverage"].mean()
        )

    else:

        average_coverage = 0

    public_resources = 0

    if "is_public" in data.columns:

        public_resources = int(
            pd.to_numeric(
                data["is_public"],
                errors="coerce"
            )
            .fillna(0)
            .eq(1)
            .sum()
        )

    resources_without_encryption = 0

    if "has_encryption" in data.columns:

        resources_without_encryption = int(
            pd.to_numeric(
                data["has_encryption"],
                errors="coerce"
            )
            .fillna(0)
            .eq(0)
            .sum()
        )

    resources_without_mfa = 0

    if "mfa_enabled" in data.columns:

        resources_without_mfa = int(
            pd.to_numeric(
                data["mfa_enabled"],
                errors="coerce"
            )
            .fillna(0)
            .eq(0)
            .sum()
        )

    p1, p2, p3, p4 = st.columns(4)

    with p1:

        st.metric(
            "Average Control Coverage",
            f"{average_coverage:.1f}%"
        )

    with p2:

        st.metric(
            "Public Resources",
            f"{public_resources:,}"
        )

    with p3:

        st.metric(
            "Without Encryption",
            f"{resources_without_encryption:,}"
        )

    with p4:

        st.metric(
            "Without MFA",
            f"{resources_without_mfa:,}"
        )

    # --------------------------------------------------------
    # CONTROL COVERAGE CHART
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🔐 Security Control Coverage"
    )

    if controls_df.empty:

        st.info(
            "Security control data is not available."
        )

    else:

        fig_controls, ax_controls = plt.subplots(
            figsize=(11, 5)
        )

        ax_controls.barh(
            controls_df["Control"],
            controls_df["Coverage"]
        )

        ax_controls.set_xlabel(
            "Coverage (%)"
        )

        ax_controls.set_xlim(
            0,
            100
        )

        ax_controls.set_title(
            "Security Control Coverage"
        )

        ax_controls.grid(
            axis="x",
            alpha=0.15
        )

        fig_controls.tight_layout()

        st.pyplot(
            fig_controls,
            use_container_width=True
        )

        plt.close(
            fig_controls
        )

    # --------------------------------------------------------
    # CONTROL TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Control Coverage Details"
    )

    if not controls_df.empty:

        controls_display = (
            controls_df
            .copy()
        )

        controls_display[
            "Coverage"
        ] = controls_display[
            "Coverage"
        ].round(1)

        controls_display[
            "Coverage"
        ] = (
            controls_display[
                "Coverage"
            ].astype(str)
            + "%"
        )

        st.dataframe(
            controls_display,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # POSTURE OBSERVATIONS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🔍 Posture Observations"
    )

    observations = []

    if public_resources > 0:

        observations.append(
            f"⚠️ {public_resources:,} resources "
            "are publicly exposed."
        )

    if resources_without_encryption > 0:

        observations.append(
            f"⚠️ {resources_without_encryption:,} "
            "resources do not have encryption enabled."
        )

    if resources_without_mfa > 0:

        observations.append(
            f"⚠️ {resources_without_mfa:,} "
            "resources do not have MFA enabled."
        )

    if average_coverage >= 80:

        observations.append(
            "✅ Overall security-control coverage "
            "is relatively strong."
        )

    elif average_coverage >= 60:

        observations.append(
            "ℹ️ Overall security-control coverage "
            "is moderate and has room for improvement."
        )

    else:

        observations.append(
            "🔴 Overall security-control coverage "
            "is low and requires attention."
        )

    for observation in observations:

        st.write(
            observation
        )


# ============================================================
# MODEL ANALYSIS
# ============================================================

elif st.session_state.page == "Model Analysis":

    st.header(
        "🤖 Model Analysis"
    )

    st.caption(
        "Comparison between the RAMA baseline and "
        "the proposed healthcare-focused risk model."
    )

    # --------------------------------------------------------
    # MODEL KPI
    # --------------------------------------------------------

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        st.metric(
            "RAMA Average",
            f"{average_rama:.2f}"
        )

    with a2:

        st.metric(
            "Proposed Average",
            f"{average_proposed:.2f}"
        )

    with a3:

        st.metric(
            "Average Difference",
            f"{average_change:+.2f}"
        )

    with a4:

        st.metric(
            "Percentage Difference",
            f"{percentage_change:+.2f}%"
        )

    # --------------------------------------------------------
    # SCORE COMPARISON
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📊 Score Comparison"
    )

    model_data = pd.DataFrame(
        {
            "Model": [
                "RAMA Baseline",
                "Proposed Model"
            ],
            "Average Score": [
                average_rama,
                average_proposed
            ]
        }
    )

    fig_model, ax_model = plt.subplots(
        figsize=(10, 5)
    )

    ax_model.bar(
        model_data["Model"],
        model_data["Average Score"]
    )

    ax_model.set_ylabel(
        "Average Risk Score"
    )

    ax_model.set_title(
        "RAMA vs Proposed Risk Score"
    )

    ax_model.grid(
        axis="y",
        alpha=0.15
    )

    for index, value in enumerate(
        model_data["Average Score"]
    ):

        ax_model.text(
            index,
            value + 1,
            f"{value:.2f}",
            ha="center",
            fontweight="bold"
        )

    fig_model.tight_layout()

    st.pyplot(
        fig_model,
        use_container_width=True
    )

    plt.close(
        fig_model
    )

    # --------------------------------------------------------
    # SCORE DIFFERENCE
    # --------------------------------------------------------

    if "score_difference" in data.columns:

        st.subheader(
            "📈 Score Difference Distribution"
        )

        fig_difference, ax_difference = plt.subplots(
            figsize=(10, 4)
        )

        ax_difference.hist(
            data[
                "score_difference"
            ].dropna(),
            bins=30
        )

        ax_difference.axvline(
            0,
            linestyle="--",
            linewidth=1.5
        )

        ax_difference.set_xlabel(
            "Proposed Score − RAMA Score"
        )

        ax_difference.set_ylabel(
            "Number of Resources"
        )

        ax_difference.set_title(
            "Distribution of Model Score Changes"
        )

        ax_difference.grid(
            axis="y",
            alpha=0.15
        )

        fig_difference.tight_layout()

        st.pyplot(
            fig_difference,
            use_container_width=True
        )

        plt.close(
            fig_difference
        )

    # --------------------------------------------------------
    # MODEL CHANGE SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Model Change Summary"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Scores Increased",
            f"{scores_increased:,}"
        )

    with c2:

        st.metric(
            "Scores Decreased",
            f"{scores_decreased:,}"
        )

    with c3:

        st.metric(
            "Scores Unchanged",
            f"{scores_unchanged:,}"
        )

    # --------------------------------------------------------
    # MODEL EXPLANATION
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🧠 Model Design"
    )

    st.markdown(
        """
### RAMA Baseline

The RAMA-style baseline provides a general security
risk assessment using confidentiality, integrity and
availability considerations.

### Proposed Healthcare Model

The proposed model extends the baseline by incorporating
healthcare-specific factors such as:

- Cloud exposure
- Healthcare data sensitivity
- Healthcare impact
- Security posture

This allows healthcare-related cloud resources to receive
risk scores that better reflect the potential impact of
security misconfigurations.
"""
    )

    # --------------------------------------------------------
    # MODEL COMPARISON FILE
    # --------------------------------------------------------

    if COMPARISON_REPORT.exists():

        st.divider()

        st.subheader(
            "📄 Detailed Model Comparison"
        )

        try:

            comparison_data = pd.read_csv(
                COMPARISON_REPORT
            )

            st.write(
                f"{len(comparison_data):,} "
                "resource comparisons available."
            )

            comparison_preview = (
                comparison_data
                .head(100)
                .copy()
            )

            st.dataframe(
                comparison_preview,
                use_container_width=True,
                height=500
            )

        except Exception as error:

            st.warning(
                "Could not load model comparison file."
            )

            st.caption(
                str(error)
            )


# ============================================================
# RECOMMENDATIONS
# ============================================================

elif st.session_state.page == "Recommendations":

    st.header(
        "💡 Security Recommendations"
    )

    st.caption(
        "Prioritized remediation guidance generated "
        "from the risk assessment."
    )

    # --------------------------------------------------------
    # RECOMMENDATION COUNTS
    # --------------------------------------------------------

    if "recommendation" in data.columns:

        recommendation_counts = (
            data["recommendation"]
            .fillna("No recommendation")
            .astype(str)
            .value_counts()
        )

    else:

        recommendation_counts = pd.Series(
            dtype="int64"
        )

    # --------------------------------------------------------
    # PRIORITY SELECTOR
    # --------------------------------------------------------

    recommendation_priority = st.selectbox(
        "Focus on Priority",
        [
            "All",
            "Critical",
            "High",
            "Medium",
            "Low"
        ]
    )

    recommendation_data = data.copy()

    if recommendation_priority != "All":

        recommendation_data = (
            recommendation_data[
                recommendation_data[
                    "priority"
                ]
                ==
                recommendation_priority
            ]
        )

    recommendation_data = (
        recommendation_data
        .sort_values(
            "proposed_score",
            ascending=False
        )
    )

    st.write(
        f"**{len(recommendation_data):,}** "
        "resources require review."
    )

    # --------------------------------------------------------
    # TOP RECOMMENDATIONS
    # --------------------------------------------------------

    if recommendation_data.empty:

        st.success(
            "No resources match this priority."
        )

    else:

        shown_recommendations = (
            recommendation_data
            .head(20)
        )

        for index, (_, row) in enumerate(
            shown_recommendations.iterrows()
        ):

            resource_id = str(
                row["resource_id"]
            )

            priority = str(
                row["priority"]
            )

            score = float(
                row["proposed_score"]
            )

            recommendation = str(
                row.get(
                    "recommendation",
                    "Review security configuration."
                )
            )

            with st.expander(
                f"🔥 {resource_id} — "
                f"{priority} — "
                f"Risk Score {score:.2f}"
            ):

                rec1, rec2 = st.columns(
                    [3, 1]
                )

                with rec1:

                    st.write(
                        "**Recommended Action**"
                    )

                    st.info(
                        recommendation
                    )

                with rec2:

                    st.metric(
                        "Risk Score",
                        f"{score:.2f}"
                    )

                    st.write(
                        f"**Priority:** {priority}"
                    )

                if st.button(
                    "Open Resource",
                    key=f"recommendation_open_{index}",
                    use_container_width=True
                ):

                    select_resource(
                        resource_id
                    )

                    st.rerun()

    # --------------------------------------------------------
    # RECOMMENDATION EXPORT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📥 Export Recommendations"
    )

    recommendation_export_columns = [
        column
        for column in [
            "resource_id",
            "provider",
            "resource_type",
            "region",
            "proposed_score",
            "priority",
            "recommendation"
        ]
        if column in recommendation_data.columns
    ]

    recommendation_export = (
        recommendation_data[
            recommendation_export_columns
        ]
        .copy()
    )

    csv_data = recommendation_export.to_csv(
        index=False
    )

    st.download_button(
        "📥 Download Recommendations CSV",
        data=csv_data,
        file_name="security_recommendations.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# FALLBACK
# ============================================================

else:

    st.session_state.page = "Dashboard"

    st.rerun()