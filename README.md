# 每日英语单词推送

每日自动生成 10 个英语单词（7个新西兰日常口语 + 3个雅思/移民词汇），推送到飞书和微信。

## 功能特点

- 📖 每日 10 词：新西兰生活口语 + 雅思移民词汇
- 🔊 点击发音：edge-tts 预生成音频，支持离线播放
- 🎵 兴趣加餐：周一/三/五/日英文歌曲，周二/四/六老友记对话
- 📱 双渠道推送：飞书 + 微信（Server酱）

## 项目结构

```
.
├── generate-today-words.py      # 生成每日单词 HTML
├── embed-daily-words-audio.py   # 嵌入音频数据
├── send-all-v2.py               # 推送到所有渠道
├── songs_db.py                  # 歌曲数据库
├── requirements.txt             # Python 依赖
└── .github/workflows/
    └── daily-words.yml          # GitHub Actions 定时任务
```

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 生成当天单词
python generate-today-words.py

# 嵌入音频
python embed-daily-words-audio.py

# 推送
python send-all-v2.py
```

## GitHub Actions 配置

1. Fork 本仓库
2. 设置 Secrets（Settings → Secrets and variables → Actions）：
   - `SERVERCHAN_KEY`: Server酱 SendKey（用于微信推送）
3. 定时任务每天 09:00（北京时间）自动运行
4. 支持手动触发（Actions → Daily English Words → Run workflow）

## 兴趣加餐轮换

| 星期 | 内容 | 主题 |
|------|------|------|
| 周一 | 🎵 英文歌曲 | Lemon Tree - 现在进行时 |
| 周二 | ☕ 老友记对话 | 口语表达 |
| 周三 | 🎵 英文歌曲 | You Are My Sunshine - 一般现在时 |
| 周四 | ☕ 老友记对话 | 口语表达 |
| 周五 | 🎵 英文歌曲 | Love Story - 过去进行时 |
| 周六 | ☕ 老友记对话 | 口语表达 |
| 周日 | 🎵 英文歌曲 | Seasons in the Sun - 现在完成时 |

## 技术栈

- Python 3.13
- edge-tts（文本转语音）
- GitHub Actions（定时任务）
- PageDrop（HTML 托管）
- 飞书机器人 / Server酱（消息推送）
