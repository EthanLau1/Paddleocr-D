#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=7860
VENV="$DIR/venv"
PYTHON="$VENV/bin/python3"

# ═══════════════════════════════════════════════
#  首次运行：自动初始化环境 + 安装依赖
# ═══════════════════════════════════════════════

if [ ! -d "$VENV" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📦 首次运行，正在初始化..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "📦 [1/3] 创建 Python 虚拟环境..."
    python3 -m venv "$VENV"
    echo "✅ 虚拟环境创建成功"
    echo ""

    echo "📦 [2/3] 升级 pip..."
    "$VENV/bin/pip" install --upgrade pip --quiet
    echo "✅ pip 已升级"
    echo ""

    echo "📦 [3/3] 安装依赖（首次约 1-5 分钟，网络慢可能更久）..."
    echo ""
    if ! "$VENV/bin/pip" install -r "$DIR/requirements.txt"; then
        echo ""
        echo "❌ 依赖安装失败"
        echo "   可能原因：网络连接不稳定"
        echo "   ───"
        echo "   重试：再次双击 Start.command"
        echo "   手动：cd \"$DIR\" && \"$VENV/bin/pip\" install -r requirements.txt"
        read -p "按回车关闭此窗口..."
        exit 1
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ 初始化完成！正在启动服务..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# ═══════════════════════════════════════════════
#  启动服务
# ═══════════════════════════════════════════════

# 检查是否已在运行
if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "✅ Paddleocr-D 已在运行 → http://localhost:$PORT"
    open "http://localhost:$PORT"
    read -p "按回车关闭此窗口..."
    exit 0
fi

# 清理占用 7860 端口的残留进程
PORT_PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PORT_PID" ]; then
    # 只有 Python 进程才杀（避免误杀其他程序）
    if ps -p "$PORT_PID" -o comm= 2>/dev/null | grep -qi python; then
        kill -9 "$PORT_PID" 2>/dev/null || true
        sleep 0.5
    fi
fi

echo "🚀 启动 Paddleocr-D..."
cd "$DIR"
nohup "$PYTHON" ocr_ui.py > "$DIR/.ocr_server.log" 2>&1 &

# 等待服务就绪（最长 60 秒）
echo -n "⏳"
for i in $(seq 1 60); do
    if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  ✅ http://localhost:$PORT"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        open "http://localhost:$PORT"
        echo ""
        read -p "服务已在后台运行。按回车关闭此窗口（不会停止服务）..."
        exit 0
    fi
    echo -n "."
    sleep 1
done

# 超时
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚠️ 启动超时（60 秒）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  查看日志："
echo "    cat \"$DIR/.ocr_server.log\""
echo ""
echo "  手动启动："
echo "    \"$PYTHON\" \"$DIR/ocr_ui.py\""
echo ""
echo "  常见原因："
echo "    · 首次运行时模型下载较慢（网络问题）"
echo "    · 端口 $PORT 被占用"
echo "    · 缺少 Python 依赖"
read -p "按回车关闭此窗口..."
exit 1
