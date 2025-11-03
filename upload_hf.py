#!/usr/bin/env python3
"""
Upload Cannabis Strains dataset to Hugging Face Hub
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, login

def main():
    # Get token from user
    token = input("Enter your Hugging Face token: ").strip()
    if not token:
        print("No token provided. Exiting.")
        return

    # Login to HF
    login(token)

    # Initialize API
    api = HfApi()

    # Dataset info
    repo_name = "cannabis-strains-dataset"
    repo_id = f"jonusnattapong/{repo_name}"

    # Create repository
    print(f"Creating repository: {repo_id}")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=False,
        exist_ok=True
    )

    # Files to upload
    files_to_upload = [
        "cannabis-strains.csv",
        "README_HF.md",
        "dataset-metadata.json",
        "scrape_seed_city.py",
        "cannabis-strains.ipynb"
    ]

    # Upload files
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            print(f"Uploading {file_path}...")
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=file_path,
                repo_id=repo_id,
                repo_type="dataset"
            )
        else:
            print(f"File {file_path} not found, skipping...")

    print(f"\nDataset uploaded successfully!")
    print(f"View at: https://huggingface.co/datasets/{repo_id}")

if __name__ == "__main__":
    main()
