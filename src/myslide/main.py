from pathlib import Path
from loguru import logger
import akshare as ak
import pandas as pd
from typing import TypedDict, Any, NotRequired
from myslide.slide_template import SlideTemplate


class Slide(TypedDict):
    template: NotRequired[str]
    title: str
    content: Any

DATA_URL = dict(
    em_df = ak.stock_zh_a_spot_em,
    sse_df = ak.stock_sse_summary
)

class StockDataProcessor:
    """处理股票数据并生成HTML报告的类 (遵循职责分离原则)"""

    def __init__(self, output_dir: str = "reveal"):
        """
        初始化处理器，设置模板和输出目录，并确保它们存在。

        :param template_dir: 模板目录路径
        :param output_dir: 输出目录路径
        """
        self.output_dir = Path().parent / output_dir
        self.setup_logging()
        logger.info(f"Output set to: {self.output_dir}")
        logger.info(DATA_URL.get("sse_df"))

        self.sse_df = self.fetch_data(DATA_URL.get("sse_df"))
        self.em_df = self.fetch_data(DATA_URL.get("em_df"))

    def setup_logging(self):
        """配置日志记录"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.add(log_dir / "stock_data_processor.log", rotation="1 MB", level="INFO")

    def fetch_data(self, data_url) -> pd.DataFrame:
        """
        获取股票数据，返回一个DataFrame对象。

        :return: 股票数据DataFrame
        """
        try:
            # 获取SSE数据
            sse_df = data_url()
            logger.info(f"SSE data fetched successfully: {sse_df.shape}")
            return sse_df
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")

        return sse_df

    def data_process(self) -> list[Slide]:
        """
        数据处理阶段：获取并处理数据，返回一个列表，每个元素是(模板名, 渲染所需数据字典)的元组。
        这样可以灵活地为一个数据配置不同的模板，或者为多个数据配置同一个模板。

        :return: 列表，元素为 (template_name, context_dict) 的元组
        """
        df_data_list: list[Slide] = []

        def inject_data(
            title: str,
            content: Any,
            template: str = "content",
            result: list[Slide] = df_data_list,
        ):
            result.append(dict(title=title, content=content, template=template))

        # cover data
        inject_data(
            title="上海证券交易所数据",
            content="""
            Presented by Eric 
            """,
        )

        # 2. 处理SSE数据为表格格式 (排除首行和最后三行)
        sse_df = self.sse_df.copy()
        table_data = sse_df.iloc[1:-3, :].set_index(sse_df.columns[0])
        table_html = table_data.to_html()
        inject_data(title="上海证券交易所数据", content=table_html)

        # 3. 处理SSE数据为系列格式 (第一列作为索引)
        dft: pd.DataFrame = table_data.T
        [
            inject_data(title=label, content=s, template="cards") #type: ignore
            for label, s in dft.items()
        ] # type: ignore

        return df_data_list

    def data_render(self, df_data_list: list[Slide]) -> str:
        """
        模板渲染阶段：遍历数据处理阶段生成的列表，渲染每个模板并组合结果。

        :param df_data_list: data_process方法返回的列表
        :return: 拼接好的HTML字符串
        """

        sections = [SlideTemplate.render_slide(slide) for slide in df_data_list]

        page = SlideTemplate.render_page(sections)

        return page

    def write_to_file(self, content: str, filename: str = "index.html"):
        """
        将最终的内容写入指定的文件。

        :param content: 要写入的字符串内容
        :param filename: 输出文件名
        """
        output_file = self.output_dir / filename

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"HTML file successfully generated: {output_file}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
            raise

    def run(self):
        """主运行方法，清晰的三步流程：处理数据 -> 渲染模板 -> 写入文件"""
        try:
            # 1. 数据处理
            data_to_render = self.data_process()

            # 2. 模板渲染 (渲染各个片段)
            rendered_content = self.data_render(data_to_render)

            # 3. 写入文件
            self.write_to_file(rendered_content)

            logger.success("Process completed successfully")

        except Exception as e:
            logger.error(f"Process failed: {e}")
            raise


def main():
    """主函数"""
    processor = StockDataProcessor()
    processor.run()


if __name__ == "__main__":
    main()
