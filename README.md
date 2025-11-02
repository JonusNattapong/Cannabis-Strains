# Cannabis Strains Dataset

This project provides a real-world catalogue of cannabis strain listings scraped from [Seed City](https://www.seed-city.com/en/list-all-products). The dataset is refreshed by running `scrape_seed_city.py`, which paginates the Seed City catalogue and extracts key product information for each strain.

## Fields

- **strain_name** – Product/strain title from Seed City.
- **breeder** – Seed breeder or brand associated with the listing.
- **description** – Short marketing description captured from the browse page.
- **current_price_gbp** – Current single-seed price (GBP) when available.
- **original_price_gbp** – Original list price prior to any discount (GBP).
- **discount_percent** – Percentage discount advertised on the listing.
- **pack_options** – Pack size and GBP pricing options as shown on the listing.
- **product_url** – Direct link to the product detail page on Seed City.
- **image_url** – Thumbnail image URL for the product.

> Note: Some fields may be empty when Seed City omits that information on the listing page.

## Refreshing the dataset

```console
python scrape_seed_city.py
```

The script writes the updated dataset to `cannabis-strains.csv`. It uses `cloudscraper` to bypass Cloudflare protection and includes a small delay between requests to remain polite.

## Quick start

```python
import pandas as pd

df = pd.read_csv("cannabis-strains.csv")
df.head()
```

See `cannabis-strains.ipynb` for a quick exploratory preview of the dataset.
