# 中文字体问题解决指南

## 问题描述

在Render或其他Linux服务器上部署后，生成的地图中所有中文都显示为方框（□□□）。

**原因**：Linux服务器默认没有安装中文字体。

---

## 🚀 快速解决方案（推荐）

### 方案1：修改Render构建命令（最简单）⭐

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 选择你的服务（china-map-generator）
3. 进入 **Settings** 页面
4. 找到 **Build Command**
5. 修改为以下内容：

```bash
pip install -r requirements.txt && apt-get update && apt-get install -y fonts-noto-cjk fonts-wqy-microhei && fc-cache -fv
```

6. 点击 **Save Changes**
7. 手动触发重新部署（Deploy → Manual Deploy → Deploy latest commit）

**优点**：
- ✅ 最简单，无需修改代码
- ✅ 字体安装到系统，性能好
- ✅ 一次配置，永久生效

---

### 方案2：提交字体文件到Git仓库

如果你有Git仓库的写权限，可以直接添加字体文件：

#### 步骤1：下载字体文件

```bash
# 在本地项目目录
cd app/static/fonts

# 下载思源黑体（约6-8MB）
# 使用腾讯云镜像（国内速度快）
wget https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf -O NotoSansSC-Regular.otf

# 或使用GitHub（国外速度快）
wget https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/SourceHanSansSC-Regular.otf -O NotoSansSC-Regular.otf
```

#### 步骤2：提交到Git

```bash
git add app/static/fonts/NotoSansSC-Regular.otf
git commit -m "Add Chinese font for Linux deployment"
git push origin main
```

#### 步骤3：Render会自动重新部署

**优点**：
- ✅ 不需要修改构建命令
- ✅ 字体随代码一起部署
- ✅ 适合团队协作

**缺点**：
- ❌ 增加仓库大小（约6-8MB）
- ❌ 如果使用GitHub免费版，可能影响速度

---

### 方案3：使用Linux安装脚本

如果你有SSH访问权限（自建服务器），可以使用提供的安装脚本：

```bash
# 下载并运行安装脚本
chmod +x install_fonts.sh
./install_fonts.sh
```

按提示选择：
- **选项1**：安装系统字体（需要sudo权限）
- **选项2**：下载字体到项目目录

---

## 📋 验证字体是否生效

### 方法1：查看应用日志

在Render Dashboard中：
1. 进入你的服务
2. 点击 **Logs** 标签
3. 查找以下信息：

**成功的日志**：
```
✓ 成功加载中文字体: /usr/share/fonts/...
  字体名称: Noto Sans CJK SC
```

**失败的日志**：
```
⚠ 未找到字体文件，使用字体族名称后备方案
```

### 方法2：生成测试地图

1. 访问你的应用URL
2. 生成一张包含中文的地图
3. 检查中文是否正常显示

---

## 🔧 推荐字体

以下是经过测试的开源中文字体：

| 字体名称 | 文件大小 | 特点 | 推荐度 |
|---------|---------|------|--------|
| **思源黑体** (Noto Sans SC) | 6-8MB | 清晰美观，Google官方 | ⭐⭐⭐⭐⭐ |
| **文泉驿微米黑** | 2-3MB | 轻量，适合服务器 | ⭐⭐⭐⭐ |
| **文泉驿正黑** | 8-10MB | 风格柔和 | ⭐⭐⭐ |

---

## 🐛 常见问题

### Q1: 修改了构建命令，但字体还是方框？

**解决方案**：
1. 确保构建命令正确复制（没有换行）
2. 手动触发重新部署
3. 查看构建日志，确认字体安装成功
4. 清除浏览器缓存后重试

### Q2: Render构建时提示权限错误？

**原因**：Render的免费计划有一些限制

**解决方案**：
- 使用方案2（提交字体文件）
- 或升级到Render付费计划

### Q3: 字体文件太大，Git提交失败？

**解决方案**：
- 使用Git LFS（Large File Storage）
- 或使用方案1（系统安装字体）

### Q4: Railway部署如何解决？

Railway使用Docker构建，Dockerfile已包含字体安装：

```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    fontconfig \
    && fc-cache -fv
```

直接部署即可，无需额外配置。

---

## 📚 技术细节

### 字体搜索优先级

项目代码会按以下顺序搜索字体：

1. **项目字体目录**：`app/static/fonts/`
   - NotoSansSC-Regular.otf
   - NotoSansCJKsc-Regular.otf
   - wqy-microhei.ttc

2. **Linux系统字体**：
   - /usr/share/fonts/opentype/noto/
   - /usr/share/fonts/truetype/wqy/

3. **Windows系统字体**：
   - C:/Windows/Fonts/msyh.ttc（微软雅黑）
   - C:/Windows/Fonts/simhei.ttf（黑体）

4. **macOS系统字体**：
   - /System/Library/Fonts/PingFang.ttc

5. **字体族名称后备**：
   - Noto Sans CJK SC
   - WenQuanYi Micro Hei
   - Microsoft YaHei

### 为什么需要字体？

matplotlib在渲染中文时需要中文字体文件。如果找不到：
- 会显示方框（tofu）
- 或显示问号
- 或完全不显示

---

## 🆘 需要帮助？

如果以上方案都无法解决问题：

1. **查看完整日志**：复制Render的完整构建和运行日志
2. **提交Issue**：访问 [GitHub Issues](https://github.com/CHNLion/china-map-generator/issues)
3. **包含信息**：
   - 部署平台（Render/Railway/其他）
   - 错误日志
   - 使用的方案

---

## ✅ 推荐配置总结

**Render部署（推荐）**：
- Build Command: `pip install -r requirements.txt && apt-get update && apt-get install -y fonts-noto-cjk fonts-wqy-microhei && fc-cache -fv`
- Start Command: `python app.py`

**Railway部署**：
- 使用Docker部署，Dockerfile已包含字体配置

**Docker部署**：
- 使用项目提供的Dockerfile，已包含字体安装

**本地开发**：
- Windows: 自动使用微软雅黑
- macOS: 自动使用PingFang
- Linux: 按本指南安装字体

---

最后更新：2025-01-15


