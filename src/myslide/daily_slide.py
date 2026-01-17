from datetime import datetime
from loguru import logger
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from myslide import dailylib
from myslide.models import Deck

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"
# (0:序号)(1:代码)(2:名称)(3:最新价)(4:涨跌幅)(5:涨跌额)(6:成交量)(7:成交额)(8:振幅)(9:最高)(10:最低)(11:今开)(12:昨收)(13:量比)(14:换手率)(15:市盈率-动态)(16:市净率)(17:总市值)(18:流通市值)(19:涨速)(20:5分钟涨跌)(21:60日涨跌幅)(22:年初至今涨跌幅)
class DailySlide:

    def __init__(self, df:pd.DataFrame, output:Path) -> None:
        self.df: pd.DataFrame = df
        self.output: Path = output
        self.clean_df = dailylib.clean(self.df)
        self.debank_df = dailylib.de_banks(self.clean_df)

    def mostn(self, df: pd.DataFrame, title:str)-> list[Deck]:
        cols = ['成交额', '总市值', '净利润']
        decks = [dailylib.get_mostn(df, title, col) for col in cols]
        return decks


    def render_deck(self, deck: Deck):
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(f'{deck.template}.html.jinja')
        html_str = template.render(title=deck.title, content=deck.data)
        return html_str


    def render_page(self, temp_name: str, deck_html: str='page'):
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(f'{temp_name}.html.jinja')
        page_html = template.render(sections=deck_html)

        return page_html


    def run(self):
        decks = [
            dailylib.get_basic(self.clean_df),
            dailylib.get_lostpct(self.clean_df),
            dailylib.get_describe(self.clean_df),
            *self.mostn(self.clean_df, '全部'),
            *self.mostn(self.debank_df, '非银')
        ]
        deck_html = '\n'.join([self.render_deck(deck) for deck in decks])
        # logger.info(deck_html)
        page_html = self.render_page("page", deck_html)

        with open(self.output, "w") as file:
            file.write(page_html)

        logger.info("page saved")


if __name__ == "__main__":
    pass
