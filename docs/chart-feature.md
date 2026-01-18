# ECharts 图表功能实现优化

## 功能概述

为项目添加 reveal.js 下 ECharts 前端渲染图表支持，使用横向柱状图（hbar）作为首个图表类型。支持添加多个图表。

## 架构设计

### 数据流程

```
DataFrame
    ↓ (plot_hbar)
dict: { title: option }
    ↓ (get_chart_options)
JSON 字符串
    ↓ (Jinja2 模板)
HTML 内嵌 (window.chartOptions)
    ↓ (JS)
ECharts 渲染
```

### 目录结构

```
reveal/
├── ashare_daily.html      # 主页面（图表数据内嵌）
├── myslides.css           # 样式文件
└── echarts.min.js         # ECharts 库
```

## 实现细节

### 后端 (Python)

| 模块 | 功能 |
|------|------|
| `dailylib.plot_hbar(df, title)` | 将 DataFrame 转换为 ECharts option dict |
| `dailylib.get_chart_options(decks)` | 收集所有图表配置，序列化为 JSON 字符串 |
| `daily_slide.copy_template_assets()` | 复制模板资源文件（如 myslides.css） |

### 前端 (JavaScript)

```javascript
window.chartOptions = { /* 内嵌 JSON 数据 */ };
const chartInstances = {};

function initOrResizeChart(slide) {
    const containers = slide.querySelectorAll('.chart-container');
    containers.forEach(container => {
        const chartId = container.id;
        if (!chartInstances[chartId]) {
            const chart = echarts.init(container);
            chartInstances[chartId] = chart;
            chart.setOption(window.chartOptions[chartId]);
        }
        chartInstances[chartId].resize();
    });
}

Reveal.initialize({ hash: true, transition: 'slide' });
Reveal.on('slidechanged', event => initOrResizeChart(event.currentSlide));
```

### 图表容器 (HTML)

```html
<section>
  <h3>图表标题</h3>
  <div id="图表标题" class="chart-container" style="width: 100%; height: 500px;"></div>
</section>
```

## 关键设计决策

1. **数据内嵌 vs 独立文件**：采用数据内嵌到 HTML 的方式，避免 file:// 协议下的 fetch CORS 问题

2. **图表标识**：使用图表标题（title）作为 div 的 id，与 window.chartOptions 中的 key 对应

3. **Dark 主题适配**：ECharts 配置包含 axisLabel、axisLine、splitLine 等深色主题样式

## 添加新图表

在 `daily_slide.py` 的 `prepare_chart_df()` 中添加数据源，在 `run()` 中调用 `plot_hbar()`：

```python
# 1. 添加数据准备
def prepare_chart_df(self):
    chart_dict = {
        'new_chart': df[['列1', '列2']].nlargest(10, '列2'),
        # ...
    }
    return chart_dict

# 2. 添加图表渲染
def run(self):
    new_chart = dailylib.plot_hbar(charts['new_chart'], '新图表标题')
    decks.append(Deck("chart", new_chart, "新图表标题"))
```

## 变更历史

- 初始版本：使用 charts.js 外部文件 + window.chartOptions
- 当前版本：数据内嵌到 HTML，移除 fetch 请求
