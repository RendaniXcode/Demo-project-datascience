#!/usr/bin/env python3
"""
South African Election Data Processing Module
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
    def __init__(self, raw_data_dir: str = "data/raw", processed_data_dir: str = "data/processed"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.processed_data_dir.mkdir(exist_ok=True)
        
        self.file_mapping = {
            2009: "National_2009.xls",
            2014: "National_2014.xls", 
            2019: "National_2019.xls",
            2024: "National_2024.xls"
        }
        
        logger.info(f"Initialized SA Election Processor")
    
    def check_data_availability(self) -> Dict[int, bool]:
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
    
    def extract_election_data(self, year: int) -> Optional[pd.DataFrame]:
        """Extract clean election data for a specific year"""
        if year not in self.file_mapping:
            logger.error(f"Year {year} not supported")
            return None
        
        file_path = self.raw_data_dir / self.file_mapping[year]
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        logger.info(f"Processing {year} election data...")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='xlrd')
            
            # Extract party data based on year
            if year == 2024:
                clean_df = self._extract_2024_data(df)
            else:
                clean_df = self._extract_historical_data(df, year)
            
            logger.info(f"✅ {year}: Extracted {len(clean_df)} parties")
            return clean_df
            
        except Exception as e:
            logger.error(f"Error processing {year} data: {e}")
            return None
    
    def _extract_2024_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract 2024 election data"""
        # Find data start (look for party names)
        data_start = None
        for i in range(len(df)):
            if pd.notna(df.iloc[i, 1]) and isinstance(df.iloc[i, 1], str):
                if len(df.iloc[i, 1].strip()) > 5:  # Reasonable party name length
                    data_start = i
                    break
        
        if data_start is None:
            data_start = 5  # Default fallback
        
        # Extract party data
        parties_data = []
        for i in range(data_start, len(df)):
            row = df.iloc[i]
            
            # Party name (column 1)
            party_name = row.iloc[1] if pd.notna(row.iloc[1]) else None
            if not party_name or len(str(party_name).strip()) < 3:
                continue
            
            # Total votes (column 33) and percentage (column 34)
            total_votes = row.iloc[33] if len(row) > 33 and pd.notna(row.iloc[33]) else 0
            total_percent = row.iloc[34] if len(row) > 34 and pd.notna(row.iloc[34]) else 0
            
            try:
                total_votes = float(str(total_votes).replace(',', '')) if total_votes else 0
                total_percent = float(str(total_percent).replace(',', '')) if total_percent else 0
            except:
                continue
            
            if total_votes > 100:  # Reasonable vote threshold
                parties_data.append({
                    'Year': 2024,
                    'Party_Name': str(party_name).strip(),
                    'Total_Votes': int(total_votes),
                    'Total_Percent': total_percent
                })
        
        return pd.DataFrame(parties_data)
    
    def _extract_historical_data(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """Extract historical election data (2009, 2014, 2019)"""
        parties_data = []
        
        # Look for data starting around row 10-20
        for i in range(10, min(len(df), 100)):
            row = df.iloc[i]
            
            # Find party name (usually first text column)
            party_name = None
            for j in range(min(5, len(row))):
                val = row.iloc[j]
                if pd.notna(val) and isinstance(val, str) and len(val.strip()) > 3:
                    # Skip header-like text
                    if not any(word in val.lower() for word in ['party', 'votes', 'total', '%']):
                        party_name = val.strip()
                        break
            
            if not party_name:
                continue
            
            # Find total votes (usually one of the last columns)
            total_votes = 0
            for j in range(len(row)-1, max(0, len(row)-10), -1):
                try:
                    val = row.iloc[j]
                    if pd.notna(val):
                        votes = float(str(val).replace(',', ''))
                        if votes > 1000:  # Reasonable vote threshold
                            total_votes = votes
                            break
                except:
                    continue
            
            if party_name and total_votes > 1000:
                # Skip summary rows
                if not any(term in party_name.lower() for term in ['total', 'spoilt', 'spoiled', 'valid']):
                    parties_data.append({
                        'Year': year,
                        'Party_Name': party_name,
                        'Total_Votes': int(total_votes)
                    })
        
        # Calculate percentages
        df_parties = pd.DataFrame(parties_data)
        if len(df_parties) > 0:
            total_valid_votes = df_parties['Total_Votes'].sum()
            df_parties['Total_Percent'] = (df_parties['Total_Votes'] / total_valid_votes) * 100
        
        return df_parties
    
    def process_all_elections(self) -> Dict[int, pd.DataFrame]:
        """Process all available election data"""
        logger.info("Processing all election data...")
        
        all_data = {}
        availability = self.check_data_availability()
        
        for year in sorted(availability.keys()):
            if availability[year]:
                df = self.extract_election_data(year)
                if df is not None and len(df) > 0:
                    all_data[year] = df
                    
                    # Save processed data
                    output_file = self.processed_data_dir / f"election_{year}_processed.csv"
                    df.to_csv(output_file, index=False)
                    logger.info(f"💾 Saved: {output_file}")
                    
                    # Show top parties
                    top_3 = df.nlargest(3, 'Total_Votes')[['Party_Name', 'Total_Percent']]
                    logger.info(f"📊 {year} Top 3: {', '.join([f'{row.Party_Name} ({row.Total_Percent:.1f}%)' for _, row in top_3.iterrows()])}")
        
        # Create combined dataset
        if all_data:
            combined_df = pd.concat(all_data.values(), ignore_index=True)
            combined_file = self.processed_data_dir / "all_elections_combined.csv"
            combined_df.to_csv(combined_file, index=False)
            logger.info(f"💾 Saved combined data: {combined_file}")
        
        return all_data

def main():
    """Main processing function"""
    print("🇿🇦 SA Election Data Processing")
    print("=" * 50)
    
    # Initialize processor
    processor = SAElectionProcessor()
    
    # Process all elections
    all_data = processor.process_all_elections()
    
    print(f"\n✅ Processing complete!")
    print(f"📊 Elections processed: {len(all_data)}")
    print(f"📁 Check data/processed/ for output files")
    
    return all_data

if __name__ == "__main__":
    all_data = main()
