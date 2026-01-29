from typing import Any
import pandas as pd
from myslide.interfaces import SlidesBuilder
from myslide.models import Deck
from loguru import logger


class NewsBuilder(SlidesBuilder):

    def builder(self, df:pd.DataFrame) -> tuple[list[Deck], str]:
        logger.info(df.columns)
        df['摘要'] = df['摘要'].str.replace(r'【[^】]*】', '', regex=True)
        decks = [
            Deck('news', t[2], t[1]) for t in df.itertuples()
        ]
        return (decks, '{}')
    
