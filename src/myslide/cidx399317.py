from faulthandler import dump_traceback_later
import io
from loguru import logger
import akshare as ak
import pandas as pd
from datetime import datetime
from pathlib import Path
from myslide.models import DataLoader, SlidesBuilder, Deck
import requests

# 该数据源2025-12-31给出了近五年来每个月的行业和市值，但到2026-01-31就只给出单月的了。
TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'
DATA_URL = {
    'cidx399317' : f"https://www.cnindex.com.cn/sample-detail/download-history?indexcode=399317"}

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

class Cidx399317Loader(DataLoader):

    def fetch(self, url:str) -> pd.DataFrame:
        cache_file = CACHE_DIR / f'{TODAY[:8]}399317.csv'
        # 发起 GET 请求

        if cache_file.exists():
            logger.info(f"Cache file exists: {cache_file}")
            df = pd.read_csv(cache_file)
            return df
        try:
            response = requests.get(DATA_URL[url], headers=headers)
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

    def all_years(self, df:pd.DataFrame) -> pd.DataFrame:
        history = pd.read_csv(CACHE_DIR/'399317_all.csv')
        all_years = pd.concat([df, history])
        all_years = all_years.drop_duplicates()
        return all_years
    
    def clean(self, url:str):
        month_df = self.fetch(url)
        all_data = self.all_years(month_df)
        all_data.to_csv(CACHE_DIR/'399317_all.csv', index=False)
        return [month_df, all_data]

# build slide decks    
class Cidx399317Builder(SlidesBuilder):
    def __init__(self) -> None:
        
        self.chart_options : dict = {}

    def builder(self, dfs: list[pd.DataFrame]) -> tuple:
        df, all_data = dfs
        df.columns = ['日期', '代码', '简称', '行业', '市值', '权重']
        all_data.columns = ['日期', '代码', '简称', '行业', '市值', '权重']
        all_month = self.all_month(all_data)
        sum_table, count_table = self.table_df(df)
        decks = [
            Deck('cover', TODAY[:7],'国证全指399317'),
            *all_month,
            self.list_count(df),
            self.last_month_rank(sum_table, '行业规模'),
            self.last_month_rank(sum_table/count_table, '平均规模'),
            *self.top_by_indu(df)
        ]
        return (decks, str(self.chart_options))

    def all_month(self, df: pd.DataFrame):
        table_sum, _ = self.table_df(df)
        cols = table_sum.columns
        decks = []
        for col in cols:
            title = f'{col}行业市值变化'
            self.chart_options[title] = self.base_plot(table_sum.index.tolist(), table_sum[col].tolist()) 
            decks.append(Deck('chart', f'{col}行业市值变化',f'{col}行业市值变化' ))
        return decks
        

    def table_df(self, df:pd.DataFrame) -> tuple[pd.DataFrame, ...]:

        # df.columns = ['日期', '代码', '简称', '行业', '市值', '权重']
        table_sum = df.pivot_table(index='日期', columns='行业', values='市值', aggfunc='sum')
        table_count = df.pivot_table(index='日期', columns='行业', values='市值', aggfunc='count')
        return (table_sum, table_count)

    def base_plot(self, x:list, y:list, type:str = 'line') -> dict:

        return {
            'backgroundColor': '',
          'xAxis': {
            'type': 'category',
            'data': x,
            'axisLabel': {
                'fontSize': 18
            }
          },
          'yAxis': {
            'type': 'value',
            'axisLabel': {
                'fontSize': 18
            }
          },
          'series': [
            {
              'data': y,
              'type': type
            }
          ]
        }

    def hbar_plot(self, x:list, y:list):
        option = {
            'backgroundColor': '',
            'xAxis': {
                'type': 'value',
                'axisLabel': { 'fontSize': 24}
            },
            'yAxis': {
                'type': 'category',
                'data': y,
                'inverse': 'true',
                'axisLabel': { 'fontSize': 36}
            },
            'series':[
                {
                'data': x,
                'type': 'bar'
                },
            ]
        }
        return option

    def get_sum_line(self, df:pd.DataFrame) :
        cols = df.columns
        decks = []
        
        for col in cols:
            deck = Deck('chart', col, col)
            decks.append(deck)
            option = self.base_plot(df.index.tolist(), df[col].tolist())
            self.chart_options[col] = option             

        return decks

    def last_month_rank(self, df:pd.DataFrame,title_sufix:str) -> Deck:
        s = df.iloc[0].sort_values(ascending=False)
        # logger.info(s.shape)
        option = self.hbar_plot(s.tolist(), s.index.tolist())
        title = f'{df.index[0]}{title_sufix}'
        self.chart_options[title]= option
        return Deck('chart', title, title)

    def top_by_indu(self, df:pd.DataFrame, title_sufix:str='', topn:int = 10):
        tops = df.sort_values(['行业','市值'], ascending=[False,False]).groupby('行业').head(topn).reset_index(drop=True)
        chunks = [tops.iloc[i:i+topn] for i in range(0, len(tops), topn)]
        decks = []
        for c in chunks:
            title = f'{c['行业'].tolist()[0]}前{topn}大'
            option = self.hbar_plot(c['市值'].tolist(), c['简称'].tolist())
            self.chart_options[title] = option
            deck = Deck('chart', title, title)
            decks.append(deck)
        return decks

    def list_count(self, df:pd.DataFrame)  -> Deck:
        s_count = df.groupby('行业')['代码'].count().sort_values(ascending=False)
        options = self.hbar_plot(s_count.tolist(), s_count.index.tolist())
        title = '各行业上市股票总数'
        self.chart_options[title] = options
        deck = Deck('chart', title,title)
        return deck
 

def main():
    """主函数"""
    test = Cidx399317Loader()
    test.clean('cidx399317')
    # print(cn317.df.head())    

if __name__ == "__main__":
    main()
