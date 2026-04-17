"""
embed-daily-words-audio.py
歌曲MP3离线嵌入脚本

功能：
1. 从HTML中提取 Cloudflare Worker 代理的歌曲音频URL
2. 通过 byfuns API 获取真实 MP3 数据（可能需要二次请求）
3. 转换为 base64 内嵌到 HTML，替换外链

注意：
- 单词/例句发音已由 generate-today-words.py 使用 speechSynthesis 实现
- 本脚本只处理歌曲MP3的离线嵌入

Usage:
  python embed-daily-words-audio.py <html_file> [output_file]
  python embed-daily-words-audio.py  # 自动查找当天文件
"""

import re
import sys
import os
import base64
import urllib.request
import ssl
import time

# 创建不验证SSL的context（解决某些环境SSL错误）
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE
OPENER = urllib.request.build_opener(urllib.request.HTTPSHandler(context=SSL_CONTEXT))


def get_mp3_from_byfuns(mp3_id):
    """通过 byfuns API 获取真实 MP3 数据"""
    api_url = f'https://api.byfuns.top/1/?id={mp3_id}'
    
    req = urllib.request.Request(api_url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    
    with OPENER.open(req, timeout=15) as resp:
        data = resp.read()
    
    # byfuns可能返回直链URL（需要再请求一次）或直接返回MP3
    text = data.decode('utf-8', errors='ignore').strip()
    
    # 如果是URL，再请求一次获取MP3
    if text.startswith('http'):
        print(f"    Got redirect URL, fetching MP3...")
        req2 = urllib.request.Request(text, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com'
        })
        with OPENER.open(req2, timeout=20) as resp2:
            mp3_data = resp2.read()
        return mp3_data
    else:
        # 直接是MP3数据
        return data


def embed_song_mp3(html_content):
    """4月15日方案：不再内嵌MP3，歌曲使用外链按钮
    保留函数签名以兼容原调用，但不做任何处理
    """
    # 新方案不再需要内嵌MP3，歌曲通过外链按钮播放
    # 如果将来需要恢复内嵌功能，只需在此函数中实现
    print("[SKIP] 歌曲使用外链按钮，不再需要内嵌MP3")
    return html_content


def main():
    from datetime import datetime
    from pathlib import Path
    
    if len(sys.argv) < 2:
        # 自动查找当天文件
        today = datetime.now().strftime('%Y-%m-%d')
        html_path = f"每日英语单词_{today}.html"
        
        if not Path(html_path).exists():
            # 尝试找最新的文件
            files = sorted(Path('.').glob('每日英语单词_*.html'), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                html_path = str(files[0])
            else:
                print("Error: No daily words HTML file found")
                sys.exit(1)
        
        output_path = html_path
        print(f"[*] Auto-detected file: {html_path}")
    else:
        html_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else html_path

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    print(f"[*] Reading: {html_path}")
    original_size = len(html)
    
    # 嵌入歌曲MP3
    html = embed_song_mp3(html)
    
    # 保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    final_size = os.path.getsize(output_path)
    print(f"[OK] Done! HTML size: {original_size:,} -> {final_size:,} bytes (delta +{final_size - original_size:,})")


if __name__ == "__main__":
    main()
