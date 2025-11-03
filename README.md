# Cannabis Strains Dataset

This project provides a real-world catalogue of cannabis strain listings scraped from [Seed City](https://www.seed-city.com/en/list-all-products). Run `scrape_seed_city.py` to paginate the catalogue, bypass Cloudflare via `cloudscraper`, and extract fresh strain details.

## Fields

Core listing data:
- **strain_name** – Product/strain title from Seed City.
- **breeder** – Brand or breeder responsible for the listing.
- **description** – Short marketing excerpt from the browse page.
- **current_price_gbp**, **original_price_gbp**, **discount_percent** – GBP pricing metadata.
- **pack_options** – Pack sizes and GBP prices surfaced in the dropdown.
- **product_url**, **image_url** – Direct product and thumbnail links.

Detail page extras:
- **overview**, **growth_and_harvest**, **experience** – Narrative sections scraped from the detail page when available.
- **seed_type**, **flowering_period_type**, **indica_sativa**, **type_ratio**, **strain_type_summary** – Taxonomy tags.
- **environment**, **strength**, **medical_strains**, **smell_taste**, **effect**, **climate**, **flavor** – Qualitative descriptors.
- **thc**, **cbd**, **yield_indoor**, **yield_outdoor**, **height_indoor**, **height_outdoor**, **indoor_height_detail** – Grow metrics and plant stature.
- **indoor_flowering_time**, **outdoor_harvest_time**, **flowering_time**, **harvest_month**, **genetic_background** – Cultivation timelines and lineage.
- **stock_availability**, **sale_item**, **most_popular_seeds** – Merchandising flags taken from Seed City tables.

> Missing values simply indicate the source page omitted that attribute.

## Refreshing the dataset

```console
python scrape_seed_city.py
```

The script writes the updated dataset to `cannabis-strains.csv`. It already includes gentle delays between requests; if you rerun it frequently, consider increasing `REQUEST_PAUSE_SEC` (main catalogue) and `DETAIL_REQUEST_PAUSE_SEC` (product pages).

On the current scrape (November 2025) the dataset contains 8,215 rows and 39 columns.

## Quick start

```python
import pandas as pd

df = pd.read_csv("cannabis-strains.csv")
df.head()
```

See `cannabis-strains.ipynb` for a quick exploratory preview of the dataset.
