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
      num_bytes: 6704078
      num_examples: 8215
  download_size: 6704078
  dataset_size: 6704078
---

# Cannabis Strains Dataset

Real-world Seed City catalogue data with both pricing metadata and rich product detail scraped via `scrape_seed_city.py`.

## Contents

- Core columns: `strain_name`, `breeder`, `description`, GBP pricing fields, `pack_options`, `product_url`, `image_url`.
- Detail sections: `overview`, `growth_and_harvest`, `experience`.
- Taxonomy & descriptors: `seed_type`, `flowering_period_type`, `indica_sativa`, `type_ratio`, `strain_type_summary`, `environment`, `strength`, `medical_strains`, `smell_taste`, `effect`, `climate`, `flavor`.
- Grow metrics: `thc`, `cbd`, `yield_indoor`, `yield_outdoor`, `height_indoor`, `height_outdoor`, `indoor_height_detail`, `indoor_flowering_time`, `outdoor_harvest_time`, `flowering_time`, `harvest_month`, `genetic_background`.
- Merchandising flags: `stock_availability`, `sale_item`, `most_popular_seeds`.

Values are already cleaned for control characters; missing fields indicate the source page omitted that attribute.

## Refresh cadence

```bash
python scrape_seed_city.py
```

This command rewrites `cannabis-strains.csv`. By default it pauses between requests; adjust `REQUEST_PAUSE_SEC` / `DETAIL_REQUEST_PAUSE_SEC` in the script if you need a slower scrape cadence.

Current snapshot (November 2025): 8,215 rows × 39 columns.

## Example usage

```python
import pandas as pd

df = pd.read_csv("cannabis-strains.csv")
df[["strain_name", "overview", "growth_and_harvest", "experience"]].head()
```
