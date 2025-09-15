## 目标

一个实现用slidev展示数据、信息、列表的应用。

## 输入

从akshare提供的接口中获取数据。

## 输出

一个可以被slidev播放的markdown文件。格式参考[demo.md](demo.md)。

## 步骤
1. 获取数据。接口参考[akshare](AKShare.md)
    - 使用：stock_sse_summary_df = ak.stock_sse_summary()，获得基本数据。
2. 处理数据。
    - 将获得的数据转换为markdowne表格格式。
3. 创建所需要的单个silde模板：使用jinja2库。格式参考[Slidev.md](Slidev.md).
    - 封面模板
    - 列表模板
    - 表格模板
    - 文字内容模板
4. 创建所需要的组件模板：比如card, cardgroup
5. 将数据写模板中。形成markdwon文本块。
    - 生成一个封面文本块。
    - 使用表格数据进行测试。

6. 组装markdown文本块。形成最终的markdown文件。
