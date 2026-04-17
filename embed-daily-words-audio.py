"""
embed-daily-words-audio.py
歌曲MP3离线嵌入脚本

功能：
1. 从HTML中提取 Cloudflare Worker 代理的歌曲音频URL
2. 通过 byfuns API 获取真实 MP3 数据
3. 转换为 base64 内嵌到 HTML，替换外链

注意：
- 单词/例句发音已由 generate-today-words.py 使用 speechSynthesis 实现（无需edge-tts）
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
import time


def embed_song_mp3(html_content):
    """从 HTML 中提取 Worker URL，下载 MP3 并 base64 嵌入，替换 src"""
    
    # 找所有指向 Worker 的 audio src（id是纯数字）
    pattern = re.compile(r'<audio[^>]+src="(https://quiet-term-cc2f\.zjunxcr\.workers\.dev/proxy/(\d+)[^"]*)"')
    matches = pattern.findall(html_content)
    
    if not matches:
        print("[SKIP] No song audio with Worker URL found in HTML")
        return html_content
    
    print(f"[*] Found {len(matches)} song audio(s) with Worker URL, embedding as base64...")
    
    for worker_url, mp3_id in matches:
        try:
            # 通过 byfuns API 获取真实 MP3
            api_url = f'https://api.byfuns.top/1/?id={mp3_id}'
            print(f"    Fetching MP3 id={mp3_id} via byfuns API...")
            
            req = urllib.request.Request(api_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://music.163.com'
            })
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                mp3_data = resp.read()
            
            print(f"    Downloaded: {len(mp3_data):,} bytes")
            
            # 转 base64
            b64_str = base64.b64encode(mp3_data).decode()
            data_uri = f'data:audio/mpeg;base64,{b64_str}'
            
            # 替换 HTML 中的 src
            html_content = html_content.replace(
                f'src="{worker_url}"',
                f'src="{data_uri}"'
            )
            
            print(f"    Embedded OK! HTML grew by {len(mp3_data)*4//3:,} bytes (base64)")
            time.sleep(0.5)  # 避免请求过快
            
        except Exception as e:
            print(f"    [WARN] Failed to embed: {e}")
    
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
    print(f"[OK] Done! HTML size: {original_size:,} -> {final_size:,} bytes (Δ +{final_size - original_size:,})")


if __name__ == "__main__":
    main()
