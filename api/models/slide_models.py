from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class StockData(BaseModel):
    """股票数据模型"""
    symbol: str
    name: str
    current_price: float
    change_percent: float
    change_amount: float
    volume: float
    turnover: float
    amplitude: float
    high: float
    low: float
    open_price: float
    prev_close: float
    volume_ratio: float
    turnover_rate: float
    pe_ratio: float
    pb_ratio: float
    total_market_cap: float
    circulating_market_cap: float
    speed_up: float
    five_min_change: float
    sixty_day_change: float
    ytd_change: float


class SlideDeck(BaseModel):
    """幻灯片甲板模型"""
    template: str
    data: List[Dict[str, Any]]
    title: str
    n_per_page: Optional[int] = 10


class SlideRequest(BaseModel):
    """创建幻灯片的请求模型"""
    stock_codes: List[str]
    template_type: str = "table"
    title: str = "股票数据幻灯片"


class SlideResponse(BaseModel):
    """幻灯片响应模型"""
    filename: str
    url: str
    created_at: datetime
    total_slides: int


class MarketSummary(BaseModel):
    """市场概要模型"""
    total_stocks: int
    total_turnover: float
    total_market_cap: float
    profit_loss_ratio: Dict[str, float]
    avg_pe_ratio: float
    top_gainers: List[StockData]
    top_losers: List[StockData]