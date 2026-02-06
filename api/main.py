from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config.settings import settings
from api.routers import slides, data

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(slides.router, prefix="/api/slides", tags=["slides"])
app.include_router(data.router, prefix="/api/data", tags=["data"])

@app.get("/")
async def root():
    return {"message": "Welcome to ShareSlide API", "version": settings.app_version}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}