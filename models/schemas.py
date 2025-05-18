from pydantic import BaseModel
from typing import List

class TickerList(BaseModel):
    tickers: List[str]
