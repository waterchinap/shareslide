import io
from loguru import logger
import pandas as pd
from datetime import datetime
from pathlib import Path
from myslide.models import DataLoader, SlidesBuilder, Deck
import requests


TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'
DATA_URL = {
    'cn399317' : f"https://www.cnindex.com.cn/sample-detail/download-history?indexcode=399317"}

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

class Cidx399317(DataLoader):

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

    
class Cidx399317Builder(SlidesBuilder):
    def __init__(self) -> None:
        
        self.chart_options : dict = {}

    def builder(self, df:pd.DataFrame) -> tuple:
        sum_table, count_table = self.table_df(df)
        all_year = self.get_sum_line(sum_table)
        decks = [
            Deck('cover', '2026-01','国证全指399317'),
            *self.list_count(df),
            self.last_year_rank(sum_table, '行业规模'),
            self.last_year_rank(sum_table/count_table, '平均规模'),
            *all_year,
            *self.top_by_indu(df)
        ]
        return (decks, str(self.chart_options))


    def table_df(self, df:pd.DataFrame) -> tuple[pd.DataFrame, ...]:

        df.columns = ['日期', '代码', '简称', '行业', '市值', '权重']
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

    def last_year_rank(self, df:pd.DataFrame,title_sufix:str) -> Deck:
        s = df.iloc[0].sort_values(ascending=False)
        option = self.hbar_plot(s.tolist(), s.index.tolist())
        title = f'{df.index[0]}{title_sufix}'
        self.chart_options[title]= option
        return Deck('chart', title, title)

    def top_by_indu(self, df:pd.DataFrame, title_sufix:str='', topn:int = 10):
        sel = df.loc[df['日期'] == '2025-12-31']
        tops = sel.sort_values(['行业','市值'], ascending=[False,False]).groupby('行业').head(10).reset_index(drop=True)
        chunks = [tops.iloc[i:i+topn] for i in range(0, len(tops), topn)]
        decks = []
        for c in chunks:
            title = f'{c['行业'].tolist()[0]}前{topn}大'
            option = self.hbar_plot(c['市值'].tolist(), c['简称'].tolist())
            self.chart_options[title] = option
            deck = Deck('chart', title, title)
            decks.append(deck)
        return decks

    def list_count(self, df:pd.DataFrame)  -> list[Deck]:
        s_count = df.groupby('日期')['代码'].count()
        # logger.info(s_count.head())
        s_diff = s_count.diff()[1:]
        options = [self.base_plot(s.index.tolist(), s.tolist(), 'bar') for s in [s_count, s_diff]]
        titles = ['上市股票总数', '新增上市股票']
        decks = []
        for title, opt in zip(titles, options):
            deck = Deck('chart', title,title)
            decks.append(deck)
            self.chart_options[title]=opt
        return decks
 

def main():
    """主函数"""
    test = Cidx399317()
    test.clean('spot_em')
    # print(cn317.df.head())    

if __name__ == "__main__":
    main()
