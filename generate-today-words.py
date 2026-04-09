"""
每日英语单词生成器 - 保持昨日样式
- 单词卡片：序号+音标+拼读+发音按钮+例句+语法标注
- 兴趣加餐：按星期轮换（歌曲/老友记对话/复习）
"""
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = Path(__file__).parent
TODAY = datetime.now().strftime('%Y-%m-%d')
OUTPUT = BASE_DIR / f"每日英语单词_{TODAY}.html"

# 导入歌曲数据库
from songs_db import SONGS_DB, WEEKDAY_SONGS, fetch_mp3_url

# 今日单词（7个NZ日常 + 3个雅思移民）
# 每个单词包含：word, phonetic, syllable, type, pos, meaning, example, example_cn, grammar, scene
# 以及 sentence_words: 例句中的3个生词 [word, phonetic, syllable, meaning]
WORDS = [
    # NZ日常口语 (7个)
    {"word": "rent", "phonetic": "/rent/", "syllable": "rent", "type": "nz", "pos": "n./v.",
     "meaning": "租金；租用",
     "example": "The rent is due on Monday.",
     "example_cn": "租金周一到期。",
     "grammar": "主系表结构 + 时间状语",
     "scene": "租房签约",
     "sentence_words": [
         ["due", "/djuː/", "due", "adj. 到期的"],
         ["Monday", "/ˈmʌndeɪ/", "Mon·day", "n. 周一"],
         ["the", "/ðə/", "the", "art. 这/那（定冠词）"]
     ]},
    {"word": "dairy", "phonetic": "/ˈdeəri/", "syllable": "dai·ry", "type": "nz", "pos": "n.",
     "meaning": "便利店（NZ特有，英式英语）",
     "example": "I'll grab milk from the dairy.",
     "example_cn": "我去便利店买牛奶。",
     "grammar": "will + 动词原形（将来时）",
     "scene": "日常购物",
     "sentence_words": [
         ["grab", "/ɡræb/", "grab", "v. 拿；取（口语常用）"],
         ["milk", "/mɪlk/", "milk", "n. 牛奶"],
         ["from", "/frɒm/", "from", "prep. 从..."]
     ]},
    {"word": "GP", "phonetic": "/ˌdʒiː ˈpiː/", "syllable": "G-P", "type": "nz", "pos": "n.",
     "meaning": "全科医生（General Practitioner）",
     "example": "You need to register with a GP.",
     "example_cn": "你需要注册一个全科医生。",
     "grammar": "need to + 动词原形（需要做某事）",
     "scene": "医疗注册",
     "sentence_words": [
         ["register", "/ˈredʒɪstə/", "re·gis·ter", "v. 注册；登记"],
         ["with", "/wɪð/", "with", "prep. 和...一起；在...处"],
         ["need", "/niːd/", "need", "v. 需要"]
     ]},
    {"word": "ASB", "phonetic": "/ˌeɪ es ˈbiː/", "syllable": "A-S-B", "type": "nz", "pos": "n.",
     "meaning": "奥克兰储蓄银行（新西兰四大银行之一）",
     "example": "I bank with ASB.",
     "example_cn": "我在ASB银行开户。",
     "grammar": "bank with（与...银行有业务往来）",
     "scene": "银行开户",
     "sentence_words": [
         ["bank", "/bæŋk/", "bank", "v. 把...存入银行；n. 银行"],
         ["with", "/wɪð/", "with", "prep. 和...一起"],
         ["I", "/aɪ/", "I", "pron. 我"]
     ]},
    {"word": "rubbish", "phonetic": "/ˈrʌbɪʃ/", "syllable": "rub·bish", "type": "nz", "pos": "n.",
     "meaning": "垃圾（NZ英式用法，美式用trash/garbage）",
     "example": "Rubbish day is Tuesday.",
     "example_cn": "垃圾日是周二。",
     "grammar": "名词作定语修饰day",
     "scene": "日常生活",
     "sentence_words": [
         ["day", "/deɪ/", "day", "n. 日子；天"],
         ["Tuesday", "/ˈtjuːzdeɪ/", "Tues·day", "n. 周二"],
         ["is", "/ɪz/", "is", "v. 是（be动词第三人称单数）"]
     ]},
    {"word": "settle in", "phonetic": "/ˈsetl ɪn/", "syllable": "set·tle in", "type": "nz", "pos": "phr.",
     "meaning": "安顿下来，适应新环境",
     "example": "It takes time to settle in.",
     "example_cn": "适应新环境需要时间。",
     "grammar": "It takes + 时间 + to do（做某事花费...）",
     "scene": "搬家适应",
     "sentence_words": [
         ["takes", "/teɪks/", "takes", "v. 花费（take的第三人称单数）"],
         ["time", "/taɪm/", "time", "n. 时间"],
         ["it", "/ɪt/", "it", "pron. 它（形式主语）"]
     ]},
    {"word": "cheers", "phonetic": "/tʃɪəz/", "syllable": "cheers", "type": "nz", "pos": "int.",
     "meaning": "谢谢；再见；干杯（NZ万能词）",
     "example": "Cheers for helping me!",
     "example_cn": "谢谢你的帮助！",
     "grammar": "Cheers for + doing（感谢做某事）",
     "scene": "日常致谢",
     "sentence_words": [
         ["helping", "/ˈhelpɪŋ/", "hel·ping", "v. 帮助（help的-ing形式）"],
         ["for", "/fɔː/", "for", "prep. 为了；因为"],
         ["me", "/miː/", "me", "pron. 我（宾格）"]
     ]},
    
    # 雅思/移民词汇 (3个)
    {"word": "opportunity", "phonetic": "/ˌɒpəˈtjuːnəti/", "syllable": "op·por·tu·ni·ty", "type": "ielts", "pos": "n.",
     "meaning": "机会",
     "example": "Studying abroad gives you great opportunities.",
     "example_cn": "出国留学给你很好的机会。",
     "grammar": "动名词作主语 + give sb sth",
     "scene": "留学申请",
     "sentence_words": [
         ["studying", "/ˈstʌdiɪŋ/", "stu·dy·ing", "v. 学习（study的-ing形式）"],
         ["abroad", "/əˈbrɔːd/", "a·broad", "adv. 在国外"],
         ["gives", "/ɡɪvz/", "gives", "v. 给（give的第三人称单数）"]
     ]},
    {"word": "reference", "phonetic": "/ˈrefrəns/", "syllable": "ref·er·ence", "type": "ielts", "pos": "n.",
     "meaning": "推荐信；参考",
     "example": "I need a reference from my employer.",
     "example_cn": "我需要雇主的推荐信。",
     "grammar": "need + 名词 + from（从...获得）",
     "scene": "求职申请",
     "sentence_words": [
         ["employer", "/ɪmˈplɔɪə/", "em·ploy·er", "n. 雇主；老板"],
         ["from", "/frɒm/", "from", "prep. 从..."],
         ["need", "/niːd/", "need", "v. 需要"]
     ]},
    {"word": "previous", "phonetic": "/ˈpriːviəs/", "syllable": "pre·vi·ous", "type": "ielts", "pos": "adj.",
     "meaning": "以前的",
     "example": "What is your previous address?",
     "example_cn": "你以前的地址是什么？",
     "grammar": "形容词previous修饰名词address",
     "scene": "表格填写",
     "sentence_words": [
         ["address", "/əˈdres/", "ad·dress", "n. 地址"],
         ["what", "/wɒt/", "what", "pron. 什么"],
         ["your", "/jɔː/", "your", "pron. 你的"]
     ]},
]

# ============ 生成单词卡片HTML ============
def generate_sentence_words(words_list):
    """生成例句生词HTML"""
    if not words_list:
        return ""
    items_html = ""
    for word_info in words_list:
        word, phonetic, syllable, meaning = word_info
        word_safe = word.replace("'", "\\'")
        items_html += f'''
    <div class="sw-item">
      <span class="sw-word">{word}</span>
      <span class="sw-phonetic">{phonetic}</span>
      <span class="sw-syllable">{syllable}</span>
      <span class="sw-mean">{meaning}</span>
      <button class="sw-speak" onclick="speakWord(this,'{word_safe}')">🔊</button>
    </div>'''
    return f'''
  <div class="sentence-words">
    <div class="sw-title">📝 例句生词</div>
    {items_html}
  </div>'''

def highlight_words_in_sentence(sentence, sentence_words):
    """在例句中高亮生词并标注音标"""
    if not sentence_words:
        return sentence
    
    # 按单词长度降序排序，避免短词替换影响长词
    sorted_words = sorted(sentence_words, key=lambda x: len(x[0]), reverse=True)
    
    result = sentence
    for word_info in sorted_words:
        word, phonetic, syllable, meaning = word_info
        # 创建高亮版本
        highlighted = f'<span class="hl-word">{word}<span class="hl-phonetic">{phonetic}</span></span>'
        # 替换（不区分大小写，但保持原大小写）
        import re
        result = re.sub(r'\b' + re.escape(word) + r'\b', highlighted, result, flags=re.IGNORECASE)
    
    return result

def generate_inline_highlight(sentence, sentence_words):
    """生成句内高亮生词（绿色块：单词+音标）"""
    if not sentence_words:
        return sentence
    
    result = sentence
    # 按单词长度降序，避免短词替换影响长词
    sorted_words = sorted(sentence_words, key=lambda x: len(x[0]), reverse=True)
    
    for word_info in sorted_words:
        word, phonetic, syllable, meaning = word_info
        # 绿色高亮块：单词 + 音标
        highlighted = f'<span class="inline-word"><span class="inline-text">{word}</span><span class="inline-phonetic">{phonetic}</span></span>'
        import re
        # 使用正则替换，保留原大小写
        result = re.sub(r'\b' + re.escape(word) + r'\b', highlighted, result, flags=re.IGNORECASE)
    
    return result

def generate_sentence_words_list(sentence_words):
    """生成例句生词列表（仿图片样式：单词+音标+拼读+含义+发音按钮）"""
    if not sentence_words:
        return ""
    
    items_html = ""
    for word_info in sentence_words:
        word, phonetic, syllable, meaning = word_info
        word_safe = word.replace("'", "\\'")
        items_html += f'''
      <div class="sw-item">
        <span class="sw-word">{word}</span>
        <span class="sw-phonetic">{phonetic}</span>
        <span class="sw-syllable">{syllable}</span>
        <span class="sw-mean">{meaning}</span>
        <button class="sw-speak" onclick="speakWord(this,'{word_safe}')">🔊</button>
      </div>'''
    
    return f'''
    <div class="sentence-words">
      <div class="sw-title">📝 例句生词</div>
      {items_html}
    </div>'''

def generate_word_card(w, index):
    word_safe = w['word'].replace("'", "\\'")
    ex_safe = w['example'].replace("'", "\\'")
    pos_class = "nz" if w['type'] == 'nz' else "ielts"
    pos_label = "NZ日常" if w['type'] == 'nz' else "雅思核心"
    
    # 生成句内高亮例句
    highlighted_example = generate_inline_highlight(w['example'], w.get('sentence_words', []))
    # 生成生词列表
    sentence_words_html = generate_sentence_words_list(w.get('sentence_words', []))
    
    return f'''
    <div class="card {pos_class}">
      <div class="card-header">
        <span class="word-index">{index:02d}</span>
        <span class="word-en">{w['word']}</span>
        <span class="pos-badge">{pos_label}</span>
      </div>
      <div class="phonetic-row">
        <span class="phonetic">{w['phonetic']}</span>
        <span class="syllable">{w['syllable']}</span>
        <button class="speak-btn" onclick="speakWord(this,'{word_safe}')">
          <svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
          听发音
        </button>
      </div>
      <div class="scene-tag">🏠 {w['scene']}</div>
      <div class="meaning-cn">{w['meaning']}</div>
      <div class="example-block">
        <div class="example-en">"{highlighted_example}"</div>
        <div class="example-cn">{w['example_cn']}</div>
        <div class="example-actions">
          <button class="speak-ex-btn" onclick="speakSentence(this,'{ex_safe}')">
            <svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
            听例句
          </button>
          <span class="grammar-tag">📝 语法：{w['grammar']}</span>
        </div>
      </div>
      {sentence_words_html}
    </div>'''

# ============ 兴趣加餐：按星期轮换 ============

# 对话生词词库
DIALOGUE_WORDS_DICT = {
    "starving": "饿极了",
    "grab": "拿，取",
    "bite": "一口（食物）",
    "mood": "心情，情绪",
    "pizza": "披萨",
    "wanting": "想要",
    "try": "尝试",
    "treat": "请客",
    "Dutch": "荷兰的（go Dutch = AA制）",
    "Fancy": "真想不到",
    "seeing": "看见",
    "grabbing": "拿，买",
    "coffee": "咖啡",
    "Mind": "介意",
    "join": "加入",
    "Actually": "其实",
    "ran into": "偶遇",
    "Really": "真的吗",
    "What's up": "怎么了",
    "advice": "建议",
    "something": "某事",
    "Dude": "哥们儿",
    "dishes": "碗碟",
    "leave": "留下",
    "sink": "水槽",
    "three": "三",
    "days": "天",
    "right after": "就在...之后",
    "show": "节目",
    "said": "说（过去式）",
    "yesterday": "昨天",
    "getting up": "起床",
}

def get_word_meaning(word):
    """获取单词中文含义"""
    return DIALOGUE_WORDS_DICT.get(word, "")

def generate_friends_dialogue():
    """周二、四、六：老友记风格场景对话"""
    # 每个对话包含：speaker, text, translation, words（生词列表：[word, phonetic]）
    dialogues = [
        {
            "scene": "☕ 咖啡馆偶遇",
            "dialogue": [
                ("A", "Hey! Fancy seeing you here!", "嘿！真巧在这儿碰到你！", 
                 [["Fancy", "/ˈfænsi/"], ["seeing", "/ˈsiːɪŋ/"]]),
                ("B", "Oh hey! I was just grabbing a coffee before work.", "哦嘿！我上班前过来买杯咖啡。",
                 [["grabbing", "/ˈɡræbɪŋ/"], ["coffee", "/ˈkɒfi/"]]),
                ("A", "Same here. Mind if I join you?", "我也是。介意我一起坐吗？",
                 [["Mind", "/maɪnd/"], ["join", "/dʒɔɪn/"]]),
                ("B", "Not at all! Actually, I'm glad I ran into you.", "完全不介意！其实我很高兴碰到你。",
                 [["Actually", "/ˈæktʃuəli/"], ["ran into", "/ræn ˈɪntuː/"]]),
                ("A", "Really? What's up?", "真的吗？怎么了？",
                 [["Really", "/ˈrɪəli/"], ["What's up", "/wɒts ʌp/"]]),
                ("B", "I need your advice on something...", "我需要你帮我出出主意...",
                 [["advice", "/ədˈvaɪs/"], ["something", "/ˈsʌmθɪŋ/"]]),
            ],
            "expressions": [
                {"en": "Fancy seeing you here!", "phonetic": "/ˈfænsi ˈsiːɪŋ juː hɪər/", "syllable": "Fan·cy see·ing you here", "grammar": "感叹句：Fancy + doing（真巧...）", "cn": "真巧在这儿碰到你！（惊喜偶遇）"},
                {"en": "Mind if I join you?", "phonetic": "/maɪnd ɪf aɪ dʒɔɪn juː/", "syllable": "Mind if I join you", "grammar": "礼貌询问：Mind if...（介意我...吗）", "cn": "介意我一起吗？（礼貌询问）"},
                {"en": "I ran into you", "phonetic": "/aɪ ræn ˈɪntuː juː/", "syllable": "I ran in·to you", "grammar": "一般过去时：run into = 偶遇", "cn": "我碰到你了（run into = 偶遇）"},
            ]
        },
        {
            "scene": "🏠 合租室友聊天",
            "dialogue": [
                ("A", "Dude, we need to talk about the dishes.", "兄弟，我们得聊聊碗的事儿。",
                 [["Dude", "/djuːd/"], ["dishes", "/ˈdɪʃɪz/"]]),
                ("B", "Oh no, did I leave them in the sink again?", "哦不，我又把碗扔水槽里了？",
                 [["leave", "/liːv/"], ["sink", "/sɪŋk/"]]),
                ("A", "It's been three days, man.", "都三天了，哥们儿。",
                 [["three", "/θriː/"], ["days", "/deɪz/"]]),
                ("B", "My bad! I'll do them right after this show.", "我的错！这集看完我就去洗。",
                 [["right after", "/raɪt ˈɑːftə/"], ["show", "/ʃəʊ/"]]),
                ("A", "You said that yesterday.", "你昨天也是这么说的。",
                 [["said", "/sed/"], ["yesterday", "/ˈjestədeɪ/"]]),
                ("B", "Okay okay, I'm getting up now...", "好好好，我现在就去...",
                 [["getting up", "/ˈɡetɪŋ ʌp/"]]),
            ],
            "expressions": [
                {"en": "My bad!", "phonetic": "/maɪ bæd/", "syllable": "My bad", "grammar": "口语省略：My bad = I'm sorry", "cn": "我的错！（口语化道歉）"},
                {"en": "I'll do them right after...", "phonetic": "/aɪl duː ðəm raɪt ˈɑːftə/", "syllable": "I'll do them right af·ter", "grammar": "将来时：will + 动词原形", "cn": "我...之后马上做"},
                {"en": "You said that yesterday.", "phonetic": "/juː sed ðæt ˈjestədeɪ/", "syllable": "You said that yes·ter·day", "grammar": "一般过去时：say → said", "cn": "你昨天也是这么说的。（吐槽专用）"},
            ]
        },
        {
            "scene": "🍕 约饭",
            "dialogue": [
                ("A", "I'm starving. Wanna grab a bite?", "我饿死了。去吃点东西？",
                 [["starving", "/ˈstɑːvɪŋ/"], ["grab", "/ɡræb/"], ["bite", "/baɪt/"]]),
                ("B", "Sure! What are you in the mood for?", "好啊！你想吃什么？",
                 [["mood", "/muːd/"]]),
                ("A", "How about that new pizza place?", "那家新开的披萨店怎么样？",
                 [["pizza", "/ˈpiːtsə/"]]),
                ("B", "Oh, I've been wanting to try that!", "哦，我一直想去试试！",
                 [["wanting", "/ˈwɒntɪŋ/"], ["try", "/traɪ/"]]),
                ("A", "Great! My treat this time.", "太好了！这次我请客。",
                 [["treat", "/triːt/"]]),
                ("B", "No way, let's go Dutch.", "不行，我们AA吧。",
                 [["Dutch", "/dʌtʃ/"]]),
            ],
            "expressions": [
                {"en": "Wanna grab a bite?", "phonetic": "/ˈwɒnə ɡræb ə baɪt/", "syllable": "Wan·na grab a bite", "grammar": "口语省略：Wanna = Want to", "cn": "去吃点东西？（bite = 一口食物）"},
                {"en": "What are you in the mood for?", "phonetic": "/wɒt ɑːr juː ɪn ðə muːd fɔːr/", "syllable": "What are you in the mood for", "grammar": "固定搭配：in the mood for（想...的心情）", "cn": "你想吃什么？/你想干嘛？"},
                {"en": "go Dutch", "phonetic": "/ɡəʊ dʌtʃ/", "syllable": "go Dutch", "grammar": "习语：Dutch = 荷兰的（各自付账）", "cn": "AA制（各自付账）"},
            ]
        },
    ]
    # 根据日期选择对话（循环使用）
    import hashlib
    day_hash = int(hashlib.md5(TODAY.encode()).hexdigest(), 16)
    d = dialogues[day_hash % len(dialogues)]
    
    dialogue_html = ""
    for speaker, text, trans, words in d["dialogue"]:
        text_safe = text.replace("'", "\\'")
        # 生成句内高亮
        highlighted_text = text
        for word, phonetic in words:
            import re
            highlighted = f'<span class="inline-word"><span class="inline-text">{word}</span><span class="inline-phonetic">{phonetic}</span></span>'
            highlighted_text = re.sub(r'\b' + re.escape(word) + r'\b', highlighted, highlighted_text, flags=re.IGNORECASE)
        
        # 生成该句的生词解释列表（带发音按钮）
        words_detail_html = ""
        if words:
            for word, phonetic in words:
                # 从预设的词库获取中文含义
                word_meaning = get_word_meaning(word)
                word_safe = word.replace("'", "\\'")
                words_detail_html += f'<span class="dw-item"><b>{word}</b> {phonetic} {word_meaning}<button class="dw-speak" onclick="speakWord(this,\'{word_safe}\')">🔊</button></span>'
        
        dialogue_html += f'''
        <div class="dialogue-line">
          <div class="dialogue-en-row">
            <span class="speaker">{speaker}:</span>
            <span class="dialogue-text">{highlighted_text}</span>
          </div>
          <div class="dialogue-cn">{trans}</div>
          <div class="dialogue-words">{words_detail_html}</div>
          <button class="dialogue-speak-btn" onclick="speakSentence(this,'{text_safe}')">
            <svg viewBox="0 0 24 24" width="12" height="12"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
            听这句
          </button>
        </div>'''
    
    expressions_html = ""
    for ex in d["expressions"]:
        ex_safe = ex['en'].replace("'", "\\'")
        phonetic = ex.get('phonetic', '')
        syllable = ex.get('syllable', '')
        grammar = ex.get('grammar', '')
        expressions_html += f'''
        <div class="expression-card">
          <div class="ex-header">
            <span class="ex-en">"{ex['en']}"</span>
            <button class="ex-speak" onclick="speakWord(this,'{ex_safe}')">🔊</button>
          </div>
          <div class="ex-phonetic">{phonetic}</div>
          <div class="ex-meta">
            <span class="ex-syllable">{syllable}</span>
            <span class="ex-grammar">{grammar}</span>
          </div>
          <div class="ex-cn">{ex['cn']}</div>
        </div>'''
    
    return f'''
<div class="bonus-section friends-day">
  <div class="bonus-title">☕ 兴趣加餐 · 老友记风格对话</div>
  <div class="bonus-content">
    <div class="scene-title">{d['scene']}</div>
    <div class="dialogue-box">
      {dialogue_html}
    </div>
    <div class="expressions-box">
      <div class="expressions-title">🗣️ 可直接套用的口语表达（点击🔊听发音）</div>
      {expressions_html}
    </div>
    <div class="bonus-tip">
      <strong>💡 学习建议：</strong>大声朗读对话3遍，然后遮住英文只看中文试着翻译，最后模仿语气跟读录音。把这些表达用到今天的聊天里！
    </div>
  </div>
</div>'''

def generate_song_section():
    """生成歌曲兴趣加餐（周一、三、五、日）"""
    weekday = datetime.now().weekday()
    song_key = WEEKDAY_SONGS[weekday]
    song = SONGS_DB[song_key]
    
    # 获取MP3链接
    mp3_url = fetch_mp3_url(song["netease_id"])
    
    # 生成歌词HTML（带俚语高亮）
    lyrics_html = ""
    for line in song["lyrics"]:
        en = line["en"]
        zh = line["zh"]
        slang_html = ""
        
        # 如果有俚语标注
        if line.get("slang"):
            for slang in line["slang"]:
                slang_html += f'<div class="slang-note">💡 <b>{slang["word"]}</b>: {slang["note"]}</div>'
        
        lyrics_html += f'''
      <div class="lyric-line">
        <div class="lyric-en">{en}</div>
        <div class="lyric-zh">{zh}</div>
        {slang_html}
      </div>'''
    
    # 生成关键词学习卡片
    keywords_html = ""
    for kw in song["keywords"]:
        phrase_safe = kw["phrase"].replace("'", "\\'")
        keywords_html += f'''
      <div class="keyword-card">
        <div class="kw-header">
          <span class="kw-phrase">{kw["phrase"]}</span>
          <button class="kw-speak" onclick="speakWord(this,'{phrase_safe}')">🔊</button>
        </div>
        <div class="kw-phonetic">{kw["phonetic"]}</div>
        <div class="kw-meta">
          <span class="kw-syllable">{kw["syllable"]}</span>
          <span class="kw-grammar">{kw["grammar"]}</span>
        </div>
        <div class="kw-mean">{kw["meaning"]}</div>
      </div>'''
    
    # 播放器HTML
    player_html = f'''
    <div class="song-player">
      <audio controls preload="none">
        <source src="{mp3_url or '#'}" type="audio/mpeg">
        您的浏览器不支持音频播放
      </audio>
    </div>''' if mp3_url else '<div class="song-player-error">⚠️ 音频链接获取失败，请手动搜索歌曲</div>'
    
    return f'''
<div class="bonus-section song-day">
  <div class="bonus-title">🎵 兴趣加餐 · 听歌学英语</div>
  <div class="bonus-content">
    <div class="song-header">
      <div class="song-info">
        <div class="song-name">{song["name"]} <span class="song-year">({song["year"]})</span></div>
        <div class="song-artist">🎤 {song["artist"]}</div>
        <div class="song-tense">
          <span class="tense-badge">{song["tense"]}</span>
          <span class="tense-en">{song["tense_en"]}</span>
        </div>
        <div class="tense-rule">📌 {song["tense_rule"]}</div>
      </div>
    </div>
    {player_html}
    <div class="lyrics-box">
      <div class="lyrics-title">🎶 歌词学习（橙色高亮为俚语/地道表达）</div>
      {lyrics_html}
    </div>
    <div class="keywords-box">
      <div class="keywords-title">🎯 重点句型解析（点击🔊听发音）</div>
      <div class="keywords-grid">
        {keywords_html}
      </div>
    </div>
    <div class="bonus-tip">
      <strong>💡 学习建议：</strong>先听1遍熟悉旋律，然后对照歌词跟唱2遍，重点模仿橙色标注的地道表达。最后遮住英文歌词，试着用今天学的时态复述歌曲内容！
    </div>
  </div>
</div>'''

def generate_bonus():
    weekday = datetime.now().weekday()
    if weekday in [1, 3, 5]:  # 周二、四、六 → 老友记对话
        return generate_friends_dialogue()
    else:  # 周一、三、五、日 → 英文歌曲
        return generate_song_section()

# ============ 完整HTML模板（保持昨日样式） ============
HTML_TEMPLATE = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>每日英语单词 · {TODAY}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%);
      min-height: 100vh;
      font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
      padding: 20px 16px 40px;
      color: #263238;
    }}
    header {{
      text-align: center;
      margin-bottom: 28px;
      padding: 28px 20px 22px;
      background: linear-gradient(120deg, #43a047, #1e88e5);
      border-radius: 20px;
      color: #fff;
      box-shadow: 0 6px 24px rgba(30,136,229,0.25);
    }}
    header .date-label {{ font-size: 15px; letter-spacing: 2px; opacity: 0.88; margin-bottom: 8px; }}
    header h1 {{ font-size: 30px; font-weight: 800; letter-spacing: 4px; text-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
    header .subtitle {{ font-size: 13px; margin-top: 10px; opacity: 0.82; letter-spacing: 1px; }}
    .tag-bar {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }}
    .tag {{ font-size: 12px; padding: 4px 14px; border-radius: 20px; font-weight: 600; letter-spacing: 1px; }}
    .tag-nz    {{ background: #c8e6c9; color: #2e7d32; }}
    .tag-ielts {{ background: #bbdefb; color: #1565c0; }}
    .card {{
      background: #fff;
      border-radius: 18px;
      padding: 22px 20px 20px;
      margin-bottom: 18px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.08);
      position: relative;
      overflow: hidden;
    }}
    .card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 5px; height: 100%; border-radius: 18px 0 0 18px; }}
    .card.nz::before    {{ background: linear-gradient(180deg, #43a047, #a5d6a7); }}
    .card.ielts::before {{ background: linear-gradient(180deg, #1e88e5, #90caf9); }}
    .card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }}
    .word-index {{ font-size: 13px; font-weight: 700; color: #9e9e9e; min-width: 26px; }}
    .word-en {{ font-size: 28px; font-weight: 800; color: #1a237e; letter-spacing: 1px; }}
    .pos-badge {{ font-size: 11px; padding: 2px 10px; border-radius: 10px; font-weight: 600; margin-left: auto; }}
    .nz .pos-badge    {{ background: #e8f5e9; color: #2e7d32; }}
    .ielts .pos-badge {{ background: #e3f2fd; color: #1565c0; }}
    .phonetic-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-left: 36px; flex-wrap: wrap; }}
    .phonetic {{ font-size: 17px; color: #757575; font-family: 'Segoe UI', Arial, sans-serif; letter-spacing: 1px; }}
    .syllable {{ font-size: 14px; color: #ff6f00; font-weight: 700; background: #fff8e1; padding: 2px 10px; border-radius: 8px; letter-spacing: 2px; }}
    .speak-btn {{
      display: inline-flex; align-items: center; gap: 5px;
      background: linear-gradient(120deg, #43a047, #1e88e5); color: #fff;
      border: none; border-radius: 20px; padding: 6px 16px;
      font-size: 14px; font-weight: 600; cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
      box-shadow: 0 2px 8px rgba(30,136,229,0.25); letter-spacing: 1px;
    }}
    .speak-btn:active {{ transform: scale(0.95); }}
    .speak-btn.playing {{ background: linear-gradient(120deg, #fb8c00, #f4511e); }}
    .speak-btn svg {{ width: 16px; height: 16px; fill: #fff; }}
    .speak-ex-btn {{
      display: inline-flex; align-items: center; gap: 4px;
      background: #e3f2fd; color: #1565c0; border: none;
      border-radius: 14px; padding: 6px 14px; font-size: 13px;
      font-weight: 600; cursor: pointer; transition: background 0.15s;
    }}
    .speak-ex-btn:hover {{ background: #bbdefb; }}
    .speak-ex-btn svg {{ width: 14px; height: 14px; fill: #1565c0; }}
    .grammar-tag {{ font-size: 12px; color: #7b1fa2; background: #f3e5f5; padding: 6px 12px; border-radius: 12px; font-weight: 600; }}
    
    /* 例句生词列表 - 仿图片样式 */
    .sentence-words {{ margin: 12px 0 0 36px; background: #fff; border-radius: 12px; padding: 14px 16px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
    .sw-title {{ font-size: 14px; color: #666; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }}
    .sw-item {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; padding: 8px 0; border-bottom: 1px dashed #eee; }}
    .sw-item:last-child {{ border-bottom: none; margin-bottom: 0; }}
    .sw-word {{ font-size: 18px; font-weight: 700; color: #1976d2; min-width: 70px; }}
    .sw-phonetic {{ font-size: 14px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; }}
    .sw-syllable {{ font-size: 13px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffcc80; }}
    .sw-mean {{ font-size: 14px; color: #333; }}
    .sw-speak {{ 
      width: 28px; height: 28px; border-radius: 50%; border: none; 
      background: #e3f2fd; color: #1976d2; font-size: 12px; 
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s; flex-shrink: 0; margin-left: 4px;
    }}
    .sw-speak:hover {{ background: #bbdefb; transform: scale(1.05); }}
    .sw-speak:active {{ transform: scale(0.95); }}
    .meaning-cn {{ font-size: 26px; font-weight: 800; color: #212121; margin: 8px 0 12px 36px; }}
    .scene-tag {{ font-size: 13px; display: inline-block; padding: 4px 12px; border-radius: 12px; background: #fff3e0; color: #e65100; margin-left: 36px; margin-bottom: 10px; font-weight: 600; }}
    .example-block {{ background: #f5f7fa; border-radius: 12px; padding: 14px 16px; margin-left: 36px; }}
    .example-en {{ font-size: 15px; color: #1a237e; font-style: italic; margin-bottom: 6px; line-height: 2; }}
    .example-cn {{ font-size: 14px; color: #607d8b; line-height: 1.5; margin-bottom: 10px; }}
    
    /* 句内生词高亮（绿色块：单词+音标） */
    .inline-word {{
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      background: #e8f5e9;
      border-radius: 8px;
      padding: 2px 8px;
      margin: 0 2px;
      vertical-align: bottom;
    }}
    .inline-text {{
      font-size: 15px;
      color: #2e7d32;
      font-weight: 700;
      font-style: normal;
    }}
    .inline-phonetic {{
      font-size: 11px;
      color: #e65100;
      font-weight: 600;
      font-style: normal;
    }}
    
    /* 例句操作区 */
    .example-actions {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
    .tip-bar {{ background: #fff8e1; border-left: 4px solid #ffca28; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #795548; margin-bottom: 20px; line-height: 1.6; }}


    /* Bonus Section - Friends Day */
    .bonus-section {{
      margin-top: 28px;
      padding: 24px 20px 22px;
      background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
      border-radius: 20px;
      box-shadow: 0 4px 18px rgba(255,152,0,0.15);
      border: 2px dashed #ffb74d;
    }}
    .bonus-title {{
      font-size: 22px;
      font-weight: 800;
      color: #e65100;
      text-align: center;
      margin-bottom: 16px;
      letter-spacing: 2px;
    }}
    .bonus-content {{ line-height: 1.8; color: #4a148c; font-size: 15px; }}
    .scene-title {{ font-size: 16px; font-weight: 700; color: #e65100; margin-bottom: 12px; text-align: center; }}
    .dialogue-box {{ background: #fff8e1; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .dialogue-line {{ margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #ffe0b2; }}
    .dialogue-line:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .dialogue-en-row {{ margin-bottom: 4px; }}
    .speaker {{ font-weight: 700; color: #e65100; }}
    .dialogue-text {{ color: #333; font-style: italic; }}
    .dialogue-cn {{ color: #777; font-size: 13px; margin-bottom: 6px; padding-left: 24px; }}
    .dialogue-speak-btn {{
      display: inline-flex; align-items: center; gap: 4px;
      background: #fff3e0; color: #e65100; border: 1px solid #ffcc80;
      border-radius: 12px; padding: 3px 10px; font-size: 11px;
      font-weight: 600; cursor: pointer; transition: all 0.15s;
      margin-left: 24px;
    }}
    .dialogue-speak-btn:hover {{ background: #ffe0b2; }}
    .dialogue-speak-btn svg {{ fill: #e65100; }}
    .dialogue-words {{ margin: 6px 0 6px 24px; font-size: 12px; color: #558b2f; line-height: 1.6; }}
    .dw-item {{ display: inline-flex; align-items: center; gap: 4px; margin-right: 12px; background: #f1f8e9; padding: 2px 8px; border-radius: 6px; }}
    .dw-speak {{
      width: 20px; height: 20px; border-radius: 50%; border: none;
      background: #e8f5e9; color: #2e7d32; font-size: 10px;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s; flex-shrink: 0;
    }}
    .dw-speak:hover {{ background: #c8e6c9; transform: scale(1.05); }}
    .dw-speak:active {{ transform: scale(0.95); }}
    .expressions-box {{ background: #e3f2fd; border-radius: 12px; padding: 14px; }}
    .expressions-title {{ font-size: 14px; font-weight: 700; color: #1565c0; margin-bottom: 12px; }}
    .expression-card {{ background: #fff; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }}
    .expression-card:last-child {{ margin-bottom: 0; }}
    .ex-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
    .ex-en {{ font-size: 18px; font-weight: 700; color: #1976d2; }}
    .ex-speak {{ 
      width: 28px; height: 28px; border-radius: 50%; border: none;
      background: #e3f2fd; color: #1976d2; font-size: 12px;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s;
    }}
    .ex-speak:hover {{ background: #bbdefb; transform: scale(1.05); }}
    .ex-speak:active {{ transform: scale(0.95); }}
    .ex-phonetic {{ font-size: 14px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; margin-bottom: 8px; }}
    .ex-meta {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }}
    .ex-syllable {{ font-size: 13px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffcc80; }}
    .ex-grammar {{ font-size: 12px; color: #6a1b9a; background: #f3e5f5; padding: 3px 10px; border-radius: 6px; font-weight: 600; }}
    .ex-cn {{ color: #333; font-size: 14px; }}
    .bonus-tip {{
      background: #f3e5f5;
      border-radius: 10px;
      padding: 12px 14px;
      margin-top: 16px;
      font-size: 13px;
      color: #6a1b9a;
      line-height: 1.7;
    }}

    /* Bonus Section - Song Day */
    .song-day {{
      background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
      border: 2px dashed #66bb6a;
    }}
    .song-day .bonus-title {{ color: #2e7d32; }}
    .song-header {{ margin-bottom: 16px; }}
    .song-info {{ text-align: center; }}
    .song-name {{ font-size: 22px; font-weight: 800; color: #1b5e20; margin-bottom: 6px; }}
    .song-year {{ font-size: 14px; color: #666; font-weight: 400; }}
    .song-artist {{ font-size: 15px; color: #555; margin-bottom: 10px; }}
    .song-tense {{ margin-bottom: 8px; }}
    .tense-badge {{ 
      background: #4caf50; color: #fff; font-size: 13px; font-weight: 700;
      padding: 4px 12px; border-radius: 20px; margin-right: 8px;
    }}
    .tense-en {{ font-size: 13px; color: #666; font-style: italic; }}
    .tense-rule {{ font-size: 13px; color: #2e7d32; background: #e8f5e9; padding: 8px 12px; border-radius: 8px; margin-top: 8px; }}
    .song-player {{ margin: 16px 0; }}
    .song-player audio {{ width: 100%; border-radius: 8px; }}
    .song-player-error {{ color: #e65100; font-size: 13px; text-align: center; padding: 12px; background: #fff3e0; border-radius: 8px; }}
    .lyrics-box {{ background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .lyrics-title {{ font-size: 14px; font-weight: 700; color: #2e7d32; margin-bottom: 12px; }}
    .lyric-line {{ margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed #e0e0e0; }}
    .lyric-line:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .lyric-en {{ font-size: 15px; color: #333; font-weight: 500; margin-bottom: 4px; }}
    .lyric-zh {{ font-size: 13px; color: #666; margin-bottom: 6px; }}
    .slang-note {{ font-size: 12px; color: #e65100; background: #fff8e1; padding: 6px 10px; border-radius: 6px; margin-top: 4px; border-left: 3px solid #ffb74d; }}
    .keywords-box {{ background: #f3e5f5; border-radius: 12px; padding: 14px; }}
    .keywords-title {{ font-size: 14px; font-weight: 700; color: #6a1b9a; margin-bottom: 12px; }}
    .keywords-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }}
    .keyword-card {{ background: #fff; border-radius: 10px; padding: 12px 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }}
    .kw-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
    .kw-phrase {{ font-size: 16px; font-weight: 700; color: #1976d2; }}
    .kw-speak {{ 
      width: 26px; height: 26px; border-radius: 50%; border: none;
      background: #e3f2fd; color: #1976d2; font-size: 11px;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s;
    }}
    .kw-speak:hover {{ background: #bbdefb; transform: scale(1.05); }}
    .kw-speak:active {{ transform: scale(0.95); }}
    .kw-phonetic {{ font-size: 13px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; margin-bottom: 6px; }}
    .kw-meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }}
    .kw-syllable {{ font-size: 12px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 2px 8px; border-radius: 5px; border: 1px solid #ffcc80; }}
    .kw-grammar {{ font-size: 11px; color: #6a1b9a; background: #f3e5f5; padding: 2px 8px; border-radius: 5px; font-weight: 600; }}
    .kw-mean {{ font-size: 13px; color: #333; }}

    footer {{ text-align: center; margin-top: 32px; padding: 22px 16px; background: linear-gradient(120deg, #43a047, #1e88e5); border-radius: 18px; color: #fff; font-size: 18px; font-weight: 700; letter-spacing: 2px; box-shadow: 0 4px 16px rgba(30,136,229,0.2); line-height: 1.8; }}
    footer span {{ display: block; font-size: 13px; font-weight: 400; margin-top: 6px; opacity: 0.85; }}
    @media (max-width: 480px) {{ .word-en {{ font-size: 23px; }} .meaning-cn {{ font-size: 18px; }} }}
  </style>
</head>
<body>
  <header>
    <div class="date-label">{TODAY}</div>
    <h1>📖 每日英语单词</h1>
    <div class="subtitle">🇳🇿 新西兰生活口语 + 🎓 雅思移民备考</div>
  </header>
  
  <div class="tag-bar">
    <span class="tag tag-nz">🟢 NZ日常 × 7</span>
    <span class="tag tag-ielts">🔵 雅思核心 × 3</span>
  </div>
  
  <div class="tip-bar">
    <strong>💡 今日学习提示：</strong>点击"听发音"听单词发音，点击"听例句"听完整句子。每个例句都标注了语法点，帮助你理解用法。
  </div>
  
  {{words_html}}
  
  {{bonus_html}}
  
  <footer>
    Keep going! 坚持就是胜利 💪
    <span>每天10个词，一年3650个词</span>
  </footer>
  
  <script>
  // 音频数据将由 embed-daily-words-audio.py 嵌入
  function speakWord(btn, word) {{ console.log('Speak word:', word); }}
  function speakSentence(btn, sentence) {{ console.log('Speak sentence:', sentence); }}
  </script>
</body>
</html>'''

# 生成单词卡片
words_html = ""
for i, w in enumerate(WORDS, 1):
    words_html += generate_word_card(w, i)

# 生成兴趣加餐
bonus_html = generate_friends_dialogue()

# 替换模板
final_html = HTML_TEMPLATE.replace("{words_html}", words_html).replace("{bonus_html}", bonus_html)

OUTPUT.write_text(final_html, encoding='utf-8')
print(f"[OK] 已生成: {OUTPUT}")
print(f"     文件大小: {OUTPUT.stat().st_size / 1024:.1f} KB")

print("\n[*] 今日单词列表（10个）：")
for i, w in enumerate(WORDS, 1):
    print(f"  {i:02d}. {w['word']} ({w['meaning']})")

print(f"\n[*] 兴趣加餐：周四 → 老友记风格对话")
