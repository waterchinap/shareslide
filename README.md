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

## 项目备忘录
这份 Python 项目管理全流程备忘录旨在帮助你系统化地管理和交付项目，涵盖了从初始化到分发的主要环节和最佳实践。

| **阶段**       | **核心活动**                               | **关键命令/工具**                                  | **主要产出/配置文件**                               |
| :------------- | :----------------------------------------- | :------------------------------------------------- | :---------------------------------------------------- |
| **1. 项目初始化** | 创建项目结构、初始化虚拟环境、初始化版本控制 | `uv`（或 `venv`）, `git init`                          | 标准化的目录结构、`.gitignore`、虚拟环境目录          |
| **2. 依赖管理**   | 声明和安装依赖、锁定依赖版本                 | `uv add`, `uv sync`, `pip install`                     | `pyproject.toml`, `uv.lock`（或 `requirements.txt`）  |
| **3. 开发与测试** | 编写代码、编写和运行测试                     | `pytest`, `unittest`                                  | 源代码（`src/`）、测试用例（`tests/`）                |
| **4. 打包分发**   | 配置入口点、构建分发包                       | `uv pip install -e .`, `python -m build`, `pyinstaller` | 可分发的 `.whl` 文件或独立可执行文件                    |
| **5. 协作与交付** | 同步代码、共享环境、持续集成                 | `git`, `uv sync`, GitHub Actions                      | 远程仓库（GitHub/GitLab）、CI/CD 配置文件           |

### 📁 1. 项目初始化与结构

为项目创建一个清晰、标准的目录结构是成功的基石。这有助于代码组织、团队协作和后续维护。

*   **推荐的项目结构**：
    ```
    my_project/                 # 项目根目录
    ├── src/                   # 源代码目录 (推荐使用 src-layout)
    │   └── my_project/         # 你的主包（应与项目根目录同名或能清晰标识）
    │       ├── __init__.py    # 标识此为Python包
    │       ├── main.py        # 主入口脚本
    │       └── utils.py       # 其他模块
    ├── tests/                 # 测试代码目录
    │   ├── __init__.py
    │   └── test_utils.py
    ├── docs/                  # 项目文档目录
    ├── .gitignore            # Git忽略规则文件
    ├── pyproject.toml        # **项目核心配置文件** (依赖、元数据、构建配置)
    └── README.md             # 项目说明文档
    ```
*   **初始化虚拟环境**：使用 `uv`（或 `venv`）创建隔离环境，避免依赖冲突。
    ```bash
    # 使用 uv (推荐)
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # 或 .venv\Scripts\activate  # Windows

    # 或使用 Python 内置 venv
    python -m venv .venv
    ```
*   **初始化版本控制**：
    ```bash
    git init
    # 将 .venv/ 等目录添加到 .gitignore
    git add .
    git commit -m "Initial commit"
    ```

### 📦 2. 依赖管理

精确的依赖管理是项目可重现和团队协作的关键。

*   **声明依赖**：在 `pyproject.toml` 中 `[project]` 或 `[tool.uv]` 部分（根据你的工具链）声明项目依赖。使用 `uv add` 命令可以自动添加依赖并更新文件。
    ```bash
    uv add requests pandas
    ```
*   **安装与同步依赖**：使用 `uv sync` 会根据 `pyproject.toml` 和锁文件安装所有依赖，确保环境一致。
    ```bash
    uv sync
    ```
*   **生成锁文件**：`uv sync` 会生成或更新 `uv.lock` 文件，**务必将其纳入版本控制**。这是保证所有环境（开发、测试、生产）依赖完全一致的密钥。

### 🖥️ 3. 开发与测试

在规范的框架下进行编码和测试，能有效提升代码质量和可维护性。

*   **绝对导入**：在包内部模块中，使用从根包名开始的绝对导入。
    ```python
    # 在 src/my_project/main.py 中
    from my_project import utils  # 正确
    # import utils  # 避免这样写（相对导入在包内有时会出错）
    ```
*   **运行测试**：使用 `pytest` 或 `unittest` 运行测试套件。
    ```bash
    # 确保在激活的虚拟环境中安装 pytest
    uv add --dev pytest
    pytest tests/
    ```

### 🚀 4. 打包与分发

将你的项目制作成可分发的形式，方便他人安装和使用。

*   **配置入口点**：在 `pyproject.toml` 中配置命令行工具入口点，使你的脚本可以作为系统命令运行。
    ```toml
    # 在 pyproject.toml 中
    [project.scripts]
    my-cli-tool = "my_project.main:main"
    ```
    重新安装后即可使用：`my-cli-tool`
*   **构建分发包**：
    ```bash
    # 确保已安装 build
    uv add --dev build
    # 构建 wheel 包
    python -m build
    ```
    构建成功后，在 `dist/` 目录下会生成 `.whl` 文件，可以分发给他人用 `pip install` 安装。
*   **创建独立可执行文件**（可选）：使用 `PyInstaller` 将应用打包成独立文件，适合分发给没有Python环境的用户。
    ```bash
    uv add pyinstaller
    pyinstaller --onefile src/my_project/main.py
    ```

### 🤝 5. 协作与交付

良好的协作流程能保障团队高效工作和项目顺利交付。

*   **代码共享与同步**：使用 GitHub/GitLab 等平台托管代码，团队成员通过 `git` 进行协作。
*   **环境重现**：协作者克隆代码后，只需运行 `uv sync`（或在传统流程中 `pip install -r requirements.txt`）即可获得完全一致的开发环境。
*   **持续集成/持续部署 (CI/CD)**：在 GitHub Actions 等CI平台配置流程，自动运行测试、检查代码质量等。
    ```yaml
    # 示例：.github/workflows/ci.yml 基本内容
    - name: Install UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
    - name: Sync dependencies
      run: uv sync
    - name: Run tests
      run: uv run pytest
    ```

### 💡 核心要点提醒

1.  **虚拟环境是必须的**：每个项目都应在其独立的虚拟环境中开发，这是Python开发的第一条军规。
2.  **锁文件是保障**：**永远将 `uv.lock`（或 `requirements.txt`）提交到版本控制**。这是实现环境一致性的关键。
3.  **绝对导入**：在包内使用绝对导入，避免不必要的麻烦。
4.  **测试至关重要**：编写并运行测试，这是保证代码质量和个人信心的安全网。
5.  **文档不是可选项**：维护良好的 `README.md` 和代码文档，方便他人和自己日后理解项目。

希望这份备忘录能成为你Python项目开发中的得力助手！
