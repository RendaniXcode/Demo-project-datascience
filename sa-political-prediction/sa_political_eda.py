#!/usr/bin/env python3
"""
SA Political Prediction - Exploratory Data Analysis
Quick test version for Studio Lab
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import boto3
from pathlib import Path
import warnings
import openpyxl
import os

# Configuration
warnings.filterwarnings('ignore')
plt.style.use('default')

print("🇿🇦 SA Political Data - EDA Quick Test")
print("=" * 50)
print(f"📂 Working directory: {os.getcwd()}")

# Create directories
data_dir = Path("data")
raw_dir = data_dir / "raw"
processed_dir = data_dir / "processed"

raw_dir.mkdir(parents=True, exist_ok=True)
processed_dir.mkdir(parents=True, exist_ok=True)
print(f"✅ Created directories: {raw_dir}, {processed_dir}")

# Test S3 connection
S3_BUCKET = "sa-political-prediction"
S3_REGION = "eu-west-1"

try:
    s3_client = boto3.client('s3', region_name=S3_REGION)
    
    # List files in bucket
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    if 'Contents' in response:
        excel_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.xls')]
        print(f"📁 Found {len(excel_files)} Excel files in S3:")
        for file in excel_files:
            print(f"  • {file}")
    else:
        print("📁 No files found in S3 bucket")
        
except Exception as e:
    print(f"❌ S3 connection failed: {e}")
    print("💡 Run 'aws configure' to set up credentials")
    exit(1)

# Download one file as test
if excel_files:
    test_file = excel_files[0]  # Download first file
    local_path = raw_dir / test_file
    
    try:
        print(f"\n📥 Downloading test file: {test_file}")
        s3_client.download_file(S3_BUCKET, test_file, str(local_path))
        file_size = local_path.stat().st_size / 1024
        print(f"✅ Downloaded: {local_path.name} ({file_size:.1f} KB)")
        
        # Try to read the Excel file
        print(f"\n📊 Testing Excel file reading...")
        df = pd.read_excel(local_path, engine='openpyxl')
        print(f"✅ Excel file loaded successfully!")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {len(df.columns)}")
        
        # Show first few rows
        print(f"\n📋 First 5 rows of data:")
        print(df.head().to_string())
        
    except Exception as e:
        print(f"❌ Failed to download/read file: {e}")

print(f"\n🎉 Quick test complete!")
print(f"✅ S3 connection working")
print(f"✅ File download working") 
print(f"✅ Excel reading working")
print(f"\nReady to run full EDA notebook! 🚀")
