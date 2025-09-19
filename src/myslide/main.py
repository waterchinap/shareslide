from myslide.data_fetch import DataFetcher
from myslide.data_process import DataProcessor
from myslide.slide_render import SlideRender
from pathlib import Path
from loguru import logger
import sys
import importlib
import warnings
from datetime import datetime


today = datetime.now().strftime("%Y-%m-%d")


warnings.filterwarnings("ignore", category=UserWarning)


def snake_2_camel(snake_str: str) -> str:
    """
    将下划线命名的字符串转换为驼峰命名字符串

    参数:
        snake_str: 下划线分隔的字符串，如 'hello_world'

    返回:
        驼峰命名字符串，如 'HelloWorld'
    """
    # 按下划线分割字符串
    parts = snake_str.split("_")
    # 将每个部分的首字母大写后拼接，空部分会被忽略
    return "".join(part.capitalize() for part in parts if part)


def get_processor(choice: str) -> DataProcessor:
    """获取数据处理器"""
    module_name = f"myslide.data_processor.{choice}"
    class_name = snake_2_camel(choice)
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_


def main():
    """主函数"""

    cache_dir = Path(__file__).parent.parent.parent / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    output_dir = Path(__file__).parent.parent.parent / "reveal"

    choice, df = DataFetcher.fetch_data()

    output_src = output_dir / f"{choice}"
    output_src.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{choice}.html"

    data_processor = get_processor(choice)

    sections = data_processor(df_data=df, output_src=output_src).run()
    SlideRender(sections, output_file=output_file).run()


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
