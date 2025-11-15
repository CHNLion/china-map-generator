# 部署指南

本项目提供多种部署方案。由于使用了 GeoPandas 等地理空间库，建议使用支持完整 Python 环境的平台。

## 🎯 推荐部署方案

### ⭐ 方案一：Render（最推荐）

**优势**：
- ✅ 完整的 Linux 环境，支持所有地理空间库
- ✅ 免费额度充足（每月 750 小时）
- ✅ 自动 HTTPS 和自定义域名
- ✅ 自动部署（Git push 触发）
- ✅ 简单易用，配置少

**部署步骤**：

1. **通过 GitHub 一键部署**
   - 访问 [GitHub 仓库](https://github.com/CHNLion/china-map-generator)
   - 点击 README 中的 "Deploy to Render" 按钮
   - 使用 GitHub 账号登录 Render
   - 点击 "Create Web Service"
   - 等待 5-10 分钟完成部署

2. **或手动创建服务**
   - 访问 [render.com](https://render.com)
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 配置：
     - **Name**: `china-map-generator`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
   - 点击 "Create Web Service"

3. **环境变量（可选）**
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - `PORT`: `5000`

4. **访问应用**
   - 部署成功后获得 `https://your-app.onrender.com` 域名

---

### 🚂 方案二：Railway

**优势**：
- ✅ 支持 Docker，完全控制环境
- ✅ 简单易用，自动检测配置
- ✅ 自动 HTTPS 和域名
- ✅ 慷慨的免费额度

**部署步骤**：

1. **一键部署**
   - 访问 [GitHub 仓库](https://github.com/CHNLion/china-map-generator)
   - 点击 README 中的 "Deploy on Railway" 按钮
   - 使用 GitHub 登录
   - 点击 "Deploy Now"

2. **或使用 Railway CLI**
   ```bash
   # 安装 Railway CLI
   npm install -g @railway/cli
   
   # 登录
   railway login
   
   # 初始化项目
   railway init
   
   # 部署
   railway up
   ```

3. **配置域名**
   - 在 Railway 控制面板中
   - Settings → Networking → Generate Domain

---

### 🐳 方案三：Docker（推荐自建服务器）

**优势**：
- ✅ 完全控制环境
- ✅ 可部署到任何支持 Docker 的平台
- ✅ 一致的运行环境
- ✅ 易于维护和更新

**使用 Docker Compose（最简单）**：

```bash
# 1. 克隆仓库
git clone https://github.com/CHNLion/china-map-generator.git
cd china-map-generator

# 2. 启动服务
docker-compose up -d

# 3. 访问应用
# 打开浏览器访问 http://localhost:5000

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

**使用 Docker（手动）**：

```bash
# 1. 构建镜像
docker build -t china-map-generator .

# 2. 运行容器
docker run -d \
  -p 5000:5000 \
  --name china-map-generator \
  china-map-generator

# 3. 访问应用
# 打开浏览器访问 http://localhost:5000
```

**部署到云服务器**：

可以部署到任何支持 Docker 的云平台：
- DigitalOcean
- AWS EC2
- Azure VM
- Google Cloud Compute Engine
- 阿里云 ECS
- 腾讯云 CVM

---

### 🚀 方案四：Heroku

**优势**：
- ✅ 成熟的 PaaS 平台
- ✅ 支持 Buildpacks
- ✅ 丰富的插件生态

**注意**：需要绑定信用卡才能使用免费额度

**部署步骤**：

```bash
# 1. 安装 Heroku CLI
# 访问 https://devcenter.heroku.com/articles/heroku-cli

# 2. 登录
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 添加 Python Buildpack
heroku buildpacks:add heroku/python

# 5. 部署
git push heroku main

# 6. 访问应用
heroku open
```

---

## 📝 本地开发部署

### 使用虚拟环境

```bash
# 1. 克隆仓库
git clone https://github.com/CHNLion/china-map-generator.git
cd china-map-generator

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行应用
python app.py

# 6. 访问应用
# 打开浏览器访问 http://localhost:5000
```

---

## ⚠️ 不推荐的部署方案

### ❌ Vercel / Netlify / AWS Lambda 等无服务器平台

**不推荐原因**：
- GeoPandas、GDAL、GEOS、PROJ 等地理空间库需要系统级依赖
- 无服务器环境通常不支持这些复杂的二进制依赖
- 安装过程会失败或超时

**如果一定要使用无服务器平台**，需要：
1. 使用预编译的二进制包
2. 使用 Lambda Layers（AWS）
3. 使用 Docker 容器（AWS Lambda Container）
4. 重写代码以使用其他地理库

---

## 🐛 常见问题

### ⚠️ 地图中文显示为方框（最常见）

**问题**：部署到Linux服务器后，生成的地图中所有中文都显示为方框（□□□）

**原因**：Linux服务器默认没有中文字体

**解决方案**（三选一）：

#### 方案1：使用项目自带字体（推荐）⭐

在项目 `app/static/fonts/` 目录下添加中文字体文件：

```bash
# 在本地或服务器上下载字体
cd app/static/fonts

# 方法1: 使用腾讯云镜像（推荐，速度快）
wget https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf -O NotoSansSC-Regular.otf

# 方法2: 从GitHub下载思源黑体
wget https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/SourceHanSansSC-Regular.otf -O NotoSansSC-Regular.otf

# 方法3: 下载文泉驿微米黑（体积小）
wget https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc
```

**推荐字体**（开源免费）：
- 思源黑体 (Noto Sans SC / Source Han Sans SC) - 推荐
- 文泉驿微米黑 (WenQuanYi Micro Hei) - 轻量
- 文泉驿正黑 (WenQuanYi Zen Hei)

**Render部署时添加字体**：

如果使用Render，可以在构建命令中添加字体下载：

1. 在Render控制面板中，修改 **Build Command**：
   ```bash
   pip install -r requirements.txt && mkdir -p app/static/fonts && wget https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf -O app/static/fonts/NotoSansSC-Regular.otf
   ```

2. 或者将字体文件提交到Git仓库（如果文件不大）

#### 方案2：在服务器上安装系统字体

**Debian/Ubuntu系统**（Render使用）：

```bash
# 安装思源黑体
apt-get update
apt-get install -y fonts-noto-cjk

# 或安装文泉驿字体（更轻量）
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei

# 清除字体缓存
fc-cache -fv
```

**CentOS/RHEL系统**：

```bash
yum install -y wqy-microhei-fonts wqy-zenhei-fonts
fc-cache -fv
```

#### 方案3：修改Dockerfile（使用Docker部署）

Dockerfile中已包含字体安装，确认以下内容存在：

```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*
```

**验证字体是否生效**：

1. 查看应用日志，确认看到以下信息：
   ```
   ✓ 成功加载中文字体: /path/to/font.ttf
     字体名称: Noto Sans CJK SC
   ```

2. 如果看到警告：
   ```
   ⚠ 未找到字体文件，使用字体族名称后备方案
   ```
   说明字体未正确安装，需要按上述方案重新配置。

---

### 依赖安装失败

**问题**：pip 安装 GeoPandas 或相关依赖失败

**解决方案**：
1. **使用 Render 或 Railway**：这些平台有完整的系统依赖
2. **使用 Docker**：Dockerfile 已配置所有必需的系统库
3. **手动安装系统依赖**（Linux）：
   ```bash
   sudo apt-get update
   sudo apt-get install -y gdal-bin libgdal-dev libgeos-dev libproj-dev
   ```

### 内存不足

**问题**：地图生成时内存溢出

**解决方案**：
1. 升级到更高内存的计划（Render Pro: 2GB+）
2. 优化 Shapefile 数据（简化几何）
3. 使用 Docker 限制内存使用

### 超时错误

**问题**：地图生成超时

**解决方案**：
1. Render: 自动处理（最多 30 秒）
2. Railway: 配置更长超时（项目设置）
3. 优化地图生成性能
4. 减少地图复杂度

### 文件上传/下载

**问题**：如何保存生成的地图

**说明**：
- 本项目使用 Base64 编码返回图片
- 无需文件存储，完全无状态
- 适合所有部署平台

---

## 🔧 高级配置

### 环境变量

在部署平台中配置以下环境变量：

- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `False`
- `PORT`: `5000` （某些平台自动设置）

### 自定义域名

**Render**:
1. 项目设置 → Settings → Custom Domains
2. 添加域名并配置 DNS

**Railway**:
1. 项目设置 → Settings → Networking
2. 添加自定义域名

### HTTPS

- Render 和 Railway 自动提供免费 HTTPS
- Docker 自建需要配置 Nginx + Let's Encrypt

---

## 📊 性能对比

| 平台 | 免费额度 | 启动时间 | 内存 | 推荐度 |
|------|---------|---------|------|--------|
| **Render** | 750小时/月 | ~30秒 | 512MB | ⭐⭐⭐⭐⭐ |
| **Railway** | $5额度/月 | ~20秒 | 512MB | ⭐⭐⭐⭐⭐ |
| **Docker** | 无限 | <5秒 | 自定义 | ⭐⭐⭐⭐ |
| **Heroku** | 需绑卡 | ~10秒 | 512MB | ⭐⭐⭐ |

---

## 🆘 需要帮助？

- 📖 查看 [README.md](README.md)
- 🐛 提交 [GitHub Issue](https://github.com/CHNLion/china-map-generator/issues)
- 📧 联系作者

---

## 🎉 部署成功后

1. 测试地图生成功能
2. 检查所有配置选项
3. 如遇问题查看平台日志
4. 享受你的在线地图生成器！
