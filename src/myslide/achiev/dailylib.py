import pandas as pd
from myslide.models import Deck
from pathlib import Path

STOCK_COLUMNS = {
    "市盈率": "市盈率",
    "p_rank": "净利排名",
    "mv_rank": "市值排名",
}

DISPLAY_COLS = [
    "名称",
    "涨跌幅",
    "代码",
    "最新价",
    "涨跌额",
    "成交额",
    "总市值",
    "市盈率",
    "市净率",
    "换手率",
    "振幅",
    "净利润",
    "净利排名",
    "市值排名",
]


def _format_value(value: float, col: str) -> str:
    """根据列名格式化数值"""
    if col in ["最新价", "涨跌额", "最高", "最低"]:
        return f"{value:.2f}"
    elif col in ["成交额", "总市值", "净利润"]:
        return f"{value:.2f}亿"
    elif col in ["市盈率", "市净率"]:
        return f"{value:.2f}"
    elif col in ["换手率", "振幅"]:
        return f"{value:.2f}%"
    elif col in ["成交量"]:
        return f"{value / 1e6:.2f}百万"
    elif col in ["p_rank", "净利排名"]:
        return f"{int(value)}"
    elif col in ["mv_rank", "市值排名"]:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"


def clean(df: pd.DataFrame, rename: bool = True, format: bool = False) -> pd.DataFrame:
    df_clean = df.dropna(how="any").copy()
    df_clean.iloc[:, 7] = df_clean.iloc[:, 7] / 1e8
    df_clean.iloc[:, 17] = df_clean.iloc[:, 17] / 1e8
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

    if rename:
        df_clean = df_clean.rename(columns=STOCK_COLUMNS)

    if format:
        for col in df_clean.columns:
            if col not in ["名称", "涨跌幅", "代码"]:
                df_clean[col] = df_clean[col].apply(lambda x: _format_value(x, col))

    return df_clean


def get_basic(df: pd.DataFrame) -> Deck:
    sel = df[["序号", "成交额", "总市值", "净利润"]]
    s = sel.sum()
    res = s[1:].div(10000).round(2)
    res["股票数"] = f"{s['序号'].round(0)}只"
    res["市场PE"] = round((res["总市值"] / res["净利润"]), 2)
    return Deck("scard", res, n_per_page=5)


def get_describe(df: pd.DataFrame) -> Deck:
    sel = df.iloc[:, [4, 8, 14, 15, 16, 19, 21, 22]]
    desc = sel.describe().round(2).iloc[1:,:]
    return Deck("tcard", desc, n_per_page=8)


def get_lostpct(df: pd.DataFrame) -> Deck:
    pe_s = df["市盈率"]
    lose_pct = round((len(pe_s[pe_s < 0]) / len(pe_s) * 100), 2)
    gain_pct = round(100 - lose_pct, 2)
    data = pd.Series([gain_pct, lose_pct], index=["盈利", "亏损"])
    return Deck("scard", data)


def get_mostn(
    df: pd.DataFrame, title: str, rank_key: str, n: int = 40, flag: str = "largest"
) -> Deck:
    cols_show = ["名称", "涨跌幅", "市盈率", "p_tier", "mv_tier"]
    if flag == "largest":
        df = df.nlargest(n, rank_key)[cols_show].reset_index(drop=True)
    else:
        df = df.nsmallest(n, rank_key)[cols_show].reset_index(drop=True)
    return Deck("table", df, f"{title}:{rank_key}")


def de_banks(df: pd.DataFrame) -> pd.DataFrame:
    non_banks = df[~df["名称"].str.contains("银行|证券|保险|中国|商行")]
    return non_banks


def df_to_hbar(df: pd.DataFrame | pd.Series) -> dict:
    if isinstance(df, pd.Series):
        names = df.index.tolist()
        values = df.values.tolist()
    else:
        names = df.iloc[:, 0].tolist()
        values = df.iloc[:, 1].tolist()

    return {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "yAxis": {
            "type": "category",
            "data": names,
            "axisLabel": {"color": "#fff", "fontSize": 30},
            "axisLine": {"lineStyle": {"color": "#888"}},
        },
        "xAxis": {
            "type": "value",
            "axisLabel": {"color": "#fff"},
            "splitLine": {"lineStyle": {"color": "#333"}},
        },
        "series": [{"type": "bar", "data": values}],
    }
