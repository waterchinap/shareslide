from datetime import datetime
from loguru import logger
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from myslide import dailylib
from myslide.models import Deck

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"

MY_CODES = ["300750", "600674", "600941", "600309", "2415", "688234", "601398"]


class StockSingleSlide:
    def __init__(self, stock_codes: list[str], df: pd.DataFrame, output: Path) -> None:
        self.stock_codes = stock_codes
        self.df = df
        self.output = output
        self.clean_df = dailylib.clean(self.df, rename=True, format=True)
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def render_deck(self, deck: Deck) -> str:
        template = self.env.get_template(f"{deck.template}.html.jinja")
        html_str = template.render(title=deck.title, content=deck.data)
        return html_str

    def render_page(self, deck_html: str) -> str:
        template = self.env.get_template("page.html.jinja")
        page_html = template.render(sections=deck_html, chart_options="{}")
        return page_html

    def copy_template_assets(self):
        css_src = TEMPLATE_DIR / "myslides.css"
        css_dst = self.output.parent / "myslides.css"
        if css_src.exists():
            css_dst.write_text(css_src.read_text())
            logger.info("myslides.css copied")

    def run(self):
        self.copy_template_assets()

        filtered = self.clean_df[
            self.clean_df["代码"].astype(str).isin(self.stock_codes)
        ][dailylib.DISPLAY_COLS].copy()

        stock_list = filtered.to_dict(orient="records")

        if not stock_list:
            logger.warning("No stock data found for the given codes")
            return

        deck = Deck("stock_single", stock_list, "个股详情")
        deck_html = self.render_deck(deck)
        page_html = self.render_page(deck_html)

        with open(self.output, "w") as file:
            file.write(page_html)

        logger.info(f"{self.output} saved")


def main():
    import akshare as ak
    from pathlib import Path

    cache_dir = Path.cwd() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path.cwd() / "reveal"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "stock_single.html"

    df = ak.stock_zh_a_spot_em()

    processor = StockSingleSlide(MY_CODES, df, output_file)
    processor.run()


if __name__ == "__main__":
    pass
