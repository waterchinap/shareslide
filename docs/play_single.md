# 个股单卡幻灯片功能

## 功能概述

生成 reveal.js 格式的个股详情幻灯片，每只股票占用一张幻灯片，显示名称、涨跌幅及14个关键指标。

## 架构设计

### 数据流程

```
ak.stock_zh_a_spot_em()
    ↓ (DataFetcher.fetch_data / 直接调用)
DataFrame
    ↓ (dailylib.clean)
清理后的 DataFrame（包含计算列：净利润、净利排名、市值排名）
    ↓ (StockSingleSlide.run)
list[dict]
    ↓ (Jinja2 模板)
HTML (reveal/stock_single.html)
```

### 目录结构

```
├── play_single.py                    # 入口程序
├── src/myslide/
│   ├── stock_single.py               # 核心类 StockSingleSlide
│   ├── dailylib.py                   # 数据清洗（DISPLAY_COLS 在此定义）
│   └── templates/
│       └── stock_single.html.jinja   # 幻灯片模板
└── reveal/
    └── stock_single.html             # 输出文件
```

## 核心设计

### 1. 列配置集中管理

所有显示列在 `dailylib.DISPLAY_COLS` 中统一配置：

```python
# src/myslide/dailylib.py

DISPLAY_COLS = [
    "名称",      # 头部第1个
    "涨跌幅",    # 头部第2个
    "代码",      # 指标区第1个
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
```

**优势**：增删指标只需修改这一处。

### 2. 数据清洗与计算

`dailylib.clean()` 完成：
- 删除缺失值行
- 单位转换（成交额、总市值 → 亿元）
- 计算派生指标：
  - 净利润 = 总市值 / 市盈率
  - 净利排名 = 净利润排名
  - 市值排名 = 总市值排名
- 列名重命名（"市盈率-动态" → "市盈率"）
- 数值格式化（根据列类型应用不同格式）

### 3. 模板简化

模板无需维护列名映射，直接从数据动态获取：

```jinja
{% for stock in content %}
<section>
  <div class="stock-single-card">
    <div class="stock-single-header">
{% set keys = stock.keys() | list %}
      <span class="stock-name ...">{{ stock[keys[0]] }}</span>
      <span class="stock-change ...">{{ stock[keys[1]] }}%</span>
    </div>
    <div class="stock-single-metrics">
{% for i in range(2, keys | length, 2) %}
      <div class="metric-row-2col">
        <div class="metric-cell">
          <span class="metric-cell-label">{{ keys[i] }}</span>
          <span class="metric-cell-value">{{ stock[keys[i]] }}</span>
        </div>
{% if i + 1 < keys | length %}
        <div class="metric-cell">
          <span class="metric-cell-label">{{ keys[i + 1] }}</span>
          <span class="metric-cell-value">{{ stock[keys[i + 1]] }}</span>
        </div>
{% endif %}
      </div>
{% endfor %}
    </div>
  </div>
</section>
{% endfor %}
```

**布局规则**：
- `keys[0]` = 名称，`keys[1]` = 涨跌幅（头部）
- `keys[2:]` = 指标区，每2个一行

## 实现细节

### 入口程序 (play_single.py)

```python
def fetch_data() -> pd.DataFrame:
    cache_file = cache_dir / f"ashare_daily_{TODAY}.csv"

    if cache_file.exists():
        logger.info(f"Cache file exists: {cache_file}")
        return pd.read_csv(cache_file)

    df = ak.stock_zh_a_spot_em()
    df.to_csv(cache_file, index=False)
    return df

def main():
    df = fetch_data()
    output_file = output_dir / "stock_single.html"
    processor = StockSingleSlide(MY_CODES, df, output_file)
    processor.run()
```

### 核心类 (stock_single.py)

```python
class StockSingleSlide:
    def __init__(self, stock_codes: list[str], df: pd.DataFrame, output: Path):
        self.stock_codes = stock_codes
        self.df = df
        self.output = output
        self.clean_df = dailylib.clean(self.df, rename=True, format=True)

    def run(self):
        filtered = self.clean_df[
            self.clean_df["代码"].astype(str).isin(self.stock_codes)
        ][dailylib.DISPLAY_COLS].copy()
        stock_list = filtered.to_dict(orient="records")
        deck = Deck("stock_single", stock_list, "个股详情")
        # ... 渲染输出
```

### 数值格式化 (_format_value)

```python
def _format_value(value: float, col: str) -> str:
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
    elif col in ["净利排名", "市值排名"]:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"
```

## 运行方式

```bash
uv run python play_single.py
```

输出：`reveal/stock_single.html`

## 添加/删除指标

在 `dailylib.DISPLAY_COLS` 中修改：

```python
DISPLAY_COLS = [
    "名称",
    "涨跌幅",
    "代码",
    "最新价",
    "涨跌额",
    # 新增指标放这里
    "成交额",
    # ...
]
```

模板会自动调整，无需其他修改。

## 变更历史

- 初始版本：独立的 `stock_single.py`（根目录）
- 重构：将核心类移至 `src/myslide/stock_single.py`
- 当前：统一列配置、简化模板、无需 label 映射
