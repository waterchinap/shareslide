from loguru import logger
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from myslide.models import Deck, DataLoader,SlidesBuilder
import akshare as ak
import pandas as pd
import time
from tenacity import retry, stop_after_attempt


TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
DATA_URL = {
    "sw_indu": ak.sw_index_third_info,
    "sw_com": ak.sw_index_third_cons,
    "sw_second": ak.sw_index_second_info,
    "sw_first": ak.sw_index_first_info,
}

# load data from web
class SwInduLoader(DataLoader):
    @retry(stop=stop_after_attempt(3))
    def fetch_tool(self, url: str, symbol: str | None = None) -> pd.DataFrame:
        sw_cache = CACHE_DIR / "sw"
        sw_cache.mkdir(parents=True, exist_ok=True)
        cache_file = sw_cache / f"{TODAY}-{url}{symbol}.csv"
        if cache_file.exists():
            logger.info(f"{cache_file.stem} file exists: {cache_file}")
            df = pd.read_csv(cache_file)
            return df
        try:
            df = DATA_URL[url](symbol) if symbol else DATA_URL[url]()
            logger.info(f"{cache_file.stem} fetched successfully: {df.shape}")
            df.to_csv(cache_file, index=False)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise

    def fetch(self, url: str):
        cache_file = CACHE_DIR / f"sw_daily_{TODAY}.csv"

        if cache_file.exists():
            logger.info(f"{cache_file.stem} file exists: {cache_file}")
            df = pd.read_csv(cache_file)
            return df

        indu_third = self.fetch_tool(url)
        com_ls = []
        for s in tqdm(indu_third["行业代码"].tolist()):
            a_indu = self.fetch_tool('sw_com', s)
            com_ls.append(a_indu)
            time.sleep(0.5)
        df = pd.concat(com_ls, ignore_index=True)
        df.to_csv(cache_file, index=False)

        logger.info(f"{cache_file.stem}:{df.shape}")
        return df

    def clean(self, url: str):
        df = self.fetch(url)
        df.columns = [
            "序号",
            "股票代码",
            "股票简称",
            "纳入时间",
            "行业",
            "行业2",
            "行业3",
            "价格",
            "pe",
            "pettm",
            "pb",
            "股息率",
            "市值",
            "净利同增",
            "上季利增",
            "营收同增",
            "上季营增",
        ]
        sw1 = DATA_URL["sw_first"]()
        logger.info("sw1 ready")
        sw2 = DATA_URL["sw_second"]().set_index("行业名称")["上级行业"]
        sw3 = DATA_URL["sw_indu"]().set_index("行业名称")["上级行业"]
        df["行业2"] = sw3[df["行业3"]].values
        df["行业"] = sw2[df["行业2"]].values
        df.to_csv(CACHE_DIR / ("sw_clean_" + TODAY + ".csv"))
        logger.info("clean file saved")
        return [df, sw1]



# build decks
class SwInduBuilder(SlidesBuilder):
    def __init__(self) -> None:
        self.chart_options: dict = {}

    def builder(self, df: list[pd.DataFrame]) -> tuple:
        com_df, sw1 = df
        decks = [
            Deck("cover", TODAY, "申万每日行业"),
            *self.sw1(sw1),
        ]
        return (decks, str(self.chart_options))

    def sw1(self, df: pd.DataFrame) -> list[Deck]:
        # ['行业代码', '行业名称', '成份个数', '静态市盈率', 'TTM(滚动)市盈率', '市净率', '静态股息率']
        sel = df[
            [
                "行业名称",
                "成份个数",
                "静态市盈率",
                "TTM(滚动)市盈率",
                "市净率",
                "静态股息率",
            ]
        ]
        sel["PE变化"] = sel["静态市盈率"] - sel["TTM(滚动)市盈率"]
        decks = []
        for i in [
            "成份个数",
            "PE变化",
            "静态股息率",
            "静态市盈率",
            "TTM(滚动)市盈率",
            "市净率",
        ]:
            sel = sel.sort_values(i, ascending=False).reset_index(drop=True)
            decks.append(Deck("table", sel[["行业名称", "成份个数", i]], i))
        return decks

    def base_plot(self, x: list, y: list, type: str = "line") -> dict:
        return {
            "backgroundColor": "",
            "xAxis": {"type": "category", "data": x, "axisLabel": {"fontSize": 18}},
            "yAxis": {"type": "value", "axisLabel": {"fontSize": 18}},
            "series": [{"data": y, "type": type}],
        }

    def hbar_plot(self, x: list, y: list):
        option = {
            "backgroundColor": "",
            "xAxis": {"type": "value", "axisLabel": {"fontSize": 24}},
            "yAxis": {
                "type": "category",
                "data": y,
                "inverse": "true",
                "axisLabel": {"fontSize": 36},
            },
            "series": [
                {"data": x, "type": "bar"},
            ],
        }
        return option

    def get_sum_line(self, df: pd.DataFrame):
        cols = df.columns
        decks = []

        for col in cols:
            deck = Deck("chart", col, col)
            decks.append(deck)
            option = self.base_plot(df.index.tolist(), df[col].tolist())
            self.chart_options[col] = option

        return decks

    def last_year_rank(self, df: pd.DataFrame, title_sufix: str) -> Deck:
        s = df.iloc[0].sort_values(ascending=False)
        option = self.hbar_plot(s.tolist(), s.index.tolist())
        title = f"{df.index[0]}{title_sufix}"
        self.chart_options[title] = option
        return Deck("chart", title, title)

    def top_by_indu(self, df: pd.DataFrame, title_sufix: str = "", topn: int = 10):
        sel = df.loc[df["日期"] == "2025-12-31"]
        tops = (
            sel.sort_values(["行业", "市值"], ascending=[False, False])
            .groupby("行业")
            .head(10)
            .reset_index(drop=True)
        )
        chunks = [tops.iloc[i : i + topn] for i in range(0, len(tops), topn)]
        decks = []
        for c in chunks:
            title = f"{c['行业'].tolist()[0]}前{topn}大"
            option = self.hbar_plot(c["市值"].tolist(), c["简称"].tolist())
            self.chart_options[title] = option
            deck = Deck("chart", title, title)
            decks.append(deck)
        return decks

    def list_count(self, df: pd.DataFrame) -> list[Deck]:
        s_count = df.groupby("日期")["代码"].count()
        # logger.info(s_count.head())
        s_diff = s_count.diff()[1:]
        options = [
            self.base_plot(s.index.tolist(), s.tolist(), "bar")
            for s in [s_count, s_diff]
        ]
        titles = ["上市股票总数", "新增上市股票"]
        decks = []
        for title, opt in zip(titles, options):
            deck = Deck("chart", title, title)
            decks.append(deck)
            self.chart_options[title] = opt
        return decks

    
def main():
    """主函数"""
    test = SwInduLoader()
    test.clean("sw_third")
    # print(cn317.df.head())


if __name__ == "__main__":
    main()

