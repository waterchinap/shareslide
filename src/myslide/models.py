from dataclasses import dataclass
import pandas as pd
from typing import Any


@dataclass
class Deck:
    template: str
    data: pd.DataFrame | pd.Series | str | dict | list[dict[Any, Any]] | list[tuple]
    title: str | None = None
    n_per_page: int = 8
