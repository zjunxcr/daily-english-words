"""
embed-daily-words-audio.py
音频嵌入脚本（完整版）

功能：
1. 扫描 HTML 中所有 speakWord / speakSentence 按钮，提取文本
2. 用 edge-tts (en-NZ-MitchellNeural) 生成 MP3，base64 嵌入 HTML
3. 注入 AUDIO_MAP + playAudio 函数，单引号键（JS对象字面量，非JSON）
4. 同时处理歌曲 MP3（Worker URL → base64 嵌入）

Usage:
  python embed-daily-words-audio.py [html_file] [output_file]
  python embed-daily-words-audio.py  # 自动查找当天文件
"""

import asyncio
import base64
import hashlib
import os
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ── SSL context（部分环境需要跳过验证）──────────────────────────────────
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE
OPENER = urllib.request.build_opener(urllib.request.HTTPSHandler(context=SSL_CONTEXT))

# ── edge-tts 语音设置 ─────────────────────────────────────────────────
VOICE_WORD     = "en-NZ-MitchellNeural"
VOICE_SENTENCE = "en-NZ-MitchellNeural"
RATE_WORD      = "-20%"
RATE_SENTENCE  = "-35%"


# ── edge-tts 生成音频 ──────────────────────────────────────────────────
async def tts_to_bytes(text: str, voice: str, rate: str) -> bytes:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    buf = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.extend(chunk["data"])
    return bytes(buf)


def make_audio_b64(text: str, is_sentence: bool = False) -> str:
    voice = VOICE_SENTENCE if is_sentence else VOICE_WORD
    rate  = RATE_SENTENCE  if is_sentence else RATE_WORD
    try:
        mp3 = asyncio.run(tts_to_bytes(text, voice, rate))
        return "data:audio/mpeg;base64," + base64.b64encode(mp3).decode()
    except Exception as e:
        print(f"    [WARN] TTS failed for '{text[:30]}': {e}")
        return ""


# ── 单词/例句 TTS 嵌入 ─────────────────────────────────────────────────
def embed_tts_audio(html: str) -> str:
    """
    扫描所有 onclick="speakWord(this,'...')" 和 speakSentence(this,'...')
    生成 edge-tts 音频并嵌入，注入 AUDIO_MAP + playAudio 函数。
    """
    # 提取所有唯一文本（避免重复生成）
    # 注意：HTML 中单引号被转义为 \'，正则提取后需要还原为真实撇号
    # 例如: "Here\'s" -> "Here's"
    # 修复（2026-04-20）：speakWord 也用正确正则，支持含撇号文本
    # [^'\\] 匹配普通字符，\\. 匹配转义序列（如 \' \" \\）
    def unescape(text):
        return text.replace("\\'", "'").replace('\\"', '"')

    word_texts     = set(unescape(t) for t in re.findall(r"speakWord\(this,'((?:[^'\\]|\\.)+)'\)", html))
    sentence_texts = set(unescape(t) for t in re.findall(r'speakSentence\(this,"((?:[^"\\]|\\.)*)"\)', html))
    sentence_texts |= set(unescape(t) for t in re.findall(r"speakSentence\(this,'((?:[^'\\]|\\.)+)'\)", html))

    total = len(word_texts) + len(sentence_texts)
    print(f"[*] Found {len(word_texts)} word texts + {len(sentence_texts)} sentence texts = {total} items")

    audio_map = {}
    for i, text in enumerate(sorted(word_texts), 1):
        print(f"  [{i}/{total}] word: {text[:40]}")
        uri = make_audio_b64(text, is_sentence=False)
        if uri:
            audio_map[text] = uri
        time.sleep(0.1)

    for i, text in enumerate(sorted(sentence_texts), len(word_texts) + 1):
        print(f"  [{i}/{total}] sentence: {text[:60]}")
        uri = make_audio_b64(text, is_sentence=True)
        if uri:
            audio_map[text] = uri
        time.sleep(0.1)

    print(f"[*] Generated {len(audio_map)}/{total} audio items")

    # ── 关键修复（2026-04-20）：改回4月15日方式
    # 直接写JS对象字面量，不用json.dumps（避免 \' 非法转义导致整个AUDIO_MAP解析失败）
    # 格式: AUDIO_MAP = { 'word': 'data:audio/mpeg;base64,...' }
    # base64不含单引号；键中含撇号(如"Don't")时，单引号键在JS里完全合法
    audio_lines = []
    for text, uri in audio_map.items():
        # Python双引号字符串里，text中的单引号/撇号就是普通字符，不需要转义
        audio_lines.append('  "' + text + '": "' + uri + '"')
    audio_map_str = ',\n'.join(audio_lines)

    inject_script = (
        '<script id="audio-pool">\n'
        '  const AUDIO_MAP = {\n'
        + audio_map_str + '\n'
        '  };\n'
        '  function playAudio(text, btn) {\n'
        '    const uri = AUDIO_MAP[text];\n'
        '    if (!uri) {\n'
        '      if (window.speechSynthesis) {\n'
        "        const u = new SpeechSynthesisUtterance(text);\n"
        '        u.lang = \'en-NZ\'; u.rate = 0.8;\n'
        '        if (btn) { btn.classList.add(\'playing\'); u.onend = () => btn.classList.remove(\'playing\'); }\n'
        '        window.speechSynthesis.speak(u);\n'
        '      }\n'
        '      return;\n'
        '    }\n'
        '    const audio = new Audio(uri);\n'
        '    if (btn) {\n'
        '      btn.classList.add(\'playing\');\n'
        '      audio.onended = () => btn.classList.remove(\'playing\');\n'
        '      audio.onerror = () => btn.classList.remove(\'playing\');\n'
        '    }\n'
        '    audio.play().catch(() => {\n'
        '      if (btn) btn.classList.remove(\'playing\');\n'
        '    });\n'
        '  }\n'
        '  function speakWord(btn, text)    { playAudio(text, btn); }\n'
        '  function speakSentence(btn, text) { playAudio(text, btn); }\n'
        '</script>\n'
    )

    # 替换原有 speechSynthesis script 块
    synth_pattern = re.compile(
        r'<script[^>]*>\s*const synth = window\.speechSynthesis.*?</script>',
        re.DOTALL
    )
    if synth_pattern.search(html):
        html = synth_pattern.sub(inject_script, html)
        print("[*] Replaced speechSynthesis script block with embedded audio player")
    else:
        html = html.replace('</body>', inject_script + '\n</body>')
        print("[*] Injected audio pool script before </body>")

    return html


# ── 歌曲 MP3 嵌入 ──────────────────────────────────────────────────────
def get_mp3_from_byfuns(mp3_id):
    api_url = f'https://api.byfuns.top/1/?id={mp3_id}'
    req = urllib.request.Request(api_url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    with OPENER.open(req, timeout=15) as resp:
        data = resp.read()
    text = data.decode('utf-8', errors='ignore').strip()
    if text.startswith('http'):
        req2 = urllib.request.Request(text, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com'
        })
        with OPENER.open(req2, timeout=20) as resp2:
            return resp2.read()
    return data


def embed_song_mp3(html: str) -> str:
    pattern = re.compile(
        r'<audio[^>]+src="(https://quiet-term-cc2f\.zjunxcr\.workers\.dev/proxy/(\d+)[^"]*)"'
    )
    matches = pattern.findall(html)
    if not matches:
        print("[SKIP] No song Worker URL found, skipping song embed")
        return html
    print(f"[*] Found {len(matches)} song audio(s), embedding...")
    for worker_url, mp3_id in matches:
        try:
            print(f"    Fetching song MP3 id={mp3_id}...")
            mp3_data = get_mp3_from_byfuns(mp3_id)
            b64 = base64.b64encode(mp3_data).decode()
            html = html.replace(f'src="{worker_url}"', f'src="data:audio/mpeg;base64,{b64}"')
            print(f"    Embedded song OK ({len(mp3_data):,} bytes)")
            time.sleep(0.5)
        except Exception as e:
            print(f"    [WARN] Song embed failed: {e}")
    return html


# ── 主流程 ───────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) >= 2:
        html_path   = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) >= 3 else html_path
    else:
        today = datetime.now().strftime('%Y-%m-%d')
        html_path = f"每日英语单词_{today}.html"
        if not Path(html_path).exists():
            files = sorted(Path('.').glob('每日英语单词_*.html'),
                           key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                html_path = str(files[0])
            else:
                print("Error: No daily words HTML file found")
                sys.exit(1)
        output_path = html_path
        print(f"[*] Auto-detected file: {html_path}")

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    orig_size = len(html)
    print(f"[*] Input: {html_path} ({orig_size:,} bytes)")

    # Step 1: 嵌入单词/例句 TTS 音频
    html = embed_tts_audio(html)

    # Step 2: 嵌入歌曲 MP3
    html = embed_song_mp3(html)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    final_size = os.path.getsize(output_path)
    print(f"[OK] Output: {output_path} ({orig_size:,} -> {final_size:,} bytes, +{final_size - orig_size:,})")


if __name__ == '__main__':
    main()
