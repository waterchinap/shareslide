import akshare as ak
import pandas as pd
from typing import TypedDict, Any
from bokeh.plotting import figure
from bokeh.io import export_png
from loguru import logger
from .base_process import BaseDataProcessor, Slide


class SseDaily(BaseDataProcessor):
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

    def data_process(self, clean_data) -> list[Slide]:
        """
        数据处理阶段：获取并处理数据，返回一个列表.

        :return: 列表
        """
        df = clean_data
        logger.debug(f"Data shape: {df}")

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
            img_name = self.output_src / f"{s.name}.png"
            export_png(p, filename=img_name)
            src = f"{img_name.parent.name}/{img_name.name}"
            return src

        sel = dft
        logger.info(f"{sel.columns}")
        sel: pd.DataFrame
        for label, s in sel.items():
            content = plot_bar(s)
            self.inject_data(label, content, "img")

    def run(self):
        clean_data = self.tidy_data()
        self.data_process(clean_data)
        self.add_cover_end()
        return self.slide_datas


def main():
    """主函数"""
    data = SseDaily(df_data=ak.stock_sse_summary())
    return data.run()


if __name__ == "__main__":
    main()
