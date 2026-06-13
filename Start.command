#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$DIR/venv/bin/python3"
PORT=7860

# 已在运行？
if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    echo "✅ Paddleocr-D 已在运行 → 浏览器打开 http://localhost:$PORT"
    open "http://localhost:$PORT"
    read -p "按回车关闭此窗口..."
    exit 0
fi

# 清理残留
lsof -ti:$PORT 2>/dev/null | xargs kill -9 2>/dev/null

echo "🚀 启动 Paddleocr-D..."
cd "$DIR"
nohup "$PYTHON" ocr_ui.py > "$DIR/.ocr_server.log" 2>&1 &

echo -n "⏳"
for i in $(seq 1 30); do
    curl -s "http://localhost:$PORT" > /dev/null 2>&1 && break
    echo -n "."
    sleep 1
done

echo ""
echo "✅ http://localhost:$PORT"
open "http://localhost:$PORT"

read -p "服务已在后台运行。按回车关闭此窗口（不会停止服务）..."
