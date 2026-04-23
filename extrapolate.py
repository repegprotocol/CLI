import argparse
import json
from datetime import datetime

from core.ATAEngine import ATAEngine
from price_feeds import CMEPriceFeed, NYSEPriceFeed, iSharesPriceFeed, EuronextPriceFeed, SSEPriceFeed
from master_assets import load_all_masters

def main():
    parser = argparse.ArgumentParser(description="REPEG ATA© Asset Price Extrapolator")
    parser.add_argument("--ticker", type=str, required=True, help="Asset ticker symbol")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"[{datetime.now()}] ATA© Oracle: Extrapolating price for {ticker}")

    masters = load_all_masters()
    active_masters = list(masters.keys())

    feeds = [
        CMEPriceFeed(), NYSEPriceFeed(), iSharesPriceFeed(),
        EuronextPriceFeed(), SSEPriceFeed()
    ]

    multi_data = {}

    for feed in feeds:
        try:
            data = feed.scrape_real_time_prices()
            for sym, asset_data in data.items():
                if ticker in sym.upper() or sym.upper() in ticker:
                    multi_data[feed.get_name()] = asset_data
                    print(f"  ✓ Matched in {feed.get_name()}: {sym}")
                    break
            if feed.get_name() not in multi_data and data:
                first = next(iter(data.values()))
                multi_data[feed.get_name()] = first
        except Exception:
            pass

    result = ATAEngine.extrapolate_price(ticker, multi_data)

    print("\n" + "=" * 80)
    print("REPEG ATA© PRICE EXTRAPOLATION RESULT")
    print("=" * 80)
    print(f"Ticker                  : {result['ticker']}")
    print(f"Extrapolated Price      : {result['extrapolated_price']}")
    print(f"Human Readable          : {result['extrapolated_price'] / 1e18:.8f}")
    print(f"Confidence              : {result['confidence'] / 100:.2f}%")
    print(f"Active Master Assets    : {active_masters}")
    print(f"Sources Used            : {len(result.get('sources_used', []))}")
    print(f"Timestamp               : {result['timestamp']}")
    print("=" * 80)

    print("\nJSON for rebase contract injection:")
    print(json.dumps({
        "ticker": result["ticker"],
        "price": result["extrapolated_price"],
        "confidence": result["confidence"]
    }, indent=2))

if __name__ == "__main__":
    main()