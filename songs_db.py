"""
英语时态歌曲数据库
每首歌对应一个时态，作为兴趣加餐素材
lyrics 字段改为完整歌词（所有段落）
每句可含 slang 字段，标注俚语/地道口语表达
"""

SONGS_DB = {

    # ---- 周一：现在进行时 ----
    "lemon_tree": {
        "name": "Lemon Tree",
        "artist": "Fool's Garden",
        "year": "1995",
        "netease_id": "17858810",
        "tense": "现在进行时",
        "tense_en": "Present Continuous",
        "tense_rule": "am/is/are + 动词ing，表示正在发生的动作",
        "lyrics": [
            {"en": "I'm sitting here in the boring room",    "zh": "我坐在这间无聊的房间里"},
            {"en": "It's just another rainy Sunday afternoon", "zh": "又是一个下雨的无聊周日午后"},
            {"en": "I'm wasting my time, I got nothing to do", "zh": "我在浪费时间，无所事事",
             "slang": [{"word": "I got nothing to do", "note": "口语：got 替代 have，等同于 I have nothing to do，极常见于美式英语"}]},
            {"en": "I'm hanging around, I'm waiting for you", "zh": "我四处闲逛，等待着你",
             "slang": [{"word": "hanging around", "note": "俚语：漫无目的地闲逛、混时间，e.g. Stop hanging around and do something!"}]},
            {"en": "I wonder how, I wonder why", "zh": "我纳闷是如何，我纳闷是为何",
             "slang": [{"word": "wonder", "note": "动词：想知道、纳闷；I wonder + 疑问词 = 我想知道……",
                        "hard_words": [
                            {"word": "wonder", "phonetic": "/ˈwʌndər/", "syllable": "won·der", "note": "v. 想知道、纳闷"}
                        ]}]},
            {"en": "Yesterday you told me about the blue, blue sky", "zh": "昨天你告诉我那蔚蓝的天空"},
            {"en": "And all that I can see is just a yellow lemon tree", "zh": "而我所能看到的只是一棵黄色的柠檬树"},
            {"en": "I'm turning my head up and down", "zh": "我不停地上下转动着头"},
            {"en": "I'm turning, turning, turning, turning, turning around", "zh": "我转啊转，转啊转"},
            {"en": "And all that I can see is just another lemon tree", "zh": "而我所能看到的只是又一棵柠檬树"},
            {"en": "Sing, sing, sing", "zh": "唱啊唱吧"},
            {"en": "I'm sitting here, I miss the power", "zh": "我坐在这里，我想念那种力量",
             "slang": [{"word": "power", "note": "名词：力量、能量；日常中也指电力（power bill 电费）",
                        "hard_words": [
                            {"word": "power", "phonetic": "/ˈpaʊər/", "syllable": "pow·er", "note": "n. 力量；电力"}
                        ]}]},
            {"en": "I'd like to go out, taking a shower", "zh": "我想出去，冲个澡",
             "slang": [{"word": "taking a shower", "note": "生活口语：take a shower（美式）比 have a shower（英式）更常见"}]},
            {"en": "But there's a heavy cloud inside my head", "zh": "但我的脑海里有一片沉重的乌云",
             "slang": [{"word": "a heavy cloud inside my head", "note": "比喻：指情绪低落、思绪混乱，相当于 I feel down / my mind is foggy"}]},
            {"en": "I feel so tired, put myself into bed", "zh": "我感到如此疲惫，把自己扔到床上",
             "slang": [{"word": "tired", "note": "形容词：疲惫的；I'm so tired = 我太累了",
                        "hard_words": [
                            {"word": "tired", "phonetic": "/ˈtaɪərd/", "syllable": "tired", "note": "adj. 疲惫的；注意tire是动词，tired是形容词"}
                        ]}]},
            {"en": "Where nothing ever happens and I wonder", "zh": "什么都没发生，我只是迷惑"},
            {"en": "Isolation, isolation, isolation", "zh": "孤立，孤立，孤立",
             "slang": [{"word": "isolation", "note": "名词：孤立、隔离；形容词形式 isolated = 孤立的",
                        "hard_words": [
                            {"word": "isolation", "phonetic": "/ˌaɪsəˈleɪʃn/", "syllable": "i·so·la·tion", "note": "n. 孤立；隔离"}
                        ]}]},
            {"en": "I'm all alone", "zh": "我完全孤单一人"},
        ],
        "keywords": [
            {
                "phrase": "I'm sitting here",
                "phonetic": "/aɪm ˈsɪtɪŋ hɪər/",
                "syllable": "I'm sit·ting here",
                "grammar": "现在进行时：am + sitting，强调此刻正在进行的动作",
                "meaning": "我正坐在这里",
            },
            {
                "phrase": "I'm wasting my time",
                "phonetic": "/aɪm ˈweɪstɪŋ maɪ taɪm/",
                "syllable": "I'm wast·ing my time",
                "grammar": "现在进行时：am + wasting，表达对当前状态的感叹",
                "meaning": "我正在浪费时间",
            },
            {
                "phrase": "I'm waiting for you",
                "phonetic": "/aɪm ˈweɪtɪŋ fər juː/",
                "syllable": "I'm wait·ing for you",
                "grammar": "现在进行时：am + waiting，常用于等待某人的情境",
                "meaning": "我正在等你",
            },
            {
                "phrase": "I wonder how",
                "phonetic": "/aɪ ˈwʌndər haʊ/",
                "syllable": "I won·der how",
                "grammar": "一般现在时：wonder 表示内心疑惑，固定搭配 I wonder + 疑问词",
                "meaning": "我想知道是怎么（发生的）",
            },
        ]
    },

    # ---- 周二：一般过去时 ----
    "yesterday_once_more": {
        "name": "Yesterday Once More",
        "artist": "Carpenters",
        "year": "1973",
        "netease_id": "3986241",
        "tense": "一般过去时",
        "tense_en": "Simple Past",
        "tense_rule": "动词过去式（规则：+ed；不规则需单独记忆），表示过去发生的动作",
        "lyrics": [
            {"en": "When I was young, I'd listen to the radio", "zh": "当我年轻的时候，我会听收音机",
             "slang": [{"word": "I'd listen", "note": "口语缩写：I would listen，表示过去的习惯，= used to listen"}]},
            {"en": "Waiting for my favorite songs", "zh": "等待着我最喜欢的歌曲",
             "slang": [{"word": "favorite", "note": "形容词：最喜爱的；美式拼写favorite，英式favourite",
                        "hard_words": [
                            {"word": "favorite", "phonetic": "/ˈfeɪvərɪt/", "syllable": "fa·vor·ite", "note": "adj. 最喜爱的"}
                        ]}]},
            {"en": "When they played I'd sing along", "zh": "当它们播放时我会跟着唱",
             "slang": [{"word": "sing along", "note": "口语搭配：跟着音乐一起唱，e.g. Let's all sing along!"}]},
            {"en": "It made me smile", "zh": "这让我微笑"},
            {"en": "Those were such happy times", "zh": "那是多么快乐的时光"},
            {"en": "And not so long ago", "zh": "而且并不是很久以前"},
            {"en": "How I wondered where they'd gone", "zh": "我曾纳闷那些时光都去哪儿了",
             "slang": [{"word": "wondered", "note": "动词wonder的过去式：纳闷、想知道",
                        "hard_words": [
                            {"word": "wondered", "phonetic": "/ˈwʌndərd/", "syllable": "won·dered", "note": "v. 纳闷（过去式）"}
                        ]}]},
            {"en": "But they're back again, just like a long-lost friend", "zh": "但他们又回来了，就像久违的老朋友",
             "slang": [{"word": "long-lost friend", "note": "固定表达：失散多年的老朋友，long-lost 形容词，指消失了很久的人或物"}]},
            {"en": "All the songs I loved so well", "zh": "所有我深爱的歌曲",
             "slang": [{"word": "loved", "note": "love的过去式；love既是动词'爱'也是名词'爱'",
                        "hard_words": [
                            {"word": "loved", "phonetic": "/lʌvd/", "syllable": "loved", "note": "v. 爱（过去式/过去分词）"}
                        ]}]},
            {"en": "Every sha-la-la-la, every wo-wo-wo still shines", "zh": "每一个sha-la-la，每一个wo-wo-wo依然闪耀",
             "slang": [{"word": "shines", "note": "动词shine的第三人称单数：闪耀；shine的过去式是shone",
                        "hard_words": [
                            {"word": "shines", "phonetic": "/ʃaɪnz/", "syllable": "shines", "note": "v. 闪耀（单三）"}
                        ]}]},
            {"en": "Every shing-a-ling-a-ling that they're beginning to sing", "zh": "每一个他们开始唱的shing-a-ling",
             "slang": [{"word": "beginning", "note": "动词begin的现在分词：开始；注意双写n再加ing",
                        "hard_words": [
                            {"word": "beginning", "phonetic": "/bɪˈɡɪnɪŋ/", "syllable": "be·gin·ning", "note": "v. 开始（现在分词）；双写n"}
                        ]}]},
            {"en": "So fine, when they get to the part", "zh": "多美妙啊，当他们唱到那一段"},
            {"en": "Where he's breaking her heart", "zh": "他正在伤她的心",
             "slang": [{"word": "breaking her heart", "note": "俚语/成语：break someone's heart，令某人心碎，极常见的情感表达"}]},
            {"en": "It can really make me cry, just like before", "zh": "这真的能让我哭泣，就像以前一样",
             "slang": [{"word": "cry", "note": "动词/名词：哭泣；cry-dried 是不规则变化吗？不，是cry → cried（规则）",
                        "hard_words": [
                            {"word": "cry", "phonetic": "/kraɪ/", "syllable": "cry", "note": "v./n. 哭泣"}
                        ]}]},
            {"en": "It's yesterday once more", "zh": "这就是昨日重现",
             "slang": [{"word": "yesterday", "note": "名词/副词：昨天；注意拼写yester+day",
                        "hard_words": [
                            {"word": "yesterday", "phonetic": "/ˈjestərdeɪ/", "syllable": "yes·ter·day", "note": "n./adv. 昨天"}
                        ]}]},
            {"en": "Looking back on how it was in years gone by", "zh": "回望那些逝去的岁月",
             "slang": [{"word": "looking back", "note": "短语动词：回顾、回头看；look back on sth = 回顾某事",
                        "hard_words": [
                            {"word": "looking back", "phonetic": "/ˈlʊkɪŋ bæk/", "syllable": "look·ing back", "note": "v. 回顾；回头看"}
                        ]}]},
            {"en": "And the good times that I had makes today seem rather sad", "zh": "曾经拥有的美好时光让今天显得有些悲伤"},
            {"en": "So much has changed", "zh": "改变了太多",
             "slang": [{"word": "changed", "note": "change的过去分词：改变；change既是动词也是名词",
                        "hard_words": [
                            {"word": "changed", "phonetic": "/tʃeɪndʒd/", "syllable": "changed", "note": "v. 改变（过去分词）"}
                        ]}]},
        ],
        "keywords": [
            {
                "phrase": "When I was young",
                "phonetic": "/wɛn aɪ wɒz jʌŋ/",
                "syllable": "When I was young",
                "grammar": "一般过去时：was 是 am/is 的过去式，when引导时间状语从句",
                "meaning": "当我年轻的时候",
            },
            {
                "phrase": "I'd listen to the radio",
                "phonetic": "/aɪd ˈlɪsən tə ðə ˈreɪdiəʊ/",
                "syllable": "I'd lis·ten to the ra·di·o",
                "grammar": "I'd = I would，表示过去的习惯性动作，相当于 used to",
                "meaning": "我（以前）常常听收音机",
            },
            {
                "phrase": "It made me smile",
                "phonetic": "/ɪt meɪd miː smaɪl/",
                "syllable": "It made me smile",
                "grammar": "一般过去时：made 是 make 的过去式；make sb. do sth. 使某人做某事",
                "meaning": "这让我微笑（了）",
            },
            {
                "phrase": "still shines",
                "phonetic": "/stɪl ʃaɪnz/",
                "syllable": "still shines",
                "grammar": "一般现在时：shines 第三人称单数，still 表示状态持续到现在",
                "meaning": "依然闪耀",
            },
        ]
    },

    # ---- 周三：一般现在时 ----
    "you_are_my_sunshine": {
        "name": "You Are My Sunshine",
        "artist": "Christina Perri",
        "year": "经典民谣",
        "netease_id": "1339805651",
        "tense": "一般现在时",
        "tense_en": "Simple Present",
        "tense_rule": "动词原形（第三人称单数+s），表示习惯、真理、状态",
        "lyrics": [
            {"en": "You are my sunshine, my only sunshine", "zh": "你是我的阳光，我唯一的阳光"},
            {"en": "You make me happy when skies are grey", "zh": "当天空阴沉时，你让我快乐",
             "slang": [{"word": "when skies are grey", "note": "比喻口语：skies are grey 指心情低落/生活艰难，与 sunshine 形成对比"}]},
            {"en": "You'll never know, dear, how much I love you", "zh": "亲爱的，你永远不会知道我有多爱你",
             "slang": [{"word": "dear", "note": "口语称谓：亲爱的，英美老歌常用；现代口语中对亲密的人也可用，如 Yes, dear"}]},
            {"en": "Please don't take my sunshine away", "zh": "请不要带走我的阳光",
             "slang": [{"word": "sunshine", "note": "名词：阳光；也用作对人的爱称'小阳光'",
                        "hard_words": [
                            {"word": "sunshine", "phonetic": "/ˈsʌnʃaɪn/", "syllable": "sun·shine", "note": "n. 阳光；阳光般的人"}
                        ]}]},
            {"en": "The other night, dear, as I lay sleeping", "zh": "另一个夜晚，亲爱的，当我躺着入睡",
             "slang": [{"word": "the other night", "note": "口语表达：某天晚上（最近的），the other day/night 指不太确定的某天，很地道"}]},
            {"en": "I dreamed I held you in my arms", "zh": "我梦见我把你抱在怀里",
             "slang": [{"word": "dreamed", "note": "dream的过去式：梦见；dream-dreamed-dreamed（规则变化）",
                        "hard_words": [
                            {"word": "dreamed", "phonetic": "/driːmd/", "syllable": "dreamed", "note": "v. 做梦（过去式）"}
                        ]}]},
            {"en": "When I awoke, dear, I was mistaken", "zh": "亲爱的，当我醒来，我发现是个错误",
             "slang": [{"word": "awoke", "note": "awake的过去式：醒来；awake-awoke-awoken（不规则变化）",
                        "hard_words": [
                            {"word": "awoke", "phonetic": "/əˈwəʊk/", "syllable": "a·woke", "note": "v. 醒来（过去式）；awake-awoke-awoken"}
                        ]},
                    {"word": "mistaken", "note": "形容词：错了的；be mistaken = 弄错了",
                        "hard_words": [
                            {"word": "mistaken", "phonetic": "/mɪˈsteɪkən/", "syllable": "mis·ta·ken", "note": "adj. 弄错的；mistake的过去分词作形容词"}
                        ]}]},
            {"en": "And I hung my head and cried", "zh": "然后我低下头哭泣",
             "slang": [{"word": "hung my head", "note": "成语：hang one's head，低头（表示羞愧/悲伤），e.g. He hung his head in shame"}]},
            {"en": "I'll always love you and make you happy", "zh": "我会永远爱你，让你快乐"},
            {"en": "If you will only say the same", "zh": "只要你也说同样的话"},
            {"en": "But if you leave me and love another", "zh": "但如果你离开我去爱另一个人"},
            {"en": "You'll regret it all some day", "zh": "总有一天你会后悔的",
             "slang": [{"word": "regret", "note": "动词：后悔、遗憾；名词形式相同",
                        "hard_words": [
                            {"word": "regret", "phonetic": "/rɪˈɡret/", "syllable": "re·gret", "note": "v./n. 后悔；遗憾"}
                        ]}]},
        ],
        "keywords": [
            {
                "phrase": "You are my sunshine",
                "phonetic": "/juː ɑː maɪ ˈsʌnʃaɪn/",
                "syllable": "You are my sun·shine",
                "grammar": "一般现在时：are 表示稳定不变的状态，用于表达永恒的情感",
                "meaning": "你是我的阳光",
            },
            {
                "phrase": "You make me happy",
                "phonetic": "/juː meɪk miː ˈhæpi/",
                "syllable": "You make me hap·py",
                "grammar": "一般现在时：make sb. + 形容词，表示使某人处于某种状态",
                "meaning": "你使我快乐",
            },
            {
                "phrase": "when skies are grey",
                "phonetic": "/wɛn skaɪz ɑː ɡreɪ/",
                "syllable": "when skies are grey",
                "grammar": "一般现在时条件/时间从句：when + 一般现在时，表示规律性条件",
                "meaning": "当天空阴沉时",
            },
            {
                "phrase": "how much I love you",
                "phonetic": "/haʊ mʌtʃ aɪ lʌv juː/",
                "syllable": "how much I love you",
                "grammar": "一般现在时：love 表示持续稳定的情感状态，how much 引导宾语从句",
                "meaning": "我有多么爱你",
            },
        ]
    },

    # ---- 周四：虚拟语气 ----
    "if_i_were_a_boy": {
        "name": "If I Were a Boy",
        "artist": "Beyoncé",
        "year": "2008",
        "netease_id": "441566935",
        "tense": "虚拟语气（过去式表非现实）",
        "tense_en": "Subjunctive Mood",
        "tense_rule": "If I were...（虚拟语气，were适用于所有人称），表示与现实相反的假设",
        "lyrics": [
            {"en": "If I were a boy, even just for a day", "zh": "如果我是个男孩，哪怕只是一天"},
            {"en": "I'd roll out of bed in the morning", "zh": "我会早上从床上滚出来",
             "slang": [{"word": "roll out of bed", "note": "俚语：懒洋洋地爬起床，带有随意感，e.g. I just rolled out of bed = 我刚睡醒爬起来",
                        "hard_words": [
                            {"word": "roll", "phonetic": "/rəʊl/", "note": "发音类似'肉'，意为滚动；注意区分row（划船/排）"}
                        ]}]},
            {"en": "And throw on what I wanted and go", "zh": "然后随便穿上衣服就走",
             "slang": [{"word": "throw on", "note": "口语：随手穿上（衣服），快速换装不在意搭配，e.g. Just throw on a jacket and let's go"}]},
            {"en": "Drink beer with the guys", "zh": "和哥们儿一起喝啤酒",
             "slang": [{"word": "beer", "note": "名词：啤酒；新西兰酒吧文化很盛行",
                        "hard_words": [
                            {"word": "beer", "phonetic": "/bɪər/", "syllable": "beer", "note": "n. 啤酒"}
                        ]},
                    {"word": "the guys", "note": "口语：哥们儿、一群朋友，the guys 是非正式表达，可指一群男性或混合群体"}]},
            {"en": "And chase after girls", "zh": "追女孩",
             "slang": [{"word": "chase after", "note": "口语：追求、追赶，chase after girls/boys 指追求异性，属于轻松口语用法"}]},
            {"en": "I'd kick it with who I wanted", "zh": "我会和我想要的人混在一起",
             "slang": [{"word": "kick it with", "note": "俚语（美式）：和某人一起放松、玩耍，= hang out with，e.g. We were just kicking it"}]},
            {"en": "And I'd never get confronted for it", "zh": "我也不会因此受到任何质问"},
            {"en": "'Cause I'm a boy", "zh": "因为我是男孩",
             "slang": [{"word": "'Cause", "note": "口语缩写：because 的简写，歌词和日常口语中极为常见"}]},
            {"en": "I think I could understand", "zh": "我想我能够理解",
             "slang": [{"word": "understand", "note": "动词：理解、明白；under-stand 在下面站着→理解",
                        "hard_words": [
                            {"word": "understand", "phonetic": "/ˌʌndəˈstænd/", "syllable": "un·der·stand", "note": "v. 理解；明白"}
                        ]}]},
            {"en": "How it feels to love a girl", "zh": "爱一个女孩是什么感觉",
             "slang": [{"word": "feels", "note": "feel的第三人称单数：感觉、觉得",
                        "hard_words": [
                            {"word": "feels", "phonetic": "/fiːlz/", "syllable": "feels", "note": "v. 感觉（单三）"}
                        ]}]},
            {"en": "I swear I'd be a better man", "zh": "我发誓我会成为更好的男人",
             "slang": [{"word": "I swear", "note": "口语：我发誓，强调诚意；日常也常用 I swear to God 来加强语气"}]},
            {"en": "I'd listen to her", "zh": "我会倾听她",
             "slang": [{"word": "listen", "note": "动词：倾听；listen to = 听（强调动作）vs hear（强调听到）",
                        "hard_words": [
                            {"word": "listen", "phonetic": "/ˈlɪsən/", "syllable": "lis·ten", "note": "v. 倾听；listen to sb"}
                        ]}]},
            {"en": "'Cause I know how it hurts", "zh": "因为我知道那有多痛",
             "slang": [{"word": "hurts", "note": "hurt的第三人称单数：疼痛、伤害；hurt-hurt-hurt（不规则不变）",
                        "hard_words": [
                            {"word": "hurts", "phonetic": "/hɜːts/", "syllable": "hurts", "note": "v. 伤痛（单三）；hurt-hurt-hurt"}
                        ]}]},
            {"en": "When you lose the one you wanted", "zh": "当你失去你想要的那个人",
             "slang": [{"word": "lose", "note": "动词：失去、丢失；lose-lost-lost（不规则变化）",
                        "hard_words": [
                            {"word": "lose", "phonetic": "/luːz/", "syllable": "lose", "note": "v. 失去；lose-lost-lost"}
                        ]}]},
            {"en": "'Cause he's taken you for granted", "zh": "因为他把你当作理所当然",
             "slang": [{"word": "take for granted", "note": "成语：认为...理所当然，不懂珍惜；e.g. Don't take your friends for granted",
                        "hard_words": [
                            {"word": "granted", "phonetic": "/ˈɡrɑːntɪd/", "note": "动词grant的过去分词，意为'被授予的、被承认的'，发音注意gr-开头"}
                        ]}]},
            {"en": "And everything you had got destroyed", "zh": "而你拥有的一切都被摧毁了",
             "slang": [{"word": "destroyed", "note": "destroy的过去式：摧毁、毁坏",
                        "hard_words": [
                            {"word": "destroyed", "phonetic": "/dɪˈstrɔɪd/", "syllable": "de·stroyed", "note": "v. 摧毁（过去式/过去分词）"}
                        ]}]},
            {"en": "It's a little too late for you to come back", "zh": "你现在想回来已经太迟了",
             "slang": [{"word": "a little too late", "note": "口语：有点太晚了，常用于表示错过时机，语气比 too late 稍委婉"}]},
        ],
        "keywords": [
            {
                "phrase": "If I were a boy",
                "phonetic": "/ɪf aɪ wɜː ə bɔɪ/",
                "syllable": "If I were a boy",
                "grammar": "虚拟语气：were 用于所有人称（不用 was），表示与现实相反的假设",
                "meaning": "如果我是个男孩（但我不是）",
            },
            {
                "phrase": "I'd roll out of bed",
                "phonetic": "/aɪd rəʊl aʊt əv bɛd/",
                "syllable": "I'd roll out of bed",
                "grammar": "虚拟语气主句：would + 动词原形，与if从句的虚拟语气搭配",
                "meaning": "我会从床上滚出来",
            },
            {
                "phrase": "throw on what I wanted",
                "phonetic": "/θrəʊ ɒn wɒt aɪ ˈwɒntɪd/",
                "syllable": "throw on what I want·ed",
                "grammar": "throw on = 随便穿上；what I wanted 是宾语从句，wanted 用过去时与主句呼应",
                "meaning": "随便穿上我想穿的",
            },
            {
                "phrase": "I think I could understand",
                "phonetic": "/aɪ θɪŋk aɪ kʊd ˌʌndəˈstænd/",
                "syllable": "I think I could un·der·stand",
                "grammar": "could 是虚拟语气中的情态动词，表示在假设情况下的能力/可能性",
                "meaning": "我想我能够理解",
            },
        ]
    },

    # ---- 周五：过去进行时 ----
    "love_story": {
        "name": "Love Story",
        "artist": "Taylor Swift",
        "year": "2008",
        "netease_id": "19292984",
        "tense": "过去进行时",
        "tense_en": "Past Continuous",
        "tense_rule": "was/were + 动词ing，表示过去某时刻正在进行的动作",
        "lyrics": [
            {"en": "We were both young when I first saw you", "zh": "我第一次见到你时，我们都还年轻"},
            {"en": "I close my eyes and the flashback starts", "zh": "我闭上眼睛，回忆开始浮现",
             "slang": [{"word": "flashback", "note": "电影/口语：闪回，指突然涌起的记忆画面；I had a flashback = 我突然想起了某件往事"}]},
            {"en": "I'm standing there on a balcony in summer air", "zh": "我站在那里，站在夏日空气中的阳台上",
             "slang": [{"word": "balcony", "note": "名词：阳台、露台；常见于公寓楼",
                        "hard_words": [
                            {"word": "balcony", "phonetic": "/ˈbælkəni/", "syllable": "bal·co·ny", "note": "n. 阳台；露台"}
                        ]}]},
            {"en": "See the lights, see the party, the ball gowns", "zh": "看到灯光，看到派对，看到舞会礼服",
             "slang": [{"word": "gowns", "note": "名词：礼服、长裙；ball gown = 舞会礼服",
                        "hard_words": [
                            {"word": "gowns", "phonetic": "/ɡaʊnz/", "syllable": "gowns", "note": "n. 礼服；长裙（复数）"}
                        ]}]},
            {"en": "See you make your way through the crowd", "zh": "看到你穿越人群走来",
             "slang": [{"word": "make your way through", "note": "口语搭配：费力穿过，e.g. make your way through the crowd / make your way to the top"}]},
            {"en": "And say hello, little did I know", "zh": "然后打了个招呼，当时我全不知道",
             "slang": [{"word": "little did I know", "note": "文学/口语倒装：当时我浑然不知，little 放句首引发倒装，表示意想不到"}]},
            {"en": "That you were Romeo, you were throwing pebbles", "zh": "你就是罗密欧，你在扔小石子",
             "slang": [{"word": "pebbles", "note": "名词：小石子、鹅卵石；pebble 指河边或路上的小石头",
                        "hard_words": [
                            {"word": "pebbles", "phonetic": "/ˈpeblz/", "syllable": "peb·bles", "note": "n. 小石子（复数）"}
                        ]}]},
            {"en": "And my daddy said 'Stay away from Juliet'", "zh": "而我爸爸说'离Juliet远一点'"},
            {"en": "And I was crying on the staircase", "zh": "而我在楼梯上哭泣",
             "slang": [{"word": "staircase", "note": "名词：楼梯、楼梯间；stair = 台阶，case = 空间",
                        "hard_words": [
                            {"word": "staircase", "phonetic": "/ˈsteəkeɪs/", "syllable": "stair·case", "note": "n. 楼梯；楼梯间"}
                        ]}]},
            {"en": "Begging you please don't go", "zh": "哭着求你不要走",
             "slang": [{"word": "begging", "note": "动词beg的现在分词：乞求、恳求",
                        "hard_words": [
                            {"word": "begging", "phonetic": "/ˈbeɡɪŋ/", "syllable": "beg·ging", "note": "v. 恳求（现在分词）；双写g"}
                        ]}]},
            {"en": "And I said Romeo, take me somewhere we can be alone", "zh": "我说罗密欧，带我去一个我们可以独处的地方",
             "slang": [{"word": "alone", "note": "形容词/副词：独自的；be alone = 独自一人",
                        "hard_words": [
                            {"word": "alone", "phonetic": "/əˈləʊn/", "syllable": "a·lone", "note": "adj./adv. 独自的"}
                        ]}]},
            {"en": "I'll be waiting, all there's left to do is run", "zh": "我将一直等待，唯一要做的就是逃走",
             "slang": [{"word": "all there's left to do", "note": "口语：剩下的唯一要做的事，= the only thing left to do，强调别无选择"}]},
            {"en": "You'll be the prince and I'll be the princess", "zh": "你将是王子，而我将是公主",
             "slang": [{"word": "princess", "note": "名词：公主；prince = 王子，princess = 公主（-ess表女性）",
                        "hard_words": [
                            {"word": "princess", "phonetic": "/prɪnˈses/", "syllable": "prin·cess", "note": "n. 公主"}
                        ]}]},
            {"en": "It's a love story, baby just say yes", "zh": "这是一个爱情故事，宝贝，就说好吧",
             "slang": [{"word": "baby", "note": "口语爱称：宝贝，英美流行歌曲和日常对话中对恋人的昵称，非常普遍"}]},
            {"en": "So I sneak out to the garden to see you", "zh": "所以我偷偷溜进花园去看你",
             "slang": [{"word": "sneak out", "note": "口语：偷偷溜出去，e.g. sneak out of the house = 偷偷从家里溜走"}]},
            {"en": "We keep quiet, 'cause we're dead if they knew", "zh": "我们保持安静，因为如果他们知道了我们就完了",
             "slang": [{"word": "quiet", "note": "形容词/名词：安静的；keep quiet = 保持安静",
                        "hard_words": [
                            {"word": "quiet", "phonetic": "/ˈkwaɪət/", "syllable": "qui·et", "note": "adj. 安静的；注意ui不发音"}
                        ]}]},
            {"en": "Marry me, Juliet, you'll never have to be alone", "zh": "嫁给我吧，Juliet，你将不再孤单",
             "slang": [{"word": "marry", "note": "动词：结婚、嫁娶；marry sb = 和某人结婚",
                        "hard_words": [
                            {"word": "marry", "phonetic": "/ˈmæri/", "syllable": "mar·ry", "note": "v. 结婚；嫁娶"}
                        ]}]},
        ],
        "keywords": [
            {
                "phrase": "We were both young",
                "phonetic": "/wiː wɜː bəʊθ jʌŋ/",
                "syllable": "We were both young",
                "grammar": "一般过去时：were 是 are 的过去式，both 强调两者都",
                "meaning": "我们两个都还年轻（那时）",
            },
            {
                "phrase": "when I first saw you",
                "phonetic": "/wɛn aɪ fɜːst sɔː juː/",
                "syllable": "when I first saw you",
                "grammar": "一般过去时：saw 是 see 的过去式（不规则），when 引导时间状语从句",
                "meaning": "当我第一次看见你",
            },
            {
                "phrase": "I was crying on the staircase",
                "phonetic": "/aɪ wɒz ˈkraɪɪŋ ɒn ðə ˈstɛəkeɪs/",
                "syllable": "I was cry·ing on the stair·case",
                "grammar": "过去进行时：was + crying，表示过去某时刻正在进行的动作",
                "meaning": "我（当时）正在楼梯上哭泣",
            },
            {
                "phrase": "the flashback starts",
                "phonetic": "/ðə ˈflæʃbæk stɑːts/",
                "syllable": "the flash·back starts",
                "grammar": "一般现在时：starts 第三人称单数，歌词中用现在时使画面更有临场感",
                "meaning": "回忆（画面）开始了",
            },
        ]
    },

    # ---- 周六：一般将来时 ----
    "monsters": {
        "name": "Monsters",
        "artist": "All Time Low ft. blackbear",
        "year": "2020",
        "netease_id": "1436357204",
        "tense": "一般将来时",
        "tense_en": "Simple Future",
        "tense_rule": "will + 动词原形，表示将来的动作或预测；也可用 be going to",
        "lyrics": [
            {"en": "You say you won't, but you know you will", "zh": "你说你不会，但你知道你会",
             "slang": [{"word": "won't", "note": "will not的缩写；发音/wəʊnt/，注意字母o不发音",
                        "hard_words": [
                            {"word": "won't", "phonetic": "/wəʊnt/", "syllable": "won't", "note": "= will not，将来时否定"}
                        ]}]},
            {"en": "Falling into old habits again", "zh": "又陷入了老习惯",
             "slang": [{"word": "falling into old habits", "note": "习语：fall into old habits，重蹈覆辙、回到老毛病，= slip back into bad patterns"}]},
            {"en": "Round and round in circles we go", "zh": "我们不停地兜圈子",
             "slang": [{"word": "go in circles", "note": "俚语：兜圈子、原地打转，比喻毫无进展，e.g. We've been going in circles on this issue"}]},
            {"en": "It's like we don't know what we know", "zh": "好像我们不知道自己知道什么"},
            {"en": "I'll follow you into the darkness", "zh": "我将跟随你进入黑暗",
             "slang": [{"word": "darkness", "note": "名词：黑暗；dark（形容词）→ darkness（名词），-ness后缀",
                        "hard_words": [
                            {"word": "darkness", "phonetic": "/ˈdɑːknəs/", "syllable": "dark·ness", "note": "n. 黑暗"}
                        ]}]},
            {"en": "We stumble in this beautiful mess", "zh": "我们在这美丽的混乱中跌跌撞撞",
             "slang": [{"word": "stumble", "note": "动词：绊倒、跌跌撞撞；stumble into = 偶然发现",
                        "hard_words": [
                            {"word": "stumble", "phonetic": "/ˈstʌmbl/", "syllable": "stum·ble", "note": "v. 绊倒；踉跄"}
                        ]}]},
            {"en": "You'll be the death of me, I think you know", "zh": "你将是我的死因，我想你知道",
             "slang": [{"word": "be the death of me", "note": "夸张俚语：让我受不了/把我折磨死了，e.g. This traffic will be the death of me！"}]},
            {"en": "We're monsters, we're monsters, we're monsters", "zh": "我们是怪物，我们是怪物，我们是怪物"},
            {"en": "I'll carry you home tonight", "zh": "今晚我会背你回家",
             "slang": [{"word": "carry", "note": "动词：携带、搬运；carry sb home = 背/扶某人回家",
                        "hard_words": [
                            {"word": "carry", "phonetic": "/ˈkæri/", "syllable": "car·ry", "note": "v. 携带；搬运"}
                        ]}]},
            {"en": "You know that I've got you for life", "zh": "你知道我会一生守护你",
             "slang": [{"word": "I've got you", "note": "口语：我罩着你/我支持你，= I have your back，表示保护或支持"}]},
            {"en": "Through hell, we'll get through it somehow", "zh": "就算是地狱，我们也会想办法度过",
             "slang": [{"word": "somehow", "note": "副词：以某种方式；somehow = 不知怎么地、设法",
                        "hard_words": [
                            {"word": "somehow", "phonetic": "/ˈsʌmhaʊ/", "syllable": "some·how", "note": "adv. 以某种方式；设法"}
                        ]}]},
            {"en": "I don't want to save myself if I can't save you now", "zh": "如果我现在不能救你，我不想只救自己",
             "slang": [{"word": "save", "note": "动词：拯救、节省；save one's life = 救某人的命",
                        "hard_words": [
                            {"word": "save", "phonetic": "/seɪv/", "syllable": "save", "note": "v. 拯救；节省"}
                        ]}]},
        ],
        "keywords": [
            {
                "phrase": "you won't",
                "phonetic": "/juː wəʊnt/",
                "syllable": "you won't",
                "grammar": "will not 的缩写 = won't，将来时的否定形式，表示将来不打算做某事",
                "meaning": "你不会（做某事）",
            },
            {
                "phrase": "I'll follow you",
                "phonetic": "/aɪl ˈfɒləʊ juː/",
                "syllable": "I'll fol·low you",
                "grammar": "I will 的缩写 = I'll，将来时，表示说话人在此刻决定要做某事",
                "meaning": "我将跟随你",
            },
            {
                "phrase": "You'll be the death of me",
                "phonetic": "/juːl biː ðə dɛθ əv miː/",
                "syllable": "You'll be the death of me",
                "grammar": "将来时预测：will be，be the death of sb. 是固定表达，意为让某人受不了",
                "meaning": "你将是我的死因 / 你让我受不了",
            },
            {
                "phrase": "falling into old habits",
                "phonetic": "/ˈfɔːlɪŋ ˈɪntuː əʊld ˈhæbɪts/",
                "syllable": "fall·ing in·to old hab·its",
                "grammar": "现在分词短语作状语；fall into habits = 养成/陷入习惯，old habits 老毛病",
                "meaning": "又陷入了老习惯",
            },
        ]
    },

    # ---- 周日：现在完成时 ----
    "seasons_in_the_sun": {
        "name": "Seasons in the Sun",
        "artist": "Terry Jacks",
        "year": "1974",
        "netease_id": "1839654699",
        "tense": "现在完成时",
        "tense_en": "Present Perfect",
        "tense_rule": "have/has + 过去分词，表示过去发生、对现在有影响的动作",
        "lyrics": [
            {"en": "Goodbye to you, my trusted friend", "zh": "再见了，我信任的朋友",
             "slang": [{"word": "trusted", "note": "trust的过去分词作形容词：值得信任的",
                        "hard_words": [
                            {"word": "trusted", "phonetic": "/ˈtrʌstɪd/", "syllable": "trust·ed", "note": "adj. 值得信任的"}
                        ]}]},
            {"en": "We've known each other since we were nine or ten", "zh": "我们从九岁十岁就认识彼此"},
            {"en": "Together we've climbed hills and trees", "zh": "我们一起爬过山丘和树木",
             "slang": [{"word": "climbed", "note": "climb的过去式：攀登；climb → climbed → climbed（规则）",
                        "hard_words": [
                            {"word": "climbed", "phonetic": "/klaɪmd/", "syllable": "climbed", "note": "v. 攀登（过去式/过去分词）"}
                        ]}]},
            {"en": "Learned of love and ABCs", "zh": "学习了爱与ABC",
             "slang": [{"word": "ABCs", "note": "口语：基础知识，= basics，the ABCs of something 表示某事的基本原理"}]},
            {"en": "Skinned our hearts and skinned our knees", "zh": "我们伤过心，也擦破过膝盖",
             "slang": [{"word": "skinned our knees", "note": "口语/习语：skin one's knee 擦破膝盖，这里与 skinned hearts 对仗，指身心都受过伤"}]},
            {"en": "Goodbye my friend, it's hard to die", "zh": "再见，我的朋友，死亡是艰难的",
             "slang": [{"word": "die", "note": "动词：死亡；die-died-died（规则变化）",
                        "hard_words": [
                            {"word": "die", "phonetic": "/daɪ/", "syllable": "die", "note": "v. 死亡；die-died-died"}
                        ]}]},
            {"en": "When all the birds are singing in the sky", "zh": "当所有的鸟都在天空中歌唱"},
            {"en": "Now that the spring is in the air", "zh": "如今春天已经来临",
             "slang": [{"word": "spring is in the air", "note": "习语：春意盎然，也引申为爱情/希望正在萌芽，e.g. Love is in the air = 爱情弥漫在空气中"}]},
            {"en": "Pretty girls are everywhere", "zh": "漂亮的女孩无处不在",
             "slang": [{"word": "everywhere", "note": "副词：到处；every + where = 每个地方",
                        "hard_words": [
                            {"word": "everywhere", "phonetic": "/ˈevriweər/", "syllable": "ev·ery·where", "note": "adv. 到处；处处"}
                        ]}]},
            {"en": "When you see them, I'll be there", "zh": "当你看到她们的时候，我将不在了"},
            {"en": "Goodbye Papa, it's hard to die", "zh": "再见了，爸爸，死亡是艰难的",
             "slang": [{"word": "Papa", "note": "名词：爸爸；比dad/daddy更老派、更有感情色彩",
                        "hard_words": [
                            {"word": "Papa", "phonetic": "/pəˈpɑː/", "syllable": "Pa·pa", "note": "n. 爸爸（亲昵称呼）"}
                        ]}]},
            {"en": "When all the birds are singing in the sky", "zh": "当所有的鸟都在天空中歌唱"},
            {"en": "Now that the spring is in the air", "zh": "如今春天已经来临"},
            {"en": "Little children everywhere", "zh": "到处都是孩子"},
            {"en": "When you see them, I'll be there", "zh": "当你看到他们的时候，我将不在了"},
            {"en": "We've had our seasons in the sun", "zh": "我们曾经拥有过阳光下的好时光",
             "slang": [{"word": "seasons in the sun", "note": "比喻/隐喻：美好的人生时光，seasons 象征生命不同阶段，in the sun 象征幸福温暖"}]},
            {"en": "With the wine and the roses now we're done", "zh": "带着美酒和玫瑰，我们已走到尽头",
             "slang": [{"word": "roses", "note": "名词：玫瑰（复数）；rose 是花也是过去式（rise → rose）",
                        "hard_words": [
                            {"word": "roses", "phonetic": "/ˈrəʊzɪz/", "syllable": "ros·es", "note": "n. 玫瑰花（复数）"}
                        ]},
                    {"word": "wine and roses", "note": "文化意象：美酒与玫瑰象征享乐与浪漫，now we're done 带有告别的苦涩"}]},
        ],
        "keywords": [
            {
                "phrase": "We've known each other",
                "phonetic": "/wiːv nəʊn iːtʃ ˈʌðər/",
                "syllable": "We've known each oth·er",
                "grammar": "现在完成时：have + known（know的过去分词），since引导时间状语，强调持续到现在",
                "meaning": "我们已经相识（并持续至今）",
            },
            {
                "phrase": "since we were nine or ten",
                "phonetic": "/sɪns wiː wɜː naɪn ɔː tɛn/",
                "syllable": "since we were nine or ten",
                "grammar": "since + 过去时间点，与现在完成时搭配，表示从某时刻起持续到现在",
                "meaning": "自从我们九岁十岁的时候",
            },
            {
                "phrase": "we've climbed hills and trees",
                "phonetic": "/wiːv klaɪmd hɪlz ænd triːz/",
                "syllable": "we've climbed hills and trees",
                "grammar": "现在完成时：have + climbed（climb的过去分词），强调共同经历对现在的情感意义",
                "meaning": "我们曾一起爬过山丘和树木",
            },
            {
                "phrase": "it's hard to die",
                "phonetic": "/ɪts hɑːd tə daɪ/",
                "syllable": "it's hard to die",
                "grammar": "it's + 形容词 + to do sth.，it 作形式主语，真正主语是 to die",
                "meaning": "死亡（离别）是艰难的",
            },
        ]
    },

    # ---- 额外歌曲：动态推荐池 ----
    "hey_jude": {
        "name": "Hey Jude",
        "artist": "The Beatles",
        "year": "1968",
        "netease_id": "4331344",
        "tense": "祈使句 + let's 结构",
        "tense_en": "Imperative & Let's",
        "tense_rule": "let + 宾语 + 动词原形，表示建议/鼓励对方做某事",
        "lyrics": [
            {"en": "Hey Jude, don't make it bad", "zh": "嘿Jude，别搞砸了",
             "slang": [{"word": "don't make it bad", "note": "口语：make it bad 搞砸了；口语中 make 常作使役动词，如 make it work / make it right"}]},
            {"en": "Take a sad song and make it better", "zh": "拿一首悲伤的歌，把它变好",
             "slang": [{"word": "make it better", "note": "口语：让事情好转，make + 宾语 + 形容词 是经典句型"}]},
            {"en": "Remember to let her into your heart", "zh": "记住让她走进你的心里",
             "slang": [{"word": "remember", "note": "动词：记住、记得；remember to do = 记得去做",
                        "hard_words": [
                            {"word": "remember", "phonetic": "/rɪˈmembər/", "syllable": "re·mem·ber", "note": "v. 记住；记得"}
                        ]}]},
            {"en": "Then you can start to make it better", "zh": "然后你就能开始让事情好转"},
            {"en": "Hey Jude, don't be afraid", "zh": "嘿Jude，别害怕"},
            {"en": "You were made to go out and get her", "zh": "你生来就是要出去追求她的",
             "slang": [{"word": "were made to", "note": "被动结构：be made to do sth 被设计/注定去做某事，口语中很常见"}]},
            {"en": "The minute you let her under your skin", "zh": "在你让她融入你的那一刻",
             "slang": [{"word": "under your skin", "note": "习语：深入内心/融入你，let someone under your skin = 让某人走进心里"}]},
            {"en": "Then you begin to make it better", "zh": "然后你开始让事情好转",
             "slang": [{"word": "begin", "note": "动词：开始；begin-began-begun（不规则变化）",
                        "hard_words": [
                            {"word": "begin", "phonetic": "/bɪˈɡɪn/", "syllable": "be·gin", "note": "v. 开始；begin-began-begun"}
                        ]}]},
            {"en": "So let it out and let it in", "zh": "所以让它出来，也让它进去"},
            {"en": "Hey Jude, begin", "zh": "嘿Jude，开始吧"},
            {"en": "You're waiting for someone to perform with", "zh": "你在等一个能一起表演的人",
             "slang": [{"word": "perform", "note": "动词：表演、演出；名词形式 performance 表演/表现",
                        "hard_words": [
                            {"word": "perform", "phonetic": "/pəˈfɔːm/", "syllable": "per·form", "note": "v. 表演、演出；per-前缀+form形式→做出形式→表演"}
                        ]}]},
            {"en": "And don't you know that it's just you", "zh": "你不知道那个人就是你自己吗",
             "slang": [{"word": "don't you know", "note": "口语反问：难道你不知道吗？用否定疑问表强调，语气比 you know 更有感染力"}]},
            {"en": "Hey Jude, you'll do", "zh": "嘿Jude，你行的",
             "slang": [{"word": "you'll do", "note": "口语：you'll do = you'll be fine / you can do it，简短鼓励"}]},
            {"en": "The movement you need is on your shoulder", "zh": "你需要的动力就在你肩上",
             "slang": [{"word": "movement", "note": "名词：运动、行动；move → movement",
                        "hard_words": [
                            {"word": "movement", "phonetic": "/ˈmuːvmənt/", "syllable": "move·ment", "note": "n. 运动；行动；动力"}
                        ]},
                    {"word": "shoulder", "note": "名词：肩膀；shoulder to cry on = 可依靠哭泣的人",
                        "hard_words": [
                            {"word": "shoulder", "phonetic": "/ˈʃəʊldər/", "syllable": "shoul·der", "note": "n. 肩膀"}
                        ]}]},
            {"en": "Na na na na na na na, na na na na, hey Jude", "zh": "啦啦啦啦啦啦，啦啦啦啦，嘿Jude"},
        ],
        "keywords": [
            {"phrase": "Don't make it bad", "phonetic": "/dəʊnt meɪk ɪt bæd/", "syllable": "Don't make it bad", "grammar": "祈使句否定：Don't + 动词原形", "meaning": "别搞砸了"},
            {"phrase": "Take a sad song and make it better", "phonetic": "/teɪk ə sæd sɒŋ ænd meɪk ɪt ˈbetər/", "syllable": "Take a sad song and make it bet·ter", "grammar": "祈使句：Take... and make...（拿……然后……）", "meaning": "拿一首悲伤的歌然后让它变好"},
            {"phrase": "let her into your heart", "phonetic": "/let hɜːr ˈɪntuː jɔː hɑːt/", "syllable": "let her in·to your heart", "grammar": "let + 宾语 + 介词短语，表示允许/让", "meaning": "让她走进你的心里"},
            {"phrase": "You were made to go out", "phonetic": "/juː wɜː meɪd tə ɡəʊ aʊt/", "syllable": "You were made to go out", "grammar": "被动语态：be made to do，be 动词 + 过去分词 + to do", "meaning": "你注定要出去追求"},
        ]
    },

    "let_it_be": {
        "name": "Let It Be",
        "artist": "The Beatles",
        "year": "1970",
        "netease_id": "167876",
        "tense": "祈使句 + 一般现在时",
        "tense_en": "Imperative & Simple Present",
        "tense_rule": "let it be 让它随缘/顺其自然；when I find 表一般现在时规律",
        "lyrics": [
            {"en": "When I find myself in times of trouble", "zh": "当我发现自己处于困境时",
             "slang": [{"word": "in times of trouble", "note": "固定搭配：在困难时期，= when things are hard/bad"}]},
            {"en": "Mother Mary comes to me", "zh": "圣母玛利亚来到我面前",
             "slang": [{"word": "comes", "note": "come的第三人称单数：来；come-came-come",
                        "hard_words": [
                            {"word": "comes", "phonetic": "/kʌmz/", "syllable": "comes", "note": "v. 来（单三）"}
                        ]}]},
            {"en": "Speaking words of wisdom, let it be", "zh": "说着智慧的话语，随它去吧",
             "slang": [{"word": "wisdom", "note": "名词：智慧；wise（形容词）→ wisdom（名词）",
                        "hard_words": [
                            {"word": "wisdom", "phonetic": "/ˈwɪzdəm/", "syllable": "wis·dom", "note": "n. 智慧"}
                        ]}]},
            {"en": "And in my hour of darkness", "zh": "在我最黑暗的时刻",
             "slang": [{"word": "hour of darkness", "note": "比喻：最黑暗/最困难的时刻，hour 这里不指具体时间，而是关键时刻"}]},
            {"en": "She is standing right in front of me", "zh": "她就站在我的面前",
             "slang": [{"word": "standing", "note": "stand的现在分词：站立着",
                        "hard_words": [
                            {"word": "standing", "phonetic": "/ˈstændɪŋ/", "syllable": "stand·ing", "note": "v. 站立（现在分词）"}
                        ]}]},
            {"en": "Speaking words of wisdom, let it be", "zh": "说着智慧的话语，随它去吧"},
            {"en": "Let it be, let it be, let it be, let it be", "zh": "随它去吧，随它去吧"},
            {"en": "Whisper words of wisdom, let it be", "zh": "轻声说着智慧的话语，随它去吧",
             "slang": [{"word": "whisper", "note": "动词：低语、轻声说，比 speak 更温柔，常用 whisper to sb = 对某人耳语"}]},
            {"en": "And when the broken-hearted people", "zh": "而那些心碎的人们",
             "slang": [{"word": "broken-hearted", "note": "复合形容词：心碎的，名词+ed构成形容词，如 open-minded, well-known"}]},
            {"en": "Living in the world agree", "zh": "生活在这个世界上都会认同",
             "slang": [{"word": "agree", "note": "口语：agree with sb/sth 同意某人/某事；这里表达人们都会赞同这句话"}]},
            {"en": "There will be an answer, let it be", "zh": "一定会有答案的，随它去吧",
             "slang": [{"word": "answer", "note": "名词/动词：答案；回答",
                        "hard_words": [
                            {"word": "answer", "phonetic": "/ˈɑːnsər/", "syllable": "an·swer", "note": "n./v. 答案；回答"}
                        ]}]},
            {"en": "For though they may be parted", "zh": "因为即使他们可能分离",
             "slang": [{"word": "for though", "note": "连词：for 因为 + though 虽然，though = even though = 即使"}]},
            {"en": "There is still a chance that they will see", "zh": "他们仍有重见的机会",
             "slang": [{"word": "chance", "note": "名词：机会；have a chance to do = 有机会做…",
                        "hard_words": [
                            {"word": "chance", "phonetic": "/tʃɑːns/", "syllable": "chance", "note": "n. 机会；可能性"}
                        ]}]},
            {"en": "There will be an answer, let it be", "zh": "一定会有答案的，随它去吧"},
        ],
        "keywords": [
            {"phrase": "let it be", "phonetic": "/let ɪt biː/", "syllable": "let it be", "grammar": "祈使句：let + 宾语 + 动词原形be，表示顺其自然", "meaning": "随它去吧；顺其自然"},
            {"phrase": "When I find myself in times of trouble", "phonetic": "/wen aɪ faɪnd maɪˈself ɪn taɪmz əv ˈtrʌbl/", "syllable": "When I find my·self in times of trou·ble", "grammar": "时间状语从句：when + 一般现在时，find oneself 发现自己处于…", "meaning": "当我发现自己在困境中"},
            {"phrase": "speaking words of wisdom", "phonetic": "/ˈspiːkɪŋ wɜːdz əv ˈwɪzdəm/", "syllable": "speak·ing words of wis·dom", "grammar": "现在分词短语作伴随状语", "meaning": "说着智慧的话语"},
            {"phrase": "There will be an answer", "phonetic": "/ðeə wɪl biː ən ˈɑːnsə/", "syllable": "There will be an an·swer", "grammar": "There be 句型 + 一般将来时：there will be = 会有", "meaning": "一定会有答案"},
        ]
    },

    "perfect": {
        "name": "Perfect",
        "artist": "Ed Sheeran",
        "year": "2017",
        "netease_id": "1877680891",
        "tense": "一般过去时 + 现在完成时",
        "tense_en": "Simple Past & Present Perfect",
        "tense_rule": "过去时叙述已发生的动作，现在完成时强调对现在的影响",
        "lyrics": [
            {"en": "I found a love for me", "zh": "我找到了属于我的爱",
             "slang": [{"word": "found a love for me", "note": "口语：find love = 找到爱情/真爱，比 fall in love 更强调寻找的结果"}]},
            {"en": "Darling, just dive right in and follow my lead", "zh": "亲爱的，直接投入吧，跟着我的步伐",
             "slang": [{"word": "dive right in", "note": "俚语：毫不犹豫地投入/开始做，= jump right in，形容果断行动"}]},
            {"en": "Well, I found a girl, beautiful and sweet", "zh": "嗯，我找到了一个女孩，美丽又温柔",
             "slang": [{"word": "beautiful", "note": "形容词：美丽的；beauty（名词）→ beautiful（形容词）",
                        "hard_words": [
                            {"word": "beautiful", "phonetic": "/ˈbjuːtɪfl/", "syllable": "beau·ti·ful", "note": "adj. 美丽的"}
                        ]}]},
            {"en": "Oh, I never knew you were the someone waiting for me", "zh": "我从不知道你就是那个一直在等我的人",
             "slang": [{"word": "the someone waiting for me", "note": "口语：the someone 那个特定的人；waiting for me 现在分词作后置定语"}]},
            {"en": "Cause we were just kids when we fell in love", "zh": "因为我们相爱时只是孩子",
             "slang": [{"word": "fell in love", "note": "过去时：fall in love 坠入爱河，fall → fell → fallen（不规则变化）"}]},
            {"en": "Not knowing what it was", "zh": "不知道那是什么感觉",
             "slang": [{"word": "Not knowing", "note": "现在分词否定式作状语：Not knowing... = 因为不知道……"}]},
            {"en": "I will not give you up this time", "zh": "这次我不会再放弃你",
             "slang": [{"word": "give you up", "note": "口语：give up = 放弃，give someone up = 放弃某人/让某人走"}]},
            {"en": "But darling, you look perfect tonight", "zh": "但是亲爱的，你今晚看起来太完美了",
             "slang": [{"word": "perfect", "note": "形容词：完美的；作动词时读/pəˈfekt/意为'使完美'",
                        "hard_words": [
                            {"word": "perfect", "phonetic": "/ˈpɜːfɪkt/", "syllable": "per·fect", "note": "adj. 完美的（作动词读/pəˈfekt/）"}
                        ]}]},
            {"en": "So I hold you close", "zh": "所以我紧紧抱住你",
             "slang": [{"word": "hold you close", "note": "口语：紧紧抱住你，hold someone close = 抱紧，比 hug 更深情"}]},
            {"en": "We found love right where we are", "zh": "我们就在这里找到了爱",
             "slang": [{"word": "right where we are", "note": "口语强调：就在我们所在的地方，right = 恰好、就在，加强语气"}]},
        ],
        "keywords": [
            {"phrase": "I found a love for me", "phonetic": "/aɪ faʊnd ə lʌv fɔː miː/", "syllable": "I found a love for me", "grammar": "一般过去时：find → found，表示已经找到", "meaning": "我找到了属于我的爱"},
            {"phrase": "dive right in", "phonetic": "/daɪv raɪt ɪn/", "syllable": "dive right in", "grammar": "祈使句：dive in = 投入，right 加强语气表示'毫不犹豫'", "meaning": "毫不犹豫地投入"},
            {"phrase": "we fell in love", "phonetic": "/wiː fɛl ɪn lʌv/", "syllable": "we fell in love", "grammar": "一般过去时：fall → fell，fall in love 坠入爱河", "meaning": "我们相爱了"},
            {"phrase": "where we are", "phonetic": "/weər wiː ɑːr/", "syllable": "where we are", "grammar": "where 引导名词性从句，表示'……的地方'", "meaning": "我们所在的地方"},
        ]
    },

    "counting_stars": {
        "name": "Counting Stars",
        "artist": "OneRepublic",
        "year": "2013",
        "netease_id": "436514312",
        "tense": "一般现在时 + 现在进行时",
        "tense_en": "Simple Present & Present Continuous",
        "tense_rule": "现在进行时表示此刻正在做，一般现在时表示习惯/状态",
        "lyrics": [
            {"en": "Lately I've been, I've been losing sleep", "zh": "最近我一直在失眠",
             "slang": [{"word": "losing", "note": "lose的现在分词：失去、丢失；lose → losing → lost",
                        "hard_words": [
                            {"word": "losing", "phonetic": "/ˈluːzɪŋ/", "syllable": "los·ing", "note": "v. 失去（现在分词）"}
                        ]}]},
            {"en": "Dreaming about the things that we could be", "zh": "梦想着我们可能成为的样子",
             "slang": [{"word": "dreaming", "note": "dream的现在分词：做梦、梦想",
                        "hard_words": [
                            {"word": "dreaming", "phonetic": "/ˈdriːmɪŋ/", "syllable": "dream·ing", "note": "v. 做梦；梦想（现在分词）"}
                        ]}]},
            {"en": "But baby, I've been, I've been praying hard", "zh": "但是宝贝，我一直在虔诚祈祷",
             "slang": [{"word": "praying hard", "note": "口语：pray hard = 拼命祈祷，hard 在这里作副词表示'努力地/强烈地'"}]},
            {"en": "Said no more counting dollars", "zh": "说不要再数钱了",
             "slang": [{"word": "no more", "note": "口语：不再……，= stop doing / never again，比 don't 更坚决"}]},
            {"en": "We'll be counting stars", "zh": "我们要数星星",
             "slang": [{"word": "counting stars", "note": "比喻：数星星=做白日梦/追求梦想，也有'仰望星空'的诗意"}]},
            {"en": "I see this life like a swinging vine", "zh": "我把这生活看作摇摆的藤蔓",
             "slang": [{"word": "vine", "note": "名词：藤蔓、葡萄藤",
                        "hard_words": [
                            {"word": "vine", "phonetic": "/vaɪn/", "syllable": "vine", "note": "n. 藤蔓"}
                        ]}]},
            {"en": "Swing my heart across the line", "zh": "把我的心荡过那条线",
             "slang": [{"word": "across the line", "note": "习语：across the line = 越过界限/做出改变，cross the line 是更常见的说法"}]},
            {"en": "In my face is flashing signs", "zh": "我面前闪烁着各种信号",
             "slang": [{"word": "flashing signs", "note": "口语：flashing = 闪烁的，指路标/信号灯闪烁，比喻各种选择/诱惑"}]},
            {"en": "Seek it out and ye shall find", "zh": "寻找你就会找到",
             "slang": [{"word": "seek and ye shall find", "note": "圣经名句：Seek and you shall find，ye 是古英语 you 的意思，歌词引用增添诗意"}]},
            {"en": "Old, but I'm not that old", "zh": "老了，但还没那么老",
             "slang": [{"word": "not that old", "note": "口语：not that = 没那么……，that 在这里作副词表示程度"}]},
            {"en": "Young, but I'm not that bold", "zh": "年轻，但没那么大胆",
             "slang": [{"word": "bold", "note": "形容词：大胆的、勇敢的，比 brave 更偏向'敢于冒险/突破'"}]},
        ],
        "keywords": [
            {"phrase": "I've been losing sleep", "phonetic": "/aɪv biːn ˈluːzɪŋ sliːp/", "syllable": "I've been los·ing sleep", "grammar": "现在完成进行时：have been + doing，表示从某时起持续到现在", "meaning": "我一直在失眠"},
            {"phrase": "no more counting dollars", "phonetic": "/nəʊ mɔːr ˈkaʊntɪŋ ˈdɒlərz/", "syllable": "no more count·ing dol·lars", "grammar": "no more + doing = 不再做某事", "meaning": "不要再数钱了（不要再只看重钱）"},
            {"phrase": "not that old", "phonetic": "/nɒt ðæt əʊld/", "syllable": "not that old", "grammar": "that 作副词表示程度：not that + 形容词 = 没那么...", "meaning": "还没那么老"},
            {"phrase": "seek it out and ye shall find", "phonetic": "/siːk ɪt aʊt ænd jiː ʃæl faɪnd/", "syllable": "seek it out and ye shall find", "grammar": "祈使句 + and + shall（古语/文学用法）", "meaning": "去寻找你就会找到"},
        ]
    },

    "stand_by_me": {
        "name": "Stand By Me",
        "artist": "Ben E. King",
        "year": "1961",
        "netease_id": "27731176",
        "tense": "一般将来时 + 条件句",
        "tense_en": "Future & Conditional",
        "tense_rule": "if 条件句 + will/won't 主句，表示假设情况下的结果",
        "lyrics": [
            {"en": "When the night has come", "zh": "当黑夜降临",
             "slang": [{"word": "has come", "note": "现在完成时：has come 表示已经到来，比 when the night comes 更强调状态"}]},
            {"en": "And the land is dark", "zh": "大地一片黑暗",
             "slang": [{"word": "land", "note": "名词：大地、土地；landlord = 房东",
                        "hard_words": [
                            {"word": "land", "phonetic": "/lænd/", "syllable": "land", "note": "n. 大地；土地"}
                        ]}]},
            {"en": "And the moon is the only light we'll see", "zh": "月亮是我们唯一能看见的光",
             "slang": [{"word": "we'll see", "note": "we will see 的缩写，will + 动词原形，表示将来会看到"}]},
            {"en": "No, I won't be afraid", "zh": "不，我不会害怕",
             "slang": [{"word": "won't", "note": "will not 的缩写 = won't，将来时的否定形式"}]},
            {"en": "No, I won't shed a tear", "zh": "不，我不会流一滴泪",
             "slang": [{"word": "shed", "note": "动词：流出、脱落；shed-shed-shed（三态相同）",
                        "hard_words": [
                            {"word": "shed", "phonetic": "/ʃed/", "syllable": "shed", "note": "v. 流（泪）；脱落；shed-shed-shed"}
                        ]}]},
            {"en": "Just as long as you stand, stand by me", "zh": "只要你站在我身边",
             "slang": [{"word": "stand by me", "note": "核心短语：站在我身边/支持我，stand by someone = 在困难时支持某人"}]},
            {"en": "If the sky that we look upon", "zh": "如果我们仰望的天空",
             "slang": [{"word": "the sky that we look upon", "note": "that 引导定语从句修饰 sky；look upon = 仰望（比 look at 更正式）"}]},
            {"en": "Should tumble and fall", "zh": "崩塌坠落",
             "slang": [{"word": "tumble and fall", "note": "口语/文学：tumble = 翻滚/崩塌，tumble and fall 强调彻底倒塌"}]},
            {"en": "And the mountains should crumble to the sea", "zh": "群山应该碎裂沉入大海",
             "slang": [{"word": "crumble to the sea", "note": "比喻：crumble = 碎裂崩塌，to the sea 表示彻底消失"}]},
            {"en": "I won't cry, I won't cry, no I won't shed a tear", "zh": "我不会哭，我不会哭，不，我不会流泪"},
            {"en": "Just as long as you stand, stand by me", "zh": "只要你站在我身边"},
        ],
        "keywords": [
            {"phrase": "I won't be afraid", "phonetic": "/aɪ wəʊnt biː əˈfreɪd/", "syllable": "I won't be a·fraid", "grammar": "一般将来时否定：will not (won't) + be + 形容词", "meaning": "我不会害怕"},
            {"phrase": "stand by me", "phonetic": "/stænd baɪ miː/", "syllable": "stand by me", "grammar": "stand by = 支持/陪伴，by 表示'在……旁边'", "meaning": "站在我身边/支持我"},
            {"phrase": "shed a tear", "phonetic": "/ʃed ə tɪər/", "syllable": "shed a tear", "grammar": "shed 是不规则动词（shed-shed-shed），意为流（泪）", "meaning": "流泪"},
            {"phrase": "tumble and fall", "phonetic": "/ˈtʌmbl ænd fɔːl/", "syllable": "tum·ble and fall", "grammar": "两个不及物动词并列，表示连续动作", "meaning": "翻滚崩塌"},
        ]
    },
}

# 星期映射（保留，供兼容使用，但v3不再依赖此映射进行固定分配）
WEEKDAY_SONGS = {
    0: "lemon_tree",           # 周一：现在进行时
    1: "yesterday_once_more",  # 周二：一般过去时
    2: "you_are_my_sunshine",  # 周三：一般现在时
    3: "if_i_were_a_boy",      # 周四：虚拟语气
    4: "love_story",           # 周五：过去进行时
    5: "monsters",             # 周六：一般将来时
    6: "seasons_in_the_sun",   # 周日：现在完成时
}


def get_today_song():
    """获取今天对应的歌曲数据"""
    from datetime import datetime
    weekday = datetime.now().weekday()
    key = WEEKDAY_SONGS[weekday]
    return SONGS_DB[key]


def fetch_mp3_url(netease_id):
    """通过第三方API获取网易云音乐MP3直链（仅供个人学习使用）"""
    import urllib.request
    api_url = f"https://api.byfuns.top/1/?id={netease_id}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            mp3_url = resp.read().decode("utf-8").strip()
            if mp3_url.startswith("http"):
                return mp3_url
    except Exception as e:
        print(f"[WARN] 获取MP3链接失败: {e}")
    return None


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    song = get_today_song()
    print(f"今日歌曲: {song['name']} - {song['artist']}")
    print(f"时态: {song['tense']} ({song['tense_en']})")
    print(f"规则: {song['tense_rule']}")
    print(f"歌词行数: {len(song['lyrics'])}")
    print(f"含俚语标注的行数: {sum(1 for l in song['lyrics'] if l.get('slang'))}")
    print(f"获取MP3链接中...")
    url = fetch_mp3_url(song["netease_id"])
    print(f"MP3链接: {url[:60]}..." if url else "获取失败")
