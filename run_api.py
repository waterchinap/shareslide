import uvicorn
from api.config.settings import settings


def main():
    """启动 FastAPI 应用"""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
        debug=settings.debug,
        workers=1
    )


if __name__ == "__main__":
    main()