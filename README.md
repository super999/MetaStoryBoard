# MuseLog

AI 画图 / AI 生视频的元数据记录与浏览工具（桌面端 GUI）

本项目是一个使用 PySide6（Qt for Python）+ qt-material 主题的桌面应用，用于整理、记录并浏览 AI 生成的图片/视频及其元数据。当前仓库已包含主窗口 UI 与启动脚本，后续会扩展具体功能页（首页、批量处理、设置等）。

---

## 功能概览（进行中）
- 左侧导航：主页、批量处理、设置
- 右侧标签页区域：可关闭的多标签页
- 统一日志记录到文件 `MuseLog/logs/app.log`
- 深色主题（基于 qt-material，可在设置中切换）

> 说明：当前仓库主要是项目脚手架，部分业务子页面还在补充中。

---

## 目录结构
```
MuseLog/
  logging_utils.py      # 日志初始化
  main.py               # 应用入口（PySide6）
  main_window.py        # 主窗口逻辑（加载 UI、路由到各 Tab）
  ui/
    compile_ui.bat      # 批量将 .ui 转换为 .py 的脚本（pyside6-uic）
    main_window.ui      # Qt Designer 设计文件
```

---

## 环境要求
- Windows 10/11（本仓库默认提供 Windows 的 UI 编译脚本）
- Python 3.9+（建议 3.10/3.11）
- 依赖：
  - PySide6
  - qt-material

你可以直接使用仓库根目录的 `requirements.txt` 安装。

---

## 快速开始（Windows / cmd）
1) 克隆并进入项目根目录：
```
git clone <your-repo-url>
cd meta_story_board
```

2) 创建并激活虚拟环境：
```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
```

3) 安装依赖：
```
pip install -r requirements.txt
```

4) 编译 Qt Designer UI 为 Python 代码（可选，修改 UI 后需要重新编译）：
```
cd MuseLog\ui
compile_ui.bat
cd ..\..
```
上述脚本会使用 `pyside6-uic` 把 `*.ui` 转成同名的 `ui_*.py` 文件。

5) 运行应用：
```
python -m MuseLog.main
```
或：
```
python MuseLog\main.py
```

---

## 常见问题（FAQ）

### 1) 运行时报 `ModuleNotFoundError: No module named 'image_resize_tool'`？
当前 `MuseLog/main_window.py` 中存在历史包名残留：
```
from image_resize_tool.ui.ui_main_window import Ui_MainWindow
```
实际 UI 代码会编译到 `MuseLog/ui/ui_main_window.py`，因此推荐将上述导入替换为：
```
from MuseLog.ui.ui_main_window import Ui_MainWindow
```
同理，`TabHomeWidget`、`TabBatchResizeWidget`、`TabSettingsWidget` 等业务页面若使用了 `image_resize_tool.*` 前缀，也需要统一替换为实际模块路径，或补充对应模块文件。

> 本仓库当前并未包含这些 `Tab*Widget` 的实现文件，因此即使 UI 导入正确，仍可能因缺少业务模块而无法完整运行。你可以先注释相关引用，或补全对应文件后再运行。

### 2) `compile_ui.bat` 找不到 `pyside6-uic`？
请确认已安装 `PySide6`：
```
pip install PySide6
```
若仍提示找不到，尝试通过完整路径调用（位于虚拟环境）：
```
.venv\Scripts\pyside6-uic.exe main_window.ui -o ui_main_window.py
```

### 3) 如何更换主题？
本项目使用 `qt-material`，示例中默认使用 `dark_cyan.xml`：
```
from qt_material import apply_stylesheet
apply_stylesheet(app, theme='dark_cyan.xml')
```
你可以使用 `qt_material.list_themes()` 查看可用主题，然后传入对应名称。

---

## 开发建议与下一步
- 统一命名空间：将遗留的 `image_resize_tool.*` 导入统一替换为 `MuseLog.*`。
- 补齐业务页面：实现 `TabHomeWidget`、`TabBatchResizeWidget`、`TabSettingsWidget`。
- 为功能模块添加最小化的单元测试与示例数据。

---

## README.rst 要怎么生成？
- reStructuredText（`.rst`）不需要特定生成器，可以直接手写。
- 若你已有 `README.md`，常见的转换方式：
  1. Pandoc（推荐）：
     - 安装 Pandoc（需要独立安装，可用官网安装包或包管理器）。
     - 转换命令（Windows/cmd）：
       ```
       pandoc -f markdown -t rst -o README.rst README.md
       ```
  2. pypandoc（Python 包装）：
     - ```
       pip install pypandoc
       python -c "import pypandoc; pypandoc.convert_file('README.md', 'rst', outputfile='README.rst')"
       ```
  3. m2r2（在 Sphinx 项目中把 Markdown 转成 reST）：
     - ```
       pip install m2r2
       m2r2 README.md -o README.rst
       ```

> 如果你的目标是发布到 PyPI，现代打包工具已支持 Markdown：在 `pyproject.toml` 里将 `long_description_content_type` 设为 `text/markdown` 即可，无需再强制转 `.rst`。

---

## 许可证
（在此填写你的开源许可证，或声明保留所有权利。）

## 致谢
- Qt for Python (PySide6)
- qt-material

