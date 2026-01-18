from datetime import datetime
from loguru import logger
import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from myslide import dailylib
from myslide.models import Deck

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"


# (0:序号)(1:代码)(2:名称)(3:最新价)(4:涨跌幅)(5:涨跌额)(6:成交量)(7:成交额)(8:振幅)(9:最高)(10:最低)(11:今开)(12:昨收)(13:量比)(14:换手率)(15:市盈率-动态)(16:市净率)(17:总市值)(18:流通市值)(19:涨速)(20:5分钟涨跌)(21:60日涨跌幅)(22:年初至今涨跌幅)
class DailySlide:
    def __init__(self, df: pd.DataFrame, output: Path) -> None:
        self.df: pd.DataFrame = df
        self.output: Path = output
        self.clean_df = dailylib.clean(self.df)
        self.debank_df = dailylib.de_banks(self.clean_df)
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def prepare_chart_df(self) -> dict:
        top_debank = self.debank_df[["名称", "净利润"]].nlargest(10, "净利润")
        top10_by_mv = self.clean_df[["名称", "总市值"]].nlargest(10, "总市值")
        top10_by_pe = self.clean_df[self.clean_df["市盈率-动态"] > 0][
            ["名称", "市盈率-动态"]
        ].nsmallest(10, "市盈率-动态")
        top10_by_gain = self.clean_df.nlargest(10, "涨跌幅")[["名称", "涨跌幅"]]
        return {
            "top10_debank": {"title": "净利润前10非银公司", "df": top_debank},
            "top10_by_mv": {"title": "市值前10", "df": top10_by_mv},
            "top10_by_pe": {"title": "低PE前10", "df": top10_by_pe},
            "top10_by_gain": {"title": "涨幅前10", "df": top10_by_gain},
        }

    def mostn(self, df: pd.DataFrame, title: str) -> list[Deck]:
        cols = ["成交额", "总市值", "净利润"]
        decks = [dailylib.get_mostn(df, title, col) for col in cols]
        return decks

    def render_deck(self, deck: Deck) -> str:
        template = self.env.get_template(f"{deck.template}.html.jinja")
        html_str = template.render(title=deck.title, content=deck.data)
        return html_str

    def render_page(
        self, temp_name: str, deck_html: str = "page", chart_options: str = "{}"
    ) -> str:
        template = self.env.get_template(f"{temp_name}.html.jinja")
        page_html = template.render(sections=deck_html, chart_options=chart_options)
        return page_html

    def copy_template_assets(self):
        css_src = TEMPLATE_DIR / "myslides.css"
        css_dst = self.output.parent / "myslides.css"
        if css_src.exists():
            css_dst.write_text(css_src.read_text())
            logger.info("myslides.css copied")

    def run(self):
        self.copy_template_assets()

        charts = self.prepare_chart_df()

        charts_options = {}
        for v in charts.values():
            charts_options[v["title"]] = dailylib.df_to_hbar(v["df"])

        decks = [
            dailylib.get_basic(self.clean_df),
            dailylib.get_lostpct(self.clean_df),
            dailylib.get_describe(self.clean_df),
            *self.mostn(self.clean_df, "全部"),
            *self.mostn(self.debank_df, "非银"),
            Deck("chart", "data", charts["top10_debank"]["title"]),
            Deck("chart", "data", charts["top10_by_mv"]["title"]),
            Deck("chart", "data", charts["top10_by_pe"]["title"]),
            Deck("chart", "data", charts["top10_by_gain"]["title"]),
        ]
        deck_html = "\n".join([self.render_deck(deck) for deck in decks])
        page_html = self.render_page(
            "page", deck_html, chart_options=json.dumps(charts_options)
        )

        with open(self.output, "w") as file:
            file.write(page_html)

        logger.info(f"{self.output} saved")


if __name__ == "__main__":
    pass
