from myslide.data_fetch import DataFetcher
from myslide.daily_slide import DailySlide
from pathlib import Path
from loguru import logger
import sys
import warnings
from datetime import datetime


today = datetime.now().strftime("%Y-%m-%d")


def main():
    """主函数"""

    # fetch data
    choice, df = DataFetcher.fetch_data()

    # setup
    cache_dir = Path.cwd() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path.cwd() / "reveal"
    output_src = output_dir / f"{choice}"
    output_src.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{choice}.html"

    # prepare data
    processor = DailySlide(df, output_file)
    processor.run()


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
