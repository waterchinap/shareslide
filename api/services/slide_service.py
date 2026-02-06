from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from loguru import logger
from api.models.slide_models import SlideDeck, SlideResponse
from api.services.data_service import DataService

OUTPUT_DIR = Path(__file__).parent.parent.parent / 'reveal'
TEMPLATE_DIR = Path(__file__).parent.parent.parent / 'src' / 'myslide' / 'templates'


class SlideService:
    """幻灯片服务类，负责生成HTML幻灯片"""
    
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_deck_from_data(self, data: List[Dict[str, Any]], template: str, title: str, n_per_page: int = 10) -> SlideDeck:
        """从数据创建幻灯片甲板"""
        return SlideDeck(template=template, data=data, title=title, n_per_page=n_per_page)
    
    def render_deck(self, deck: SlideDeck) -> str:
        """渲染单个幻灯片甲板"""
        template = self.env.get_template(f"{deck.template}.html.jinja")
        html_str = template.render(title=deck.title, content=deck.data, n=deck.n_per_page)
        return html_str
    
    def render_multiple_decks(self, decks: List[SlideDeck]) -> str:
        """渲染多个幻灯片甲板"""
        deck_html_parts = []
        for deck in decks:
            deck_html = self.render_deck(deck)
            deck_html_parts.append(deck_html)
        return "\n".join(deck_html_parts)
    
    def create_slide_page(self, decks: List[SlideDeck], filename: str, chart_options: str = '{}') -> SlideResponse:
        """创建完整的幻灯片页面"""
        decks_html = self.render_multiple_decks(decks)
        logger.info("所有甲板渲染完成")
        
        page_template = self.env.get_template("page.html.jinja")
        page_html = page_template.render(sections=decks_html, chart_options=chart_options)
        
        output_path = OUTPUT_DIR / f"{filename}.html"
        
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(page_html)
        
        logger.info(f"幻灯片已保存至: {output_path}")
        
        return SlideResponse(
            filename=f"{filename}.html",
            url=f"/reveal/{filename}.html",
            created_at=datetime.now(),
            total_slides=len(decks)
        )
    
    def create_stock_slides(self, stock_codes: List[str], filename: str = "stock_slides") -> SlideResponse:
        """创建个股幻灯片"""
        # 获取数据
        raw_df = DataService.fetch_stock_data()
        clean_df = DataService.clean_stock_data(raw_df)
        
        # 筛选指定股票
        filtered_df = DataService.filter_by_codes(clean_df, stock_codes)
        stock_list = filtered_df.to_dict(orient="records")
        
        if not stock_list:
            logger.warning("未找到指定股票代码的数据")
            # 返回空的幻灯片
            deck = self.create_deck_from_data([], "stock_single", "个股详情")
            return self.create_slide_page([deck], filename)
        
        # 创建幻灯片甲板
        deck = self.create_deck_from_data(stock_list, "stock_single", "个股详情")
        return self.create_slide_page([deck], filename)
    
    def create_market_summary_slides(self, filename: str = "market_summary") -> SlideResponse:
        """创建市场概要幻灯片"""
        # 获取数据
        raw_df = DataService.fetch_stock_data()
        clean_df = DataService.clean_stock_data(raw_df)
        
        # 创建不同类型的甲板
        summary_deck = self._create_summary_deck(clean_df)
        top_gainers_deck = self._create_top_gainers_deck(clean_df)
        top_losers_deck = self._create_top_losers_deck(clean_df)
        
        return self.create_slide_page(
            [summary_deck, top_gainers_deck, top_losers_deck],
            filename
        )
    
    def _create_summary_deck(self, df: pd.DataFrame) -> SlideDeck:
        """创建市场概要甲板"""
        # 从原项目 dailylib.py 获取相关函数逻辑
        sel = df[["序号", "成交额", "总市值", "净利润"]]
        s = sel.sum()
        res = s[1:].div(10000).round(2)
        res["股票数"] = f"{s['序号'].round(0)}只"
        res["市场PE"] = round((res["总市值"] / res["净利润"]), 2)
        
        summary_data = [{"key": k, "value": v} for k, v in res.items()]
        return self.create_deck_from_data(summary_data, "scard", "市场概要", n_per_page=5)
    
    def _create_top_gainers_deck(self, df: pd.DataFrame) -> SlideDeck:
        """创建涨幅榜甲板"""
        top_gainers = df.nlargest(10, '涨跌幅')[['名称', '涨跌幅', '代码', '最新价']].to_dict('records')
        return self.create_deck_from_data(top_gainers, "table", "涨幅榜", n_per_page=10)
    
    def _create_top_losers_deck(self, df: pd.DataFrame) -> SlideDeck:
        """创建跌幅榜甲板"""
        top_losers = df.nsmallest(10, '涨跌幅')[['名称', '涨跌幅', '代码', '最新价']].to_dict('records')
        return self.create_deck_from_data(top_losers, "table", "跌幅榜", n_per_page=10)