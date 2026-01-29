import io
from loguru import logger
import akshare as ak
import pandas as pd
from datetime import datetime
from pathlib import Path
from myslide.interfaces import DataLoader
import requests


TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'
DATA_URL = {
    'spot_em': ak.stock_zh_a_spot_em,
    'sse_daily': ak.stock_sse_summary,
    'news_em':ak.stock_info_global_em,
    'cn399317' : 
f"https://www.cnindex.com.cn/sample-detail/download-history?indexcode=399317"}

url = f"https://www.cnindex.com.cn/sample-detail/download-history?indexcode=399317"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Referer": f"https://www.cnindex.com.cn/module/index-detail.html?act_menu=1&indexCode=399317",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

class NewsEm(DataLoader):
        
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
    
    
class SpotEm(DataLoader):
        
    def fetch(self, url:str) -> pd.DataFrame:
        cache_file = CACHE_DIR / f"{TODAY}_spot_em.csv"
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

    def clean(self, url: str) -> pd.DataFrame:
        df = self.fetch(url)
        df_clean = df.dropna(how="any").copy()
        df_clean.iloc[:, 7] = df_clean.iloc[:, 7] / 1e8
        df_clean.iloc[:, 17] = df_clean.iloc[:, 17] / 1e8
        df_clean.iloc[:, 0] = 1
        df_clean["净利润"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 15]
        df_clean["净资产"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 16]
        df_clean["净利排名"] = df_clean["净利润"].rank(ascending=False)
        df_clean["p_tier"] = (
            df_clean["净利润"].rank(ascending=False, pct=True) * 100
        ).round(3)
        df_clean["市值排名"] = df_clean.iloc[:, 17].rank(ascending=False)
        df_clean["mv_tier"] = (
            df_clean.iloc[:, 17].rank(ascending=False, pct=True) * 100
        ).round(3)

        df_clean = df_clean.rename(columns={"市盈率-动态": "市盈率"})

        return df_clean

class Cn399317(DataLoader):

    def fetch(self, url:str) -> pd.DataFrame:
        cache_file = CACHE_DIR / f'{TODAY[:8]}399317.csv'
        # 发起 GET 请求

        if cache_file.exists():
            logger.info(f"Cache file exists: {cache_file}")
            df = pd.read_csv(cache_file)
            return df
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 如果状态码不是 2xx，抛出异常
            excel_data = io.BytesIO(response.content)
            df = pd.read_excel(excel_data, engine='openpyxl')
            logger.info(f"spot_em data fetched successfully: {df.shape}")
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(cache_file, index=False)
            logger.info(f"文件已成功下载并保存为：{cache_file}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise

    def clean(self, url:str):
        df = self.fetch(url)
        df.columns = ['日期', '代码', '简称', '行业', '市值', '权重']
        table_sum = df.pivot_table(index='日期', columns='行业', values='市值', aggfunc='sum')
        table_count = df.pivot_table(index='日期', columns='行业', values='市值', aggfunc='count')
        return (table_sum, table_count)


def main():
    """主函数"""
    test = SpotEm()
    test.clean('spot_em')
    # print(cn317.df.head())    

if __name__ == "__main__":
    main()
