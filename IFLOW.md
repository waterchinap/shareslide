# 项目概述

本项目旨在创建一个应用程序，利用 [Slidev](https://sli.dev) 展示来自 [AKShare](https://akshare.akfamily.xyz/) 的金融数据。其主要目标是获取股票市场数据（如上海证券交易所和深圳证券交易所的概况），将其处理成 Markdown 表格格式，并使用 Jinja2 模板引擎将其嵌入到 Slidev 兼容的 Markdown 文件中，最终生成可播放的幻灯片。

## 核心功能流程

1.  **数据获取**: 使用 `akshare` 库提供的接口（如 `stock_sse_summary`, `stock_szse_summary` 等）从中国股票市场（例如上交所、深交所）获取数据。
2.  **数据处理**: 将获取的原始数据（通常是 Pandas DataFrame）转换为 Markdown 表格格式。
3.  **模板渲染**: 使用 [Jinja2](https://jinja.palletsprojects.com/) 模板引擎，将处理后的数据填充到预定义的 Slidev 模板中。这些模板包括：
    *   封面页模板
    *   列表页模板
    *   表格页模板
    *   文字内容页模板
    *   组件模板（如卡片、卡片组等）
4.  **幻灯片生成**: 将渲染后的 Markdown 文本块组装成一个完整的 Markdown 文件（格式参考 `demo.md`），该文件可直接用于 Slidev 演示。

## 项目结构与关键文件

*   **`README.md`**: 项目目标、输入、输出和实现步骤的简要说明。
*   **`AKShare.md`**: 详细记录了可用于数据获取的 AKShare 接口及其用法示例。
*   **`Slidev.md`**: 包含 Slidev Markdown 语法的参考文档。
*   **`demo.md`**: Slidev 输出文件的格式示例。
*   **`main.py`**: 当前是项目的入口点，但目前仅包含一个打印 "Hello from slide!" 的函数。这是未来实现核心逻辑的地方。
*   **`pyproject.toml`**: 定义了项目的元数据和依赖项（目前依赖项为空）。

## 开发约定与技术栈

*   **编程语言**: Python (版本 >= 3.13.7，根据 `pyproject.toml` 推断)。
*   **主要库**:
    *   `akshare`: 用于获取金融数据。
    *   `jinja2`: 用于模板渲染。
    *   (潜在) `pandas`: 用于数据处理（虽然 `pyproject.toml` 中未明确列出，但 AKShare 通常依赖它）。
*   **输出格式**: Slidev 兼容的 Markdown 文件。

## 构建与运行

由于 `main.py` 尚未实现核心功能，目前无法直接构建或运行完整的数据获取和幻灯片生成功能。当前的运行方式为：

```bash
python main.py
```

这将输出 `Hello from slide!`。

要实现完整功能，需要在 `main.py` 中编写代码来执行以下操作：
1.  调用 AKShare 接口获取数据。
2.  处理数据为 Markdown 表格。
3.  使用 Jinja2 加载模板并渲染数据。
4.  将渲染结果写入到一个 `.md` 文件中。
5.  最终用户可以使用 `slidev your_generated_file.md` 命令来播放生成的幻灯片。

## 注意事项

*   项目的依赖项需要在 `pyproject.toml` 中正确声明，特别是 `akshare` 和 `jinja2`。
*   需要创建 Jinja2 模板文件来定义幻灯片的结构和样式。