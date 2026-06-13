#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=7860
VENV="$DIR/venv"
PYTHON="$VENV/bin/python3"

# ═══════════════════════════════════════════
# 首次运行：自动创建环境 + 安装依赖
# ═══════════════════════════════════════════

if [ ! -d "$VENV" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📦 首次运行，正在初始化..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 1. 创建虚拟环境
    echo "📦 [1/3] 创建 Python 虚拟环境..."
    python3 -m venv "$VENV"
    echo "✅ 虚拟环境创建成功"
    echo ""

    # 2. 升级 pip
    echo "📦 [2/3] 升级 pip..."
    "$VENV/bin/pip" install --upgrade pip --quiet
    echo "✅ pip 已升级"
    echo ""

    # 3. 安装依赖（预计 1-3 分钟）
    echo "📦 [3/3] 安装依赖（首次约 1-3 分钟，请耐心等待）..."
    echo ""
    "$VENV/bin/pip" install -r "$DIR/requirements.txt"
    INSTALL_EXIT=$?

    if [ $INSTALL_EXIT -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败，请检查网络连接后重试"
        echo "   或手动运行: $VENV/bin/pip install -r requirements.txt"
        read -p "按回车关闭此窗口..."
        exit 1
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ 初始化完成！正在启动服务..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# ═══════════════════════════════════════════
# 启动服务
# ═══════════════════════════════════════════

# 检查是否已在运行
if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "✅ Paddleocr-D 已在运行 → http://localhost:$PORT"
    open "http://localhost:$PORT"
    read -p "按回车关闭此窗口..."
    exit 0
fi

# 清理残留端口
lsof -ti:$PORT 2>/dev/null | xargs kill -9 2>/dev/null

echo "🚀 启动 Paddleocr-D..."
cd "$DIR"
nohup "$PYTHON" ocr_ui.py > "$DIR/.ocr_server.log" 2>&1 &

# 等待服务就绪
echo -n "⏳"
for i in $(seq 1 30); do
    curl -s "http://localhost:$PORT" > /dev/null 2>&1 && break
    echo -n "."
    sleep 1
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ http://localhost:$PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
open "http://localhost:$PORT"

echo ""
read -p "服务已在后台运行。按回车关闭此窗口（不会停止服务）..."
