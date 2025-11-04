---
dataset_info:
  features:
    - name: strain_name
      dtype: string
    - name: breeder
      dtype: string
    - name: description
      dtype: string
    - name: current_price_gbp
      dtype: float64
    - name: original_price_gbp
      dtype: float64
    - name: discount_percent
      dtype: float64
    - name: pack_options
      dtype: string
    - name: product_url
      dtype: string
    - name: image_url
      dtype: string
    - name: overview
      dtype: string
    - name: growth_and_harvest
      dtype: string
    - name: experience
      dtype: string
    - name: seed_type
      dtype: string
    - name: flowering_period_type
      dtype: string
    - name: indica_sativa
      dtype: string
    - name: type_ratio
      dtype: string
    - name: strain_type_summary
      dtype: string
    - name: environment
      dtype: string
    - name: strength
      dtype: string
    - name: medical_strains
      dtype: string
    - name: smell_taste
      dtype: string
    - name: effect
      dtype: string
    - name: climate
      dtype: string
    - name: flavor
      dtype: string
    - name: thc
      dtype: string
    - name: cbd
      dtype: string
    - name: yield_indoor
      dtype: string
    - name: yield_outdoor
      dtype: string
    - name: height_indoor
      dtype: string
    - name: height_outdoor
      dtype: string
    - name: indoor_height_detail
      dtype: string
    - name: indoor_flowering_time
      dtype: string
    - name: outdoor_harvest_time
      dtype: string
    - name: flowering_time
      dtype: string
    - name: harvest_month
      dtype: string
    - name: genetic_background
      dtype: string
    - name: stock_availability
      dtype: string
    - name: sale_item
      dtype: string
    - name: most_popular_seeds
      dtype: string
  splits:
    - name: train
      num_bytes: 7577085
      num_examples: 8910
  download_size: 7577085
  dataset_size: 7577085
---

# 🌿 Cannabis Strains Dataset

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Dataset Size](https://img.shields.io/badge/dataset-8,910%20strains-green.svg)](https://huggingface.co/datasets/jonusnattapong/cannabis-strains-dataset)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/jonusnattapong/cannabis-strains-dataset)

A comprehensive dataset of cannabis strain listings scraped from [Seed City](https://www.seed-city.com/en/list-all-products), featuring detailed cultivation information, pricing, and strain characteristics.

## 📊 Dataset Overview

- **Total Records**: 8,910 cannabis strains
- **Total Columns**: 39 attributes
- **Data Source**: Seed City (UK-based seed bank)
- **Last Updated**: November 2025
- **Data Completeness**: 47.6%
- **Price Range**: £0.00 - £999.79 GBP
- **Format**: CSV with UTF-8 encoding

## 📋 Data Fields

### Core Listing Information
- **strain_name** (string) – Product/strain title from Seed City
- **breeder** (string) – Brand or breeder responsible for the listing
- **description** (string) – Short marketing excerpt from the browse page
- **current_price_gbp** (float64), **original_price_gbp** (float64), **discount_percent** (float64) – GBP pricing metadata
- **pack_options** (string) – Pack sizes and GBP prices from dropdown
- **product_url** (string), **image_url** (string) – Direct product and thumbnail links

### Detailed Strain Characteristics
- **overview** (string), **growth_and_harvest** (string), **experience** (string) – Narrative sections from detail pages
- **seed_type** (string), **flowering_period_type** (string), **indica_sativa** (string), **type_ratio** (string), **strain_type_summary** (string) – Taxonomy and classification
- **environment** (string), **strength** (string), **medical_strains** (string), **smell_taste** (string), **effect** (string), **climate** (string), **flavor** (string) – Qualitative descriptors
- **thc** (string), **cbd** (string) – Cannabinoid content percentages
- **yield_indoor** (string), **yield_outdoor** (string) – Expected yields
- **height_indoor** (string), **height_outdoor** (string), **indoor_height_detail** (string) – Plant stature metrics
- **indoor_flowering_time** (string), **outdoor_harvest_time** (string), **flowering_time** (string), **harvest_month** (string) – Cultivation timelines
- **genetic_background** (string) – Strain lineage information
- **stock_availability** (string), **sale_item** (string), **most_popular_seeds** (string) – Merchandising flags

> **Note**: Missing values indicate that the source page omitted that attribute. This is normal and expected.

## 🚀 Quick Start

### Load the Dataset
```python
from datasets import load_dataset

# Load from Hugging Face
dataset = load_dataset("jonusnattapong/cannabis-strains-dataset")

# Access the data
df = dataset['train'].to_pandas()
print(f"Dataset shape: {df.shape}")
```

### Alternative: Load from CSV
```python
import pandas as pd

# Direct CSV loading
df = pd.read_csv("https://huggingface.co/datasets/jonusnattapong/cannabis-strains-dataset/resolve/main/cannabis-strains.csv")
df.head()
```

### Basic Analysis
```python
# Most common breeders
df['breeder'].value_counts().head(10)

# Average prices by breeder
df.groupby('breeder')['current_price_gbp'].mean().sort_values(ascending=False).head(10)

# Strain types distribution
df['indica_sativa'].value_counts()
```

## 📊 Data Quality & Statistics

Current dataset completeness: **47.6%**
- **sale_item**: 11.44% complete (88.56% missing)
- **discount_percent**: 11.57% complete (88.43% missing)
- **outdoor_harvest_time**: 36.74% complete (63.26% missing)
- **indoor_height_detail**: 47.24% complete (52.76% missing)
- **smell_taste**: 79.81% complete (20.19% missing)

### Key Insights
- **Price Range**: £0.00 - £999.79 GBP
- **Most Common Type**: Feminized seeds (90%+)
- **Popular Categories**: Autoflowering, Indica-dominant, High-THC strains
- **Top Breeders**: Seed City Bulk Cannabis Seeds, Cannabis Seed Sale Items, Royal Queen Seeds

## 🔄 Data Collection

The dataset was collected using web scraping techniques from Seed City's product catalog. The scraping process includes:

- **Rate Limiting**: Polite delays between requests (0.6s catalog, 0.35s details)
- **Cloudflare Bypass**: Using cloudscraper to handle anti-bot protection
- **Error Handling**: Robust retry logic for failed requests
- **Data Validation**: Quality checks on scraped content

### Update Process
```bash
# From the source repository
git clone https://github.com/JonusNattapong/Cannabis-Strains.git
cd Cannabis-Strains

# Scrape new data
python scrape_seed_city.py

# Update metadata
python update_metadata.py

# Upload to Hugging Face
python upload_hf_updated.py
```

## 📄 License

This dataset is released under the **CC0 1.0 Universal (CC0 1.0) Public Domain Dedication**.

## ⚠️ Legal Notice

This dataset is for educational and research purposes only. Cannabis laws vary by jurisdiction. Always comply with local regulations regarding cannabis cultivation and usage.

## 🙏 Acknowledgments

- **Data Source**: [Seed City](https://www.seed-city.com) for providing comprehensive strain information
- **Tools**: BeautifulSoup, CloudScraper, Pandas for data collection and analysis
- **Community**: Open source contributions and feedback

---

**Dataset Version**: v1.1.0
**Last Updated**: November 2025
**Source Repository**: [GitHub](https://github.com/JonusNattapong/Cannabis-Strains)