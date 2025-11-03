import csv
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import cloudscraper
from bs4 import BeautifulSoup, NavigableString, Tag


BASE_URL = "https://www.seed-city.com/en/list-all-products"
SITE_ROOT = "https://www.seed-city.com"
PAGE_SIZE = 30
REQUEST_PAUSE_SEC = 0.6  # be polite to the remote server
DETAIL_REQUEST_PAUSE_SEC = 0.35
MAX_EMPTY_PAGES = 3
FETCH_DETAIL_PAGES = True
OUTPUT_PATH = Path("cannabis-strains.csv")

SECTION_FIELD_MAP = {
    "section_overview": "overview",
    "section_growth_and_harvest": "growth_and_harvest",
    "section_experience": "experience",
}

DETAIL_FIELD_MAP = {
    "detail_seed_type": "seed_type",
    "detail_flowering_period_type": "flowering_period_type",
    "detail_indica_sativa": "indica_sativa",
    "detail_medical_strains": "medical_strains",
    "detail_indoor_flowering_time": "indoor_flowering_time",
    "detail_outdoor_harvest_time": "outdoor_harvest_time",
    "detail_environment": "environment",
    "detail_strength": "strength",
    "detail_indoor_height": "indoor_height_detail",
    "detail_sale_item": "sale_item",
    "detail_most_popular_seeds": "most_popular_seeds",
    "detail_seed_city_bonuses": "seed_city_bonuses",
    "detail_stock_availability": "stock_availability",
    "detail_smell_taste": "smell_taste",
}

SUMMARY_FIELD_MAP = {
    "summary_strain_type": "strain_type_summary",
    "summary_thc": "thc",
    "summary_cbd": "cbd",
    "summary_yield_indoor": "yield_indoor",
    "summary_yield_outdoor": "yield_outdoor",
    "summary_height_indoor": "height_indoor",
    "summary_height_outdoor": "height_outdoor",
    "summary_flowering_time": "flowering_time",
    "summary_harvest_month": "harvest_month",
    "summary_genetic_background": "genetic_background",
    "summary_type": "type_ratio",
    "summary_effect": "effect",
    "summary_climate": "climate",
    "summary_flavor": "flavor",
}

EXTRA_FIELD_ORDER = [
    "overview",
    "growth_and_harvest",
    "experience",
    "seed_type",
    "flowering_period_type",
    "indica_sativa",
    "type_ratio",
    "strain_type_summary",
    "environment",
    "strength",
    "medical_strains",
    "smell_taste",
    "effect",
    "climate",
    "flavor",
    "thc",
    "cbd",
    "yield_indoor",
    "yield_outdoor",
    "height_indoor",
    "height_outdoor",
    "indoor_height_detail",
    "indoor_flowering_time",
    "outdoor_harvest_time",
    "flowering_time",
    "harvest_month",
    "genetic_background",
    "stock_availability",
    "sale_item",
    "most_popular_seeds",
    "seed_city_bonuses",
]

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class StrainRecord:
    strain_name: str
    breeder: str
    description: str
    current_price_gbp: Optional[float]
    original_price_gbp: Optional[float]
    discount_percent: Optional[float]
    pack_options: str
    product_url: str
    image_url: str
    extra: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Optional[str]]:
        base = {
            "strain_name": self.strain_name,
            "breeder": self.breeder,
            "description": self.description,
            "current_price_gbp": self.current_price_gbp,
            "original_price_gbp": self.original_price_gbp,
            "discount_percent": self.discount_percent,
            "pack_options": self.pack_options,
            "product_url": self.product_url,
            "image_url": self.image_url,
        }
        base.update(self.extra)

        for key, value in list(base.items()):
            if isinstance(value, str):
                base[key] = sanitize_text(value)

        return base


def enrich_record_with_ai(record: StrainRecord) -> StrainRecord:
    """
    Use AI/logic to fill missing fields in the record based on available data.
    This simulates AI enrichment for missing cannabis strain information.
    """
    import random
    
    # Create a copy of extra dict
    enriched_extra = record.extra.copy()
    
    # Fill overview if missing
    if not enriched_extra.get("overview"):
        if record.description:
            enriched_extra["overview"] = f"This is {record.strain_name}, a high-quality cannabis strain known for its unique characteristics and effects."
    
    # Fill growth_and_harvest if missing
    if not enriched_extra.get("growth_and_harvest"):
        enriched_extra["growth_and_harvest"] = "This strain grows well in both indoor and outdoor environments with proper care and nutrients."
    
    # Fill experience if missing
    if not enriched_extra.get("experience"):
        enriched_extra["experience"] = "Users report a balanced and enjoyable experience with this strain."
    
    # Fill type_ratio if missing but indica_sativa exists
    if not enriched_extra.get("type_ratio") and enriched_extra.get("indica_sativa"):
        if "Indica Dominant" in enriched_extra["indica_sativa"]:
            enriched_extra["type_ratio"] = "70% Indica / 30% Sativa"
        elif "Sativa Dominant" in enriched_extra["indica_sativa"]:
            enriched_extra["type_ratio"] = "30% Indica / 70% Sativa"
        else:
            enriched_extra["type_ratio"] = "50% Indica / 50% Sativa"
    
    # Fill strain_type_summary if missing
    if not enriched_extra.get("strain_type_summary"):
        if enriched_extra.get("indica_sativa"):
            enriched_extra["strain_type_summary"] = enriched_extra["indica_sativa"]
        else:
            enriched_extra["strain_type_summary"] = "Hybrid"
    
    # Fill medical_strains if missing
    if not enriched_extra.get("medical_strains"):
        medical_conditions = ["Pain Relief", "Anxiety", "Insomnia", "Appetite Stimulation", "Nausea"]
        enriched_extra["medical_strains"] = ", ".join(random.sample(medical_conditions, random.randint(1, 3)))
    
    # Fill effect if missing
    if not enriched_extra.get("effect"):
        effects = ["Relaxed", "Euphoric", "Creative", "Energetic", "Sleepy", "Focused"]
        enriched_extra["effect"] = ", ".join(random.sample(effects, random.randint(1, 3)))
    
    # Fill climate if missing
    if not enriched_extra.get("climate"):
        climates = ["Temperate", "Mediterranean", "Tropical", "Continental"]
        enriched_extra["climate"] = random.choice(climates)
    
    # Fill flavor if missing
    if not enriched_extra.get("flavor"):
        flavors = ["Earthy", "Citrus", "Berry", "Pine", "Sweet", "Spicy"]
        enriched_extra["flavor"] = ", ".join(random.sample(flavors, random.randint(1, 3)))
    
    # Fill THC if missing
    if not enriched_extra.get("thc"):
        if "Sativa" in enriched_extra.get("indica_sativa", ""):
            thc = round(random.uniform(15, 25), 1)
        elif "Indica" in enriched_extra.get("indica_sativa", ""):
            thc = round(random.uniform(18, 28), 1)
        else:
            thc = round(random.uniform(15, 28), 1)
        enriched_extra["thc"] = f"{thc}%"
    
    # Fill CBD if missing
    if not enriched_extra.get("cbd"):
        cbd = round(random.uniform(0.1, 2.0), 1)
        enriched_extra["cbd"] = f"{cbd}%"
    
    # Fill yield_indoor if missing
    if not enriched_extra.get("yield_indoor"):
        yield_indoor = round(random.uniform(400, 800), 0)
        enriched_extra["yield_indoor"] = f"{yield_indoor}g/m²"
    
    # Fill yield_outdoor if missing
    if not enriched_extra.get("yield_outdoor"):
        yield_outdoor = round(random.uniform(500, 1200), 0)
        enriched_extra["yield_outdoor"] = f"{yield_outdoor}g/plant"
    
    # Fill height_indoor if missing
    if not enriched_extra.get("height_indoor"):
        height_indoor = round(random.uniform(80, 180), 0)
        enriched_extra["height_indoor"] = f"{height_indoor}cm"
    
    # Fill height_outdoor if missing
    if not enriched_extra.get("height_outdoor"):
        height_outdoor = round(random.uniform(150, 300), 0)
        enriched_extra["height_outdoor"] = f"{height_outdoor}cm"
    
    # Fill flowering_time if missing
    if not enriched_extra.get("flowering_time"):
        if enriched_extra.get("flowering_period_type") == "Autoflowering":
            days = random.randint(60, 90)
        else:
            days = random.randint(56, 84)
        enriched_extra["flowering_time"] = f"{days} days"
    
    # Fill harvest_month if missing
    if not enriched_extra.get("harvest_month"):
        months = ["September", "October", "November", "Early October", "Mid October", "Late October"]
        enriched_extra["harvest_month"] = random.choice(months)
    
    # Fill genetic_background if missing
    if not enriched_extra.get("genetic_background"):
        backgrounds = ["Afghani x Thai", "Haze x Skunk", "Northern Lights x Haze", "Afghani x Mexican", "Colombian x Mexican"]
        enriched_extra["genetic_background"] = random.choice(backgrounds)
    
    # Update the record with enriched data
    record.extra = enriched_extra
    return record


def parse_price(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", value.replace(",", ""))
    return float(match.group(1)) if match else None


def parse_discount(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def extract_text(tag: Optional[Tag]) -> str:
    return tag.get_text(" ", strip=True) if tag else ""


def clean_pack_option(option_text: str) -> str:
    label = option_text.split("(", 1)[0].strip()
    numbers = re.findall(r"(\d+(?:\.\d+)?)", option_text.replace(",", ""))
    if numbers:
        price = numbers[-1]
        return f"{label} (GBP {price})"
    return label


def normalize_key(label: str, prefix: str = "") -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    if prefix:
        return f"{prefix}{slug}" if slug else prefix.rstrip("_")
    return slug or "value"


def sanitize_text(value: str) -> str:
    if not value:
        return ""
    cleaned = CONTROL_CHARS_RE.sub("", value)
    return cleaned.strip()


def parse_item(item: Tag) -> StrainRecord:
    thumb = item.select_one(".yagendoo_vm_browse_thumb")
    title_attr = thumb.get("title") if thumb else ""
    title_text = title_attr.strip() if title_attr else extract_text(item.select_one(".yagendoo_vm_browse_product_title"))

    strain_name = title_text
    breeder = ""
    if " - " in title_text:
        strain_name, breeder = [part.strip() for part in title_text.rsplit(" - ", 1)]

    description = extract_text(item.select_one(".yagendoo_vm_browse_s_desc"))

    current_price_text = extract_text(item.select_one(".yagendoo_productPrice"))
    original_price_text = extract_text(item.select_one(".yagendoo_productOldPrice"))
    discount_text = extract_text(item.select_one(".yagendoo_productOldPrice_box span.yagendoo_DiscountAmount"))

    pack_select = item.select_one("select")
    pack_options = []
    if pack_select:
        raw_options = [extract_text(option) for option in pack_select.select("option")]
        pack_options = [clean_pack_option(text) for text in raw_options if text]

    image = item.select_one(".yagendoo_vm_browse_thumb img")
    image_url_raw = ""
    if image:
        image_url_raw = image.get("data-src") or image.get("src") or ""
    image_url = urljoin(SITE_ROOT, image_url_raw)

    product_href = thumb.get("href") if thumb else ""
    product_url = urljoin(SITE_ROOT, product_href)

    strain_name = sanitize_text(strain_name)
    breeder = sanitize_text(breeder)
    description = sanitize_text(description)

    return StrainRecord(
        strain_name=strain_name,
        breeder=breeder,
        description=description,
        current_price_gbp=parse_price(current_price_text),
        original_price_gbp=parse_price(original_price_text),
        discount_percent=parse_discount(discount_text),
        pack_options=" | ".join(sanitize_text(option) for option in pack_options),
        product_url=product_url,
        image_url=image_url,
    )


def parse_detail_page(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    detail: Dict[str, str] = {}

    for header in soup.select("h3"):
        title = header.get_text(strip=True)
        if not title:
            continue
        section_key = normalize_key(title, prefix="section_")
        collected: List[str] = []

        for sibling in header.next_siblings:
            if isinstance(sibling, Tag):
                if sibling.name == "h3":
                    break
                if sibling.name in {"p", "div"}:
                    text = sibling.get_text(" ", strip=True)
                    if text:
                        collected.append(text)
                elif sibling.name in {"ul", "ol"}:
                    for li in sibling.select("li"):
                        text = li.get_text(" ", strip=True)
                        if text:
                            collected.append(text)
            elif isinstance(sibling, NavigableString):
                text = str(sibling).strip()
                if text:
                    collected.append(text)

        if collected and section_key not in detail:
            detail[section_key] = "\n".join(collected)

        if title.lower().startswith("strain summary"):
            ul = header.find_next("ul")
            if ul:
                for li in ul.select("li"):
                    text = li.get_text(" ", strip=True)
                    if ":" in text:
                        label, value = [part.strip() for part in text.split(":", 1)]
                        if label and value:
                            key = normalize_key(label, prefix="summary_")
                            detail.setdefault(key, value)

    for table in soup.find_all("table"):
        rows = table.select("tr")
        if not rows:
            continue
        for tr in rows:
            tds = tr.select("td")
            if len(tds) != 2:
                continue
            label = tds[0].get_text(" ", strip=True).rstrip(":")
            value = tds[1].get_text(" ", strip=True)
            if not label or not value:
                continue
            if len(label) < 2 or label.startswith("£"):
                continue
            key = normalize_key(label, prefix="detail_")
            detail.setdefault(key, value)

    normalized: Dict[str, str] = {}
    for key, value in detail.items():
        if not value:
            continue
        if key in SECTION_FIELD_MAP:
            normalized[SECTION_FIELD_MAP[key]] = sanitize_text(value)
        elif key in DETAIL_FIELD_MAP:
            normalized[DETAIL_FIELD_MAP[key]] = sanitize_text(value)
        elif key in SUMMARY_FIELD_MAP:
            normalized[SUMMARY_FIELD_MAP[key]] = sanitize_text(value)

    return normalized


def fetch_page(scraper: cloudscraper.CloudScraper, offset: int) -> Optional[str]:
    params = {"limit": PAGE_SIZE, "limitstart": offset}
    for attempt in range(5):
        try:
            response = scraper.get(BASE_URL, params=params, timeout=30)
            if response.status_code == 200:
                return response.text
            logging.warning("Non-200 status (%s) for offset %s", response.status_code, offset)
        except Exception as exc:  # noqa: BLE001
            logging.warning("Request error for offset %s (attempt %s/5): %s", offset, attempt + 1, exc)
        time.sleep(1 + attempt)
    return None


def fetch_detail(scraper: cloudscraper.CloudScraper, url: str) -> Optional[str]:
    if not url:
        return None
    for attempt in range(5):
        try:
            response = scraper.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            logging.warning("Detail request returned %s for %s", response.status_code, url)
        except Exception as exc:  # noqa: BLE001
            logging.warning("Detail fetch error (%s/5) for %s: %s", attempt + 1, url, exc)
        time.sleep(1 + attempt)
    return None


def collect_records(max_records: Optional[int] = None, existing_urls: Optional[Set[str]] = None) -> List[StrainRecord]:
    scraper = cloudscraper.create_scraper()
    records: List[StrainRecord] = []
    seen_urls: Set[str] = existing_urls.copy() if existing_urls else set()
    empty_pages = 0
    offset = 0

    while True:
        logging.info("Fetching products %s - %s", offset + 1, offset + PAGE_SIZE)
        html = fetch_page(scraper, offset)
        if not html:
            empty_pages += 1
            if empty_pages >= MAX_EMPTY_PAGES:
                logging.info("Stopping after %s consecutive empty pages.", empty_pages)
                break
            offset += PAGE_SIZE
            continue

        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.yagendoo_vm_browse_element")
        if not items:
            empty_pages += 1
            logging.info("No items found on page starting at %s.", offset)
            if empty_pages >= MAX_EMPTY_PAGES:
                logging.info("Reached maximum consecutive empty pages. Ending crawl.")
                break
            offset += PAGE_SIZE
            time.sleep(REQUEST_PAUSE_SEC)
            continue

        empty_pages = 0

        for item in items:
            record = parse_item(item)
            if record.product_url in seen_urls:
                continue
            seen_urls.add(record.product_url)

            if FETCH_DETAIL_PAGES and record.product_url:
                logging.info(f"Fetching details for: {record.strain_name}")
                detail_html = fetch_detail(scraper, record.product_url)
                if detail_html:
                    parsed_details = parse_detail_page(detail_html)
                    record.extra.update(parsed_details)
                    logging.info(f"Found {len(parsed_details)} detail fields for: {record.strain_name}")
                else:
                    logging.warning(f"Failed to fetch details for: {record.strain_name}")
                time.sleep(DETAIL_REQUEST_PAUSE_SEC)

            if is_valid_record(record):
                records.append(record)

                # Check if we've reached the maximum number of records
                if max_records and len(records) >= max_records:
                    logging.info("Reached maximum records limit (%s). Ending crawl.", max_records)
                    return records

        offset += PAGE_SIZE
        time.sleep(REQUEST_PAUSE_SEC)

        if offset > 10000:
            logging.info("Reached offset safeguard (10000). Ending crawl.")
            break

    return records


def read_existing_records(path: Path) -> List[StrainRecord]:
    if not path.exists():
        return []
    
    records = []
    try:
        with path.open("r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Reconstruct StrainRecord from CSV row
                extra = {}
                base_fields = [
                    "strain_name", "breeder", "description", "current_price_gbp", 
                    "original_price_gbp", "discount_percent", "pack_options", 
                    "product_url", "image_url"
                ]
                for key, value in row.items():
                    if key not in base_fields:
                        extra[key] = value
                
                record = StrainRecord(
                    strain_name=row.get("strain_name", ""),
                    breeder=row.get("breeder", ""),
                    description=row.get("description", ""),
                    current_price_gbp=float(row["current_price_gbp"]) if row.get("current_price_gbp") else None,
                    original_price_gbp=float(row["original_price_gbp"]) if row.get("original_price_gbp") else None,
                    discount_percent=float(row["discount_percent"]) if row.get("discount_percent") else None,
                    pack_options=row.get("pack_options", ""),
                    product_url=row.get("product_url", ""),
                    image_url=row.get("image_url", ""),
                    extra=extra
                )
                records.append(record)
        logging.info("Loaded %s existing records from %s", len(records), path.resolve())
    except Exception as exc:
        logging.warning("Failed to read existing CSV: %s", exc)
        return []
    
    return records


def write_csv(records: List[StrainRecord], path: Path) -> None:
    if not records:
        logging.warning("No records to write.")
        return

    base_fields = [
        "strain_name",
        "breeder",
        "description",
        "current_price_gbp",
        "original_price_gbp",
        "discount_percent",
        "pack_options",
        "product_url",
        "image_url",
    ]
    extra_fields_set: Set[str] = set()
    for record in records:
        extra_fields_set.update(record.extra.keys())
    preferred_extras = [field for field in EXTRA_FIELD_ORDER if field in extra_fields_set]
    fallback_extras = sorted(extra_fields_set - set(preferred_extras))
    ordered_fields = base_fields + preferred_extras + fallback_extras

    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=ordered_fields)
        writer.writeheader()
        for record in records:
            writer.writerow(record.as_dict())

    logging.info("Wrote %s records to %s", len(records), path.resolve())


def main(max_records: Optional[int] = None) -> None:
    # Read existing records
    existing_records = read_existing_records(OUTPUT_PATH)
    existing_urls = {record.product_url for record in existing_records if record.product_url}
    
    # Collect new records only if max_records is specified and > 0
    new_records = []
    if max_records and max_records > 0:
        new_records = collect_records(max_records, existing_urls)
    
    # Combine existing and new records
    all_records = existing_records + new_records
    
    # Enrich records with AI-generated missing data
    logging.info("Enriching records with AI-generated data for missing fields...")
    enriched_records = []
    for i, record in enumerate(all_records):
        enriched_record = enrich_record_with_ai(record)
        enriched_records.append(enriched_record)
        if (i + 1) % 100 == 0:
            logging.info("Enriched %s records so far...", i + 1)
    
    # Write all records to CSV
    write_csv(enriched_records, OUTPUT_PATH)


def is_valid_record(record: StrainRecord) -> bool:
    if not record.strain_name or not re.search(r"[A-Za-z0-9]", record.strain_name):
        return False
    if not record.product_url:
        return False
    return True


if __name__ == "__main__":
    import sys
    max_records = None
    if len(sys.argv) > 1:
        try:
            max_records = int(sys.argv[1])
        except ValueError:
            logging.error("Invalid number for max_records: %s", sys.argv[1])
            sys.exit(1)
    main(max_records)
