import os, sys, argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper import run_scraper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Website Metadata Scraper for SEA-SEQ")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    outfile = run_scraper(args.url, args.out)
    print(f"✅ Metadata scraped and saved to {outfile}")
