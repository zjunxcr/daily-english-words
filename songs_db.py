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
            {"en": "I wonder how, I wonder why", "zh": "我纳闷是如何，我纳闷是为何"},
            {"en": "Yesterday you told me about the blue, blue sky", "zh": "昨天你告诉我那蔚蓝的天空"},
            {"en": "And all that I can see is just a yellow lemon tree", "zh": "而我所能看到的只是一棵黄色的柠檬树"},
            {"en": "I'm turning my head up and down", "zh": "我不停地上下转动着头"},
            {"en": "I'm turning, turning, turning, turning, turning around", "zh": "我转啊转，转啊转"},
            {"en": "And all that I can see is just another lemon tree", "zh": "而我所能看到的只是又一棵柠檬树"},
            {"en": "Sing, sing, sing", "zh": "唱啊唱吧"},
            {"en": "I'm sitting here, I miss the power", "zh": "我坐在这里，我想念那种力量"},
            {"en": "I'd like to go out, taking a shower", "zh": "我想出去，冲个澡",
             "slang": [{"word": "taking a shower", "note": "生活口语：take a shower（美式）比 have a shower（英式）更常见"}]},
            {"en": "But there's a heavy cloud inside my head", "zh": "但我的脑海里有一片沉重的乌云",
             "slang": [{"word": "a heavy cloud inside my head", "note": "比喻：指情绪低落、思绪混乱，相当于 I feel down / my mind is foggy"}]},
            {"en": "I feel so tired, put myself into bed", "zh": "我感到如此疲惫，把自己扔到床上"},
            {"en": "Where nothing ever happens and I wonder", "zh": "什么都没发生，我只是迷惑"},
            {"en": "Isolation, isolation, isolation", "zh": "孤立，孤立，孤立"},
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
            {"en": "Waiting for my favorite songs", "zh": "等待着我最喜欢的歌曲"},
            {"en": "When they played I'd sing along", "zh": "当它们播放时我会跟着唱",
             "slang": [{"word": "sing along", "note": "口语搭配：跟着音乐一起唱，e.g. Let's all sing along!"}]},
            {"en": "It made me smile", "zh": "这让我微笑"},
            {"en": "Those were such happy times", "zh": "那是多么快乐的时光"},
            {"en": "And not so long ago", "zh": "而且并不是很久以前"},
            {"en": "How I wondered where they'd gone", "zh": "我曾纳闷那些时光都去哪儿了"},
            {"en": "But they're back again, just like a long-lost friend", "zh": "但他们又回来了，就像久违的老朋友",
             "slang": [{"word": "long-lost friend", "note": "固定表达：失散多年的老朋友，long-lost 形容词，指消失了很久的人或物"}]},
            {"en": "All the songs I loved so well", "zh": "所有我深爱的歌曲"},
            {"en": "Every sha-la-la-la, every wo-wo-wo still shines", "zh": "每一个sha-la-la，每一个wo-wo-wo依然闪耀"},
            {"en": "Every shing-a-ling-a-ling that they're beginning to sing", "zh": "每一个他们开始唱的shing-a-ling"},
            {"en": "So fine, when they get to the part", "zh": "多美妙啊，当他们唱到那一段"},
            {"en": "Where he's breaking her heart", "zh": "他正在伤她的心",
             "slang": [{"word": "breaking her heart", "note": "俚语/成语：break someone's heart，令某人心碎，极常见的情感表达"}]},
            {"en": "It can really make me cry, just like before", "zh": "这真的能让我哭泣，就像以前一样"},
            {"en": "It's yesterday once more", "zh": "这就是昨日重现"},
            {"en": "Looking back on how it was in years gone by", "zh": "回望那些逝去的岁月"},
            {"en": "And the good times that I had makes today seem rather sad", "zh": "曾经拥有的美好时光让今天显得有些悲伤"},
            {"en": "So much has changed", "zh": "改变了太多"},
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
            {"en": "Please don't take my sunshine away", "zh": "请不要带走我的阳光"},
            {"en": "The other night, dear, as I lay sleeping", "zh": "另一个夜晚，亲爱的，当我躺着入睡",
             "slang": [{"word": "the other night", "note": "口语表达：某天晚上（最近的），the other day/night 指不太确定的某天，很地道"}]},
            {"en": "I dreamed I held you in my arms", "zh": "我梦见我把你抱在怀里"},
            {"en": "When I awoke, dear, I was mistaken", "zh": "亲爱的，当我醒来，我发现是个错误"},
            {"en": "And I hung my head and cried", "zh": "然后我低下头哭泣",
             "slang": [{"word": "hung my head", "note": "成语：hang one's head，低头（表示羞愧/悲伤），e.g. He hung his head in shame"}]},
            {"en": "I'll always love you and make you happy", "zh": "我会永远爱你，让你快乐"},
            {"en": "If you will only say the same", "zh": "只要你也说同样的话"},
            {"en": "But if you leave me and love another", "zh": "但如果你离开我去爱另一个人"},
            {"en": "You'll regret it all some day", "zh": "总有一天你会后悔的"},
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
             "slang": [{"word": "the guys", "note": "口语：哥们儿、一群朋友，the guys 是非正式表达，可指一群男性或混合群体"}]},
            {"en": "And chase after girls", "zh": "追女孩",
             "slang": [{"word": "chase after", "note": "口语：追求、追赶，chase after girls/boys 指追求异性，属于轻松口语用法"}]},
            {"en": "I'd kick it with who I wanted", "zh": "我会和我想要的人混在一起",
             "slang": [{"word": "kick it with", "note": "俚语（美式）：和某人一起放松、玩耍，= hang out with，e.g. We were just kicking it"}]},
            {"en": "And I'd never get confronted for it", "zh": "我也不会因此受到任何质问"},
            {"en": "'Cause I'm a boy", "zh": "因为我是男孩",
             "slang": [{"word": "'Cause", "note": "口语缩写：because 的简写，歌词和日常口语中极为常见"}]},
            {"en": "I think I could understand", "zh": "我想我能够理解"},
            {"en": "How it feels to love a girl", "zh": "爱一个女孩是什么感觉"},
            {"en": "I swear I'd be a better man", "zh": "我发誓我会成为更好的男人",
             "slang": [{"word": "I swear", "note": "口语：我发誓，强调诚意；日常也常用 I swear to God 来加强语气"}]},
            {"en": "I'd listen to her", "zh": "我会倾听她"},
            {"en": "'Cause I know how it hurts", "zh": "因为我知道那有多痛"},
            {"en": "When you lose the one you wanted", "zh": "当你失去你想要的那个人"},
            {"en": "'Cause he's taken you for granted", "zh": "因为他把你当作理所当然",
             "slang": [{"word": "take for granted", "note": "成语：认为...理所当然，不懂珍惜；e.g. Don't take your friends for granted",
                        "hard_words": [
                            {"word": "granted", "phonetic": "/ˈɡrɑːntɪd/", "note": "动词grant的过去分词，意为'被授予的、被承认的'，发音注意gr-开头"}
                        ]}]},
            {"en": "And everything you had got destroyed", "zh": "而你拥有的一切都被摧毁了"},
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
            {"en": "I'm standing there on a balcony in summer air", "zh": "我站在那里，站在夏日空气中的阳台上"},
            {"en": "See the lights, see the party, the ball gowns", "zh": "看到灯光，看到派对，看到舞会礼服"},
            {"en": "See you make your way through the crowd", "zh": "看到你穿越人群走来",
             "slang": [{"word": "make your way through", "note": "口语搭配：费力穿过，e.g. make your way through the crowd / make your way to the top"}]},
            {"en": "And say hello, little did I know", "zh": "然后打了个招呼，当时我全不知道",
             "slang": [{"word": "little did I know", "note": "文学/口语倒装：当时我浑然不知，little 放句首引发倒装，表示意想不到"}]},
            {"en": "That you were Romeo, you were throwing pebbles", "zh": "你就是罗密欧，你在扔小石子",
             "slang": [{"word": "throwing pebbles", "note": "典故：指在恋人窗下扔石子示意，是西方浪漫的传统追求方式"}]},
            {"en": "And my daddy said 'Stay away from Juliet'", "zh": "而我爸爸说'离Juliet远一点'"},
            {"en": "And I was crying on the staircase", "zh": "而我在楼梯上哭泣",
             "slang": [{"word": "I was crying", "note": "核心时态：was + crying，过去进行时，表示那时正在哭泣"}]},
            {"en": "Begging you please don't go", "zh": "哭着求你不要走"},
            {"en": "And I said Romeo, take me somewhere we can be alone", "zh": "我说罗密欧，带我去一个我们可以独处的地方"},
            {"en": "I'll be waiting, all there's left to do is run", "zh": "我将一直等待，唯一要做的就是逃走",
             "slang": [{"word": "all there's left to do", "note": "口语：剩下的唯一要做的事，= the only thing left to do，强调别无选择"}]},
            {"en": "You'll be the prince and I'll be the princess", "zh": "你将是王子，而我将是公主"},
            {"en": "It's a love story, baby just say yes", "zh": "这是一个爱情故事，宝贝，就说好吧",
             "slang": [{"word": "baby", "note": "口语爱称：宝贝，英美流行歌曲和日常对话中对恋人的昵称，非常普遍"}]},
            {"en": "So I sneak out to the garden to see you", "zh": "所以我偷偷溜进花园去看你",
             "slang": [{"word": "sneak out", "note": "口语：偷偷溜出去，e.g. sneak out of the house = 偷偷从家里溜走"}]},
            {"en": "We keep quiet, 'cause we're dead if they knew", "zh": "我们保持安静，因为如果他们知道了我们就完了",
             "slang": [{"word": "we're dead", "note": "口语夸张：我们完了/死定了，= we're in big trouble，表示会有严重后果"}]},
            {"en": "Marry me, Juliet, you'll never have to be alone", "zh": "嫁给我吧，Juliet，你将不再孤单"},
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
            {"en": "You say you won't, but you know you will", "zh": "你说你不会，但你知道你会"},
            {"en": "Falling into old habits again", "zh": "又陷入了老习惯",
             "slang": [{"word": "falling into old habits", "note": "习语：fall into old habits，重蹈覆辙、回到老毛病，= slip back into bad patterns"}]},
            {"en": "Round and round in circles we go", "zh": "我们不停地兜圈子",
             "slang": [{"word": "go in circles", "note": "俚语：兜圈子、原地打转，比喻毫无进展，e.g. We've been going in circles on this issue"}]},
            {"en": "It's like we don't know what we know", "zh": "好像我们不知道自己知道什么"},
            {"en": "I'll follow you into the darkness", "zh": "我将跟随你进入黑暗"},
            {"en": "We stumble in this beautiful mess", "zh": "我们在这美丽的混乱中跌跌撞撞",
             "slang": [{"word": "beautiful mess", "note": "反义俚语：beautiful mess 指混乱却有魅力的关系/状态，常用于描述复杂感情"}]},
            {"en": "You'll be the death of me, I think you know", "zh": "你将是我的死因，我想你知道",
             "slang": [{"word": "be the death of me", "note": "夸张俚语：让我受不了/把我折磨死了，e.g. This traffic will be the death of me！"}]},
            {"en": "We're monsters, we're monsters, we're monsters", "zh": "我们是怪物，我们是怪物，我们是怪物"},
            {"en": "I'll carry you home tonight", "zh": "今晚我会背你回家"},
            {"en": "You know that I've got you for life", "zh": "你知道我会一生守护你",
             "slang": [{"word": "I've got you", "note": "口语：我罩着你/我支持你，= I have your back，表示保护或支持"}]},
            {"en": "Through hell, we'll get through it somehow", "zh": "就算是地狱，我们也会想办法度过",
             "slang": [{"word": "through hell", "note": "俚语夸张：经历极度痛苦，go through hell = 经历地狱般的折磨"}]},
            {"en": "I don't want to save myself if I can't save you now", "zh": "如果我现在不能救你，我不想只救自己"},
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
             "slang": [{"word": "trusted friend", "note": "口语：信得过的朋友，trusted 强调长期的信任感，比 good friend 情感更深"}]},
            {"en": "We've known each other since we were nine or ten", "zh": "我们从九岁十岁就认识彼此"},
            {"en": "Together we've climbed hills and trees", "zh": "我们一起爬过山丘和树木"},
            {"en": "Learned of love and ABCs", "zh": "学习了爱与ABC",
             "slang": [{"word": "ABCs", "note": "口语：基础知识，= basics，the ABCs of something 表示某事的基本原理"}]},
            {"en": "Skinned our hearts and skinned our knees", "zh": "我们伤过心，也擦破过膝盖",
             "slang": [{"word": "skinned our knees", "note": "口语/习语：skin one's knee 擦破膝盖，这里与 skinned hearts 对仗，指身心都受过伤"}]},
            {"en": "Goodbye my friend, it's hard to die", "zh": "再见，我的朋友，死亡是艰难的"},
            {"en": "When all the birds are singing in the sky", "zh": "当所有的鸟都在天空中歌唱"},
            {"en": "Now that the spring is in the air", "zh": "如今春天已经来临",
             "slang": [{"word": "spring is in the air", "note": "习语：春意盎然，也引申为爱情/希望正在萌芽，e.g. Love is in the air = 爱情弥漫在空气中"}]},
            {"en": "Pretty girls are everywhere", "zh": "漂亮的女孩无处不在",
             "slang": [{"word": "everywhere", "note": "口语夸张：到处都是，e.g. I've looked everywhere = 我找遍了所有地方"}]},
            {"en": "When you see them, I'll be there", "zh": "当你看到她们的时候，我将不在了"},
            {"en": "Goodbye Papa, it's hard to die", "zh": "再见了，爸爸，死亡是艰难的"},
            {"en": "When all the birds are singing in the sky", "zh": "当所有的鸟都在天空中歌唱"},
            {"en": "Now that the spring is in the air", "zh": "如今春天已经来临"},
            {"en": "Little children everywhere", "zh": "到处都是孩子"},
            {"en": "When you see them, I'll be there", "zh": "当你看到他们的时候，我将不在了"},
            {"en": "We've had our seasons in the sun", "zh": "我们曾经拥有过阳光下的好时光",
             "slang": [{"word": "seasons in the sun", "note": "比喻/隐喻：美好的人生时光，seasons 象征生命不同阶段，in the sun 象征幸福温暖"}]},
            {"en": "With the wine and the roses now we're done", "zh": "带着美酒和玫瑰，我们已走到尽头",
             "slang": [{"word": "wine and roses", "note": "文化意象：美酒与玫瑰象征享乐与浪漫，now we're done 带有告别的苦涩"}]},
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
}

# 星期映射（周一=0 ... 周日=6）
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
