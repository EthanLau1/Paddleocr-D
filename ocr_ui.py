#!/usr/bin/env python3
"""
Paddleocr-D — 图片 + PDF | 自动或指定语言 | 纯文本 + 置信度表格
http://localhost:7860
"""

import os
import tempfile
import gradio as gr
from paddleocr import PaddleOCR
from PIL import Image
import pypdfium2 as pdfium

# ── 语言配置 ────────────────────────────────────────────
LANGS = {
    "ch": "中文",
    "en": "英文",
    "es": "西班牙语",
    "japan": "日语",
    "korean": "韩语",
    "pt": "葡萄牙语",
    "ar": "阿拉伯语",
    "it": "意大利语",
    "fr": "法语",
    "german": "德语",
    "ru": "俄语",
}
LANG_CHOICES = [("🌐 自动识别", "auto")] + [(v, k) for k, v in LANGS.items()]

print("⏳ 预加载中文模型...")
ocr_engines = {"ch": PaddleOCR(lang="ch", use_textline_orientation=True)}
print("✅ 中文模型就绪")


# ── 输出构建 ──────────────────────────────────────────

def _build_output(texts, scores, boxes, best_lang, avg, lang_mode):
    """
    组装输出：
      main_text — 纯文本，按段落分组（方便复制）
      detail_md — 置信度详情 Markdown（折叠面板内显示）
    """
    lang_name = LANGS.get(best_lang, best_lang)
    flag = "🌐 自动识别" if lang_mode else "🎯 指定语言"

    # ── 正文：按 Y 坐标分段落 ──
    if boxes:
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
        main_text = "\n\n".join(texts)

    # ── 详情：用列表代替表格（更紧凑） ──
    detail = f"**{flag}**: {lang_name}  ·  **平均置信度**: {avg:.1%}  ·  **文本段**: {len(texts)}\n\n"
    for txt, score in zip(texts, scores):
        icon = "🟢" if score >= 0.95 else ("🟡" if score >= 0.8 else "🔴")
        detail += f"- {icon} `{score:.0%}` {txt}\n"

    return main_text, detail


def _get_engine(lang: str) -> PaddleOCR:
    if lang not in ocr_engines:
        print(f"⏳ 加载 {lang} 模型...")
        ocr_engines[lang] = PaddleOCR(lang=lang, use_textline_orientation=True)
        print(f"✅ {lang} 模型就绪")
    return ocr_engines[lang]


def _predict(engine, image_path):
    results = engine.predict(image_path)
    if not results or not results[0].get("rec_texts"):
        return None, None, 0, None
    r = results[0]
    return r["rec_texts"], r["rec_scores"], sum(r["rec_scores"]) / len(r["rec_scores"]) if r["rec_scores"] else 0, r.get("boxes", [])


def _ocr_single(image_path: str, lang: str):
    if lang == "auto":
        texts, scores, avg, boxes = _predict(_get_engine("ch"), image_path)
        best_lang = "ch"
        if (not texts) or avg < 0.90:
            for code in LANGS:
                if code == "ch":
                    continue
                try:
                    t, s, a, b = _predict(_get_engine(code), image_path)
                    if t and a > avg:
                        texts, scores, avg, boxes = t, s, a, b
                        best_lang = code
                except Exception:
                    continue
    else:
        texts, scores, avg, boxes = _predict(_get_engine(lang), image_path)
        best_lang = lang

    if not texts:
        return "", "❌ 未检测到文字"
    return _build_output(texts, scores, boxes, best_lang, avg, lang == "auto")


def _is_pdf(filepath: str) -> bool:
    if filepath.lower().endswith(".pdf"):
        return True
    with open(filepath, "rb") as f:
        return f.read(5) == b"%PDF-"


def _pdf_to_images(pdf_path: str, dpi: int = 200):
    pdf = pdfium.PdfDocument(pdf_path)
    out = []
    for idx in range(len(pdf)):
        bitmap = pdf[idx].render(scale=dpi / 72)
        out.append(bitmap.to_pil())
    return out


# ═══════════════════ 处理函数 ═════════════════════════

def ocr_handler(file, lang: str, progress=gr.Progress()):
    """入口：图片/PDF → OCR → 纯文本 + 详情 Markdown。"""
    if file is None:
        return "", "⚠️ 请先上传文件"

    progress(0, desc="准备中...")
    path = file.name if hasattr(file, "name") else str(file)

    if _is_pdf(path):
        pages = _pdf_to_images(path)
        all_text, all_detail = [], []

        for i, pil_img in enumerate(pages):
            progress((i + 1) / len(pages), desc=f"识别第 {i+1}/{len(pages)} 页...")
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            pil_img.save(tmp.name)
            text, detail = _ocr_single(tmp.name, lang)
            os.unlink(tmp.name)

            if len(pages) > 1:
                all_text.append(f"── 第 {i+1}/{len(pages)} 页 ──\n{text}")
                all_detail.append(f"**第 {i+1} 页**\n\n{detail}")
            else:
                all_text.append(text)
                all_detail.append(detail)

        progress(1.0, desc="完成")
        return "\n\n".join(all_text), "\n\n".join(all_detail)
    else:
        progress(0.5, desc="识别中...")
        text, detail = _ocr_single(path, lang)
        progress(1.0, desc="完成")
        return text or "_（未识别到文字）_", detail if text else "❌ 未检测到文字"


# ═══════════════════ 界面 ═════════════════════════════

CSS = """
footer {display:none !important}
"""

with gr.Blocks(title="Paddleocr-D") as ui:
    gr.Markdown(
        "# 🖼️ Paddleocr-D 文字识别\n"
        "**支持 JPG / PNG / PDF · 自动或指定 11 种语言 · 纯文本输出**"
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(
                label="📁 上传图片或 PDF",
                file_types=[".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"],
            )

            lang_input = gr.Dropdown(
                choices=LANG_CHOICES,
                value="auto",
                label="🌐 选择语言",
                info="自动识别 = 先试中文，置信度不够自动换其他 10 种语言",
            )

            btn = gr.Button("🚀 开始识别", variant="primary", size="lg")

            with gr.Accordion("📊 置信度详情", open=False):
                detail_output = gr.Markdown()

        with gr.Column(scale=2):
            text_output = gr.Textbox(
                label="📝 识别结果",
                lines=22,
                max_lines=40,
                placeholder="点击「开始识别」后结果出现在这里",
            )

    lang_list = " | ".join(LANGS.values())
    gr.Markdown(f"---\n🌐 支持语言: {lang_list}")

    btn.click(
        fn=ocr_handler,
        inputs=[file_input, lang_input],
        outputs=[text_output, detail_output],
    )


if __name__ == "__main__":
    ui.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        theme=gr.themes.Monochrome(),
        css=CSS,
    )
