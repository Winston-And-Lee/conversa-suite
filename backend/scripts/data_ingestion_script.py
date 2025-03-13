#!/usr/bin/env python3
"""
Script to submit sample data to the data ingestion API.
This script reads sample data from sample_data_ingestion.json and submits it to the API.
"""

import json
import os
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your actual API URL
DATA_INGESTION_ENDPOINT = f"{API_BASE_URL}/api/data-ingestion/"
SCRIPTS_DIR = Path(__file__).parent
RESOURCES_DIR = SCRIPTS_DIR.parent / "../resources"

def load_sample_data():
    """Load sample data from JSON file."""
    sample_data_path = RESOURCES_DIR / "sample_data_ingestion.json"
    with open(sample_data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def submit_data_ingestion(data_item):
    """Submit a single data ingestion item to the API."""
    # Prepare form data
    form_data = {
        "title": data_item["title"],
        "specified_text": data_item["specified_text"],
        "data_type": data_item["data_type"],
        "content": data_item.get("content", ""),  # New content field
        "reference": data_item["reference"],
        "keywords": json.dumps(data_item["keywords"])  # Convert list to JSON string for form data
    }
    
    # Check if we should attach a file
    files = None
    if data_item.get("file_url"):
        # If file_url is provided, add it to the form data
        form_data["file_url"] = data_item["file_url"]
        print(f"   Using file URL: {data_item['file_url']}")
    # elif data_item.get("data_type") == "ตัวบทกฎหมาย" or data_item.get("data_type") == "FICTION":
    #     # For legal text or fiction, attach the sample document
    #     sample_doc_path = RESOURCES_DIR / "sample_document.txt"
    #     if sample_doc_path.exists():
    #         files = {
    #             "file": ("sample_document.pdf", open(sample_doc_path, "rb"), "application/pdf")
    #         }
    
    try:
        # Make the API request
        response = requests.post(
            DATA_INGESTION_ENDPOINT,
            data=form_data,
            files=files
        )
        
        # Check response
        if response.status_code == 201:
            print(f"✅ Successfully submitted: {data_item['title']}")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to submit: {data_item['title']}")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error submitting {data_item['title']}: {str(e)}")
    
    finally:
        # Close file if opened
        if files and "file" in files:
            files["file"][1].close()

def main():
    """Main function to submit all sample data."""
    print("🚀 Starting data ingestion submission...")
    
    # Load sample data
    sample_data = load_sample_data()
    print(f"📋 Loaded {len(sample_data)} sample data items")
    
    # Submit each data item
    for i, data_item in enumerate(sample_data, 1):
        print(f"\n[{i}/{len(sample_data)}] Submitting: {data_item['title']}")
        submit_data_ingestion(data_item)
    
    print("\n✨ Data ingestion submission completed!")

if __name__ == "__main__":
    main() 