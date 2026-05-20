"""
LanFund — 基金实时估值（服务端渲染）
首次打开页面直接显示数据，无需 JS 加载
"""

import os, json, threading, re
from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

_watch_list = ["110011", "000001", "161725"]
_list_lock = threading.Lock()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Referer": "http://fund.eastmoney.com/",
}

def fetch_funds(codes):
    """抓取基金实时数据"""
    result = {}
    threads = []
    lock = threading.Lock()

    def fetch(code):
        try:
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            r = requests.get(url, headers=HEADERS, timeout=8)
            r.encoding = "utf-8"
            m = re.search(r"jsonpgz\((.*)\);?\s*$", r.text.strip())
            if m:
                d = json.loads(m.group(1))
                with lock:
                    result[code] = {
                        "name": d.get("name", ""),
                        "dwjz": d.get("dwjz", "--"),
                        "gsz": d.get("gsz", "--"),
                        "gszzl": d.get("gszzl", "--"),
                        "gztime": d.get("gztime", ""),
                    }
        except:
            with lock:
                result[code] = None

    for c in codes:
        t = threading.Thread(target=fetch, args=(c,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=12)
    return result


@app.route("/")
def index():
    with _list_lock:
        codes = list(_watch_list)

    if not codes:
        rows = '<div class="empty">在下方输入基金代码添加</div>'
    else:
        data = fetch_funds(codes)
        rows = ""
        for c in codes:
            f = data.get(c)
            if not f:
                rows += f'<div class="item"><span class="code">{c}</span><span class="name err">无数据</span></div>'
                continue
            p = f["gszzl"]
            cls = "up" if p != "--" and float(p) >= 0 else "down"
            rows += f'''<div class="item" onclick="del('{c}')">
                <span class="code">{c}</span>
                <span class="name">{f["name"]}</span>
                <div class="price">
                    <span class="val">{f["gsz"]}</span>
                    <span class="pct {cls}">{p}%</span>
                </div>
                <span class="time">{f["gztime"][-5:]}</span>
            </div>'''

    return render_template_string(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>基金实时估值</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif}}
body{{background:#0f1923;color:#e8edf0;padding-bottom:100px}}
.header{{padding:16px;background:#1a2c38;position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between}}
.header h1{{font-size:18px}}
.actions{{display:flex;gap:8px}}
.btn{{padding:8px 14px;border:none;border-radius:8px;font-size:14px;cursor:pointer}}
.btn-primary{{background:#00c853;color:#000;font-weight:600}}
.btn-secondary{{background:#2a3f4e;color:#e8edf0}}
.btn:active{{opacity:.7}}
.add-bar{{display:flex;gap:8px;padding:12px 16px;background:#1a2c38;border-top:1px solid #2a3f4e;position:fixed;bottom:0;left:0;right:0;max-width:480px;margin:0 auto}}
.add-bar input{{flex:1;padding:10px 14px;background:#0f1923;border:1px solid #2a3f4e;border-radius:8px;color:#e8edf0;font-size:16px;outline:none}}
.add-bar input:focus{{border-color:#00c853}}
.list{{padding:8px 16px}}
.item{{display:flex;align-items:center;padding:12px 0;border-bottom:1px solid rgba(42,63,78,.4)}}
.code{{font-family:monospace;font-size:12px;color:#8899aa;width:70px}}
.name{{flex:1;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.name.err{{color:#8899aa;font-style:italic}}
.price{{text-align:right;margin-left:8px;font-family:monospace;font-size:14px}}
.price .val{{display:block}}
.price .pct{{font-size:16px;font-weight:700}}
.time{{font-size:11px;color:#8899aa;width:50px;text-align:right}}
.up{{color:#ff4444}}
.down{{color:#00c853}}
.empty{{text-align:center;padding:60px 20px;color:#8899aa;font-size:14px}}
.toast{{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#1a2c38;color:#e8edf0;padding:12px 24px;border-radius:10px;font-size:14px;z-index:99;border:1px solid #2a3f4e;animation:fade .3s}}
@keyframes fade{{from{{opacity:0;transform:translate(-50%,-40%)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
</style>
</head>
<body>
<div class="header">
  <h1>📈 基金实时估值</h1>
  <div class="actions">
    <button class="btn btn-secondary" onclick="location.reload()">🔄</button>
  </div>
</div>
<div class="list">{rows}</div>
<div class="add-bar">
  <input type="text" id="codeInput" placeholder="输入基金代码" maxlength="6" autocomplete="off">
  <button class="btn btn-primary" onclick="addFund()">添加</button>
</div>
<script>
function addFund(){{
  var c=document.getElementById("codeInput").value.trim();
  if(!c||c.length<6){{show("请输入6位代码");return}}
  var x=new XMLHttpRequest();
  x.open("POST","/api/add",true);
  x.setRequestHeader("Content-Type","application/json");
  x.onload=function(){{
    var d=JSON.parse(x.responseText);
    if(d.ok){{show("已添加 "+c);location.reload()}}
    else show(d.msg||"失败");
  }};
  x.onerror=function(){{show("网络错误")}};
  x.send(JSON.stringify({{code:c}}));
}}
function del(c){{
  if(!confirm("删除 "+c+"？"))return;
  var x=new XMLHttpRequest();
  x.open("POST","/api/remove",true);
  x.setRequestHeader("Content-Type","application/json");
  x.onload=function(){{location.reload()}};
  x.send(JSON.stringify({{code:c}}));
}}
function show(m){{
  var t=document.createElement("div");t.className="toast";t.textContent=m;
  document.body.appendChild(t);setTimeout(function(){{t.remove()}},2000);
}}
</script>
</body>
</html>""")


@app.route("/api/add", methods=["POST"])
def api_add():
    code = request.get_json(force=True).get("code", "").strip()
    if not code or len(code) != 6:
        return jsonify({"ok": False, "msg": "无效代码"})
    with _list_lock:
        if code not in _watch_list:
            _watch_list.append(code)
    return jsonify({"ok": True})


@app.route("/api/remove", methods=["POST"])
def api_remove():
    code = request.get_json(force=True).get("code", "").strip()
    with _list_lock:
        if code in _watch_list:
            _watch_list.remove(code)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8311, debug=False)
