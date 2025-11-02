import csv
import logging
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urljoin

import cloudscraper
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://www.seed-city.com/en/list-all-products"
SITE_ROOT = "https://www.seed-city.com"
PAGE_SIZE = 30
REQUEST_PAUSE_SEC = 0.6  # be polite to the remote server
MAX_EMPTY_PAGES = 3
OUTPUT_PATH = Path("cannabis-strains.csv")


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

    return StrainRecord(
        strain_name=strain_name,
        breeder=breeder,
        description=description,
        current_price_gbp=parse_price(current_price_text),
        original_price_gbp=parse_price(original_price_text),
        discount_percent=parse_discount(discount_text),
        pack_options=" | ".join(pack_options),
        product_url=product_url,
        image_url=image_url,
    )


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


def collect_records() -> List[StrainRecord]:
    scraper = cloudscraper.create_scraper()
    records: List[StrainRecord] = []
    seen_urls: Set[str] = set()
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
            records.append(record)

        offset += PAGE_SIZE
        time.sleep(REQUEST_PAUSE_SEC)

        if offset > 10000:
            logging.info("Reached offset safeguard (10000). Ending crawl.")
            break

    return records


def write_csv(records: List[StrainRecord], path: Path) -> None:
    if not records:
        logging.warning("No records to write.")
        return

    fieldnames = list(asdict(records[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

    logging.info("Wrote %s records to %s", len(records), path.resolve())


def main() -> None:
    records = collect_records()
    write_csv(records, OUTPUT_PATH)


if __name__ == "__main__":
    main()
