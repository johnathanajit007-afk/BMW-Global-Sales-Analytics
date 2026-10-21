import os
import io
import pandas as pd
from azure.storage.blob import BlobServiceClient

# ==============================================================================
# 1. Configuration & Data Paths
# ==============================================================================
# Cloud parameters (Retained to demonstrate Azure architecture layout)
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "YOUR_AZURE_STORAGE_CONNECTION_STRING_HERE")
CONTAINER_NAME = "raw-data"
BLOB_NAME = "BMW sales data (2010-2024).csv"

# Local fallback path for portfolio execution after cloud resource deletion
LOCAL_RAW_PATH = "data/raw/BMW_sales_data_(2010-2024).csv"
OUTPUT_FILENAME = "cleaned_bmw_sales_data.csv"

def run_etl():
    df = None
    
    # ==============================================================================
    # 2. Extract Stage (Cloud Extraction with Local Fallback)
    # ==============================================================================
    # Attempting Cloud Ingestion if a valid Connection String exists
    if CONNECTION_STRING and CONNECTION_STRING != "YOUR_AZURE_STORAGE_CONNECTION_STRING_HERE":
        try:
            print("Connecting to Azure Blob Storage...")
            blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            
            print(f"Downloading '{BLOB_NAME}' from container '{CONTAINER_NAME}'...")
            blob_client = container_client.get_blob_client(BLOB_NAME)
            download_stream = blob_client.download_blob()
            df = pd.read_csv(io.BytesIO(download_stream.readall()))
            print(f"Successfully extracted {len(df)} rows from Azure Blob Storage.")
        except Exception as e:
            print(f"Azure Connection failed/unavailable: {e}")
            print("Switching to local fallback data environment...")

    # Local Ingestion Fallback (Ensures the pipeline runs smoothly on GitHub portfolios)
    if df is None:
        if os.path.exists(LOCAL_RAW_PATH):
            print(f"Extracting local raw data from reference path: '{LOCAL_RAW_PATH}'...")
            df = pd.read_csv(LOCAL_RAW_PATH)
            print(f"Successfully extracted {len(df)} rows from local storage.")
        else:
            print(f"\n🛑 Error: Data source missing! Please place the raw CSV file at: '{LOCAL_RAW_PATH}'")
            return

    print("\n--- Raw Data Preview ---")
    print(df.head(3))
    
    # ==============================================================================
    # 3. Transform & Enrich Stage
    # ==============================================================================
    print("\nTransforming and enriching data...")
    
    # Standardize column headers (remove spaces, replace with underscores)
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    # Handle missing values safely
    df = df.dropna()
    
    print("\n--- Cleaned Data Preview ---")
    print(df.head(3))
    
    # ==============================================================================
    # 4. Load Stage (Local Output Generation)
    # ==============================================================================
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"\nTransformations complete. Cleaned file saved to: '{OUTPUT_FILENAME}'")

if __name__ == "__main__":
    run_etl()
