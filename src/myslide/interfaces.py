from typing import Protocol, Any
from myslide.models import Deck

class DataLoader(Protocol):
    def fetch(self, url: str) -> Any: # must imply
        ...

    def clean(self, data: Any) -> Any: 
        ...
    
class SlidesBuilder(Protocol):
    def builder(self, df) -> Any: ...

class Render(Protocol):
    def render_page(self, decks:list[Deck], fn:str, chart_options = '{}') -> None: ...
