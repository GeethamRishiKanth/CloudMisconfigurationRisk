import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


def download_dataset():

    # =====================================================
    # LOAD ENVIRONMENT VARIABLES
    # =====================================================

    load_dotenv()

    account_name = os.getenv(
        "AZURE_STORAGE_ACCOUNT_NAME"
    )

    account_key = os.getenv(
        "AZURE_STORAGE_ACCOUNT_KEY"
    )

    container_name = os.getenv(
        "AZURE_CONTAINER_NAME"
    )

    blob_name = os.getenv(
        "AZURE_BLOB_NAME"
    )

    # =====================================================
    # VALIDATE AZURE CONFIGURATION
    # =====================================================

    if not account_name or not account_key:

        raise ValueError(
            "Azure storage credentials are missing from .env"
        )

    if not container_name or not blob_name:

        raise ValueError(
            "Azure container name or blob name is missing from .env"
        )

    # =====================================================
    # CREATE CONNECTION STRING
    # =====================================================

    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account_name};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )

    # =====================================================
    # CONNECT TO AZURE BLOB STORAGE
    # =====================================================

    blob_service_client = (
        BlobServiceClient.from_connection_string(
            connection_string
        )
    )

    blob_client = (
        blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
    )

    # =====================================================
    # PROJECT DATA DIRECTORY
    # =====================================================

    base_dir = Path(
        __file__
    ).resolve().parent

    data_dir = (
        base_dir
        / "data"
    )

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    download_path = (
        data_dir
        / "misconfigurations.csv"
    )

    # =====================================================
    # DOWNLOAD DATASET
    # =====================================================

    print(
        "Downloading dataset from Azure..."
    )

    with open(
        download_path,
        "wb"
    ) as file:

        file.write(
            blob_client
            .download_blob()
            .readall()
        )

    # =====================================================
    # VERIFY DOWNLOADED DATASET
    # =====================================================

    try:

        data = pd.read_csv(
            download_path,
            sep=None,
            engine="python"
        )

    except Exception as error:

        raise ValueError(
            "Azure file was downloaded, but it could "
            "not be read as a CSV."
        ) from error

    # =====================================================
    # DISPLAY DOWNLOAD INFORMATION
    # =====================================================

    print(
        f"Downloaded successfully: {download_path}"
    )

    print(
        f"Rows downloaded: {len(data):,}"
    )

    print(
        f"Columns detected: {len(data.columns)}"
    )

    # =====================================================
    # WARN IF DATASET SIZE IS NOT 2,000
    # =====================================================

    if len(data) != 2000:

        print(
            "\nWARNING:"
        )

        print(
            "The Azure dataset does not contain "
            "exactly 2,000 rows."
        )

        print(
            f"Expected: 2000"
        )

        print(
            f"Received: {len(data)}"
        )

    else:

        print(
            "Dataset size verified: 2,000 rows."
        )

    return str(
        download_path
    )


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    download_dataset()