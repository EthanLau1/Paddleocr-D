#!/usr/bin/env python3
"""
Paddleocr-D — 多文件 OCR 工具，支持预览 / 结果下载 / 自动语言识别
http://localhost:7860
"""
import os
import sys
import tempfile
import traceback

import gradio as gr
from paddleocr import PaddleOCR
from PIL import Image
import pypdfium2 as pdfium

# ── 常量 ──
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# ══════════════════════════════════════════════
#  语言配置
# ══════════════════════════════════════════════

LANGS = {
    "ch": "中文",
    "en": "English",
    "es": "Español",
    "japan": "日本語",
    "korean": "한국어",
    "pt": "Português",
    "ar": "العربية",
    "it": "Italiano",
    "fr": "Français",
    "german": "Deutsch",
    "ru": "Русский",
}
LANG_CHOICES = [("🌐 自动识别 (Auto)", "auto")] + [(v, k) for k, v in LANGS.items()]

# ══════════════════════════════════════════════
#  PaddleOCR 引擎（惰性加载）
# ══════════════════════════════════════════════

ocr_engines: dict[str, PaddleOCR] = {}

print("⏳ 预加载中文模型...")
try:
    ocr_engines["ch"] = PaddleOCR(lang="ch", use_textline_orientation=True)
    print("✅ 中文模型就绪")
except Exception as e:
    print(f"❌ 中文模型加载失败: {e}")
    sys.exit(1)


def _get_engine(lang: str) -> PaddleOCR:
    """惰性加载指定语言的 OCR 引擎。"""
    if lang not in ocr_engines:
        name = LANGS.get(lang, lang)
        print(f"⏳ 加载 {name} 模型...")
        ocr_engines[lang] = PaddleOCR(lang=lang, use_textline_orientation=True)
        print(f"✅ {name} 模型就绪")
    return ocr_engines[lang]


# ══════════════════════════════════════════════
#  OCR 核心
# ══════════════════════════════════════════════


def _predict(engine: PaddleOCR, image_path: str):
    """单张图片 OCR，返回 (texts, scores, avg_score, boxes) 或全 None。"""
    try:
        results = engine.predict(image_path)
        if not results or not results[0].get("rec_texts"):
            return None, None, 0, None
        r = results[0]
        texts = r["rec_texts"]
        scores = r["rec_scores"]
        avg = sum(scores) / len(scores) if scores else 0
        return texts, scores, avg, r.get("boxes", [])
    except Exception as e:
        print(f"  ⚠️ OCR 预测失败: {e}")
        return None, None, 0, None


def _build_output(texts, scores, boxes, best_lang: str, avg: float, lang_mode: bool):
    """组装纯文本 + 置信度详情。"""
    lang_name = LANGS.get(best_lang, best_lang)
    flag = "🌐 自动识别" if lang_mode else "🎯 指定语言"

    # ── 正文：按 Y 坐标分段落 ──
    if boxes and texts:
        items = sorted(zip(texts, scores, boxes), key=lambda x: x[2][0][1])
        paragraphs, buf = [], []
        last_y = None
        for txt, _, box in items:
            y = box[0][1]
            if last_y is not None and abs(y - last_y) > 25:
                paragraphs.append(" ".join(buf))
                buf = [txt]
            else:
                buf.append(txt)
            last_y = y
        if buf:
            paragraphs.append(" ".join(buf))
        main_text = "\n\n".join(paragraphs)
    else:
        main_text = "\n\n".join(texts) if texts else ""

    # ── 详情 ──
    detail = (
        f"**{flag}**: {lang_name}  ·  **平均置信度**: {avg:.1%}"
        f"  ·  **文本段**: {len(texts)}\n\n"
    )
    for txt, score in zip(texts, scores):
        icon = "🟢" if score >= 0.95 else ("🟡" if score >= 0.8 else "🔴")
        detail += f"- {icon} `{score:.0%}` {txt}\n"

    return main_text, detail


def _ocr_single(image_path: str, lang: str, progress=None):
    """识别单张图片。

    Args:
        image_path: 图片路径
        lang: "auto" 或语言代码
        progress: 可选 gr.Progress()，传入时会在识别过程中更新状态文字
    """
    if lang == "auto":
        if progress:
            progress(desc="🌐 自动模式：正在尝试 中文...")
        texts, scores, avg, boxes = _predict(_get_engine("ch"), image_path)
        best_lang = "ch"
        if (not texts) or avg < 0.90:
            for code in LANGS:
                if code == "ch":
                    continue
                if progress:
                    progress(desc=f"🌐 自动模式：正在尝试 {LANGS[code]}...")
                try:
                    t, s, a, b = _predict(_get_engine(code), image_path)
                    if t and a > avg:
                        texts, scores, avg, boxes = t, s, a, b
                        best_lang = code
                except Exception:
                    continue
    else:
        if progress:
            progress(desc=f"🎯 {LANGS.get(lang, lang)}...")
        texts, scores, avg, boxes = _predict(_get_engine(lang), image_path)
        best_lang = lang

    if not texts:
        return "", "❌ 未检测到文字"
    return _build_output(texts, scores, boxes, best_lang, avg, lang == "auto")


# ══════════════════════════════════════════════
#  文件辅助
# ══════════════════════════════════════════════

def _is_pdf(filepath: str) -> bool:
    if filepath.lower().endswith(".pdf"):
        return True
    try:
        with open(filepath, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def _pdf_to_images(pdf_path: str, dpi: int = 200):
    """PDF 逐页转 PIL Image。"""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:
        raise gr.Error(f"无法读取 PDF（可能加密或已损坏）: {e}")

    pages = []
    for idx in range(len(pdf)):
        bitmap = pdf[idx].render(scale=dpi / 72)
        pages.append(bitmap.to_pil())
    return pages


def _validate_file(path: str):
    """验证文件合法性，不通过则抛出 gr.Error。"""
    if not os.path.exists(path):
        raise gr.Error(f"文件不存在: {path}")

    size = os.path.getsize(path)
    if size > _MAX_FILE_SIZE:
        raise gr.Error(
            f"文件超过 50MB 限制（当前 {size / 1024 / 1024:.1f}MB）: "
            f"{os.path.basename(path)}"
        )

    if not _is_pdf(path):
        try:
            img = Image.open(path)
            img.verify()
        except Exception:
            raise gr.Error(
                f"无法识别的文件格式（支持 JPG/PNG/BMP/TIFF/PDF）: "
                f"{os.path.basename(path)}"
            )


# ══════════════════════════════════════════════
#  主处理函数
# ══════════════════════════════════════════════

def ocr_handler(files, lang: str, progress=gr.Progress()):
    """多文件 OCR：图片 / PDF → 识别结果 + 可下载文件。"""
    # ── 输入检查 ──
    if not files:
        raise gr.Error("⚠️ 请先上传文件")

    # 兼容单文件 / 多文件
    if not isinstance(files, list):
        files = [files]
    files = [f for f in files if f is not None]
    if not files:
        raise gr.Error("⚠️ 请先上传文件")

    total = len(files)
    all_texts: list[str] = []
    all_details: list[str] = []

    try:
        for idx, file in enumerate(files):
            path = file.name if hasattr(file, "name") else str(file)
            name = os.path.basename(path)

            # ── 验证 ──
            _validate_file(path)

            if _is_pdf(path):
                # ── PDF 处理 ──
                progress((idx + 0.05) / total, desc=f"📄 解析 {name}...")
                pages = _pdf_to_images(path)
                page_texts, page_details = [], []

                for pidx, pil_img in enumerate(pages):
                    pct = (idx + 0.1 + 0.85 * (pidx + 1) / len(pages)) / total
                    progress(pct, desc=f"📄 {name} — 第 {pidx+1}/{len(pages)} 页")

                    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    pil_img.save(tmp.name)
                    try:
                        text, detail = _ocr_single(tmp.name, lang)  # 不加 progress，外层已在报页数
                    finally:
                        os.unlink(tmp.name)

                    if len(pages) > 1:
                        page_texts.append(f"── 第 {pidx+1}/{len(pages)} 页 ──\n{text}")
                        page_details.append(f"**第 {pidx+1} 页**\n\n{detail}")
                    else:
                        page_texts.append(text)
                        page_details.append(detail)

                if total > 1:
                    all_texts.append(f"【{name}】\n{''.join(page_texts)}")
                    all_details.append(f"## {name}\n\n{''.join(page_details)}")
                else:
                    all_texts.append("\n\n".join(page_texts))
                    all_details.append("\n\n".join(page_details))

            else:
                # ── 图片处理 ──
                pct = (idx + 0.5) / total
                progress(pct, desc=f"🖼️ 识别 {name}...")
                text, detail = _ocr_single(path, lang, progress)

                if total > 1:
                    all_texts.append(f"【{name}】\n{text}" if text else f"【{name}】\n_（未识别到文字）_")
                    all_details.append(f"## {name}\n\n{detail}" if detail else f"## {name}\n\n❌ 未检测到文字")
                else:
                    all_texts.append(text)
                    all_details.append(detail)

        # ── 组装最终结果 ──
        progress(0.98, desc="📦 生成下载文件...")
        final_text = "\n\n".join(all_texts) if all_texts else "_（未识别到文字）_"
        final_detail = "\n\n".join(all_details) if all_details else "❌ 未检测到文字"

        # 生成可下载的临时文件
        txt_path = tempfile.NamedTemporaryFile(
            suffix=".txt", prefix="ocr_", delete=False, mode="w"
        )
        txt_path.write(final_text)
        txt_path.close()

        md_path = tempfile.NamedTemporaryFile(
            suffix=".md", prefix="ocr_", delete=False, mode="w"
        )
        md_path.write(f"# Paddleocr-D 识别结果\n\n{final_detail}")
        md_path.close()

        progress(1.0, desc="完成 ✅")

        has_result = bool(final_text and not final_text.startswith("_"))
        return (
            final_text,
            final_detail,
            gr.update(value=txt_path.name, visible=has_result),
            gr.update(value=md_path.name, visible=has_result),
            gr.update(visible=True),   # 恢复「开始识别」
            gr.update(visible=False),  # 隐藏「取消」
        )

    except gr.Error as e:
        # 内部校验失败 → 显示错误信息 + 恢复按钮
        return (
            f"❌ {e}", "",
            None, None,
            gr.update(visible=True),
            gr.update(visible=False),
        )
    except MemoryError:
        return (
            "❌ 内存不足！图片过大，请压缩后再试。", "",
            None, None,
            gr.update(visible=True),
            gr.update(visible=False),
        )
    except Exception as e:
        traceback.print_exc()
        return (
            f"❌ 发生未知错误: {type(e).__name__}: {e}", "",
            None, None,
            gr.update(visible=True),
            gr.update(visible=False),
        )


# ══════════════════════════════════════════════
#  预览生成
# ══════════════════════════════════════════════

def create_preview(file):
    """上传后生成缩略图预览（仅第一张）。"""
    if file is None:
        return None
    files = file if isinstance(file, list) else [file]
    files = [f for f in files if f is not None]
    if not files:
        return None
    first = files[0]
    path = first.name if hasattr(first, "name") else str(first)
    try:
        if _is_pdf(path):
            pdf = pdfium.PdfDocument(path)
            bitmap = pdf[0].render(scale=150 / 72)
            img = bitmap.to_pil()
        else:
            img = Image.open(path)
        img.thumbnail((400, 600))
        return img
    except Exception:
        return None


# ══════════════════════════════════════════════
#  Gradio UI
# ══════════════════════════════════════════════

CSS = """
footer {display:none !important}
"""

ui = gr.Blocks(title="Paddleocr-D", css=CSS, theme=gr.themes.Monochrome())
ui.queue(default_concurrency_limit=1)  # 支持取消 + 单次只跑一个 OCR

with ui:
    gr.Markdown(
        "# 🖼️ Paddleocr-D 文字识别\n"
        "拖入图片或 PDF 自动识别文字 · 支持多文件 · 自动语言检测 · 结果可下载"
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="📁 上传图片或 PDF（支持多选）",
                file_types=[".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"],
                file_count="multiple",
            )

            preview = gr.Image(
                label="👁️ 预览",
                type="pil",
                height=300,
            )

            lang_input = gr.Dropdown(
                choices=LANG_CHOICES,
                value="auto",
                label="🌐 选择语言",
                info="自动识别 = 先试中文，置信度不足自动切换其他 10 种语言",
            )

            with gr.Row():
                btn = gr.Button("🚀 开始识别", variant="primary", size="lg", scale=3)
                cancel_btn = gr.Button("⏹ 取消", variant="stop", size="lg", scale=1, visible=False)

            gr.Examples(
                examples=[["images/test.jpg"]],
                inputs=[file_input],
                label="📋 试试样例图片",
            )

        with gr.Column(scale=2):
            text_output = gr.Textbox(
                label="📝 识别结果",
                lines=20,
                max_lines=40,
                placeholder="上传文件后点击「开始识别」…",
            )

            with gr.Row():
                txt_download = gr.File(
                    label="📥 下载纯文本 (.txt)", visible=False, scale=1
                )
                md_download = gr.File(
                    label="📥 下载 Markdown (.md)", visible=False, scale=1
                )

            with gr.Accordion("📊 置信度详情", open=False):
                detail_output = gr.Markdown()

    # ── 事件绑定 ──
    file_input.change(fn=create_preview, inputs=file_input, outputs=preview)

    # 点击「开始识别」→ 隐藏按钮/显示取消 → 执行 OCR → 恢复按钮
    ocr_event = btn.click(
        fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
        outputs=[btn, cancel_btn],
    ).then(
        fn=ocr_handler,
        inputs=[file_input, lang_input],
        outputs=[text_output, detail_output, txt_download, md_download, btn, cancel_btn],
    )

    # 点击「取消」→ 停止 OCR + 恢复按钮
    cancel_btn.click(
        fn=lambda: (
            "⏹ 已取消", "",
            None, None,
            gr.update(visible=True),
            gr.update(visible=False),
        ),
        outputs=[text_output, detail_output, txt_download, md_download, btn, cancel_btn],
        cancels=[ocr_event],
    )

    lang_list = " · ".join(LANGS.values())
    gr.Markdown(f"---\n🌐 支持语言: {lang_list}")


if __name__ == "__main__":
    ui.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )
