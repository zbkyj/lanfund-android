"""
LanFund Android 入口
启动 Flask 后台服务器 → 打开 WebView → 显示基金实时估值
"""
import os, sys, threading, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

_ANDROID = False
try:
    from android.os import Build
    _ANDROID = True
except ImportError:
    pass


def start_flask(port=8311):
    from server import app
    # Flask 在后台线程阻塞运行
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main():
    port = 8311

    # 后台启动 Flask
    t = threading.Thread(target=start_flask, args=(port,), daemon=True)
    t.start()

    # 等服务器就绪（最多等 15 秒）
    import urllib.request
    ready = False
    for _ in range(30):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            ready = True
            break
        except Exception:
            time.sleep(0.5)

    if not ready:
        print("[LanFund] 服务器启动超时")
        return

    print(f"[LanFund] 就绪 http://127.0.0.1:{port}")

    if _ANDROID:
        # Python-for-Android: WebView 自动加载此 URL
        try:
            from android.activity import PythonActivity
            PythonActivity.setWebViewUrl(f"http://127.0.0.1:{port}")
            print("[LanFund] WebView 已指向本地服务器")
        except Exception as e:
            print(f"[LanFund] WebView 错误: {e}")
    else:
        print(f"[LanFund] 浏览器打开 http://127.0.0.1:{port}")

    # 保持主线程
    t.join()


if __name__ == "__main__":
    main()
