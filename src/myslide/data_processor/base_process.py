from abc import ABC, abstractmethod
import pandas as pd
from typing import TypedDict, Any
from pathlib import Path
from loguru import logger
from datetime import datetime


class Slide(TypedDict, total=False):
    template: str
    title: str
    content: Any


class BaseDataProcessor(ABC):
    """数据处理抽象基类，定义接口和通用实现"""

    def __init__(
        self,
        df_data: pd.DataFrame,
        output_src: Path,
        cover_title: str = "股市数据大屏展示",
    ):
        self.df = df_data
        self.output_src = output_src
        self.cover_title = cover_title
        self.date_now = datetime.now().strftime("%Y-%m-%d")
        self.slide_datas: list[Slide] = []  # 幻灯片数据列表
        logger.debug(f"Output src: {self.output_src}")

    def inject_data(self, title: str, content: Any, template: str = "content") -> None:
        """注入幻灯片数据（通用实现）"""
        slide: Slide = {"title": title, "content": content, "template": template}
        self.slide_datas.append(slide)

    def inject_dcards(self, content: Any, template: str = "dcards") -> None:
        """注入幻灯片数据（通用实现）"""
        slide: Slide = {"content": content, "template": template}
        logger.debug(slide)
        self.slide_datas.append(slide)

    def add_cover_end(self) -> None:
        """添加封面和尾页（通用实现）"""
        cover: Slide = {
            "title": self.cover_title,
            "content": f"data on:{self.date_now}",
            "template": "cover",
        }
        self.slide_datas.insert(0, cover)
        self.inject_data(
            title="Thank You", content="waterchinap@qq.com", template="cover"
        )

    def tidy_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗和整理（通用实现，子类可按需覆盖）
        返回处理后的DataFrame
        """
        df = df.copy()
        # 这里放置你的通用清洗逻辑，例如：
        # df = df.iloc[1:-3, :].set_index(df.columns[0])
        # df = df.apply(lambda x: pd.to_numeric(x, errors="coerce"))
        # df = df.dropna(axis=1, how="all")
        # df = df.dropna(axis=0, how="all")
        return df

    @abstractmethod
    def data_process(self) -> None:
        """
        抽象方法：核心数据处理逻辑，生成幻灯片内容并调用inject_data（子类必须实现）
        """
        pass

    def run(self) -> list[Slide]:
        """
        模板方法：定义执行流程（通用实现）
        1. 获取数据
        2. 整理数据
        3. 处理数据并生成幻灯片
        4. 添加封面和封底
        """
        cleaned_df = self.tidy_data(self.df)
        self.data_process(cleaned_df)  # 将清理后的数据传递给处理逻辑
        self.add_cover_end()
        return self.slide_datas
