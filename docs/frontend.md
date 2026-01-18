这是一个非常现代且易于维护的开发模式。我们将项目结构拆分为三个部分：**HTML（结构）**、**JS（逻辑）**、**JSON（数据）**。

### 项目目录结构

建议在你的项目文件夹中建立如下结构：

```text
reveal/
├── index.html          # 页面结构
├── js/
│   └── main.js         # 业务逻辑 (加载 JSON 并渲染)
└── data/
    └── charts.json     # 图表配置数据 (只负责数据)
```

---

### 1. 数据层

这个文件纯粹是数据，没有逻辑代码，方便以后替换或由后端 API 生成。

```json
{
  "bar-chart": {
    "title": { "text": "柱状图示例", "textStyle": { "color": "#fff" } },
    "tooltip": {},
    "xAxis": {
      "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
      "axisLabel": { "color": "#fff" }
    },
    "yAxis": { "axisLabel": { "color": "#fff" } },
    "series": [
      { "name": "销量", "type": "bar", "data": [5, 20, 36, 10, 10, 20] }
    ]
  },
  "line-chart": {
    "title": { "text": "折线图示例", "textStyle": { "color": "#fff" } },
    "xAxis": {
      "type": "category",
      "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "axisLabel": { "color": "#fff" }
    },
    "yAxis": { "type": "value", "axisLabel": { "color": "#fff" } },
    "series": [
      { "data": [150, 230, 224, 218, 135, 147, 260], "type": "line" }
    ]
  },
  "pie-chart": {
    "title": { "text": "饼图示例", "textStyle": { "color": "#fff" }, "left": "center" },
    "tooltip": { "trigger": "item" },
    "series": [
      {
        "type": "pie",
        "radius": "50%",
        "data": [
          { "value": 1048, "name": "搜索引擎" },
          { "value": 735, "name": "直接访问" },
          { "value": 580, "name": "邮件营销" },
          { "value": 484, "name": "联盟广告" },
          { "value": 300, "name": "视频广告" }
        ]
      }
    ]
  }
}
```

---

### 2. 页面结构层

注意 `data-option` 属性的值必须与 JSON 文件中的 Key（如 `"bar-chart"`）完全对应。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reveal.js + JSON Data</title>
    
    <!-- Reveal.js CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reset.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/black.min.css">

    <style>
        .chart-container {
            width: 100%;
            height: 500px;
            border: 1px solid #444;
            background-color: rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
<body>

    <div class="reveal">
        <div class="slides">

            <section>
                <h1>数据可视化演示</h1>
                <p>数据从 charts.json 异步加载</p>
            </section>

            <!-- 这里的 bar-chart, line-chart 对应 JSON 里的 Key -->
            <section>
                <h2>销售分析</h2>
                <div id="chart-1" class="chart-container" data-option="bar-chart"></div>
            </section>

            <section>
                <h2>趋势分析</h2>
                <div id="chart-2" class="chart-container" data-option="line-chart"></div>
            </section>

            <section>
                <h2>占比分析</h2>
                <div id="chart-3" class="chart-container" data-option="pie-chart"></div>
            </section>

        </div>
    </div>

    <!-- 引入库 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
    
    <!-- 引入我们的逻辑文件 -->
    <script src="js/main.js"></script>
</body>
</html>
```

---

### 3. 逻辑控制层

这里是核心。我们使用 `fetch` API 异步加载 JSON，加载完成后初始化 Reveal.js。

注意：由于加载 JSON 是异步的，我们通过 Promise 确保 Reveal.js 初始化是在数据准备好之后（或者至少在数据加载过程中）进行的。

```javascript
// js/main.js

// 全局变量存储图表配置
let chartDataMap = {};

// 1. 异步加载 JSON 数据
async function loadChartData() {
    try {
        const response = await fetch('data/charts.json');
        if (!response.ok) throw new Error("HTTP error " + response.status);
        chartDataMap = await response.json();
        console.log("图表数据加载完成:", chartDataMap);
        return true;
    } catch (error) {
        console.error("加载图表数据失败:", error);
        // 即使数据加载失败，Reveal.js 也可以启动，只是图表不显示
        return false;
    }
}

// 2. 初始化 Reveal.js
function initReveal() {
    Reveal.initialize({
        hash: true,
        transition: 'slide',
    });
}

// 3. 渲染当前页面的图表
function renderCharts(event) {
    // 获取当前显示的 Slide DOM 元素
    const currentSlide = event.currentSlide;
    
    // 查找该 Slide 下所有待渲染的图表容器
    const containers = currentSlide.querySelectorAll('.chart-container');

    containers.forEach(container => {
        // 获取配置的 key (如 "bar-chart")
        const key = container.getAttribute('data-option');
        
        // 如果数据已加载、容器未被渲染过、且配置存在
        if (chartDataMap[key] && !container.getAttribute('data-rendered')) {
            
            console.log(`正在渲染图表: ${key}`);
            
            const myChart = echarts.init(container);
            myChart.setOption(chartDataMap[key]);
            
            // 标记已渲染
            container.setAttribute('data-rendered', 'true');

            // 窗口大小改变时重绘
            window.addEventListener('resize', () => {
                myChart.resize();
            });
        }
    });
}

// 4. 程序入口
(async function boot() {
    // 先加载数据 (也可以并行处理，这里为了演示顺序)
    await loadChartData();
    
    // 初始化 Reveal
    initReveal();

    // 绑定事件
    Reveal.on('slidechanged', renderCharts);
    
    // 处理第一页如果是图表的情况
    Reveal.on('ready', renderCharts);
    
})();
```

---

### 关键说明

1.  **跨域问题 (CORS)**：
    *   如果你直接双击 `index.html` 打开（协议是 `file://`），`fetch` 可能会因为浏览器安全策略报错。
    *   **解决方法**：请使用本地服务器运行。例如使用 VS Code 的 **Live Server** 插件，或者在命令行运行 `npx http-server`。这是前端开发的最佳实践。

2.  **加载顺序控制**：
    *   代码使用了 `async/await`。虽然我们可以先初始化 Reveal.js，然后在后台默默加载 JSON，但为了防止用户翻页太快导致数据还没加载过来，`await loadChartData()` 确保了数据至少已经开始请求了。

3.  **扩展性**：
    *   现在你想加新图？只需要：
        1.  在 `charts.json` 里复制一段配置改个 Key。
        2.  在 HTML 里加一个 `<div data-option="新Key">`。
    *   完全不需要触碰 `main.js` 逻辑代码。

这个框架非常适合**内容经常变动**或者**图表数量巨大**的演示文稿项目。
