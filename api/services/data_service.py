from typing import List, Dict, Any, Tuple
import akshare as ak
import pandas as pd
from datetime import datetime
from pathlib import Path
from loguru import logger
import json
from api.models.slide_models import StockData, MarketSummary
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

TODAY = datetime.now().strftime("%Y-%m-%d")
CACHE_DIR = Path(__file__).parent.parent.parent / 'cache'


class DataService:
    """数据服务类，封装数据获取和处理逻辑"""
    
    @staticmethod
    def fetch_stock_data(use_cache: bool = True) -> pd.DataFrame:
        """获取A股实时数据"""
        cache_file = CACHE_DIR / f"{TODAY}_spot_em.csv"
        
        if use_cache and cache_file.exists():
            logger.info(f"从缓存加载数据: {cache_file}")
            df = pd.read_csv(cache_file)
            return df
        
        try:
            df = ak.stock_zh_a_spot_em()
            logger.info(f"成功获取股票数据: {df.shape}")
            
            # 创建缓存目录
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(cache_file, index=False)
            
            return df
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            raise
    
    @staticmethod
    def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗股票数据"""
        df_clean = df.dropna(how="any").copy()
        df_clean.iloc[:, 7] = df_clean.iloc[:, 7] / 1e8  # 成交额转为亿
        df_clean.iloc[:, 17] = df_clean.iloc[:, 17] / 1e8  # 总市值转为亿
        df_clean.iloc[:, 0] = 1
        df_clean["净利润"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 15]
        df_clean["净资产"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 16]
        df_clean["净利排名"] = df_clean["净利润"].rank(ascending=False)
        df_clean["p_tier"] = (
            df_clean["净利润"].rank(ascending=False, pct=True) * 100
        ).round(3)
        df_clean["市值排名"] = df_clean.iloc[:, 17].rank(ascending=False)
        df_clean["mv_tier"] = (
            df_clean.iloc[:, 17].rank(ascending=False, pct=True) * 100
        ).round(3)

        df_clean = df_clean.rename(columns={"市盈率-动态": "市盈率"})
        
        return df_clean
    
    @staticmethod
    def get_market_summary(df: pd.DataFrame) -> MarketSummary:
        """获取市场概要信息"""
        total_stocks = len(df)
        total_turnover = df.iloc[:, 7].sum()  # 成交额
        total_market_cap = df.iloc[:, 17].sum()  # 总市值
        
        # 计算盈亏比例
        positive_pe = len(df[df['市盈率'] > 0])
        negative_pe = len(df[df['市盈率'] < 0])
        total_with_pe = positive_pe + negative_pe
        profit_loss_ratio = {
            "profit": round(positive_pe / total_with_pe * 100, 2) if total_with_pe > 0 else 0,
            "loss": round(negative_pe / total_with_pe * 100, 2) if total_with_pe > 0 else 0
        }
        
        # 平均市盈率
        avg_pe_ratio = df[df['市盈率'] > 0]['市盈率'].mean()
        
        # 涨跌幅排序
        top_gainers_df = df.nlargest(5, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅']].to_dict('records')
        top_losers_df = df.nsmallest(5, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅']].to_dict('records')
        
        # 转换为 StockData 对象
        top_gainers = [
            StockData(
                symbol=item['代码'],
                name=item['名称'],
                current_price=item['最新价'],
                change_percent=item['涨跌幅'],
                change_amount=0,  # 这里简化处理
                volume=0,
                turnover=0,
                amplitude=0,
                high=0,
                low=0,
                open_price=0,
                prev_close=0,
                volume_ratio=0,
                turnover_rate=0,
                pe_ratio=0,
                pb_ratio=0,
                total_market_cap=0,
                circulating_market_cap=0,
                speed_up=0,
                five_min_change=0,
                sixty_day_change=0,
                ytd_change=0
            ) for item in top_gainers_df
        ]
        
        top_losers = [
            StockData(
                symbol=item['代码'],
                name=item['名称'],
                current_price=item['最新价'],
                change_percent=item['涨跌幅'],
                change_amount=0,
                volume=0,
                turnover=0,
                amplitude=0,
                high=0,
                low=0,
                open_price=0,
                prev_close=0,
                volume_ratio=0,
                turnover_rate=0,
                pe_ratio=0,
                pb_ratio=0,
                total_market_cap=0,
                circulating_market_cap=0,
                speed_up=0,
                five_min_change=0,
                sixty_day_change=0,
                ytd_change=0
            ) for item in top_losers_df
        ]
        
        return MarketSummary(
            total_stocks=total_stocks,
            total_turnover=total_turnover,
            total_market_cap=total_market_cap,
            profit_loss_ratio=profit_loss_ratio,
            avg_pe_ratio=avg_pe_ratio,
            top_gainers=top_gainers,
            top_losers=top_losers
        )
    
    @staticmethod
    def filter_by_codes(df: pd.DataFrame, codes: List[str]) -> pd.DataFrame:
        """根据股票代码筛选数据"""
        filtered_df = df[df["代码"].astype(str).isin(codes)]
        return filtered_df