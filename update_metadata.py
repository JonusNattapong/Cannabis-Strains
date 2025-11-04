#!/usr/bin/env python3
"""
Update dataset metadata with correct statistics
"""

import json
import pandas as pd
from pathlib import Path

def main():
    # Read current dataset
    df = pd.read_csv('cannabis-strains.csv')

    # Calculate statistics
    num_examples = len(df)
    num_columns = len(df.columns)
    num_bytes = Path('cannabis-strains.csv').stat().st_size

    # Count missing values
    missing_data = df.isnull().sum()
    total_missing = missing_data.sum()
    completeness_pct = ((len(df) * len(df.columns) - total_missing) / (len(df) * len(df.columns))) * 100

    # Get price statistics
    price_stats = {}
    if 'current_price_gbp' in df.columns:
        prices = pd.to_numeric(df['current_price_gbp'], errors='coerce')
        price_stats = {
            "min_price_gbp": float(prices.min()) if not prices.isna().all() else None,
            "max_price_gbp": float(prices.max()) if not prices.isna().all() else None,
            "avg_price_gbp": float(prices.mean()) if not prices.isna().all() else None,
            "median_price_gbp": float(prices.median()) if not prices.isna().all() else None
        }

    # Get breeder statistics
    top_breeders = []
    if 'breeder' in df.columns:
        breeder_counts = df['breeder'].value_counts().head(5)
        top_breeders = [{"name": breeder, "count": int(count)} for breeder, count in breeder_counts.items()]

    # Get strain type distribution
    strain_types = {}
    if 'indica_sativa' in df.columns:
        type_counts = df['indica_sativa'].value_counts()
        strain_types = {str(k): int(v) for k, v in type_counts.items()}

    # Create description with statistics
    top_breeders_text = "\n".join([f"- {b['name']}: {b['count']} strains" for b in top_breeders[:3]])
    strain_types_text = "\n".join([f"- {k}: {v} strains" for k, v in list(strain_types.items())[:3]])

    description = f"""Real-world cannabis strain listings scraped from the Seed City catalogue (https://www.seed-city.com/en/list-all-products).

**Dataset Statistics:**
- Total strains: {num_examples:,}
- Total attributes: {num_columns}
- Data completeness: {completeness_pct:.1f}%
- File size: {num_bytes:,} bytes
- Price range: £{price_stats.get('min_price_gbp', 'N/A'):.2f} - £{price_stats.get('max_price_gbp', 'N/A'):.2f}
- Average price: £{price_stats.get('avg_price_gbp', 'N/A'):.2f}

**Top Breeders:**
{top_breeders_text}

**Strain Types:**
{strain_types_text}

Each row captures base product metadata (name, breeder, GBP prices, pack options, product/image URLs) plus detail-page narrative sections (overview, growth_and_harvest, experience), taxonomy tags (seed_type, flowering_period_type, indica_sativa, type_ratio, strain_type_summary), descriptive attributes (environment, strength, medical_strains, smell_taste, effect, climate, flavor), grow metrics (thc, cbd, yield_indoor/outdoor, height_indoor/outdoor, indoor_height_detail, indoor_flowering_time, outdoor_harvest_time, flowering_time, harvest_month, genetic_background), and merchandising indicators (stock_availability, sale_item, most_popular_seeds).

Scraping is performed with `scrape_seed_city.py`, which handles pagination, polite delays, and Cloudflare bypass via cloudscraper. Missing values simply reflect attributes the source page did not publish. Ideal use cases include market analysis, cultivar comparison, and cultivation planning benchmarks."""

    # Update metadata
    metadata = {
        "title": "Cannabis Strains Dataset",
        "id": "jonusnattapong/cannabis-strains-dataset",
        "licenses": [{"name": "CC0-1.0"}],
        "subtitle": f"Real cannabis strain listings scraped from Seed City website ({num_examples:,} strains)",
        "description": description,
        "keywords": [
            "cannabis",
            "strains",
            "marijuana",
            "prices",
            "market-data",
            "web-scraping",
            "cultivation",
            "breeders",
            "seed-bank"
        ],
        "resources": [
            {
                "path": "cannabis-strains.csv",
                "description": f"Main dataset file containing {num_examples:,} scraped cannabis strain records",
                "num_examples": num_examples,
                "num_columns": num_columns
            }
        ],
        "acknowledgements": "Data scraped from Seed City website. Please respect their terms of service and robots.txt when using this data.",
        "version": "1.1.0",
        "last_updated": "2025-11-04"
    }

    # Save updated metadata
    with open('dataset-metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated metadata: {num_examples:,} examples, {num_bytes:,} bytes")
    print(f"📊 Completeness: {completeness_pct:.1f}%")
    print(f"💰 Price range: £{price_stats.get('min_price_gbp', 'N/A'):.2f} - £{price_stats.get('max_price_gbp', 'N/A'):.2f}")
    print(f"🏢 Top breeders: {', '.join([b['name'] for b in top_breeders[:3]])}")

if __name__ == "__main__":
    main()