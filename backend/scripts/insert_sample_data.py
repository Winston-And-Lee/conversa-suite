#!/usr/bin/env python3
"""
Script to insert sample data into the database using the insert-sample-data endpoint.
This is a simpler alternative to the data_ingestion_script.py that directly uses the API.
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your actual API URL
INSERT_SAMPLE_DATA_ENDPOINT = f"{API_BASE_URL}/api/data-ingestion/insert-sample-data"

def insert_sample_data():
    """Insert sample data using the API endpoint."""
    try:
        # Make the API request
        response = requests.post(INSERT_SAMPLE_DATA_ENDPOINT)
        
        # Check response
        if response.status_code == 201:
            print("✅ Successfully inserted sample data")
            print("📊 Inserted items:")
            
            # Pretty print the inserted items
            items = response.json()
            for i, item in enumerate(items, 1):
                print(f"\n[{i}/{len(items)}] {item['title']}")
                print(f"   ID: {item['id']}")
                print(f"   Data Type: {item['data_type']}")
                print(f"   File URL: {item['file_url'] or 'None'}")
                if item['file_url']:
                    print(f"   File Name: {item['file_name'] or 'Unknown'}")
                
            print(f"\n✨ Total items inserted: {len(items)}")
        else:
            print("❌ Failed to insert sample data")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function."""
    print("🚀 Starting sample data insertion...")
    insert_sample_data()
    print("\n✨ Process completed!")

if __name__ == "__main__":
    main() 