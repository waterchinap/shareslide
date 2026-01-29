import akshare as ak
import pandas as pd
from pathlib import Path
from loguru import logger
import sys
import warnings
from datetime import datetime

from myslide.stock_single import StockSingleSlide, MY_CODES

warnings.filterwarnings("ignore", category=UserWarning)

logger.remove(0)
custom_format = "<green>{time:MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, format=custom_format)

TODAY = datetime.now().strftime("%Y-%m-%d")


def fetch_data() -> pd.DataFrame:
    """获取股票数据，使用缓存"""
    cache_dir = Path("cache")
    cache_file = cache_dir / f"ashare_daily_{TODAY}.csv"

    if cache_file.exists():
        logger.info(f"Cache file exists: {cache_file}")
        df = pd.read_csv(cache_file)
        return df

    try:
        df = ak.stock_zh_a_spot_em()
        logger.info(f"Data fetched successfully: {df.shape}")
        cache_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file, index=False)
        return df
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        raise


def main():
    df = fetch_data()

    cache_dir = Path.cwd() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path.cwd() / "reveal"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "stock_single.html"

    processor = StockSingleSlide(MY_CODES, df, output_file)
    processor.run()


if __name__ == "__main__":
    main()
