from dataclasses import dataclass
from typing import List

@dataclass
class NewsArticle:
    title: str
    url: str
    source: str
    content: str

@dataclass
class BotResponse:
    message: str
    references: List[NewsArticle]