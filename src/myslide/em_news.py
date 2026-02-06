from loguru import logger
import akshare as ak
import pandas as pd
from datetime import datetime
from pathlib import Path
from myslide.models import DataLoader, SlidesBuilder, Deck


TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'
DATA_URL = {
    'em_news':ak.stock_info_global_em,
}

class EmNewsLoader(DataLoader):
        
    def fetch(self, url:str) -> pd.DataFrame:
        cache_file = CACHE_DIR / f"{TODAY}news_em.csv"
        if cache_file.exists():
            logger.info(f"Cache file exists: {cache_file}")
            df = pd.read_csv(cache_file)
            return df
        try:
            df = DATA_URL[url]()
            logger.info(f"spot_em data fetched successfully: {df.shape}")
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(cache_file, index=False)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise

    def clean(self, url:str):
        df = self.fetch(url)
        sel = df[['标题','摘要','发布时间']]
        return sel
    

class EmNewsBuilder(SlidesBuilder):

    def builder(self, df:pd.DataFrame) -> tuple[list[Deck], str]:
        logger.info(df.columns)
        df['摘要'] = df['摘要'].str.replace(r'【[^】]*】', '', regex=True)
        decks = [
            Deck('news', t[2], t[1]) for t in df.itertuples()
        ]
        return (decks, '{}')
    

def main():
    """主函数"""
    test = EmNewsLoader()
    test.clean('spot_em')
    # print(cn317.df.head())    

if __name__ == "__main__":
    main()
