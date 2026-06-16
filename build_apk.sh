#!/bin/bash
set -e

echo "=== RadAtlas Android APK 构建脚本 ==="

sudo apt-get update
sudo apt-get install -y python3-pip python3-venv zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev libltdl-dev

pip3 install --user buildozer cython

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "正在构建 APK，首次构建需要下载 SDK/NDK，请耐心等待..."
buildozer android debug

echo ""
echo "=== 构建完成 ==="
echo "APK 文件位于: $SCRIPT_DIR/bin/"
ls -la bin/*.apk 2>/dev/null || echo "未找到 APK 文件，请检查构建日志"
