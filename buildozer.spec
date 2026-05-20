[app]

# 应用信息
title = LanFund
package.name = lanfund
package.domain = org.lanfund.app
source.dir = .
source.include_exts = py,txt
version = 1.0.0

# 依赖（纯 Python，交叉编译零障碍）
requirements = python3,flask,requests

# Android SDK 版本
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 27
android.ndk_api = 21
android.archs = arm64-v8a

# 入口
android.entrypoint = main.py
android.wakelock = True
android.orientation = portrait

# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# WebView 模式 —— APK 启动后打开一个全屏 WebView
android.webview = True
android.enable_android_webview = True

# 启动画面色
presplash.color = #0f1923

# 启动后自动加载的 URL（main.py 中会覆盖此值）
android.webview.url = http://127.0.0.1:8311

# 图标（用默认的）
# icon = icon.png

[buildozer]
log_level = 2
warn_on_root = 0
build_dir = ./.build
bin_dir = ./bin

# Docker 构建
docker_build_command = docker run -v %(source.dir)s:/home/host --rm --privileged -it kivy/buildozer-android-arm64-v8a:latest buildozer android debug
