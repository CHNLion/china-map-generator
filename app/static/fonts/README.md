# 字体文件说明

## 📁 当前字体文件

本目录包含：
- **SourceHanSansSC-Regular.otf** (15.8MB) - Adobe 思源黑体 SC Regular

## 为什么需要字体文件？

在Linux服务器（如Render、Railway）上部署时，系统默认没有中文字体，导致地图上的中文显示为方框（□□□）。

## ✅ 自动加载

项目会自动优先使用此目录下的字体文件，无需手动配置。

程序会按以下优先级查找字体：
1. **本目录下的字体文件** （最高优先级）
   - SourceHanSansSC-Regular.otf
   - NotoSansSC-Regular.otf
   - wqy-microhei.ttc
2. Linux系统字体路径
3. Windows系统字体路径
4. macOS系统字体路径

## 📝 添加其他字体

如需添加其他字体，支持以下格式：
- `.otf` (OpenType Font)
- `.ttf` (TrueType Font)
- `.ttc` (TrueType Collection)

**推荐的开源中文字体**：
- **思源黑体** (Source Han Sans / Noto Sans SC) - 已内置 ✓
- **文泉驿微米黑** (WenQuanYi Micro Hei) - 轻量级
- **文泉驿正黑** (WenQuanYi Zen Hei) - 传统风格

### 下载其他字体

如需替换或添加其他字体：

```bash
# 文泉驿微米黑（2-3MB，更小）
wget https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc

# 思源黑体（备用下载地址）
wget https://mirrors.cloud.tencent.com/noto-cjk/NotoSansCJKsc-Regular.otf
```

## 🔍 验证字体

### 查看日志输出

程序启动时会输出字体加载信息：

```
✓ 成功加载中文字体: app/static/fonts/SourceHanSansSC-Regular.otf
  字体名称: Source Han Sans SC
  字体将强制应用到所有matplotlib绘图
```

### 生成测试地图

访问应用并生成一张地图，检查：
- ✅ 地区名称标签显示正常
- ✅ 地图标题显示正常
- ✅ 比例尺文字显示正常

## 📚 更多信息

详细的字体问题解决方案，请参考：[FONT_FIX_GUIDE.md](../../../FONT_FIX_GUIDE.md)

---

**最后更新**：2025-11-15  
**当前版本**：v2.2.1+


