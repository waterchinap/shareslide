from datetime import datetime
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from myslide.models import Deck, Render

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"


# (0:序号)(1:代码)(2:名称)(3:最新价)(4:涨跌幅)(5:涨跌额)(6:成交量)(7:成交额)(8:振幅)(9:最高)(10:最低)(11:今开)(12:昨收)(13:量比)(14:换手率)(15:市盈率-动态)(16:市净率)(17:总市值)(18:流通市值)(19:涨速)(20:5分钟涨跌)(21:60日涨跌幅)(22:年初至今涨跌幅)
class SlideRender(Render):
    def __init__(self) -> None:
        self.reveal_dir: Path = Path(__file__).parent.parent.parent / 'reveal'
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def render_a_deck(self, deck: Deck) -> str:
        template = self.env.get_template(f"{deck.template}.html.jinja")
        html_str = template.render(title=deck.title, content=deck.data, n = deck.n_per_page)
        return html_str

    def render_decks(self, decks:list[Deck]):
        deck_html = "\n".join([self.render_a_deck(deck) for deck in decks])
        return deck_html

    def render_page(self, decks: list[Deck], fn: str, chart_options: str ='{}') -> None:
        
        decks_html = self.render_decks(decks)
        logger.info("decks all ready.")
        page_render = self.env.get_template("page.html.jinja").render
        page_html = page_render(sections = decks_html, chart_options=chart_options)
        output = self.reveal_dir / f'{fn}.html'

        with open(output, "w") as file:
            file.write(page_html)
        logger.info(f"{output} saved")


def main():
    pass

if __name__ == "__main__":
    main()
