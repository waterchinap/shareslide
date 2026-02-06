from fastapi import APIRouter, HTTPException
from api.models.slide_models import MarketSummary
from api.services.data_service import DataService

router = APIRouter()


@router.get("/market-summary", response_model=MarketSummary)
async def get_market_summary():
    """获取市场概要数据"""
    try:
        raw_df = DataService.fetch_stock_data()
        clean_df = DataService.clean_stock_data(raw_df)
        summary = DataService.get_market_summary(clean_df)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks")
async def get_all_stocks():
    """获取所有股票数据"""
    try:
        df = DataService.fetch_stock_data()
        # 只返回部分字段以减少数据传输
        selected_cols = ['代码', '名称', '最新价', '涨跌幅', '成交额', '总市值', '市盈率']
        result = df[selected_cols].head(100).to_dict('records')  # 限制返回数量
        return {"data": result, "total": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/{symbol}")
async def get_stock_detail(symbol: str):
    """获取特定股票详情"""
    try:
        df = DataService.fetch_stock_data()
        stock_data = df[df['代码'] == symbol]
        
        if stock_data.empty:
            raise HTTPException(status_code=404, detail=f"未找到股票代码: {symbol}")
        
        # 返回该股票的详细信息
        result = stock_data.iloc[0].to_dict()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))