from myslide.scraper import NewsImageScraper
from myslide.cn399317_builder import Cn399317Builder
from myslide.data_fetcher import Cn399317, NewsEm, SpotEm
from myslide.interfaces import DataLoader, SlidesBuilder, Render
from myslide.news_builder import ImgNewsBuilder, NewsBuilder
from myslide.slide_render import SlideRender
from myslide.spot_em import SpotEmBuilder
from loguru import logger
from typer import Typer

app = Typer()

class SlidePipeline:
    def __init__(self, loader: DataLoader, decks_builder: SlidesBuilder, render: Render) -> None:
        self.loader = loader
        self.decks = decks_builder
        self.render = render

    def run(self,data_url:str, fn:str):
        df = self.loader.fetch(data_url)
        decks, chart_optons = self.decks.builder(df)
        self.render.render_page(decks, fn, chart_optons)

@app.command()
def spot_em():
    daily_info = SlidePipeline(
        loader=SpotEm(),
        decks_builder=SpotEmBuilder(),
        render=SlideRender()
    )

    daily_info.run('spot_em', 'spot_em')

@app.command()
def cn399317():
    pipe = SlidePipeline(
        loader=Cn399317(),
        decks_builder=Cn399317Builder(),
        render=SlideRender()
    )
    pipe.run('cn399317', 'cn399317')

@app.command()
def newsem():
    pipe = SlidePipeline(
        loader=NewsEm(),
        decks_builder=NewsBuilder(),
        render=SlideRender()
    )
    pipe.run('news_em', 'news_em')


@app.command()
def imgnews():
    pipe = SlidePipeline(
        loader=NewsImageScraper(),
        decks_builder=ImgNewsBuilder(),
        render=SlideRender()
    )
    pipe.run('cn_news', 'cn_news')
    
if __name__ == '__main__':
    app()
