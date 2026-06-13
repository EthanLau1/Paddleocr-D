#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=7860
VENV="$DIR/venv"
PYTHON="$VENV/bin/python3"

# ═══════════════════════════════════════════════
#  首次运行：自动创建环境 + 安装依赖
#  全部中文提示，孩子也能看懂
# ═══════════════════════════════════════════════

if [ ! -d "$VENV" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📦 第一次使用，正在准备……"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  ⏱ 大概需要 2-10 分钟，取决于网速"
    echo "  装完以后下次再开就很快了！"
    echo ""

    # 1. 检查 Python
    echo "📦 [1/4] 检查 Python 版本……"
    PY_OK=$(python3 -c "import sys; v=sys.version_info; print('ok' if v.major==3 and v.minor>=9 else 'bad')" 2>/dev/null)
    if [ "$PY_OK" != "ok" ]; then
        echo "❌ 需要 Python 3.9 或更高版本"
        echo "   请从 https://python.org 下载安装"
        echo "   装完之后再双击本文件"
        read -p "按回车关闭此窗口..."
        exit 1
    fi
    echo "✅ Python 版本满足要求"
    echo ""

    # 2. 创建虚拟环境
    echo "📦 [2/4] 创建 Python 虚拟环境……"
    python3 -m venv "$VENV"
    if [ $? -ne 0 ]; then
        echo "❌ 创建失败，请检查磁盘空间"
        read -p "按回车关闭此窗口..."
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
    echo ""

    # 3. 升级 pip
    echo "📦 [3/4] 准备安装工具……"
    "$VENV/bin/python3" -m pip install --upgrade pip -q
    echo "✅ 安装工具就绪"
    echo ""

    # 4. 安装依赖（这是最慢的一步）
    echo "📦 [4/4] 下载识别引擎（第一次会比较慢，耐心等待哦）……"
    echo "   正在下载大小约 200-500MB 的文件"
    echo "   网速快的话 1-2 分钟，慢的话可能 5-10 分钟"
    echo ""
    if ! "$VENV/bin/python3" -m pip install -r "$DIR/requirements.txt"; then
        echo ""
        echo "❌ 下载失败了 😢"
        echo "   可能原因：网络不稳定"
        echo ""
        echo "   💡 解决办法："
        echo "   1. 检查 Wi-Fi 是否正常"
        echo "   2. 再次双击本文件重试"
        echo "   3. 如果还是不行，换个网络试试"
        read -p "按回车关闭此窗口..."
        exit 1
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ 全部准备就绪！正在打开工具……"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# ═══════════════════════════════════════════════
#  启动服务
# ═══════════════════════════════════════════════

# 如果已经在运行，直接打开
if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "✅ 工具已经在运行 → http://localhost:$PORT"
    echo "   正在打开浏览器……"
    open "http://localhost:$PORT"
    read -p "按回车关闭此窗口..."
    exit 0
fi

# 清理占用端口的老进程
PORT_PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PORT_PID" ]; then
    if ps -p "$PORT_PID" -o comm= 2>/dev/null | grep -qi python; then
        kill -9 "$PORT_PID" 2>/dev/null || true
        sleep 0.5
    fi
fi

echo "🚀 正在打开 Paddleocr-D……"
cd "$DIR"
nohup "$PYTHON" ocr_ui.py > "$DIR/.ocr_server.log" 2>&1 &

# 等待启动（最长 120 秒）
echo -n "⏳"
for i in $(seq 1 120); do
    if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  ✅ 工具已经打开！"
        echo "  在浏览器里操作就可以了 🎉"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        open "http://localhost:$PORT"
        echo ""
        read -p "按回车关闭此窗口（工具不会关闭）..."
        exit 0
    fi
    echo -n "."
    sleep 1
done

# 超时
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚠️ 启动超时（超过 2 分钟）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  可能的原因："
echo "  · 网络比较慢，模型还没下完"
echo "  · 电脑配置较低，启动比较慢"
echo ""
echo "  💡 再双击一次本文件重试"
echo "  如果一直不行，检查一下 Wi-Fi 连接"
echo ""
echo "  日志文件：cat \"$DIR/.ocr_server.log\""
read -p "按回车关闭此窗口..."
exit 1
