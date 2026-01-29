from myslide.data_fetch import DataFetcher
from myslide.daily_slide import DailySlide
from myslide.stock_slide import StockSlide
from pathlib import Path
from loguru import logger
import sys
import warnings
from datetime import datetime


today = datetime.now().strftime("%Y-%m-%d")

MY_CODES = ["300750", "600674", "600941", "600309", "002415", "688234", "601398"]


def run_daily_slide():
    """运行全市场数据幻灯片"""
    choice, df = DataFetcher.fetch_data()

    cache_dir = Path.cwd() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path.cwd() / "reveal"
    output_src = output_dir / f"{choice}"
    output_src.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{choice}.html"

    processor = DailySlide(df, output_file)
    processor.run()


def run_stock_slide():
    """运行个股展示幻灯片"""
    choice, df = DataFetcher.fetch_data()

    cache_dir = Path.cwd() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path.cwd() / "reveal"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "stock.html"

    processor = StockSlide(MY_CODES, df, output_file)
    processor.run()


def main():
    page_list = ["全市场数据幻灯片", "个股展示幻灯片"]
    for i, page in enumerate(page_list):
        print(f"{i}. {page}")

    choice = int(input("请选择功能："))

    if choice >= len(page_list):
        raise ValueError("Invalid choice")

    if choice == 0:
        run_daily_slide()
    elif choice == 1:
        run_stock_slide()


if __name__ == "__main__":
    # 移除默认处理器，以便完全控制格式
    warnings.filterwarnings("ignore", category=UserWarning)

    logger.remove(0)

    # 定义不含年份的格式字符串
    # {time:MM-DD HH:mm:ss} 表示 月-日 时:分:秒
    custom_format = "<green>{time:MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # 添加一个使用新格式的处理器
    logger.add(sys.stderr, format=custom_format)

    main()
