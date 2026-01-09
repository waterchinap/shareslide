import akshare as ak
import pandas as pd
from loguru import logger
from .base_process import BaseDataProcessor, Slide
import numpy as np
# from plotnine import *
from plotnine import ggplot, aes, geom_text, theme_tufte, labs, theme, geom_point, element_text
from plotnine.options import set_option

set_option("figure_size", (16, 9))
pd.options.mode.copy_on_write = True

class AshareDaily(BaseDataProcessor):
    def tidy_data(self) -> pd.DataFrame:
        """
        数据处理阶段：数据清洗、转换、处理。

        :return: 处理后的DataFrame
        """
        # 1. 获取数据
        df = self.df.copy()

        return df

    def data_process(self, clean_data) -> list[Slide]:
        """
        数据处理阶段：获取并处理数据，返回一个列表.

        :return: 列表
        """
        df = clean_data.copy()
        logger.debug(f"Data shape: {df.shape}")
        # '(0: 序号),(1: 代码),(2: 名称),(3: 最新价),(4: 涨跌幅),(5: 涨跌额),(6: 成交量),(7: 成交额),(8: 振幅),(9: 最高),(10: 最低),(11: 今开),(12: 昨收),(13: 量比),(14: 换手率),(15: 市盈率-动态),(16: 市净率),(17: 总市值),(18: 流通市值),(19: 涨速),(20: 5分钟涨跌),(21: 60日涨跌幅),(22: 年初至今涨跌幅)'
        cols = df.columns

        # overview
        condition = [df[cols[4]] > 0, df[cols[4]] < 0, df[cols[4]] == 0]
        choice = ["涨", "跌", "平"]
        df["group"] = np.select(condition, choice, default="平")
        df[cols[0]] = 1

        # grouped = df.groupby("group")

        def inject_overview(col: int, title: str):
            s = (
                (df.groupby("group")[cols[col]].sum() / df[cols[col]].sum() * 100)
                .round(2)
                .sort_index()
            )
            self.inject_data(title=title, content=s, template="cards")

        data = {
            "涨跌数百分比": 0,
            "总市值百分比": 17,
            "成交额百分比": 7,
            "成交量百分比": 6,
        }

        for k, v in data.items():
            inject_overview(v, k)

        # del nan and add some useful columns
        def clean(df: pd.DataFrame) -> pd.DataFrame:
            df_clean = df.dropna(how="any").copy()  # 删除所有有缺失值的行
            df_clean.iloc[:, 7] = df_clean.iloc[:, 7] / 1e8  # 将数据转换为亿元
            df_clean.iloc[:, 17] = df_clean.iloc[:, 17] / 1e8
            df_clean.iloc[:, 0] = 1  # 将第一行设为1,用于统计个数
            df_clean["净利润"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 15]  # 计算利润
            df_clean["净资产"] = df_clean.iloc[:, 17] / df_clean.iloc[:, 16]  # 计算利润
            df_clean["p_rank"] = df_clean["净利润"].rank(
                ascending=False
            )  # 计算利润排名
            df_clean["p_tier"] = (
                df_clean["净利润"].rank(ascending=False, pct=True) * 100
            ).round(3)  # 计算利润百分位
            df_clean["mv_rank"] = df_clean.iloc[:, 17].rank(
                ascending=False
            )  # 计算总市值排名
            df_clean["mv_tier"] = (
                df_clean.iloc[:, 17].rank(ascending=False, pct=True) * 100
            ).round(3)  # 计算总市值百分位
            return df_clean

        df = clean(df)

        cols = df.columns
        # logger.debug(cols)
        # ''.join([f'({i}:{j})' for i, j in pd.Series(df.columns).items()])
        # (0:序号)(1:代码)(2:名称)(3:最新价)(4:涨跌幅)(5:涨跌额)(6:成交量)(7:成交额)(8:振幅)(9:最高)(10:最低)(11:今开)(12:昨收)(13:量比)(14:换手率)(15:市盈率-动态)(16:市净率)(17:总市值)(18:流通市值)(19:涨速)(20:5分钟涨跌)(21:60日涨跌幅)(22:年初至今涨跌幅)(23:净利润)(24:净资产)(25:p_rank)(26:p_tier)(27:mv_rank)(28:mv_tier)

        # 基本数据
        sum_s = df.sum()
        data = dict(
            股票数=f"{sum_s['序号']}",
            成交额=f"{round(sum_s['成交额'] / 10000, 2)}万亿",
            总市值=f"{round(sum_s['总市值'] / 10000, 2)}万亿",
            净利润=f"{round(sum_s['净利润'] / 10000, 2)}万亿",
            市场PE=f"{round(sum_s['总市值'] / sum_s['净利润'], 2)}",
        )

        self.inject_dcards(content=data)

        # 盈亏分布
        pe_s = df["市盈率-动态"]
        lose_pct = round((len(pe_s[pe_s < 0]) / len(pe_s) * 100), 2)
        gain_pct = 100 - lose_pct
        self.inject_data(
            title="盈亏分布",
            content=pd.Series([gain_pct, lose_pct], index=["盈利", "亏损"]),
            template="cards",
        )

        # rank
        def inject_rank(
            title: str, df: pd.DataFrame, nrow: int = 8
        ):  # 用天渲染长表，每次取8行进行渲染
            for i in range(0, len(df), nrow):
                content = df.iloc[i : i + nrow, :].to_html()
                self.inject_data(title=title, content=content, template="content")

        cols_show = ["名称", "涨跌幅", "市盈率-动态", "p_tier", "mv_tier"]

        # 涨幅排名
        inject_rank(
            title="涨幅排名",
            df=df.nlargest(40, "涨跌幅")[cols_show].reset_index(drop=True),
        )
        inject_rank(
            title="跌幅排名",
            df=df.nsmallest(40, "涨跌幅")[cols_show].reset_index(drop=True),
        )

        # 总市值前40

        inject_rank(
            "总市值排名前列",
            df=df.nlargest(40, "总市值")[cols_show].reset_index(drop=True),
        )
        inject_rank(
            "总市值排名最后",
            df=df.nsmallest(40, "总市值")[cols_show].reset_index(drop=True),
        )

        # 利润排名
        inject_rank(
            "利润排名", df=df.nlargest(40, "净利润")[cols_show].reset_index(drop=True)
        )
        inject_rank(
            "亏损排名", df=df.nsmallest(40, "净利润")[cols_show].reset_index(drop=True)
        )

        # 利润去掉：中国，银行，证券，保险后排名
        non_banks = df[~df["名称"].str.contains("银行|证券|保险|中国")]
        inject_rank(
            "利润排名(去掉银行、证券、保险、中国)",
            non_banks.nlargest(40, "净利润")[cols_show].reset_index(drop=True),
        )

        # plot points
        def plot_points(df: pd.DataFrame, title: str = "title", labn: int = 20):
            """
            df: dataframe需要3列，最后一列是数据标签列
            title: 标题，用时间命名文件
            labn: 显示的标签数量
            """
            cols = df.columns
            df['rank'] = df.iloc[:,0] - df.iloc[:,1]
            lab_df = df.nlargest(labn, 'rank')
            p = (
                ggplot(df, aes(cols[0], cols[1]))
                + geom_point(color="#0394fc")
                + geom_text(aes(label=cols[2]), size=8, data=lab_df)
                + labs(
                    title=title,
                    x=cols[0],
                    y=cols[1],
                )
                + theme_tufte()
                + theme(text=element_text(family="WenQuanYi Micro Hei"))
            )
            output_file = self.output_src / f"{title}.png"
            p.save(output_file)
            img_url = f"{output_file.parent.name}/{output_file.name}"

            return (title, img_url)

        title, img = plot_points(
            non_banks[["mv_tier", "p_tier", "名称"]], title="市值利润对比"
        )
        # logger.debug(f"{title} ,{img}")
        self.inject_data(
            title=title,
            content=img,
            template="img",
        )

        def get_cornner(n:int, length:int = 100):
            step = int(length / n)
            bottom_x = [i for i in range(0, length, step)]
            # bottom_xy = itertools.combinations(bottom_x, 2)
            # right corners x alway > y
            bottom_xy = [(i,j) for i in bottom_x for j in bottom_x if i > j]
            # x, y plus step get the right top corner
            block_xy = [(*i, i[0]+step, i[1]+step) for i in bottom_xy]
            return block_xy

        blocks = get_cornner(4)
        sel = df[['mv_tier', 'p_tier', '名称']].copy()
        for t in blocks:
            block = sel.query(f'{t[0]}<mv_tier<{t[2]} and {t[1]}<p_tier<{t[3]}').copy()
            title, img = plot_points(block, title=f"f{t[0]}-{t[1]}-{t[2]}-{t[3]}")
            self.inject_data(
            title=title,
            content=img,
            template="img",
        )
   

    def run(self):
        clean_data = self.tidy_data()
        self.data_process(clean_data)
        self.add_cover_end()
        return self.slide_datas


def main():
    """主函数"""
    data = AshareDaily(df_data=ak.stock_sse_summary())
    return data.run()


if __name__ == "__main__":
    main()
