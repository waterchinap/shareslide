import akshare as ak
import pandas as pd
from typing import TypedDict, Any
from bokeh.plotting import figure
from bokeh.io import export_png
from loguru import logger
from pathlib import Path


class Slide(TypedDict, total=False):
    template: str
    title: str
    content: Any



class DataProcessor:
    """处理股票数据并生成HTML报告的类 (遵循职责分离原则)"""

    def __init__(
        self, 
        output_file: str,
        df_data: pd.DataFrame,
        output_dir: str = "reveal",
        cover_title: str = "股市数据大屏展示"):
        """
        :param df_data: 股票数据DataFrame
        """
        self.df = df_data
        self.cover_title = cover_title
        self.output_src = Path(__file__).parent.parent.parent / output_dir / f"{output_file}"
        self.output_file = Path(__file__).resolve().parent.parent.parent / output_dir / f"{output_file}.html"
        
        self.output_src.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output src: {self.output_src}")
        self.slide_datas: list[Slide] = []

    def tidy_data(self) -> pd.DataFrame:
        """
        数据处理阶段：数据清洗、转换、处理。

        :return: 处理后的DataFrame
        """
        # 1. 获取数据
        df = self.df.copy()
        df = df.iloc[1:-3, :].set_index(df.columns[0])
        df = df.apply(lambda x: pd.to_numeric(x, errors="coerce"))

        df = df.dropna(axis=1, how="all")
        df = df.dropna(axis=0, how="all")

        return df

    def inject_data(
        self, 
        title: str,
        content: Any,
        template: str = "content",
    ):
        self.slide_datas.append(dict(title=title, content=content, template=template))

    def add_cover_end(self):
        """
        添加封面和尾页。

        :return: None
        """
        cover = dict(title=self.cover_title, content="Present by Eric", template="cover")
        self.slide_datas.insert(0, cover)
        self.inject_data(title="Thank You", content="waterchinap@qq.com", template="cover")

    def data_process(self) -> list[Slide]:
        """
        数据处理阶段：获取并处理数据，返回一个列表.

        :return: 列表
        """
        df = self.tidy_data()
        logger.debug(f"Data shape: {df}")

        # cover data
        self.inject_data(
            title="上海证券交易所数据",
            content="""
            Presented by Eric 
            """,
        )

        # 2. 处理SSE数据为表格格式 (排除首行和最后三行)
        table_data = df
        logger.debug(f"table: \n{table_data}")
        table_html = table_data.to_html()
        self.inject_data(title="上海证券交易所数据", content=table_html)

        # 3. 处理SSE数据为系列格式 (第一列作为索引)
        dft: pd.DataFrame = table_data.T
        logger.debug(f"Data shape: \n{dft}")
        logger.debug(f"Data shape: \n{dft.columns}")

        for label, s in dft.items():
            self.inject_data(title=label, content=s, template="cards")

        # 4. 处理SSE数据为柱状图格式
        def plot_bar(s):
            p = figure(
                title=s.name,
                height=50 * len(s) + 120,
                y_range=s.index.tolist(),
            )
            p.hbar(y=s.index.tolist(), right=s.values, height=0.5)
            img_name = self.output_src / f"{l}.png"
            export_png(p, filename=img_name)
            src = f"{img_name.parent.name}/{img_name.name}"
            return src

        sel = dft
        logger.info(f"{sel.columns}")
        for l, s in sel.items():
            content = plot_bar(s)
            self.inject_data(l, content, "img")

    def run(self):
        self.data_process()
        self.add_cover_end()
        return (self.output_file, self.slide_datas)


def main():
    """主函数"""
    data = DataProcessor(df_data=ak.stock_sse_summary())
    return data.run()

if __name__ == "__main__":
    main()
