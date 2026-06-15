# RadAtlas Android - 医学影像图鉴助手

楚雄州人民医院 医学影像中心 张兴文

## 简介
RadAtlas Android 是 RadAtlas 影像图鉴助手的 Android 移动版本，基于 Kivy 框架开发，支持医学影像浏览、诊断查询、笔记编辑和 AI 辅助诊断。

## 功能特性
- 疾病影像数据库浏览与搜索
- 多模态影像查看（CT/X-Ray/MRI/PET-CT）
- 医学笔记编辑（支持多级笔记）
- AI 影像诊断查询（支持多模型并行）
- 知识库查询（腾讯/火山方舟）
- 图像加密存储
- 用户认证与权限管理

## 技术栈
- Python 3.11+
- Kivy 2.3+ (跨平台 UI 框架)
- Buildozer (Android 打包)
- SQLite (本地数据库)
- cryptography (数据加密)

## 开发环境搭建

### 桌面调试
```bash
pip install kivy
python main.py
```

### Android 打包
```bash
pip install buildozer
buildozer android debug
```

## 项目结构
```
RadAtlas_Android/
├── main.py              # 应用入口
├── core/
│   ├── __init__.py
│   ├── models.py        # 数据库模型（复用桌面版）
│   └── ai_helper.py     # AI 调用模块（复用桌面版）
├── ui/
│   ├── __init__.py
│   ├── app.py           # 主应用类
│   ├── screens.py       # 各屏幕页面
│   ├── widgets.py       # 自定义组件
│   └── theme.py         # 主题配色
├── assets/
│   ├── icons/           # 图标资源
│   └── fonts/           # 字体资源
├── buildozer.spec       # Buildozer 打包配置
└── requirements.txt     # Python 依赖
```
