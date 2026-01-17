from dataclasses import dataclass
import pandas as pd

@dataclass
class Deck:
    template: str
    data: pd.DataFrame | pd.Series
    title: str | None = None

