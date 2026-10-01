import GEOparse
from io import BytesIO
import requests

def fetch_geo_dataset(dataset_id):
    """
    Fetch GEO dataset by ID using GEOparse, process it in-memory.
    Args:
        dataset_id (str): GEO dataset ID (e.g., "GSE12345").
    Returns:
        GEOparse.GEO: Parsed GEO dataset if successful, None otherwise.
    """
    try:
        print(f"📥 Fetching GEO dataset with ID: {dataset_id}...")
        url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{dataset_id[:-3]}nnn/{dataset_id}/soft/{dataset_id}_family.soft.gz"

        # Fetch the data directly from the GEO FTP server
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        # Parse the data directly from the response content
        geo = GEOparse.get_GEO(filepath=BytesIO(response.content))
        print(f"✅ Successfully fetched GEO dataset: {dataset_id}")

        return geo

    except Exception as e:
        print(f"❌ Error fetching GEO dataset: {e}")
        return None
