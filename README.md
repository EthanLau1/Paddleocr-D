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
| 📚 Batch Processing | Select multiple files at once — process them all in one go |
| 👁️ Preview | See the uploaded image/PDF before OCR starts |
| 🌐 Auto Language | Starts with Chinese; if confidence is low, falls back through 10 other languages |
| 🎯 Manual Language | Pick a specific language for better accuracy |
| 📝 Smart Formatting | Paragraph grouping by Y-coordinate + confidence score per text line |
| 📥 Download Results | Save recognized text as `.txt` or `.md` file |
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

# Requirements are auto-installed on first launch.
# Or manually:
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

Then **double-click `Start.command`** or run:

```bash
./Start.command         # macOS
venv/bin/python3 ocr_ui.py  # Linux/WSL
```

### How It Works

1. **Upload** — one or more images (JPG/PNG/BMP/TIFF) or PDFs. Preview shows the first file.
2. **OCR** — PaddleOCR runs locally. In auto mode, language is detected automatically with real-time progress feedback.
3. **Format** — text is grouped into paragraphs by Y-coordinate proximity; each line gets a confidence score.
4. **Output** — clean text ready to copy. Download as `.txt` or `.md` file with one click.
5. **PDF** — pages are rendered to images via `pypdfium2`, then OCR'd page by page.

In **auto mode**, the tool first tries Chinese. If average confidence is below 90%, it iterates through all 11 languages and keeps the best result.

### Project Structure

```
Paddleocr-D/
├── ocr_ui.py         # Main web app (Gradio)
├── Start.command     # One-click launcher (macOS)
├── Stop.command      # One-click stopper (macOS)
├── README.md
├── requirements.txt  # Python dependencies
└── images/           # Test images
```

---

## 🇨🇳 中文

### 产品简介

Paddleocr-D 是一个轻量级的 OCR 网页工具，在浏览器里拖拽图片或 PDF 即可识别文字。基于 PaddleOCR 引擎，本地运行，无需联网，数据不会离开你的电脑。

### 功能特性

| 功能 | 说明 |
|------|------|
| 📸 图片识别 | JPG / PNG / BMP / TIFF 拖拽即识别 |
| 📄 PDF 识别 | 自动将 PDF 逐页转为图片并 OCR |
| 📚 批量处理 | 一次选择多张图片/PDF，批量识别 |
| 👁️ 文件预览 | 上传后自动显示图片/PDF 缩略图 |
| 🌐 自动语言 | 默认用中文，置信度不足自动切换其他 10 种语言 |
| 🎯 手动指定 | 选定特定语言，准确率更高 |
| 📝 智能排版 | 按 Y 坐标自动分段 + 每行文字置信度评分 |
| 📥 结果下载 | 识别结果一键保存为 `.txt` 或 `.md` 文件 |
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
```

**然后双击 `Start.command` 即可**，首次运行会自动完成：

1. ✅ 自动创建 Python 虚拟环境
2. ✅ 自动安装所有依赖（约 1-3 分钟）
3. ✅ 自动启动服务并打开浏览器

就是这么简单。用完双击 `Stop.command` 关闭服务。

### 工作原理

1. **上传** — 拖入单张或多张图片/PDF，自动显示首张缩略图
2. **OCR** — PaddleOCR 本地运行，自动模式实时显示正在尝试的语言
3. **排版** — 根据 Y 坐标自动分段落，每行文字标注置信度
4. **输出** — 纯文本可复制，或一键下载为 `.txt` / `.md` 文件
5. **PDF** — 通过 `pypdfium2` 将每一页渲染为图片，逐页 OCR

**自动语言模式**的识别策略：先用中文模型识别，如果平均置信度低于 90%，则遍历全部 11 种语言，取最优结果。

### 文件说明

```
Paddleocr-D/
├── ocr_ui.py         # 主程序（Gradio Web UI）
├── Start.command     # 一键启动脚本（macOS）
├── Stop.command      # 一键停止脚本（macOS）
├── README.md
├── requirements.txt  # Python 依赖列表
└── images/           # 测试图片
```

---

*Built with [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) · [Gradio](https://www.gradio.app/)*
