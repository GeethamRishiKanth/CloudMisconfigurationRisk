
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


# =====================================================
# LOAD CONFIGURATION
# =====================================================

load_dotenv()


def get_config(name):
    """Read configuration from environment variables or Streamlit Secrets."""

    value = os.getenv(name)

    if value:
        return value

    try:
        import streamlit as st
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value


# =====================================================
# DOWNLOAD DATASET FROM AZURE
# =====================================================

def download_dataset():

    account_name = get_config("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = get_config("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = get_config("AZURE_CONTAINER_NAME")
    blob_name = get_config("AZURE_BLOB_NAME")

    # Validate configuration
    if not account_name or not account_key:
        raise ValueError(
            "Azure storage credentials are missing. "
            "Configure your local .env file or Streamlit Secrets."
        )

    if not container_name or not blob_name:
        raise ValueError(
            "Azure container name or blob name is missing. "
            "Check your .env file or Streamlit Secrets."
        )

    # Create Azure connection string
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account_name};"
        f"AccountKey={account_key};"
        f"EndpointSuffix=core.windows.net"
    )

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    # Determine project data directory
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    download_path = data_dir / "misconfigurations.csv"

    # Download dataset
    print("Downloading dataset from Azure...")

    with open(download_path, "wb") as file:
        file.write(blob_client.download_blob().readall())

    # Verify downloaded CSV
    try:
        data = pd.read_csv(
            download_path,
            sep=None,
            engine="python"
        )
    except Exception as error:
        raise ValueError(
            "Azure file was downloaded, but it could not be read as a CSV."
        ) from error

    # Display download information
    print(f"Downloaded successfully: {download_path}")
    print(f"Rows downloaded: {len(data):,}")
    print(f"Columns detected: {len(data.columns)}")

    # Verify expected dataset size
    if len(data) != 2000:
        print("\nWARNING:")
        print("The Azure dataset does not contain exactly 2,000 rows.")
        print("Expected: 2000")
        print(f"Received: {len(data)}")
    else:
        print("Dataset size verified: 2,000 rows.")

    return str(download_path)


# =====================================================
# RUN DIRECTLY
# =====================================================

if __name__ == "__main__":
    download_dataset()
