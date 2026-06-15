[app]

# 应用名称
title = RadAtlas 影像图鉴助手

# 包名
package.name = radatlas

# 包域名
package.domain = org.radatlas

# 源码目录（包含所有 .py 文件的根目录）
source.dir = .

# 包含目录（递归包含子目录中的源码）
source.include_exts = py,png,jpg,kv,atlas,ttf,otf,json,txt

# 排除不需要的文件
source.exclude_exts = spec,md,gitignore

# 排除不需要的目录
source.exclude_dirs = tests,bin,build,.git,.github,.buildozer,__pycache__,assets/icons,assets/fonts

# 应用版本
version = 1.0.0

# 依赖
requirements = python3==3.11.6,kivy==2.3.0,Pillow,cryptography,requests,pyjnius

# Android 权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA

# 自动接受 Android SDK 许可证
android.accept_sdk_license = True

# Android API 级别
android.api = 33
android.minapi = 24
android.ndk = 28c

# 架构
android.archs = arm64-v8a, armeabi-v7a

# 图标
# android.icon = assets/icons/icon.png

# 启动画面
# android.presplash = assets/icons/presplash.png

# 方向
orientation = portrait

# 全屏
fullscreen = 0

# Android 启动模式
android.allow_backup = True

# 日志级别
log_level = 2

# 是否使用 p4a 预编译
# p4a.branch = master
