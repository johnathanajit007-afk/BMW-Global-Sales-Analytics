import os
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io

# 1. Azure Storage Connection Details
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "YOUR_AZURE_STORAGE_CONNECTION_STRING_HERE")
CONTAINER_NAME = "raw-data"
BLOB_NAME = "BMW sales data (2010-2024).csv" # Updated to match your exact file name

def run_etl():
    print("Connecting to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # 2. Extract: Download CSV from Azure
    print(f"Downloading '{BLOB_NAME}' from container '{CONTAINER_NAME}'...")
    blob_client = container_client.get_blob_client(BLOB_NAME)
    download_stream = blob_client.download_blob()
    df = pd.read_csv(io.BytesIO(download_stream.readall()))
    
    print(f"Successfully downloaded {len(df)} rows of raw data.")
    print("Raw Data Preview:")
    print(df.head(3))
    
    # 3. Transform & Enrich Data
    print("\nTransforming and enriching data...")
    
    # Standardize column headers or text formatting if present
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    # Handle missing values safely
    df = df.dropna()
    
    print("Transformation complete. Cleaned Data Preview:")
    print(df.head(3))
    
    # 4. Save locally as a processed file (ready for SQL/Database loading)
    output_filename = "cleaned_bmw_sales_data.csv"
    df.to_csv(output_filename, index=False)
    print(f"\nSaved processed data locally to '{output_filename}'.")

if __name__ == "__main__":
    run_etl()
