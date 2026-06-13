# 🖼️ Paddleocr-D

> **A lightweight OCR web tool — drag & drop images or PDFs, get text in seconds.**  
> Built on [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) with a clean Gradio interface.

---

## 🇬🇧 English

### Overview

Paddleocr-D is a browser-based OCR (Optical Character Recognition) tool that runs locally. Upload an image or PDF, and it extracts text with confidence scoring, automatic language detection, and clean formatting.

No data leaves your machine — everything runs on your own computer.

### Features

| Feature | Description |
|---------|-------------|
| 📸 Image OCR | JPG / PNG / BMP / TIFF — drag and recognize |
| 📄 PDF OCR | Automatically converts PDF pages to images, OCRs each page |
| 🌐 Auto Language | Starts with Chinese; if confidence is low, falls back through 10 other languages |
| 🎯 Manual Language | Pick a specific language for better accuracy |
| 📝 Markdown Output | Paragraph grouping by Y-coordinate + confidence detail panel |
| ⚡ One-click Start | Double-click `Start.command` to launch, auto-opens browser |

### Supported Languages

Chinese · English · Spanish · Japanese · Korean · Portuguese · Arabic · Italian · French · German · Russian

### Quick Start

```bash
# 1. Start the server
ocr-start          # or double-click Start.command

# 2. Open browser (auto)
# → http://localhost:7860

# 3. Upload image or PDF → click "识别" → done

# 4. Stop when finished
ocr-stop           # or double-click Stop.command
```

### Requirements

- Python 3.9+
- macOS (Linux/WSL also works, tested on macOS)

### Install from Scratch

```bash
git clone https://github.com/EthanLau1/Paddleocr-D.git
cd Paddleocr-D

python3 -m venv venv
source venv/bin/activate

# Install PaddleOCR (CPU version)
pip install paddlepaddle paddleocr gradio pypdfium2 pillow

# Run
./venv/bin/python3 ocr_ui.py
```

### How It Works

1. **Upload** — image (JPG/PNG/BMP/TIFF) or PDF
2. **OCR** — PaddleOCR runs locally, detects text and bounding boxes
3. **Format** — text is grouped into paragraphs by Y-coordinate proximity
4. **Output** — clean text for copying + detailed confidence table
5. **PDF** — pages are rendered to images via `pypdfium2`, then OCR'd page by page

In **auto mode**, the tool first tries Chinese. If average confidence is below 90%, it iterates through all 11 languages and keeps the best result.

### Project Structure

```
Paddleocr-D/
├── ocr_ui.py         # Main web app (Gradio)
├── Start.command     # One-click launcher (macOS)
├── Stop.command      # One-click stopper (macOS)
├── README.md
└── images/           # Test images
```

---

## 🇨🇳 中文

### 产品简介

Paddleocr-D 是一个轻量级的 OCR 网页工具，在浏览器里拖拽图片或 PDF 即可识别文字。基于 PaddleOCR 引擎，本地运行，无需联网，数据不会离开你的电脑。

### 功能特性

| 功能 | 说明 |
|------|------|
| 📸 图片识别 | JPG / PNG / BMP / TIFF 格式拖拽即识别 |
| 📄 PDF 识别 | 自动将 PDF 逐页转为图片并 OCR |
| 🌐 自动语言 | 默认用中文识别，置信度不足自动切换其他 10 种语言 |
| 🎯 手动指定 | 选定特定语言，准确率更高 |
| 📝 Markdown 输出 | 按 Y 坐标自动分段，带置信度详情面板 |
| ⚡ 一键启动 | 双击 `Start.command` 启动，自动打开浏览器 |

### 支持语言

中文 · 英文 · 西班牙语 · 日语 · 韩语 · 葡萄牙语 · 阿拉伯语 · 意大利语 · 法语 · 德语 · 俄语

### 使用方式

```bash
# 1. 启动服务
ocr-start          # 或双击 Start.command

# 2. 浏览器自动打开
# → http://localhost:7860

# 3. 上传图片或 PDF → 点击「开始识别」→ 完成

# 4. 用完关闭
ocr-stop           # 或双击 Stop.command
```

### 环境要求

- Python 3.9+
- macOS（Linux/WSL 也可用，已在 macOS 测试）

### 从零安装

```bash
git clone https://github.com/EthanLau1/Paddleocr-D.git
cd Paddleocr-D

python3 -m venv venv
source venv/bin/activate

# 安装 PaddleOCR（CPU 版本）
pip install paddlepaddle paddleocr gradio pypdfium2 pillow

# 启动
./venv/bin/python3 ocr_ui.py
```

### 工作原理

1. **上传** — 拖入图片（JPG/PNG/BMP/TIFF）或 PDF 文件
2. **OCR** — PaddleOCR 本地运行，检测文字及边界框
3. **排版** — 根据 Y 坐标将文字自动分段落
4. **输出** — 纯文本供复制 + 置信度详情面板
5. **PDF** — 通过 `pypdfium2` 将每一页渲染为图片，逐页 OCR

**自动语言模式**的识别策略：先用中文模型识别，如果平均置信度低于 90%，则遍历全部 11 种语言，取最优结果。

### 文件说明

```
Paddleocr-D/
├── ocr_ui.py         # 主程序（Gradio Web UI）
├── Start.command     # 一键启动脚本（macOS）
├── Stop.command      # 一键停止脚本（macOS）
├── README.md
└── images/           # 测试图片
```

---

*Built with [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) · [Gradio](https://www.gradio.app/)*
