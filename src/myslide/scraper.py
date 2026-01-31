#!/usr/bin/env python3
"""
新闻图片爬虫 - 从中新网提取图片和标题
从 https://channel.chinanews.com.cn/u/pic/news.shtml 提取新闻图片和标题
"""
from typer import Typer
from loguru import logger
from typing_extensions import Any
import pandas as pd
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
from myslide.interfaces import DataLoader

data_sources = {
    'cn_news':"https://channel.chinanews.com.cn/u/pic/news.shtml"
}
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
class NewsImageScraper(DataLoader):
    def __init__(self, headless=True):
        """初始化爬虫"""
        self.news_data = []
        self.df = pd.DataFrame()

        # 配置Chrome选项
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={user_agent}")

        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def load_page(self, url_key:str):
        """加载网页"""
        url = data_sources[url_key]
        try:
            print(f"正在加载网页: {url}")
            self.driver.get(url)

            # 等待页面加载完成
            self.wait.until(EC.presence_of_element_located((By.ID, "ent0")))
            print("网页加载完成")
            time.sleep(2)  # 额外等待确保JS执行完成

        except TimeoutException:
            print("页面加载超时")
            return False
        except Exception as e:
            print(f"加载页面时出错: {e}")
            return False

        return True

    def extract_from_dom(self):
        """从DOM中提取数据"""
        try:
            # 查找新闻列表容器
            news_list = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ul.news_list_ul#ent0")
                )
            )

            # 查找所有li元素
            news_items = news_list.find_elements(By.TAG_NAME, "li")
            print(f"找到 {len(news_items)} 个新闻项")

            for i, item in enumerate(news_items):
                try:
                    # 提取图片URL
                    img_element = item.find_element(By.CSS_SELECTOR, ".left img")
                    img_src = img_element.get_attribute("src")

                    # 提取新闻标题
                    title_element = item.find_element(By.CSS_SELECTOR, ".news_title")
                    news_title = title_element.text.strip()

                    # 添加到数据列表
                    news_item = {
                        "index": i + 1,
                        "img_src": img_src,
                        "news_title": news_title,
                    }
                    self.news_data.append(news_item)

                    print(f"提取到第 {i + 1} 条: {news_title[:30]}...")

                except Exception as e:
                    print(f"提取第 {i + 1} 个新闻项时出错: {e}")
                    continue

        except Exception as e:
            print(f"从DOM提取数据时出错: {e}")
            return False

        return True

    def extract_from_javascript(self):
        """从JavaScript变量中提取数据"""
        try:
            # 获取页面中的docArr变量
            doc_arr_script = "return docArr;"
            doc_arr = self.driver.execute_script(doc_arr_script)

            if doc_arr:
                print(f"从JavaScript变量中找到 {len(doc_arr)} 条新闻数据")

                for i, doc in enumerate(doc_arr):
                    # 提取图片URL和标题
                    img_src = doc.get("img", "")
                    news_title = doc.get("title", "")

                    if img_src and news_title:  # 只处理有图片和标题的新闻
                        news_item = {
                            "index": i + 1,
                            "img_src": img_src,
                            "news_title": news_title,
                        }
                        self.news_data.append(news_item)
                        self.df = pd.DataFrame(self.news_data)
                        # print(f"提取到第 {i + 1} 条: {news_title[:30]}...")
                logger.info(f'{self.df.shape} fetched')

                return True
            else:
                print("未找到docArr变量")
                return False

        except Exception as e:
            print(f"从JavaScript变量提取数据时出错: {e}")
            return False

    def save_data(self, filename="news_data.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.news_data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {filename}")
            return True
        except Exception as e:
            print(f"保存数据时出错: {e}")
            return False

    def print_results(self):
        """打印提取结果"""
        print("\n" + "=" * 50)
        print("提取结果:")
        print("=" * 50)

        for item in self.news_data:
            print(f"\n{item['index']}. {item['news_title']}")
            print(f"   图片: {item['img_src']}")

        print(f"\n总计提取到 {len(self.news_data)} 条新闻")

    def fetch(self, url:str):
        """运行爬虫"""
        print("开始运行新闻图片爬虫...")

        # 加载页面
        if not self.load_page(url):
            return None

        # 尝试从JavaScript变量提取数据（更可靠）
        if not self.extract_from_javascript():
            # 如果JS方法失败，尝试从DOM提取
            print("尝试从DOM提取数据...")
            if not self.extract_from_dom():
                print("两种方法都失败了")
                return None

        # 保存和显示结果
        if self.news_data:
            self.save_data()
            # self.print_results()
            # logger.info(self.df.shape)
            return self.df
        else:
            print("没有提取到任何数据")
            return None

    def close(self):
        """关闭浏览器"""
        if hasattr(self, "driver"):
            self.driver.quit()
            print("浏览器已关闭")

    def clean(self, data: Any) -> Any:
        return pd.DataFrame(data)

app = Typer()

@app.command()
def main():
    """主函数"""
    scraper = NewsImageScraper(headless=True)

    url = "https://channel.chinanews.com.cn/u/pic/news.shtml"
    try:
        df = scraper.fetch(url)
        if df is not None:
            logger.info(df.head())
    except KeyboardInterrupt:
        print("\n用户中断爬虫运行")
    except Exception as e:
        print(f"\n爬虫运行时出现错误: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    app()
