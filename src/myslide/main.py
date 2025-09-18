from myslide.data_fetch import DataFetcher
from myslide.data_process import DataProcessor
from myslide.slide_render import SlideRender


def main():
    """主函数"""
    choice, df = DataFetcher.fetch_data()
    output_file, sections = DataProcessor(df_data=df, output_file=choice).run()
    SlideRender(sections, output_file=output_file).run()


if __name__ == "__main__":
    main()
