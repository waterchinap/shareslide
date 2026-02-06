from datetime import datetime
from loguru import logger
import pandas as pd
from pathlib import Path

from myslide import dailylib
from myslide.models import Deck

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"


# (0:序号)(1:代码)(2:名称)(3:最新价)(4:涨跌幅)(5:涨跌额)(6:成交量)(7:成交额)(8:振幅)(9:最高)(10:最低)(11:今开)(12:昨收)(13:量比)(14:换手率)(15:市盈率-动态)(16:市净率)(17:总市值)(18:流通市值)(19:涨速)(20:5分钟涨跌)(21:60日涨跌幅)(22:年初至今涨跌幅)
class SpotEmBuilder:

    def mostn(self, df: pd.DataFrame, title: str) -> list[Deck]:
        cols = ["成交额", "总市值", "净利润"]
        decks = [dailylib.get_mostn(df, title, col, 16) for col in cols]
        return decks


    def builder(self, df):
        debank_df = dailylib.de_banks(df)
        decks = [
            Deck('cover', TODAY, '每日数据'),
            dailylib.get_basic(df),
            dailylib.get_lostpct(df),
            dailylib.get_describe(df),
            *self.mostn(df, "全部"),
            *self.mostn(debank_df, "非银"),
        ]

        return decks
    
if __name__ == "__main__":
    pass
