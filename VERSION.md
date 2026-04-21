# 每日英语单词推送 - 基准版本

**基准日期**：2026-04-21  
**版本号**：v3.1（以此版本为后续迭代起点）

---

## 核心文件清单

| 文件 | 用途 | 说明 |
|------|------|------|
| `generate-today-words.py` | 主生成脚本 | 生成每日HTML页面，含单词、例句、兴趣加餐 |
| `auto_songs.py` | 歌曲自动化模块 | 60+首歌曲元数据库，网易云API获取歌词，去重追踪 |
| `embed-daily-words-audio.py` | 音频嵌入脚本 | edge-tts生成MP3，base64嵌入HTML |
| `send-all-v2.py` | 推送脚本 | 飞书机器人 + Server酱微信 + PageDrop三通道 |
| `requirements.txt` | 依赖清单 | Python依赖包列表 |
| `.github/workflows/daily-words.yml` | GitHub Actions | cron UTC 01:00（北京09:00）自动触发 |

---

## 功能特性（v3.1基准）

### 每日单词（10个）
- 7个新西兰日常口语词
- 3个雅思/移民词汇
- 含音标、音节拆分、词性、中文释义
- edge-tts（en-NZ-MitchellNeural）MP3发音，base64嵌入
- 词库200+，自动随机抽取，自动去重（读取memory.md）

### 兴趣加餐（按星期轮换）
- **周一/三/五** → 英文歌曲
  - 58首歌曲库，按日期哈希选择，去重追踪（已修复，写入memory.md）
  - 网易云API实时获取歌词（英文+中文翻译）
  - 自动检测生词，标注俚语/地道表达
  - 内嵌MP3音频，播放失败时外链备用
- **周二/四/六** → 老友记风格对话
  - 14个场景对话（2026-04-21扩充，原6个）
  - 每个场景含6行对话 + 3个重点句型解析
  - 含音标、音节拆分、语法注释
- **周日** → 轻松复习（回顾本周10个单词+迷你对话）

### 推送渠道
1. **飞书自定义机器人**（图文消息）
2. **Server酱 → 微信**（公众号推送）
3. **PageDrop公网链接**（完整HTML，可分享）

### GitHub Actions 自动化
- cron: `0 1 * * *`（UTC 01:00 = 北京 09:00）
- 完整pipeline：generate → embed audio → send
- WorkBuddy本地自动化：仅生成HTML，不推送（避免重复）

---

## 关键路径

```
单词去重记录：.codebuddy/automations/automation/memory.md（## 已用单词）
歌曲去重记录：.codebuddy/automations/automation/memory.md（## 歌曲历史）
GitHub仓库：zjunxcr/daily-english-words（branch: main）
```

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2026-04-03 | 首次推送，QQ邮箱渠道 |
| v2.0 | 2026-04-08 | 加入兴趣加餐；渠道切换为飞书 |
| v3.0 | 2026-04-13 | 词库自动化；兴趣加餐轮换；歌曲动态选择；周日复习版 |
| v3.1 | 2026-04-21 | 老友记对话从6个扩充到14个；修复歌曲去重追踪Bug |

---

*后续每次功能更新，请在此文件追加版本记录。*
