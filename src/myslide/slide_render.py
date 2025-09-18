from pathlib import Path
from loguru import logger
from myslide.slide_template import SlideTemplate


class SlideRender:
    """处理股票数据并生成HTML报告的类 (遵循职责分离原则)"""

    def __init__(self, slide_string: list[str], output_file: Path):
        """
        :param output_dir: 输出目录路径
        """
        self.slide_string = slide_string
        self.output_file = output_file
        self.setup_logging()
        logger.info(f"Output set to: {self.output_file}")

    def setup_logging(self):
        """配置日志记录"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.add(log_dir / "stock_data_processor.log", rotation="1 MB", level="INFO")

    def data_render(self) -> str:
        """
        模板渲染阶段：遍历数据处理阶段生成的列表，渲染每个模板并组合结果。
        :return: 拼接好的HTML字符串
        """
        slides_data = self.slide_string
        sections = [SlideTemplate.render_slide(slide) for slide in slides_data]

        page = SlideTemplate.render_page(sections)

        return page

    def write_to_file(self, content: str, filename: str = "index.html"):
        """
        将最终的内容写入指定的文件。
        :param content: 要写入的字符串内容
        :param filename: 输出文件名
        """

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"HTML file successfully generated: {self.output_file}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
            raise

    def run(self):
        """主运行方法，渲染模板 -> 写入文件"""
        try:
            # 1. 模板渲染 (渲染各个片段)
            rendered_content = self.data_render()

            # 2. 写入文件
            self.write_to_file(rendered_content)

            logger.success("Process completed successfully")

        except Exception as e:
            logger.error(f"Process failed: {e}")
            raise


def main():
    """主函数"""
    processor = SlideRender()
    processor.run()


if __name__ == "__main__":
    main()
