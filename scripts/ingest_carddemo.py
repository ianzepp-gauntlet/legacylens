#!/usr/bin/env python3
"""One-shot ingestion runner for CardDemo codebase."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from legacylens.config import settings
from legacylens.ingest import ingest_codebase
from legacylens.vectorstore import delete_namespace


def main():
    carddemo_path = settings.carddemo_path
    if not carddemo_path:
        print("Error: CARDDEMO_PATH not set in .env")
        print("Set it to the path of the CardDemo app/ directory")
        sys.exit(1)

    if not Path(carddemo_path).is_dir():
        print(f"Error: {carddemo_path} is not a directory")
        sys.exit(1)

    print(f"CardDemo path: {carddemo_path}")
    print(f"Pinecone index: {settings.pinecone_index_name}")
    print(f"Namespace: {settings.pinecone_namespace}")
    print()

    # Ask before clearing
    if "--clean" in sys.argv:
        print("Clearing existing namespace...")
        delete_namespace()
        print("Done.\n")

    result = ingest_codebase(carddemo_path, verbose=True)
    print(f"\nIngestion complete: {result['files']} files, "
          f"{result['chunks']} chunks, {result['vectors']} vectors")


if __name__ == "__main__":
    main()
