# 🌿 Cannabis Strains Dataset

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dataset Size](https://img.shields.io/badge/dataset-743%20strains-green.svg)](https://github.com/JonusNattapong/Cannabis-Strains)

A comprehensive dataset of cannabis strain listings scraped from [Seed City](https://www.seed-city.com/en/list-all-products), featuring detailed cultivation information, pricing, and strain characteristics.

## 📊 Dataset Overview

- **Total Records**: 8,910 cannabis strains
- **Total Columns**: 39 attributes
- **Data Source**: Seed City (UK-based seed bank)
- **Last Updated**: November 2025
- **Data Completeness**: 47.6%
- **Price Range**: £0.00 - £999.79 GBP
- **Format**: CSV with UTF-8 encoding

## 🏗️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
pip install cloudscraper beautifulsoup4 pandas requests
```

### Optional Dependencies (for analysis)
```bash
pip install jupyter matplotlib seaborn scikit-learn
```

## 📋 Data Fields

### Core Listing Information
- **strain_name** – Product/strain title from Seed City
- **breeder** – Brand or breeder responsible for the listing
- **description** – Short marketing excerpt from the browse page
- **current_price_gbp**, **original_price_gbp**, **discount_percent** – GBP pricing metadata
- **pack_options** – Pack sizes and GBP prices from dropdown
- **product_url**, **image_url** – Direct product and thumbnail links

### Detailed Strain Characteristics
- **overview**, **growth_and_harvest**, **experience** – Narrative sections from detail pages
- **seed_type**, **flowering_period_type**, **indica_sativa**, **type_ratio**, **strain_type_summary** – Taxonomy and classification
- **environment**, **strength**, **medical_strains**, **smell_taste**, **effect**, **climate**, **flavor** – Qualitative descriptors
- **thc**, **cbd** – Cannabinoid content percentages
- **yield_indoor**, **yield_outdoor** – Expected yields
- **height_indoor**, **height_outdoor**, **indoor_height_detail** – Plant stature metrics
- **indoor_flowering_time**, **outdoor_harvest_time**, **flowering_time**, **harvest_month** – Cultivation timelines
- **genetic_background** – Strain lineage information
- **stock_availability**, **sale_item**, **most_popular_seeds** – Merchandising flags

> **Note**: Missing values indicate that the source page omitted that attribute. This is normal and expected.

## 🔄 Data Collection & Updates

### Basic Scraping
```bash
# Scrape new data (continues from existing CSV)
python scrape_seed_city.py

# Scrape specific number of new records
python scrape_seed_city.py 50
```

### Advanced Options
```bash
# Analyze missing data patterns
python analyze_missing_data.py

# Use ML to fill missing data (fast alternative)
python ml_fill_strategy.py
```

### Configuration
The scraper includes built-in rate limiting:
- `REQUEST_PAUSE_SEC = 0.6` – Delay between catalog pages
- `DETAIL_REQUEST_PAUSE_SEC = 0.35` – Delay between detail page fetches
- `MAX_EMPTY_PAGES = 3` – Stop if no new data found

## 📈 Data Quality & Missing Values

Current dataset completeness: **47.6%**
- **sale_item**: 11.44% complete (88.56% missing)
- **discount_percent**: 11.57% complete (88.43% missing)
- **outdoor_harvest_time**: 36.74% complete (63.26% missing)
- **indoor_height_detail**: 47.24% complete (52.76% missing)
- **smell_taste**: 79.81% complete (20.19% missing)

### Strategies to Improve Completeness

1. **ML-Based Filling** (Recommended - 10-15 minutes)
   ```bash
   python ml_fill_strategy.py
   ```
   - Uses breeder patterns and strain naming conventions
   - Fills ~40% of missing data using intelligent inference

2. **Continue Web Scraping** (4+ hours)
   ```bash
   python scrape_seed_city.py --refetch
   ```
   - Fetches remaining detail pages
   - 100% accurate but time-consuming

3. **Hybrid Approach** (1-2 hours - Best Balance)
   - Run ML filling first
   - Then scrape remaining high-priority fields

## 🚀 Quick Start

### Load and Explore Data
```python
import pandas as pd

# Load the dataset
df = pd.read_csv("cannabis-strains.csv")

# Basic overview
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# View first few rows
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

## 📊 Exploratory Data Analysis

See `cannabis-strains.ipynb` for comprehensive analysis including:
- Price distributions and correlations
- Strain type analysis
- Breeder market share
- Missing data visualization
- Cultivation parameter insights

### Key Insights from Current Data
- **Price Range**: £0.00 - £999.79 GBP
- **Most Common Type**: Feminized seeds (90%+)
- **Popular Categories**: Autoflowering, Indica-dominant, High-THC strains
- **Top Breeders**: Seed City Bulk Cannabis Seeds, Cannabis Seed Sale Items, Royal Queen Seeds

## 🤖 ML Data Completion

The project includes intelligent data filling strategies:

### Breeder-Based Inference
```python
# Example: Infer strain types based on breeder patterns
breeder_patterns = df.groupby('breeder')['indica_sativa'].agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown')
```

### Name Pattern Recognition
- "Auto" strains → Autoflowering
- "Kush" strains → Indica-dominant
- "Haze" strains → Sativa-dominant
- THC/CBD ratios from descriptions

## 📤 Data Publishing

### Upload to Hugging Face
```bash
python upload_hf.py
```

### GitHub Integration
```bash
git add .
git commit -m "Update dataset with new strains"
git push origin main
```

## 🔧 Development

### Project Structure
```
cannabis-strains/
├── cannabis-strains.csv          # Main dataset
├── scrape_seed_city.py           # Web scraper
├── analyze_missing_data.py       # Data quality analysis
├── ml_fill_strategy.py           # ML-based data completion
├── upload_hf.py                  # Hugging Face uploader
├── cannabis-strains.ipynb        # Analysis notebook
├── dataset-metadata.json         # Dataset metadata
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This dataset is for educational and research purposes only. Cannabis laws vary by jurisdiction. Always comply with local regulations regarding cannabis cultivation and usage.

## 🙏 Acknowledgments

- **Data Source**: [Seed City](https://www.seed-city.com) for providing comprehensive strain information
- **Tools**: BeautifulSoup, CloudScraper, Pandas for data collection and analysis
- **Community**: Open source contributions and feedback

---

**Last Updated**: November 2025
**Dataset Version**: v1.0
**Contact**: [GitHub Issues](https://github.com/JonusNattapong/Cannabis-Strains/issues)
