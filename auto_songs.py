"""
auto_songs - 自动化歌曲学习系统（入口模块）
兼容 generate-today-words.py 中的 import auto_songs
实际实现位于 auto_songs_latest.py
"""
from auto_songs_latest import (
    generate_auto_song_html,
    select_daily_song,
    get_used_songs,
    SONG_LIBRARY,
)

__all__ = [
    'generate_auto_song_html',
    'select_daily_song',
    'get_used_songs',
    'SONG_LIBRARY',
]
