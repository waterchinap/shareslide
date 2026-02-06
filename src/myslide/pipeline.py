from myslide.models import DataLoader, SlidesBuilder, Render
from myslide.slide_render import TEMPLATE_DIR, SlideRender
from loguru import logger
from typer import Typer
import importlib
from dataclasses import dataclass
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

LINES = ['cn_img', 'sw_indu', 'em_news', 'cidx399317']
TIMES = [240000, 240000, 600000, 300000]

app = Typer()

@dataclass
class SlidePipeline:
    """幻灯片生成流水线"""
    loader: DataLoader
    builder: SlidesBuilder
    render: Render
    
    def run(self, data_url: str, fn: str) -> None:
        """运行流水线"""
        logger.info(f"开始处理: {data_url}")
        
        df = self.loader.clean(data_url)
        decks, chart_options = self.builder.builder(df)
        self.render.render_page(decks, fn, chart_options)
        
        logger.success(f"处理完成: {fn}")

def create_pipeline(name: str) -> SlidePipeline:
    """
    根据名称自动创建流水线
    约定：模块在 myslide.{name}，类名为 {Name}Loader, {Name}Builder, {Name}Render
    """
    # 转换名称格式：sw_indu -> SwIndu
    class_prefix = ''.join(word.title() for word in name.split('_'))
    
    # 模块路径
    module_path = f"myslide.{name}"
    
    try:
        # 动态导入模块
        module = importlib.import_module(module_path)
        
        # 获取类
        LoaderClass = getattr(module, f"{class_prefix}Loader")
        BuilderClass = getattr(module, f"{class_prefix}Builder")
        RenderClass = SlideRender
        
        # 创建实例
        loader = LoaderClass()
        builder = BuilderClass()
        render = RenderClass()
        
        return SlidePipeline(loader=loader, builder=builder, render=render)
        
    except ImportError as e:
        logger.error(f"无法导入模块 {module_path}: {e}")
        raise
    except AttributeError as e:
        logger.error(f"模块 {module_path} 中缺少必要的类: {e}")
        logger.info(f"期望的类: {class_prefix}Loader, {class_prefix}Builder, {class_prefix}Render")
        raise


@app.command()
def run_pipeline(name: str, data_url: str | None = None, fn: str | None = None):
    """运行指定的流水线"""
    if data_url is None:
        data_url = name
    if fn is None:
        fn = f"{name}_report"
    
    try:
        pipeline = create_pipeline(name)
        pipeline.run(data_url, fn)
        logger.success(f"流水线 {name} 运行成功")
    except Exception as e:
        logger.error(f"流水线 {name} 运行失败: {e}")


@app.command()
def run_all():
    """运行多个流水线"""
    
    for name in LINES:
        try:
            logger.info(f"开始运行流水线: {name}")
            pipeline = create_pipeline(name)
            pipeline.run(name, f"{name}_report")
            logger.success(f"流水线 {name} 运行成功")
        except Exception as e:
            logger.error(f"流水线 {name} 运行失败: {e}")

@app.command()     
def update_starter():
    template_path = Path(__file__).parent / 'templates'
    reveal_dir: Path = Path(__file__).parent.parent.parent / 'reveal'
    env = Environment(loader=FileSystemLoader(template_path))
    src = [f'./{i}_report.html' for i in LINES]
    data = [{'src': s, 'duration':t} for s, t in list(zip(src, TIMES))]
    starter_html = env.get_template('starter.html.jinja').render(pages = data)
    with open(reveal_dir / 'starter.html', 'w') as f:
        f.write(starter_html)
    logger.info('starter updated')    

if __name__ == '__main__':
    app()
