#!/usr/bin/env python3
"""
South African Election Data Processing Module

This module provides comprehensive data processing functionality for 
SA National Election data from 2009-2024.

Author: SA Political Prediction Project
Date: 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import logging
import json
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')

class SAElectionProcessor:
    """
    Comprehensive processor for South African election data
    """
    
    def __init__(self, raw_data_dir: str = "data/raw", processed_data_dir: str = "data/processed"):
        """
        Initialize the election data processor
        
        Args:
            raw_data_dir: Directory containing raw election files
            processed_data_dir: Directory for processed output files
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.processed_data_dir.mkdir(exist_ok=True)
        
        # File mapping for elections
        self.file_mapping = {
            2009: "National_2009.xls",
            2014: "National_2014.xls", 
            2019: "National_2019.xls",
            2024: "National_2024.xls"
        }
        
        # Province mapping for standardization
        self.provinces = [
            'Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal',
            'Limpopo', 'Mpumalanga', 'North West', 'Northern Cape', 
            'Western Cape', 'Out of Country'
        ]
        
        # Standard party mappings for consistency
        self.party_mappings = {
            'AFRICAN NATIONAL CONGRESS': 'ANC',
            'DEMOCRATIC ALLIANCE': 'DA',
            'ECONOMIC FREEDOM FIGHTERS': 'EFF',
            'UMKHONTO WESIZWE': 'MK',
            'INKATHA FREEDOM PARTY': 'IFP'
        }
        
        logger.info(f"Initialized SA Election Processor")
        logger.info(f"Raw data directory: {self.raw_data_dir}")
        logger.info(f"Processed data directory: {self.processed_data_dir}")
    
    def check_data_availability(self) -> Dict[int, bool]:
        """Check which election data files are available"""
        availability = {}
        
        logger.info("Checking data file availability...")
        for year, filename in self.file_mapping.items():
            file_path = self.raw_data_dir / filename
            availability[year] = file_path.exists()
            
            if availability[year]:
                size_kb = file_path.stat().st_size / 1024
                logger.info(f"✅ {year}: {filename} ({size_kb:.1f} KB)")
            else:
                logger.warning(f"❌ {year}: {filename} - NOT FOUND")
        
        return availability

def main():
    """Main processing function"""
    print("🇿🇦 SA Election Data Processing")
    print("=" * 50)
    
    # Initialize processor
    processor = SAElectionProcessor()
    
    # Check data availability
    availability = processor.check_data_availability()
    
    print(f"\n✅ Data availability check complete!")
    print(f"📊 Available elections: {sum(availability.values())}")
    
    return processor

if __name__ == "__main__":
    processor = main()
