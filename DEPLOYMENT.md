# 部署到 Vercel

本项目支持部署到 Vercel 平台。

## 📋 前提条件

- GitHub 账号
- Vercel 账号（可使用 GitHub 登录）

## 🚀 部署步骤

### 方法一：通过 Vercel 网站部署（推荐）

1. **访问 Vercel**
   - 打开 [vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "New Project"
   - 选择 "Import Git Repository"
   - 选择 `china-map-generator` 仓库

3. **配置项目**
   - Project Name: `china-map-generator`（或自定义）
   - Framework Preset: 选择 "Other"
   - Root Directory: `./`（保持默认）
   - Build Command: 留空
   - Output Directory: 留空

4. **部署**
   - 点击 "Deploy"
   - 等待 2-3 分钟完成部署
   - 部署成功后会获得一个 `.vercel.app` 域名

### 方法二：使用 Vercel CLI

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录
vercel login

# 3. 在项目目录下运行
vercel

# 4. 按照提示完成配置
```

## ⚙️ 配置说明

项目已包含以下 Vercel 配置文件：

- `vercel.json` - Vercel 部署配置
- `.vercelignore` - 忽略上传的文件

## 📝 注意事项

### 1. 文件存储限制

⚠️ **重要**: Vercel 是无服务器平台，不支持持久化文件存储。

**当前配置**：
- 地图生成使用 Base64 编码直接返回
- 不保存文件到服务器
- 完全适配 Vercel 无状态特性

### 2. 执行时间限制

- **免费版**: 10秒超时限制
- **Pro版**: 60秒超时限制

**优化建议**：
- 大型地图可能需要较长生成时间
- 建议使用 Pro 版本以获得更长超时时间
- 或考虑优化地图生成性能

### 3. 内存限制

- **免费版**: 1024 MB
- **Pro版**: 3008 MB

项目使用 GeoPandas 和 Matplotlib，内存占用适中，免费版通常足够。

### 4. 环境变量（可选）

如需设置环境变量，在 Vercel 控制面板中添加：

- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `False`

## 🔗 自定义域名

1. 在 Vercel 项目设置中
2. 进入 "Domains"
3. 添加自定义域名
4. 按照提示配置 DNS

## 🔄 自动部署

- 推送到 GitHub `main` 分支会自动触发部署
- 每次推送都会创建预览部署
- 生产部署只在 main 分支上进行

## 🐛 常见问题

### 部署失败

**问题**: 依赖安装失败

**解决**:
- 检查 `requirements.txt` 格式
- 确保所有依赖版本兼容
- 查看 Vercel 部署日志

### 超时错误

**问题**: 地图生成超过10秒

**解决**:
- 升级到 Vercel Pro
- 优化地图生成代码
- 减少地图复杂度

### 内存不足

**问题**: 内存超过 1GB 限制

**解决**:
- 升级到 Vercel Pro
- 优化数据处理流程
- 使用更小的 Shapefile

## 📊 监控和日志

- 访问 Vercel 控制面板查看：
  - 部署状态
  - 运行时日志
  - 性能指标
  - 错误追踪

## 💡 替代方案

如果 Vercel 限制不满足需求，可考虑：

1. **Heroku** - 支持持久化存储（有免费额度）
2. **Railway** - 类似 Heroku，配置简单
3. **Render** - 免费版功能丰富
4. **自建服务器** - 完全控制，使用 Docker 部署

## 📚 相关文档

- [Vercel Python 部署文档](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Flask 部署最佳实践](https://flask.palletsprojects.com/en/2.0.x/deploying/)

