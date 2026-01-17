import pandas as pd
from myslide.models import Deck


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

def get_basic(df:pd.DataFrame) -> Deck: 
    sel = df[['序号', '成交额', '总市值', '净利润']]
    s = sel.sum()
    res = s[1:].div(10000).round(2)
    res['股票数量'] = f'{s["序号"].round(0)}只'
    res['市场PE'] = round((res['总市值'] / res['净利润']), 2)
    return Deck('scard', res)

def get_describe(df:pd.DataFrame) -> Deck:
    sel = df.iloc[:,[4, 8, 14, 15, 16, 19, 21, 22]]
    desc = sel.describe().round(2)
    return Deck('tcard', desc)


def get_lostpct(df: pd.DataFrame) -> Deck:
    pe_s = df["市盈率-动态"]
    lose_pct = round((len(pe_s[pe_s < 0]) / len(pe_s) * 100), 2)
    gain_pct = 100 - lose_pct
    data = pd.Series([gain_pct, lose_pct], index=["盈利", "亏损"])
    return Deck('scard', data)


def get_mostn(df: pd.DataFrame, title:str, rank_key: str, n: int = 40, flag: str= 'largest') -> Deck:
    cols_show = ["名称", "涨跌幅", "市盈率-动态", "p_tier", "mv_tier"]
    if flag == 'largest':
        df = df.nlargest(n, rank_key)[cols_show].reset_index(drop=True)
    else:
        df = df.nsmallest(n, rank_key)[cols_show].reset_index(drop=True)
    return Deck('table', df, f'{title}:{rank_key}')


def de_banks(df: pd.DataFrame) -> pd.DataFrame:
    non_banks = df[~df["名称"].str.contains("银行|证券|保险|中国|商行")]
    return non_banks
