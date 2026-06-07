<div align="center">

# 🧠 ClipMind-TUI

**Lightweight Terminal Intelligent Clipboard Manager**

*轻量级终端智能剪贴板管理引擎*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Win%2FMac%2FLinux-orange)](https://github.com/gitstq/ClipMind-TUI)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)](requirements.txt)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

## <a name="english"></a> 🎉 Introduction

**ClipMind-TUI** is a lightweight, cross-platform terminal clipboard manager built with pure Python and **zero external dependencies**. It runs entirely in your terminal with a beautiful TUI (Terminal User Interface), featuring intelligent auto-categorization, full-text search, favorites, and real-time clipboard monitoring.

### ✨ Key Features

- 🚀 **Zero Dependencies** — Pure Python standard library, no pip install needed
- 🖥️ **Beautiful TUI** — ANSI-powered terminal UI with colors and navigation
- 🧠 **Smart Categorization** — Auto-detects URLs, emails, code, paths, keys, markdown
- 🔍 **Full-Text Search** — Instantly search through your entire clipboard history
- ⭐ **Favorites** — Pin important clips for quick access
- 📊 **Statistics** — Visual category distribution and usage stats
- 🔄 **Real-Time Monitoring** — Background thread watches clipboard changes
- 💾 **JSON Storage** — Human-readable, exportable local database
- 🌐 **Cross-Platform** — Windows, macOS, and Linux support
- 🔒 **Privacy-First** — All data stays local, no cloud upload

### 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/gitstq/ClipMind-TUI.git
cd ClipMind-TUI

# Run directly (no install needed)
python3 clipmind.py

# Or install via pip
pip install -e .
clipmind
```

### 📖 Usage Guide

#### TUI Mode (Interactive)

```bash
python3 clipmind.py
```

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate items |
| `Enter` | Copy selected to clipboard |
| `n` | Manually add new content |
| `s` | Search mode |
| `c` | Browse by category |
| `f` | View favorites |
| `S` | Statistics dashboard |
| `*` | Toggle favorite |
| `d` | Delete selected item |
| `Space` | Preview content |
| `q` | Quit |

#### CLI Mode

```bash
# Add content
clipmind add "Hello World"

# List recent items
clipmind list

# Search history
clipmind search "github"

# Show statistics
clipmind stats

# Export data
clipmind export backup.json

# Import data
clipmind import backup.json

# Clear all history
clipmind clear
```

### 💡 Design Philosophy

ClipMind-TUI was born from a simple observation: developers spend countless hours copying and pasting, yet most clipboard managers are either bloated GUI apps or lack intelligent organization. We built ClipMind-TUI to be:

1. **Terminal-Native** — Stays in your workflow, no context switching
2. **Intelligent** — Automatically categorizes content without ML dependencies
3. **Lightweight** — Under 900 lines of pure Python
4. **Portable** — Single file, run anywhere Python exists

### 📦 Packaging & Deployment

```bash
# Build wheel
python setup.py sdist bdist_wheel

# Install from source
pip install .

# Run tests
make test

# Clean build artifacts
make clean
```

### 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with clear messages (`git commit -m 'feat: add amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## <a name="简体中文"></a> 🎉 项目介绍

**ClipMind-TUI** 是一款轻量级、跨平台的终端剪贴板管理器，使用纯 Python 编写，**零外部依赖**。它在终端中提供美观的 TUI（终端用户界面），具备智能自动分类、全文搜索、收藏夹和实时剪贴板监控功能。

### ✨ 核心特性

- 🚀 **零依赖** — 纯 Python 标准库，无需 pip 安装
- 🖥️ **精美 TUI** — 基于 ANSI 的彩色终端界面，支持导航
- 🧠 **智能分类** — 自动识别 URL、邮箱、代码、路径、密钥、Markdown
- 🔍 **全文搜索** — 瞬间搜索整个剪贴板历史
- ⭐ **收藏夹** — 固定重要内容，快速访问
- 📊 **统计面板** — 可视化分类分布和使用统计
- 🔄 **实时监控** — 后台线程监听剪贴板变化
- 💾 **JSON 存储** — 人类可读、可导出的本地数据库
- 🌐 **跨平台** — 支持 Windows、macOS 和 Linux
- 🔒 **隐私优先** — 所有数据本地存储，不上传云端

### 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/gitstq/ClipMind-TUI.git
cd ClipMind-TUI

# 直接运行（无需安装）
python3 clipmind.py

# 或通过 pip 安装
pip install -e .
clipmind
```

### 📖 使用指南

#### TUI 模式（交互式）

```bash
python3 clipmind.py
```

| 按键 | 功能 |
|-----|------|
| `↑/↓` 或 `j/k` | 导航项目 |
| `Enter` | 复制选中项到剪贴板 |
| `n` | 手动添加新内容 |
| `s` | 搜索模式 |
| `c` | 按分类浏览 |
| `f` | 查看收藏夹 |
| `S` | 统计面板 |
| `*` | 收藏/取消收藏 |
| `d` | 删除选中项 |
| `Space` | 预览内容 |
| `q` | 退出 |

#### CLI 模式

```bash
# 添加内容
clipmind add "你好世界"

# 列出最近项目
clipmind list

# 搜索历史
clipmind search "github"

# 显示统计
clipmind stats

# 导出数据
clipmind export backup.json

# 导入数据
clipmind import backup.json

# 清空历史
clipmind clear
```

### 💡 设计思路

ClipMind-TUI 诞生于一个简单的观察：开发者花费无数小时复制粘贴，但大多数剪贴板管理器要么是臃肿的 GUI 应用，要么缺乏智能组织功能。我们构建 ClipMind-TUI 的目标是：

1. **终端原生** — 留在你的工作流中，无需切换上下文
2. **智能高效** — 无需 ML 依赖即可自动分类内容
3. **轻量简洁** — 不足 900 行纯 Python 代码
4. **随处可用** — 单文件，任何有 Python 的地方都能运行

### 📦 打包与部署

```bash
# 构建 wheel
python setup.py sdist bdist_wheel

# 从源码安装
pip install .

# 运行测试
make test

# 清理构建产物
make clean
```

### 🤝 贡献指南

欢迎贡献！请遵循以下规范：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/ amazing-feature`)
3. 提交清晰的提交信息 (`git commit -m 'feat: 添加 amazing 功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 发起 Pull Request

### 📄 开源协议

本项目基于 MIT 协议开源 — 详见 [LICENSE](LICENSE) 文件。

---

## <a name="繁體中文"></a> 🎉 專案介紹

**ClipMind-TUI** 是一款輕量級、跨平台的終端剪貼簿管理器，使用純 Python 編寫，**零外部依賴**。它在終端中提供美觀的 TUI（終端使用者介面），具備智慧自動分類、全文搜尋、收藏夾和即時剪貼簿監控功能。

### ✨ 核心特性

- 🚀 **零依賴** — 純 Python 標準庫，無需 pip 安裝
- 🖥️ **精美 TUI** — 基於 ANSI 的彩色終端介面，支援導航
- 🧠 **智慧分類** — 自動識別 URL、郵箱、程式碼、路徑、金鑰、Markdown
- 🔍 **全文搜尋** — 瞬間搜尋整個剪貼簿歷史
- ⭐ **收藏夾** — 固定重要內容，快速訪問
- 📊 **統計面板** — 視覺化分類分佈和使用統計
- 🔄 **即時監控** — 背景執行緒監聽剪貼簿變化
- 💾 **JSON 儲存** — 人類可讀、可匯出的本地資料庫
- 🌐 **跨平台** — 支援 Windows、macOS 和 Linux
- 🔒 **隱私優先** — 所有資料本地儲存，不上傳雲端

### 🚀 快速開始

```bash
# 克隆倉庫
git clone https://github.com/gitstq/ClipMind-TUI.git
cd ClipMind-TUI

# 直接執行（無需安裝）
python3 clipmind.py

# 或透過 pip 安裝
pip install -e .
clipmind
```

### 📖 使用指南

#### TUI 模式（互動式）

```bash
python3 clipmind.py
```

| 按鍵 | 功能 |
|-----|------|
| `↑/↓` 或 `j/k` | 導航項目 |
| `Enter` | 複製選中項到剪貼簿 |
| `n` | 手動新增內容 |
| `s` | 搜尋模式 |
| `c` | 按分類瀏覽 |
| `f` | 查看收藏夾 |
| `S` | 統計面板 |
| `*` | 收藏/取消收藏 |
| `d` | 刪除選中項 |
| `Space` | 預覽內容 |
| `q` | 退出 |

#### CLI 模式

```bash
# 新增內容
clipmind add "你好世界"

# 列出最近項目
clipmind list

# 搜尋歷史
clipmind search "github"

# 顯示統計
clipmind stats

# 匯出資料
clipmind export backup.json

# 匯入資料
clipmind import backup.json

# 清空歷史
clipmind clear
```

### 💡 設計理念

ClipMind-TUI 誕生於一個簡單的觀察：開發者花費無數小時複製貼上，但大多數剪貼簿管理器要麼是臃腫的 GUI 應用，要麼缺乏智慧組織功能。我們構建 ClipMind-TUI 的目標是：

1. **終端原生** — 留在你的工作流中，無需切換上下文
2. **智慧高效** — 無需 ML 依賴即可自動分類內容
3. **輕量簡潔** — 不足 900 行純 Python 程式碼
4. **隨處可用** — 單檔案，任何有 Python 的地方都能執行

### 📦 打包與部署

```bash
# 構建 wheel
python setup.py sdist bdist_wheel

# 從原始碼安裝
pip install .

# 執行測試
make test

# 清理構建產物
make clean
```

### 🤝 貢獻指南

歡迎貢獻！請遵循以下規範：

1. Fork 本倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交清晰的提交資訊 (`git commit -m 'feat: 新增 amazing 功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 發起 Pull Request

### 📄 開源協議

本專案基於 MIT 協議開源 — 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with ❤️ by gitstq**

⭐ Star us on GitHub — it motivates us to keep building!

</div>
