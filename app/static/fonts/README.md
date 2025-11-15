# 字体文件说明

## 为什么需要字体文件？

在Linux服务器（如Render、Railway）上部署时，系统默认没有中文字体，导致地图上的中文显示为方框（□□□）。

## 解决方案

### 方法1：使用项目自带字体（推荐）

将开源中文字体文件放在此目录下，程序会自动加载。

**推荐字体**：
- **思源黑体** (Noto Sans SC) - Google开源字体
- **文泉驿微米黑** (WenQuanYi Micro Hei) - 开源黑体
- **文泉驿正黑** (WenQuanYi Zen Hei) - 开源正黑体

### 下载字体

#### 思源黑体 (Noto Sans SC) - 推荐
```bash
# 下载OTF格式
wget https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf -O app/static/fonts/NotoSansSC-Regular.otf

# 或者从GitHub下载（可能较慢）
wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf -O app/static/fonts/NotoSansSC-Regular.otf
```

#### 文泉驿微米黑
```bash
# Debian/Ubuntu
apt-get install -y fonts-wqy-microhei

# 或直接下载TTF文件
wget https://www.wqy.org/download/wqy-microhei-0.2.0-beta.tar.gz
tar -xzf wqy-microhei-0.2.0-beta.tar.gz
cp wqy-microhei/wqy-microhei.ttc app/static/fonts/
```

### 方法2：系统安装字体

在服务器上安装字体包：

```bash
# Debian/Ubuntu
apt-get update
apt-get install -y fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei

# CentOS/RHEL
yum install -y wqy-microhei-fonts wqy-zenhei-fonts
```

## 字体文件要求

- 格式：`.ttf`, `.otf`, `.ttc` 均可
- 必须支持中文简体
- 建议文件大小：5-15MB

## 当前支持的字体

程序会按以下优先级查找字体：
1. `app/static/fonts/` 目录下的字体文件
2. 系统字体：Noto Sans CJK SC, WenQuanYi Micro Hei, WenQuanYi Zen Hei, Droid Sans Fallback
3. Windows系统字体：Microsoft YaHei (微软雅黑), SimHei (黑体)

## 验证字体

部署后可以通过以下方式验证：
1. 生成一张地图查看是否显示正常
2. 查看日志输出，确认使用的字体路径


