#!/bin/bash

PORT=7860
DIR="$(cd "$(dirname "$0")" && pwd)"

lsof -ti:$PORT 2>/dev/null | xargs kill -9 2>/dev/null
rm -f "$DIR/.ocr_server.pid"

echo "🛑 Paddleocr-D 已停止"
read -p "按回车关闭此窗口..."
