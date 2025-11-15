#!/bin/bash
# 中文字体安装脚本
# 用于在Linux服务器上安装中文字体以解决地图中文显示问题

set -e  # 遇到错误立即退出

echo "=================================================="
echo "中国地图生成器 - 中文字体安装脚本"
echo "=================================================="
echo ""

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    echo "检测到操作系统: $OS ($VERSION)"
else
    echo "⚠ 无法检测操作系统类型"
    OS="unknown"
fi

echo ""
echo "选择安装方式："
echo "1. 安装系统字体包（推荐，需要root权限）"
echo "2. 下载字体到项目目录（不需要root权限）"
echo ""
read -p "请输入选择 (1 或 2): " choice

case $choice in
    1)
        echo ""
        echo ">>> 方式1: 安装系统字体包"
        echo ""
        
        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            echo "检测到 Debian/Ubuntu 系统"
            echo "正在安装字体..."
            sudo apt-get update
            sudo apt-get install -y fonts-noto-cjk fonts-wqy-microhei fontconfig
            sudo fc-cache -fv
            echo "✓ 字体安装成功！"
            
        elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
            echo "检测到 CentOS/RHEL/Fedora 系统"
            echo "正在安装字体..."
            sudo yum install -y wqy-microhei-fonts wqy-zenhei-fonts fontconfig
            sudo fc-cache -fv
            echo "✓ 字体安装成功！"
            
        else
            echo "⚠ 不支持的操作系统，请手动安装字体"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo ">>> 方式2: 下载字体到项目目录"
        echo ""
        
        # 创建字体目录
        FONT_DIR="app/static/fonts"
        mkdir -p "$FONT_DIR"
        
        echo "字体目录: $FONT_DIR"
        echo ""
        
        # 尝试多个下载源
        FONT_FILE="$FONT_DIR/NotoSansSC-Regular.otf"
        
        echo "正在下载思源黑体（Noto Sans SC）..."
        echo ""
        
        # 下载源列表
        SOURCES=(
            "https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf"
            "https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/SourceHanSansSC-Regular.otf"
        )
        
        SUCCESS=0
        for SOURCE in "${SOURCES[@]}"; do
            echo "尝试从: $SOURCE"
            if wget -O "$FONT_FILE" "$SOURCE" 2>/dev/null; then
                if [ -f "$FONT_FILE" ] && [ -s "$FONT_FILE" ]; then
                    FILE_SIZE=$(du -h "$FONT_FILE" | cut -f1)
                    echo "✓ 下载成功！文件大小: $FILE_SIZE"
                    SUCCESS=1
                    break
                else
                    echo "✗ 文件无效，尝试下一个源..."
                    rm -f "$FONT_FILE"
                fi
            else
                echo "✗ 下载失败，尝试下一个源..."
            fi
            echo ""
        done
        
        if [ $SUCCESS -eq 0 ]; then
            echo ""
            echo "⚠ 所有下载源都失败了！"
            echo ""
            echo "请手动下载字体："
            echo "1. 访问: https://github.com/googlefonts/noto-cjk/releases"
            echo "2. 下载 NotoSansCJKsc-Regular.otf"
            echo "3. 保存到: $FONT_DIR/"
            exit 1
        fi
        
        echo ""
        echo "✓ 字体文件已保存到: $FONT_FILE"
        ;;
        
    *)
        echo "无效的选择"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "✓ 安装完成！"
echo "=================================================="
echo ""
echo "验证方式："
echo "1. 重启应用: python app.py"
echo "2. 查看日志中是否有: '✓ 成功加载中文字体'"
echo "3. 生成一张地图，检查中文是否正常显示"
echo ""


