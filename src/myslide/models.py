from dataclasses import dataclass
import pandas as pd
from typing import Any
from typing import Protocol, Any

@dataclass
class Deck:
    template: str
    data: pd.DataFrame | pd.Series | str | dict | list[dict[Any, Any]] | list[tuple]
    title: str | None = None
    n_per_page: int = 8

class DataLoader(Protocol):
    def fetch(self, url: str) -> Any: # must imply
        ...

    def clean(self, url: str) -> Any: 
        ...
    
class SlidesBuilder(Protocol):
    def builder(self, df) -> Any: ...

class Render(Protocol):
    def render_page(self, decks:list[Deck], fn:str, chart_options:str = '{}') -> None: ...
