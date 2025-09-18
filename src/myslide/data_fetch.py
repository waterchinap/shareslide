from loguru import logger
import akshare as ak
import pandas as pd


class DataFetcher:
    """fetch data"""

    DATA_URL = dict(
    ashare_daily=ak.stock_zh_a_spot_em, sse_daily=ak.stock_sse_summary)
    
    @classmethod
    def fetch_data(cls) -> (str, pd.DataFrame):
        """
        获取股票数据，返回一个DataFrame对象。

        :return: 股票数据DataFrame
        """
        page_list = list(cls.DATA_URL.keys())
        for i, page in enumerate(page_list):
            print(f"{i}. {page}")

        choice = int(input("请选择数据源："))

        if choice >= len(page_list):
            raise ValueError("Invalid choice")
            
        data_key = page_list[choice]

        try:
            df = cls.DATA_URL.get(data_key)()
            logger.info(f"SSE data fetched successfully: {df.shape}")
            return (data_key, df)
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")

def main():
    """主函数"""
    DataFetcher.fetch_data()


if __name__ == "__main__":
    main()
