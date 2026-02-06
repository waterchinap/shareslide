from fastapi import APIRouter, HTTPException, Query
from typing import List
from api.models.slide_models import SlideRequest, SlideResponse, MarketSummary
from api.services.slide_service import SlideService
from api.services.data_service import DataService

router = APIRouter()
slide_service = SlideService()


@router.post("/generate", response_model=SlideResponse)
async def generate_slides(request: SlideRequest):
    """生成股票数据幻灯片"""
    try:
        response = slide_service.create_stock_slides(
            stock_codes=request.stock_codes,
            filename=request.title.replace(" ", "_").lower()
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-summary", response_model=SlideResponse)
async def generate_market_summary(filename: str = Query("market_summary", description="输出文件名")):
    """生成市场概要幻灯片"""
    try:
        response = slide_service.create_market_summary_slides(filename=filename)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-codes", response_model=List[str])
async def get_sample_codes():
    """获取示例股票代码列表"""
    sample_codes = ["300750", "600674", "600941", "600309", "002415", "688234", "601398"]
    return sample_codes