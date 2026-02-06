from pathlib import Path
from loguru import logger
import pandas as pd
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from myslide.models import Deck
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from myslide.models import Deck

TODAY = datetime.now().strftime("%Y-%m-%d")
TEMPLATE_DIR = Path(__file__).parent / "templates"

class ImgChart:
    def __init__(self, df:pd.DataFrame, img_root:Path, output:Path)-> None:
        self.df = df
        self.img_root = img_root
        self.output = output
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        self.setup_matplotlib()

        
    def setup_matplotlib(self):
        # 找到字体文件
        font_path = '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'

        # 添加字体到matplotlib
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()

        # 设置字体
        matplotlib.rcParams['font.sans-serif'] = [font_name]
        matplotlib.rcParams['axes.unicode_minus'] = False
        # 设置全局背景透明
        matplotlib.rcParams.update({
            'figure.facecolor': 'none',    # 图形区域透明
            'axes.facecolor': 'none',      # 坐标轴区域透明
            'savefig.facecolor': 'none',   # 保存时背景透明
            'savefig.edgecolor': 'none',   # 保存时边框透明
        })
        plt.style.use('dark_background')
        # plt.tight_layout()
        
    def plot_line(self, df:pd.DataFrame, col:str):
        fn = self.img_root / f'{col}.png'
        url = f'img/{col}.png'
        ax = df[col].plot(figsize=(16,9))
        self.write_png(ax, fn)
        return (col, url)

    def write_png(self, ax, fn:Path):
        fig = ax.get_figure()
        fig.savefig(fn)
        plt.close(fig)


    def write_page(self, decks: list[Deck]):
        slides ='\n'.join( [self.env.get_template(f'{deck.template}.html.jinja').render(deck.data) for deck in decks])
        
        page_render = self.env.get_template('page.html.jinja').render

        page_html = page_render(sections = slides)
        with open(self.output, 'w') as f:
            f.write(page_html)

        logger.info(f'{self.output} write')

    def run(self):
        cols = self.df.columns
        data_line = [ self.plot_line(self.df, col) for col in cols]
        decks = [
            Deck('img', data_line )
        ]
        self.write_page(decks)
