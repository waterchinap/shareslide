# AGENTS.md - Guidelines for Agentic Coding Assistants

This document provides guidelines for agents working in this repository.

## Project Overview

This is a **Python 3.13+** project called "slide" that generates HTML presentations from stock market data using reveal.js and Bokeh visualizations. The project fetches data from akshare, processes it with pandas, and renders it as reveal.js slides.

**Main entry point**: `main.py` (run with `python main.py` or `uv run python main.py`)

---

## Build, Lint, and Test Commands

### Package Management (uv)

```bash
uv sync              # Install all dependencies from pyproject.toml and uv.lock
uv add <package>     # Add a dependency
uv add --dev <pkg>   # Add a dev dependency
uv run <command>     # Run a command in the virtual environment
uv run python        # Open Python REPL with dependencies loaded
```

### Linting (ruff)

```bash
uv run ruff check .              # Check all Python files
uv run ruff check --fix .        # Check and auto-fix issues
uv run ruff check <file.py>      # Check specific file
uv run ruff format <file.py>     # Format a single file
```

### Type Checking (basedpyright)

```bash
uv run basedpyright .                    # Type check all files
uv run basedpyright <file.py>            # Type check specific file
```

### Running the Application

```bash
uv run python main.py                  # Run the main entry point
```

### Testing

**Note**: This project currently has no dedicated test suite. When adding tests:

```bash
uv add --dev pytest              # Install pytest if not present
uv run pytest                    # Run all tests
uv run pytest tests/             # Run tests in tests/ directory
uv run pytest tests/test_*.py    # Run specific test file
uv run pytest -v                 # Run with verbose output
uv run pytest -k "test_name"     # Run tests matching pattern
```

---

## Code Style Guidelines

### Imports

- **Use absolute imports** from the package root:
  ```python
  from myslide.data_fetch import DataFetcher  # Correct
  from .data_fetch import DataFetcher         # Avoid in package modules
  ```

- **Import order** (separated by blank lines):
  1. Standard library imports (sys, os, datetime, etc.)
  2. Third-party imports (loguru, pandas, akshare, etc.)
  3. Local application imports

  ```python
  from loguru import logger
  import akshare as ak
  import pandas as pd
  from datetime import datetime
  from pathlib import Path

  from myslide.data_fetch import DataFetcher
  from myslide.data_process import DataProcessor
  ```

### Formatting

- **Line length**: Follow ruff defaults (approximately 88 characters)
- **Blank lines**: Two blank lines between class definitions, one blank line between method definitions in a class
- **No trailing whitespace**: Remove trailing spaces from all lines
- **Line endings**: Use LF (Unix-style)

### Types

- **Use type hints** for all function signatures:
  ```python
  def fetch_data(cls) -> (str, pd.DataFrame):
      ...

  def inject_data(
      self,
      title: str,
      content: Any,
      template: str = "content",
  ) -> None:
  ```

- **Use dataclass** for structured data:
  ```python
  @dataclass
  class Deck:
      template: str
      data: pd.DataFrame | pd.Series
      title: str | None = None
  ```

- **Generic types** for collections:
  ```python
  decks: list[Deck] = []
  ```

### Naming Conventions

- **Classes**: PascalCase
  ```python
  class DataFetcher: ...
  class DataProcessor: ...
  class SlideRender: ...
  ```

- **Functions and variables**: snake_case
  ```python
  def snake_2_camel(snake_str: str) -> str: ...
  def tidy_data(self) -> pd.DataFrame: ...
  cache_dir = Path("cache")
  ```

- **Constants**: UPPER_SNAKE_CASE (when truly constant)
  ```python
  DATA_URL = dict(ashare_daily=ak.stock_zh_a_spot_em, ...)
  ```

- **Private methods/attributes**: Leading underscore
  ```python
  def _private_method(self): ...
  self._private_attr = value
  ```

### Error Handling

- **Use try/except** with specific exception types:
  ```python
  try:
      df = cls.DATA_URL.get(data_key)()
      cache_dir.mkdir(parents=True, exist_ok=True)
      df.to_csv(cache_file, index=False)
  except Exception as e:
      logger.error(f"Failed to fetch data: {e}")
  ```

- **Reraise exceptions** after logging:
  ```python
  except IOError as e:
      logger.error(f"Failed to write output file: {e}")
      raise
  ```

- **Validate inputs** and raise ValueError for invalid choices:
  ```python
  if choice >= len(page_list):
      raise ValueError("Invalid choice")
  ```

### Logging

- **Use loguru** for logging (already configured in project):
  ```python
  from loguru import logger

  logger.debug(f"Output src: {self.output_src}")
  logger.info(f"SSE data fetched successfully: {df.shape}")
  logger.error(f"Failed to fetch data: {e}")
  logger.success("Process completed successfully")
  ```

- **Remove default handlers** and configure custom format in main:
  ```python
  logger.remove(0)
  custom_format = "<green>{time:MM-DD HH:mm:ss}</green> | ..."
  logger.add(sys.stderr, format=custom_format)
  ```

### Docstrings

- **Use docstrings** for all public functions and classes:
  ```python
  def snake_2_camel(snake_str: str) -> str:
      """
      将下划线命名的字符串转换为驼峰命名字符串

      参数:
          snake_str: 下划线分隔的字符串，如 'hello_world'

      返回:
          驼峰命名字符串，如 'HelloWorld'
      """
  ```

- **Single-line docstrings** for simple functions:
  ```python
  def main():
      """主函数"""
  ```

### File Organization

- **Source files** go in `src/myslide/`
- **Template files** go in `src/myslide/templates/`
- **Tests** (when added) should go in `tests/` directory at project root
- **Cache files** stored in `cache/` directory
- **Output files** stored in `reveal/` directory
- **Logs** stored in `logs/` directory

### Other Conventions

- **Suppress warnings** when appropriate:
  ```python
  warnings.filterwarnings("ignore", category=UserWarning)
  ```

- **Use pathlib** for path operations (not os.path):
  ```python
  from pathlib import Path
  cache_dir = Path(__file__).parent.parent.parent / "cache"
  ```

- **Use dataclasses** for structured data rather than TypedDict or dictionaries with magic keys
