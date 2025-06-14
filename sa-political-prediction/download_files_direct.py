#!/usr/bin/env python3
"""
Download SA election files directly from S3 URLs
"""

import requests
import pandas as pd
from pathlib import Path
import os

print("🇿🇦 SA Political Data - Direct Download")
print("=" * 50)

# Create directories
data_dir = Path("data")
raw_dir = data_dir / "raw"
processed_dir = data_dir / "processed"

raw_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)

# File URLs (based on your S3 bucket structure)
base_url = "https://sa-political-prediction.s3.eu-west-1.amazonaws.com"
files = {
    "National_2009.xls": 2009,
    "National_2014.xls": 2014,
    "National_2019.xls": 2019,
    "National_2024.xls": 2024
}

print(f"📥 Downloading {len(files)} election files...")

downloaded_files = {}
for filename, year in files.items():
    url = f"{base_url}/{filename}"
    local_path = raw_dir / filename
    
    try:
        print(f"⬇️  Downloading {filename}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Save file
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        file_size = local_path.stat().st_size / 1024
        print(f"✅ Downloaded: {filename} ({file_size:.1f} KB)")
        downloaded_files[year] = local_path
        
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

if downloaded_files:
    print(f"\n🎉 Successfully downloaded {len(downloaded_files)} files!")
    
    # Test reading one file
    test_year = min(downloaded_files.keys())
    test_file = downloaded_files[test_year]
    
    try:
        print(f"\n📊 Testing Excel reading with {test_file.name}...")
        df = pd.read_excel(test_file, engine='openpyxl')
        print(f"✅ Excel file loaded successfully!")
        print(f"   Shape: {df.shape}")
        print(f"   Sample data preview:")
        
        # Show non-empty rows
        for i, row in df.head(10).iterrows():
            row_data = [str(cell)[:20] for cell in row if pd.notna(cell) and str(cell).strip()]
            if row_data:
                print(f"   Row {i}: {' | '.join(row_data[:4])}")
        
        print(f"\n✅ Ready for full EDA analysis!")
        
    except Exception as e:
        print(f"❌ Excel reading failed: {e}")
else:
    print("❌ No files were downloaded successfully")

print("\n🚀 Next step: Run full EDA notebook!")
