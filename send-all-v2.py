"""
每日英语单词 - 全渠道推送 v2
功能：
1. 读取当天 HTML 文件
2. 上传到 PageDrop 获取公网链接
3. 推送到飞书（卡片消息）
4. 推送到 QQ（Qmsg酱）
5. 推送到微信（PushPlus）

配置：
- 飞书：WEBHOOK_URL（已配置）
- QQ：QMSG_KEY（需用户配置）
- 微信：PUSHPLUS_TOKEN（需用户配置）
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# 设置UTF-8编码，避免Windows控制台输出问题
sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/8d37d8fb-d868-4820-b5cf-c31153569508"
QMSG_KEY = os.environ.get("QMSG_KEY", "")
QMSG_API = "https://qmsg.zendee.cn/send"
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "SCT335607TXU66l0c7orQDokUTfbNPbmiZ")
SERVERCHAN_API = "https://sctapi.ftqq.com"

BASE_DIR = Path(__file__).resolve().parent

# ============ 工具函数 ============
def clean_text(value):
    return re.sub(r'\s+', ' ', re.sub(r'<.*?>', '', value or '')).strip()

def resolve_html_path():
    today = datetime.now().strftime('%Y-%m-%d')
    file_name = f'每日英语单词_{today}.html'
    candidates = [
        BASE_DIR / file_name,
        Path.home() / 'Desktop' / file_name,
    ]
    for p in candidates:
        if p.is_file():
            return p
    checked = '\n'.join(str(p) for p in candidates)
    raise SystemExit(f'未找到当天 HTML 文件：{file_name}\n已检查路径：\n{checked}')

def compute_html_hash(html_body):
    return hashlib.sha256(html_body.encode('utf-8')).hexdigest()

def upload_to_pagedrop(html_body, cache_path):
    """上传 HTML 到 PageDrop 获取公网 URL"""
    boundary = f'----WorkBuddyBoundary{uuid4().hex}'
    data = bytearray()
    data.extend(f'--{boundary}\r\n'.encode('utf-8'))
    data.extend(b'Content-Disposition: form-data; name="file"; filename="index.html"\r\n')
    data.extend(b'Content-Type: text/html; charset=utf-8\r\n\r\n')
    data.extend(html_body.encode('utf-8'))
    data.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

    request = urllib.request.Request(
        'https://pagedrop.dev/api/v1/sites',
        data=bytes(data),
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode('utf-8'))

    if payload.get('status') != 'success' or 'data' not in payload:
        raise RuntimeError(f'PageDrop 返回异常：{payload}')

    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return payload['data']['url']

def resolve_public_url(html_body, html_path):
    """获取或生成公网 URL"""
    cache_path = html_path.with_suffix('.pagedrop.json')
    current_hash = compute_html_hash(html_body)
    if cache_path.is_file():
        try:
            cache_data = json.loads(cache_path.read_text(encoding='utf-8'))
            cached_url = cache_data.get('data', {}).get('url', '').strip()
            cached_hash = cache_data.get('workbuddy', {}).get('html_sha256', '').strip()
            if cached_url and cached_hash == current_hash:
                return cached_url, 'cache'
        except json.JSONDecodeError:
            pass

    url = upload_to_pagedrop(html_body, cache_path)
    # 更新缓存中的hash
    cache_data = json.loads(cache_path.read_text(encoding='utf-8'))
    cache_data['workbuddy'] = {'html_sha256': current_hash}
    cache_path.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8')
    return url, 'pagedrop'

def extract_bonus(html_body):
    """提取兴趣加餐标题"""
    patterns = [
        r'<div class="bonus-title">(.*?)</div>',
        r'<div class="bonus-song-name">(.*?)</div>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_body, re.S)
        if match:
            return clean_text(match.group(1))
    return ""

def build_feishu_card(html_body, public_url):
    """构建飞书交互式卡片"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekday_names[today.weekday()]
    header_colors = ["blue", "turquoise", "green", "yellow", "orange", "violet", "indigo"]
    header_color = header_colors[today.weekday()]

    word_matches = re.findall(
        r'<div class="card (nz|ielts)">.*?<span class="word-en">(.*?)</span>.*?'
        r'<span class="phonetic">(.*?)</span>.*?'
        r'<div class="meaning-cn">(.*?)</div>',
        html_body, re.S
    )

    word_lines = []
    for i, (wtype, en, ph, cn) in enumerate(word_matches[:10], 1):
        tag = "🟢" if wtype == "nz" else "🔵"
        type_label = "NZ日常" if wtype == "nz" else "雅思"
        word_lines.append(f"**{tag} {i:02d}. {en}** {ph}\n{cn}")

    bonus_title = extract_bonus(html_body)

    elements = [
        {"tag": "div", "text": {"tag": "lark_md", "content": "🇳🇿 新西兰生活口语 + 🎓 雅思移民备考"}},
        {"tag": "hr"},
        {"tag": "div", "text": {"tag": "lark_md", "content": "\n".join(word_lines)}},
        {"tag": "hr"},
    ]

    if bonus_title:
        bonus_text = f"🎁 **兴趣加餐**\n{bonus_title}"
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": bonus_text}})
        elements.append({"tag": "hr"})

    if public_url:
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "📖 打开完整学习页（含听发音+歌曲）"},
                "url": public_url,
                "type": "primary"
            }]
        })

    elements.append({"tag": "note", "elements": [
        {"tag": "plain_text", "content": f"🌱 每天进步一点点！点上方按钮打开完整学习页，支持听发音、看歌词、学语法 🇳🇿 | {date_str}"}
    ]})

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📖 每日英语 10 词 · {date_str}（{weekday}）"},
                "template": header_color
            },
            "elements": elements
        }
    }
    return card

def send_to_feishu(card):
    """发送飞书消息"""
    data = json.dumps(card, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(FEISHU_WEBHOOK, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("StatusCode") == 0 or result.get("code") == 0:
                return True, "OK"
            else:
                return False, str(result)
    except Exception as e:
        return False, str(e)

def build_qq_message(html_body, public_url):
    """构建QQ消息文本"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekday_names[today.weekday()]

    word_matches = re.findall(
        r'<div class="card (nz|ielts)">.*?<span class="word-en">(.*?)</span>.*?'
        r'<span class="phonetic">(.*?)</span>.*?'
        r'<div class="meaning-cn">(.*?)</div>',
        html_body, re.S
    )

    lines = [
        f"📖 每日英语 10 词 · {date_str}（{weekday}）",
        "",
        "🇳🇿 新西兰生活口语 + 🎓 雅思移民备考",
        "",
        "━" * 20,
        "",
    ]

    for i, (wtype, en, ph, cn) in enumerate(word_matches[:10], 1):
        tag = "🟢" if wtype == "nz" else "🔵"
        lines.append(f"{tag} {i:02d}. {en} {ph}")
        lines.append(f"   {cn}")
        lines.append("")

    bonus_title = extract_bonus(html_body)
    if bonus_title:
        lines.extend([
            "━" * 20,
            "",
            f"🎁 兴趣加餐：{bonus_title}",
            "",
        ])

    if public_url:
        lines.extend([
            "━" * 20,
            "",
            "📱 完整学习页（含听发音+歌曲）：",
            public_url,
            "",
        ])

    lines.extend([
        "━" * 20,
        "",
        "🌱 每天进步一点点！",
        "坚持学习，你的新西兰生活已在路上 🇳🇿",
    ])

    return "\n".join(lines)

def send_to_qq(message):
    """发送消息到QQ（通过Qmsg酱）"""
    if not QMSG_KEY:
        return False, "QMSG_KEY 未配置"

    url = f"{QMSG_API}/{QMSG_KEY}"
    data = {"msg": message}
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')

    req = urllib.request.Request(url, data=encoded_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("success") or result.get("code") == 0:
                return True, "OK"
            else:
                return False, str(result)
    except Exception as e:
        return False, str(e)

def build_serverchan_content(html_body, public_url):
    """构建Server酱消息内容（Markdown格式）"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekday_names[today.weekday()]
    
    word_matches = re.findall(
        r'<div class="card (nz|ielts)">.*?<span class="word-en">(.*?)</span>.*?'
        r'<span class="phonetic">(.*?)</span>.*?'
        r'<div class="meaning-cn">(.*?)</div>',
        html_body, re.S
    )
    
    # 构建Markdown内容
    lines = [
        f"**📖 每日英语 10 词 · {date_str}（{weekday}）**",
        "",
        "> 🇳🇿 新西兰生活口语 + 🎓 雅思移民备考",
        "",
        "---",
        "",
    ]
    
    for i, (wtype, en, ph, cn) in enumerate(word_matches[:10], 1):
        tag = "🟢 NZ" if wtype == "nz" else "🔵 雅思"
        lines.append(f"**{i:02d}. {en}** `{ph}` {tag}")
        lines.append(f"> {cn}")
        lines.append("")
    
    bonus_title = extract_bonus(html_body)
    if bonus_title:
        lines.extend([
            "---",
            "",
            f"🎁 **兴趣加餐**：{bonus_title}",
            "",
        ])
    
    if public_url:
        lines.extend([
            "---",
            "",
            f"📱 **[打开完整学习页（含听发音+歌曲）]({public_url})**",
            "",
        ])
    
    lines.extend([
        "---",
        "",
        "🌱 每天进步一点点！",
        "坚持学习，你的新西兰生活已在路上 🇳🇿",
    ])
    
    return "\n".join(lines)

def send_to_serverchan(title, content):
    """发送消息到微信（通过Server酱）"""
    if not SERVERCHAN_KEY:
        return False, "SERVERCHAN_KEY 未配置"
    
    url = f"{SERVERCHAN_API}/{SERVERCHAN_KEY}.send"
    data = {
        "title": title,
        "desp": content
    }
    
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded_data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 0 or result.get("data", {}).get("errno") == 0:
                return True, "OK"
            else:
                return False, str(result)
    except Exception as e:
        return False, str(e)

# ============ 主流程 ============
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='指定HTML文件路径（不指定则自动找当天文件）')
    args, _ = parser.parse_known_args()

    today = datetime.now().strftime('%Y-%m-%d')
    print(f"[*] 每日英语单词推送 - {today}")
    print("=" * 50)

    print("\n[1/5] Reading HTML...")
    if args.file:
        html_path = Path(args.file)
    else:
        html_path = resolve_html_path()
    html_body = html_path.read_text(encoding='utf-8')
    print(f"  -> {html_path}")

    print("\n[2/5] Uploading to PageDrop...")
    public_url = ""
    try:
        public_url, source = resolve_public_url(html_body, html_path)
        print(f"  -> URL ({source}): {public_url}")
    except Exception as e:
        print(f"  -> Failed: {e}")

    print("\n[3/5] Sending to Feishu...")
    card = build_feishu_card(html_body, public_url)
    ok, msg = send_to_feishu(card)
    if ok:
        print("  -> ✓ Feishu sent OK!")
    else:
        print(f"  -> ✗ Feishu failed: {msg}")

    print("\n[4/5] Sending to QQ...")
    if QMSG_KEY:
        message = build_qq_message(html_body, public_url)
        ok, msg = send_to_qq(message)
        if ok:
            print("  -> ✓ QQ sent OK!")
        else:
            print(f"  -> ✗ QQ failed: {msg}")
    else:
        print("  -> ⚠ Skipped (QMSG_KEY not configured)")
        print("      访问 https://qmsg.zendee.cn/login 获取 Key")
        print("      然后设置环境变量: set QMSG_KEY=你的key")

    print("\n[5/5] Sending to WeChat (Server酱)...")
    if SERVERCHAN_KEY:
        title = f"📖 每日英语 10 词 · {datetime.now().strftime('%m-%d')}"
        desp = build_serverchan_content(html_body, public_url)
        ok, msg = send_to_serverchan(title, desp)
        if ok:
            print("  -> ✓ WeChat sent OK!")
        else:
            print(f"  -> ✗ WeChat failed: {msg}")
    else:
        print("  -> ⚠ Skipped (SERVERCHAN_KEY not configured)")
        print("      访问 https://sct.ftqq.com/ 扫码登录获取 SendKey")

    print("\n" + "=" * 50)
    print("Done!")
