"""
auto_songs.py - 自动化歌曲学习系统
根据初一英语水平自动挑选适合的英文歌曲，自动获取歌词、标注生词和俚语

功能：
1. 60+首适合初中英语水平的歌曲库（元数据+难度分级）
2. 通过网易云API自动获取歌词和中文翻译
3. 基于基础词表自动检测歌词中的生词
4. 200+常用俚语/语法表达自动匹配
5. 自动生成音标、拼读、发音功能
"""

import re
import urllib.request
import urllib.parse
import json
import time
import random

# ============================================================
# 音标缓存（避免重复请求）
# ============================================================
_pronunciation_cache = {}

def get_phonetic(word):
    """通过 Free Dictionary API 获取音标和词性"""
    if word in _pronunciation_cache:
        return _pronunciation_cache[word]
    
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                entry = data[0]
                # 优先取英式音标
                phonetics = entry.get("phonetics", [])
                ipa = ""
                for p in phonetics:
                    if p.get("text", "").startswith("/"):
                        ipa = p["text"]
                        break
                if not ipa and phonetics:
                    ipa = phonetics[0].get("text", "")
                
                # 取词性和释义
                meanings = entry.get("meanings", [])
                pos = ""
                definition = ""
                if meanings:
                    pos = meanings[0].get("partOfSpeech", "")
                    defs = meanings[0].get("definitions", [])
                    if defs:
                        definition = defs[0].get("definition", "")
                
                result = {
                    "ipa": ipa,
                    "pos": pos,
                    "definition": definition
                }
                _pronunciation_cache[word] = result
                return result
    except Exception as e:
        pass
    
    _pronunciation_cache[word] = {"ipa": "", "pos": "", "definition": ""}
    return {"ipa": "", "pos": "", "definition": ""}

def syllabify(word):
    """简单的音节拆分（基于元音分组）"""
    vowels = "aeiouy"
    syllables = []
    current = ""
    for i, char in enumerate(word.lower()):
        current += char
        if char in vowels:
            # 检查是否是非重读e结尾
            if i > 0 and i < len(word) - 1 and (word[i+1] if i+1 < len(word) else "") == "e":
                continue
            # 找下一个辅音
            j = i + 1
            while j < len(word) and word[j] not in vowels and j < len(word) - 1:
                current += word[j]
                j += 1
            syllables.append(current)
            current = ""
    if current:
        syllables.append(current)
    return "·".join(syllables) if syllables else word



import re
import urllib.request
import urllib.parse
import json
import time

# ============================================================
# 初一水平基础词表（约800词）——这些词不需要标注
# ============================================================
BASIC_WORDS = set("""
a about above across after again ago air all almost along also always am among an
and animal any another answer are area around as ask at away back bad be became
because become been before began begin behind being believe below best better between
big black blue board body book both bottom box boy bring brought brown build building
bus but buy by call came can car card care carry case cat catch caught center certain
change child children city class clean clear close cold come common community company
complete computer control cook cool corner cost could country course cover cross cry
cut dance day dead deal dear death decide deep did die different difficult dinner
direction do does dog done door down draw drove during each ear early earth east eat
education eight either else end energy enough even evening ever every example eye face
fact fall family far farm fast father feel felt few field finally find fine finger
first fish five floor fly follow food foot for force foreign form found four free
friend from front full further game garden gave get girl give given glass go god going
gold gone good got government great green ground group grow gun had hair half hand
hang happen happy hard has have he head hear heard heart heat heavy help her here high
him his history hit hold hole home hope hot hour house how hundred idea if important
in include increase industry information interest into is island it its job join just
keep key kill kind king kitchen knew know land language large last late later laugh
lay lead learn least leave left less let letter level lie life light like line list
listen little live long look lost lot love low machine main make man many map market
material matter may me mean measure meet member men might mind minute miss modern
moment money month moon more morning most mother mountain mouth move much music must
my name nation nature near necessary need never new news next night nine no north
nose not note nothing now number of off office often oh old on once one only open
or order other our out outside over own page paper part party pass past pattern pay
people per perhaps person picture piece place plan plant play player please point
police political poor position possible power president press problem produce product
program provide public pull put question quickly quite race radio rain ran rather reach
read ready real really reason receive record red remember report rest result return
right river road rock room run said same sat saw say school science sea second see
seem send serve service set seven several shall shape ship short should show side
sight sign similar since sing sir sister sit six size small so some something son
song soon sort sound south space speak special stand start state stay step still stop
store story street strong student study such suddenly sun sure system table take talk
teach teacher tell ten test than that the their them then there these they thing think
third this those thought three through time to today together too top toward town
tree true try turn two type under understand united until up upon us use usually
value very voice walk wall want war warm was watch water we week well went were west
western what when where whether which while white who whole why wide will wind window
wish with within without woman women wonder wood word work world would write wrong
year yes yet you young your
""".split())

# 额外的基础词（初一教材常见）
BASIC_WORDS_EXTRA = set("""
able above across activity actually add advice against ago already although always
amazing ancient angry another anybody anymore anything anywhere appear around arrive
artist asleep attention August avoid awake baby back bad badly bag balance ball
beautiful became because bedroom believe beside best better between beyond billion
blanket blood blow body bone borrow bottom breathe bridge broken bucket build
burn business busy butterfly cake calm camp cancel candle capital capture careful
carefully carry catch celebrate century chance change charge cheese chicken childhood
choice choose church circle citizen city classical classroom client climb close
clothes cloud club coal coffee coin cold collect college color comfortable common
communicate community compare competition complete computer concern condition
conduct confirm connect consider contact continue control conversation cook
correct cost cotton count couple courage course cousin cover crack crash crazy
cream create crowd cry culture cup curious customer cute damage danger dangerous
dark daughter deal dear death decision decrease deep deeply defeat defend degree
delay deliver demand department depend describe desert design desire detail develop
device die diet dinner direction director dirty discover discussion disease dish
distance district divide doctor dollar door double doubt down downstairs downtown
draft drama draw dream dress drink drive drop drug dry due during dust duty each
eager eagle earn earth east eastern edge education effect effort egg eight either
elder electric else emotion encourage enemy energy engine enjoy enough enter
entertainment entire entrance envelope environment episode equal equipment escape
especially essay essential even evening event eventually ever every everybody
everyone everything evidence evil exact exactly exam examination example excellent
except exchange excite excited exercise exist expect experience experiment explain
express extremely eye face fact factory fail fair fairly faith fall familiar family
famous fan fancy fantasy far farther fashion fast fat fate fault favor favorite
fear feed feel fellow female fence fever fewer fiction field fifth fight figure
fill film final finally find fine finger finish fire firm first fit five fix flag
flame flat flee flight floor flower fly fold follow fool food foot football for
force foreign forest forever forget form formal former fortunate forward found four
frame free freedom freeze fresh friend friendly frighten front fruit fuel full fun
function funny furniture further future gain game garage garden gate gather general
generation gentle gentleman gently gift girl girlfriend glad glass global glory go
goal god gold golden gone good govern government grab grade gradually grain grand
grandfather grandmother grant grass gray great green greet grow growth guard guess
guide guilty gun guy habit hair half hall hand handle hang happen happy hardly
hate have head headline health healthy hear hearing heart heat heaven heavy height
helicopter help helpful her here hero hide high highly hill him hint hire his
history hit hold hole holiday honest honor hope hopefully horrible horse hospital
host hot hotel hour house household housing how however huge human humor hundred
hungry hurt husband ice idea ignore ill imagine immediately impact import important
impossible impress improve include income increase indeed independence independent
industry influence inform initial injury inner input insect inside insist install
instance instead interest interesting internal international internet interview
into introduce invasion invest investigate invitation invite iron island issue item
its itself jacket jail January join joke journal journey joy judge judgment juice
jump junior jury just keen keep key kick kid kill kind king kiss kitchen knee knew
knife knock know knowledge lab labor lack lady lake land language large last late
lately later laugh launch law lawyer lay layer lead leader leaf league lean learn
least leave lecture left leg legal lemon less lesson let letter level library lie
life lifestyle lift light like likely limit line link lion lip list listen little
live load loan local locate location lock long look lose loss lost lot loud love
lovely low lower luck lucky lunch machine mad magazine magic main mainly major
majority make male mall man manage manager manner many map march mark market
marriage married marry mask mass master match matter may maybe meal mean meaning
measure meat media medical medicine medium meet meeting member memory mental mention
message method middle might military million mind mine minister minor minute mirror
miss mission mistake mix mixture model modern modest moment money monitor month mood
moon moral more morning most mostly mother motion mountain mouth move movement movie
much murder museum music musical must mutual my myself mystery name narrow nation
national natural nature near nearly necessarily necessary neck need negative neither
nervous net network never new news newspaper next nice night nine nobody nod noise
none nor normal normally north northern nose note nothing notice notion novel now
nowhere number nurse ocean odd of off offense office officer official often oh oil
old once one only onto open operation operator opinion opponent opportunity oppose
opposite option orange order ordinary organization original other otherwise ought
our out outcome output outside over overall own owner pace pack package page pain
paint painting pair palace pale pan panel paper parent park parking part partly
partner party pass passenger past path patient pattern pause pay peace peaceful
peak pen people per percent perfect perhaps period permanent permit person personal
personally pet phone photo photograph phrase physical piano pick picture piece pig
pile pilot pin pink pipe pitch place plan plane planet plant plastic plate play
player pleasant please pleasure plenty pocket poem poet point pole police polite
pond pool poor popular population position positive possible possibly post pot potato
potential pound pour poverty power powerful practical practice praise pray precious
predict prefer prepare present presentation president press pressure pretend pretty
prevent previous price primarily primary principle priority prison private probably
problem procedure process produce product production professional professor profit
program progress project promise promote proper properly protect protection proud
prove provide province public pull punishment purpose pursue push put qualify
quality quarter queen question quickly quiet quietly quit quite quote race radio
rage rain raise range rank rapid rapidly rare rat rather raw reach react reaction
read reader ready real reality realize really reason receive recent recently
recognize recommend record recover red reduce refer reference reflect reform
region register regular relate relationship release relevant relief religion rely
remain remember remind remote remove rent repair repeat replace reply report
represent republic reputation request require research reserve resident resist
resolution resolve resource respect respond response responsibility responsible rest
restaurant result retain retire return reveal revenue review revolution rhythm rice
rich rid ride right ring riot rise risk river road rock role roll romantic roof room
root rope rough round route row royal rule run rush sad safe safety sail sake salary
sale salt same sample sand satellite satisfy save say scale scene schedule scheme
scholar school science scientist score screen sea search season seat second secret
section secure security seed seek seem select self sell send senior sense sensitive
sentence separate serious seriously serve service session set setting settle
settlement seven several severe sex sexual shake shall shape share sharp she sheet
shelf shell shelter shift shine ship shirt shock shoe shoot shop shore short shot
shoulder shout show shut sick side sight sign signal silence silent silver similar
similarly simple simply since sing singer single sir sister sit site situation
six size skill skin sky slave sleep slide slight slightly slip slow slowly small
smart smell smile smoke smooth snow social society soft software soil solar soldier
solid solution solve some somebody someday somehow someone something sometimes
somewhat somewhere son song soon sorry sort soul sound source south southeast
southern space speak speaker special specialist specific speech speed spend spirit
split sport spot spread spring square stable staff stage stair stand standard star
start state statement station status stay steady steal steam steel step stick still
stir stock stomach stone stop store storm story straight strange stranger strategic
strategy stream street strength stress stretch strike string strip stroke strong
strongly structure struggle student studio study stuff stupid style subject submit
substance succeed success successful such suddenly suffer sugar suggest suit summer
sun super supply support suppose sure surely surface surgery surprise surprisingly
surround survey survive suspect sweet swim swing switch symbol system table tail
take tale talent talk tall tank tape target task tax tea teach teacher teaching team
technology television tell temperature ten tend term terrible test text than thank
that the theater their them theme then theory there therefore they thick thin
thing think third this those though thought thousand threat three throat through
throughout throw thus ticket tie tight till time tiny tip tire tired title today
together tomorrow tone tonight too tool top topic total totally touch tough tour
tourist toward tower town toy track trade tradition traditional traffic trail train
transfer transform transition translate transportation travel treat treatment tree
trend trial trick trip troop trouble truck true truly trust truth try tube turn
twelve twenty twice twin two type typical typically ugly ultimate uncle under
understand unfortunately union unique unit united universe university unknown
unless unlike until unusual up upon upper urban urge use used useful user usual
usually vacation valley valuable value variable variety various vast vehicle version
very victim victory video view village violate violence virtual virtue visible
vision visit visitor vital voice volume vote wage wait wake walk wall wander want
war warm warn warning wash waste watch water wave way weak weakness wealth weapon
wear weather web website wedding Wednesday week weekend weigh weight welcome
welfare well west western wet what whatever wheel when whenever where whereas
wherever whether which while whisper white who whole whom whose why wide widely
widespread wife wild will willing win wind window wine wing winner winter wire
wireless wise wish with within without witness woman wonder wonderful wood wooden
word work worker working world worried worry worse worst worth worthy would
wound wrap write writer writing wrong yard yeah year yell yellow yes yesterday yet
yield you young youngster your yourself youth zone
""".split())

# 合并基础词表
ALL_BASIC_WORDS = BASIC_WORDS | BASIC_WORDS_EXTRA


# ============================================================
# 60+首适合初中英语水平的歌曲（元数据库）
# ============================================================
SONG_LIBRARY = [
    # ---- 入门级（词汇简单，语速慢）----
    {"name": "Lemon Tree", "artist": "Fool's Garden", "year": "1995", "netease_id": "17858810",
     "tense": "现在进行时", "tense_en": "Present Continuous", "level": 1,
     "tense_rule": "am/is/are + 动词ing，表示正在发生的动作"},
    {"name": "Big Big World", "artist": "Emilia", "year": "1998", "netease_id": "2534006",
     "tense": "一般现在时 + 条件句", "tense_en": "Simple Present + Conditionals", "level": 1,
     "tense_rule": "主语+动词原形(三单加s)；if引导条件句"},
    {"name": "You Are My Sunshine", "artist": "Christina Perri", "year": "经典民谣", "netease_id": "1339805651",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 1,
     "tense_rule": "主语+动词原形(三单加s)，表达习惯和事实"},
    {"name": "Right Here Waiting", "artist": "Richard Marx", "year": "1989", "netease_id": "109673",
     "tense": "现在进行时", "tense_en": "Present Continuous", "level": 1,
     "tense_rule": "am/is/are + 动词ing"},
    {"name": "My Heart Will Go On", "artist": "Celine Dion", "year": "1997", "netease_id": "188200",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 1,
     "tense_rule": "will + 动词原形"},
    {"name": "What a Wonderful World", "artist": "Louis Armstrong", "year": "1967", "netease_id": "4215755",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 1,
     "tense_rule": "主语+动词原形，描述看到的世界"},
    {"name": "Yesterday Once More", "artist": "Carpenters", "year": "1973", "netease_id": "3986241",
     "tense": "一般过去时", "tense_en": "Simple Past", "level": 1,
     "tense_rule": "主语+动词过去式，描述过去的经历"},
    {"name": "The Day You Went Away", "artist": "M2M", "year": "2000", "netease_id": "572378",
     "tense": "一般过去时 + 现在完成时", "tense_en": "Simple Past + Present Perfect", "level": 1,
     "tense_rule": "过去式描述具体事件；have/has+过去分词描述对现在的影响"},
    {"name": "Pretty Boy", "artist": "M2M", "year": "2000", "netease_id": "572375",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 1,
     "tense_rule": "主语+动词原形(三单加s)"},
    {"name": "Scarborough Fair", "artist": "Sarah Brightman", "year": "经典民歌", "netease_id": "2082132",
     "tense": "祈使句", "tense_en": "Imperative Mood", "level": 1,
     "tense_rule": "动词原形开头，表示请求或命令"},

    # ---- 初级（词汇适中，有常用短语）----
    {"name": "Love Story", "artist": "Taylor Swift", "year": "2008", "netease_id": "19292984",
     "tense": "过去进行时 + 一般过去时", "tense_en": "Past Continuous + Simple Past", "level": 2,
     "tense_rule": "was/were + 动词ing（当时正在）；动词过去式（瞬间动作）"},
    {"name": "Hey Jude", "artist": "The Beatles", "year": "1968", "netease_id": "4331344",
     "tense": "祈使句 + let's结构", "tense_en": "Imperative + Let's", "level": 2,
     "tense_rule": "let's + 动词原形 = 让我们做某事"},
    {"name": "Let It Be", "artist": "The Beatles", "year": "1970", "netease_id": "167876",
     "tense": "祈使句 + 一般现在时", "tense_en": "Imperative + Simple Present", "level": 2,
     "tense_rule": "let it be = 随它去吧"},
    {"name": "Take Me To Your Heart", "artist": "Michael Learns to Rock", "year": "2004", "netease_id": "209401",
     "tense": "祈使句 + 一般现在时", "tense_en": "Imperative + Simple Present", "level": 2,
     "tense_rule": "take me to = 带我去..."},
    {"name": "As Long As You Love Me", "artist": "Backstreet Boys", "year": "1997", "netease_id": "191248",
     "tense": "一般现在时 + 条件句", "tense_en": "Simple Present + Conditionals", "level": 2,
     "tense_rule": "as long as = 只要；条件状语从句"},
    {"name": "I Want It That Way", "artist": "Backstreet Boys", "year": "1999", "netease_id": "16835293",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 2,
     "tense_rule": "主语+动词原形，表达想法和感受"},
    {"name": "My Love", "artist": "Westlife", "year": "2000", "netease_id": "230232",
     "tense": "一般现在时 + 现在进行时", "tense_en": "Simple Present + Present Continuous", "level": 2,
     "tense_rule": "混合时态表达"},
    {"name": "Heal the World", "artist": "Michael Jackson", "year": "1991", "netease_id": "1697541",
     "tense": "祈使句 + 一般将来时", "tense_en": "Imperative + Simple Future", "level": 2,
     "tense_rule": "there will be = 将会有；make it a better place = 让它成为更好的地方"},
    {"name": "Last Christmas", "artist": "Wham!", "year": "1984", "netease_id": "347405",
     "tense": "一般过去时", "tense_en": "Simple Past", "level": 2,
     "tense_rule": "gave my heart = 给了我我的心（过去式）"},
    {"name": "Seasons in the Sun", "artist": "Terry Jacks", "year": "1974", "netease_id": "1839654699",
     "tense": "现在完成时 + 一般过去时", "tense_en": "Present Perfect + Simple Past", "level": 2,
     "tense_rule": "have/has + 过去分词（现在完成时）"},
    {"name": "Cry On My Shoulder", "artist": "Deutschland Sucht Den Superstar", "year": "2003", "netease_id": "191595",
     "tense": "一般将来时 + 祈使句", "tense_en": "Simple Future + Imperative", "level": 2,
     "tense_rule": "if you need someone = 如果你需要某人"},
    {"name": "Never Had A Dream Come True", "artist": "S Club 7", "year": "2001", "netease_id": "228711",
     "tense": "现在完成时", "tense_en": "Present Perfect", "level": 2,
     "tense_rule": "have never done = 从未做过"},
    {"name": "Stand By Me", "artist": "Ben E. King", "year": "1961", "netease_id": "27731176",
     "tense": "一般将来时 + 条件句", "tense_en": "Simple Future + Conditionals", "level": 2,
     "tense_rule": "I won't be afraid = 我不会害怕；if you just stand by me = 如果你陪着我"},
    {"name": "Just One Last Dance", "artist": "Sarah Connor", "year": "2003", "netease_id": "190574",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 2,
     "tense_rule": "just one last dance = 就最后一支舞"},
    {"name": "Burning", "artist": "Maria Arredondo", "year": "2004", "netease_id": "190557",
     "tense": "现在进行时", "tense_en": "Present Continuous", "level": 2,
     "tense_rule": "is burning = 正在燃烧"},
    {"name": "Anyone of Us", "artist": "Gareth Gates", "year": "2002", "netease_id": "227912",
     "tense": "一般过去时 + 虚拟语气", "tense_en": "Simple Past + Subjunctive", "level": 2,
     "tense_rule": "if I had been there = 如果我在那里（虚拟语气）"},

    # ---- 中级（词汇稍难，表达更丰富）----
    {"name": "Monsters", "artist": "All Time Low ft. blackbear", "year": "2020", "netease_id": "1436357204",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "I'll tell you = 我会告诉你"},
    {"name": "Perfect", "artist": "Ed Sheeran", "year": "2017", "netease_id": "1877680891",
     "tense": "一般过去时 + 现在完成时", "tense_en": "Simple Past + Present Perfect", "level": 3,
     "tense_rule": "I found a woman = 我遇到了一个女人（过去式）；I have never felt = 我从未感到"},
    {"name": "Counting Stars", "artist": "OneRepublic", "year": "2013", "netease_id": "436514312",
     "tense": "一般现在时 + 现在进行时", "tense_en": "Simple Present + Present Continuous", "level": 3,
     "tense_rule": "I see this life = 我看到这生活；make that money = 赚那些钱"},
    {"name": "If I Were a Boy", "artist": "Beyonce", "year": "2008", "netease_id": "441566935",
     "tense": "虚拟语气（过去式表非现实）", "tense_en": "Subjunctive Mood", "level": 3,
     "tense_rule": "if I were... I would... = 如果我是...我会...（虚拟语气）"},
    {"name": "Someone Like You", "artist": "Adele", "year": "2011", "netease_id": "152916",
     "tense": "一般过去时 + 一般将来时", "tense_en": "Simple Past + Simple Future", "level": 3,
     "tense_rule": "I heard that = 我听说；nevermind I'll find = 没关系我会找到"},
    {"name": "Hotel California", "artist": "Eagles", "year": "1977", "netease_id": "441491828",
     "tense": "一般过去时", "tense_en": "Simple Past", "level": 3,
     "tense_rule": "could not stop = 停不下来"},
    {"name": "When You Believe", "artist": "Whitney Houston & Mariah Carey", "year": "1998", "netease_id": "110472",
     "tense": "一般现在时 + 一般过去时", "tense_en": "Simple Present + Simple Past", "level": 3,
     "tense_rule": "when you believe = 当你相信时"},
    {"name": "Hero", "artist": "Mariah Carey", "year": "1993", "netease_id": "115078",
     "tense": "一般现在时 + 情态动词", "tense_en": "Simple Present + Modals", "level": 3,
     "tense_rule": "you don't need to be afraid = 你不需要害怕"},
    {"name": "Can You Feel the Love Tonight", "artist": "Elton John", "year": "1994", "netease_id": "153048",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "can you feel = 你能感觉到吗"},
    {"name": "Because of You", "artist": "Kelly Clarkson", "year": "2004", "netease_id": "176459",
     "tense": "一般现在时 + 一般过去时", "tense_en": "Simple Present + Simple Past", "level": 3,
     "tense_rule": "because of you = 因为你"},
    {"name": "My Happy Ending", "artist": "Avril Lavigne", "year": "2004", "netease_id": "246695",
     "tense": "一般过去时", "tense_en": "Simple Past", "level": 3,
     "tense_rule": "all the things you said = 你说过的所有话"},
    {"name": "Tomorrow", "artist": "Avril Lavigne", "year": "2002", "netease_id": "246700",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "I'll be there = 我会在那里"},
    {"name": "Thank You", "artist": "Dido", "year": "1999", "netease_id": "106841",
     "tense": "一般现在时 + 一般过去时", "tense_en": "Simple Present + Simple Past", "level": 3,
     "tense_rule": "my tea's gone cold = 我的茶凉了"},
    {"name": "Moon River", "artist": "Audrey Hepburn", "year": "1961", "netease_id": "115114",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "wherever you're going = 无论你去哪里"},
    {"name": "Show Me The Meaning of Being Lonely", "artist": "Backstreet Boys", "year": "2000", "netease_id": "191251",
     "tense": "一般现在时 + 动名词", "tense_en": "Simple Present + Gerund", "level": 3,
     "tense_rule": "show me the meaning = 告诉我这个意义"},
    {"name": "Baby One More Time", "artist": "Britney Spears", "year": "1998", "netease_id": "115174",
     "tense": "祈使句 + 一般现在时", "tense_en": "Imperative + Simple Present", "level": 3,
     "tense_rule": "hit me baby one more time = 宝贝再打我一次（再来一次）"},
    {"name": "It's My Life", "artist": "Bon Jovi", "year": "2000", "netease_id": "271555",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "it's my life = 这是我的人生"},
    {"name": "Love To Be Loved By You", "artist": "Marc Terenzi", "year": "2005", "netease_id": "199243",
     "tense": "不定式", "tense_en": "Infinitive", "level": 3,
     "tense_rule": "love to be loved = 爱被爱"},
    {"name": "Amarantine", "artist": "Enya", "year": "2005", "netease_id": "220346",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "you are = 你是（永恒不变）"},

    # ---- 中高级（词汇较丰富，适合进阶）----
    {"name": "Make You Feel My Love", "artist": "Bob Dylan", "year": "1997", "netease_id": "286868",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "I'd go hungry = 我宁愿挨饿"},
    {"name": "Million Reasons", "artist": "Lady Gaga", "year": "2016", "netease_id": "424525172",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "I bow down to pray = 我跪下祈祷"},
    {"name": "Always Come Back to Your Love", "artist": "Samantha Mumba", "year": "2000", "netease_id": "227908",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "will always come back = 总会回来"},
    {"name": "She", "artist": "Groove Coverage", "year": "2004", "netease_id": "195984",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "she may be the face = 她可能是那张面孔"},
    {"name": "One Love", "artist": "Blue", "year": "2002", "netease_id": "227909",
     "tense": "一般现在时", "tense_en": "Simple Present", "level": 3,
     "tense_rule": "one love = 一个爱"},
    {"name": "If You Come Back", "artist": "Blue", "year": "2001", "netease_id": "227907",
     "tense": "条件句", "tense_en": "Conditional", "level": 3,
     "tense_rule": "if you come back = 如果你回来"},
    {"name": "You Are Not Alone", "artist": "Michael Jackson", "year": "1995", "netease_id": "1697507",
     "tense": "一般现在时 + 一般将来时", "tense_en": "Simple Present + Simple Future", "level": 2,
     "tense_rule": "you are not alone = 你不是一个人"},
    {"name": "May It Be", "artist": "Enya", "year": "2001", "netease_id": "220340",
     "tense": "情态动词 + 祈使句", "tense_en": "Modals + Imperative", "level": 2,
     "tense_rule": "may it be = 但愿"},
    {"name": "Fighter", "artist": "Christina Aguilera", "year": "2002", "netease_id": "115129",
     "tense": "一般过去时", "tense_en": "Simple Past", "level": 3,
     "tense_rule": "made me that much stronger = 让我更强大"},
    {"name": "Forever Young", "artist": "Alphaville", "year": "1984", "netease_id": "195918",
     "tense": "祈使句", "tense_en": "Imperative", "level": 2,
     "tense_rule": "let's stay young = 让我们保持年轻"},
    {"name": "Toxic", "artist": "Britney Spears", "year": "2003", "netease_id": "115175",
     "tense": "现在进行时", "tense_en": "Present Continuous", "level": 3,
     "tense_rule": "don't you know that you're toxic = 你不知道你有毒吗"},
    {"name": "Winter Things", "artist": "Ariana Grande", "year": "2015", "netease_id": "37075507",
     "tense": "一般将来时", "tense_en": "Simple Future", "level": 3,
     "tense_rule": "wouldn't call it = 不会称之为"},
    {"name": "You Must Love Me", "artist": "Madonna", "year": "1996", "netease_id": "115132",
     "tense": "情态动词", "tense_en": "Modals", "level": 3,
     "tense_rule": "you must love me = 你必须爱我"},
]


# ============================================================
# 常用俚语/地道表达字典（200+条目）
# 匹配歌词中的表达后自动标注
# ============================================================
SLANG_DB = [
    # ---- 情感类 ----
    {"phrase": "break my heart", "meaning": "让我心碎", "grammar": "break one's heart 让某人心碎"},
    {"phrase": "fall in love", "meaning": "坠入爱河", "grammar": "fall in love with sb 与某人相爱"},
    {"phrase": "head over heels", "meaning": "深深爱上", "grammar": "head over heels (in love) 彻底倾倒"},
    {"phrase": "crazy about", "meaning": "为...疯狂", "grammar": "be crazy about sth 对...极度喜爱"},
    {"phrase": "can't help", "meaning": "忍不住", "grammar": "can't help doing sth 忍不住做某事"},
    {"phrase": "miss you", "meaning": "想你", "grammar": "miss sb 想念某人"},
    {"phrase": "dream come true", "meaning": "梦想成真", "grammar": "a dream come true = 梦想实现"},
    {"phrase": "tear apart", "meaning": "撕碎/拆散", "grammar": "tear sth apart 撕开"},
    {"phrase": "on my mind", "meaning": "在我心里/挂念", "grammar": "have sth on one's mind 心里想着"},
    {"phrase": "can't let go", "meaning": "无法放手", "grammar": "can't let go of sth 无法释怀"},
    {"phrase": "give up", "meaning": "放弃", "grammar": "give up doing sth 放弃做某事"},
    {"phrase": "hold on", "meaning": "坚持/等一下", "grammar": "hold on 坚持/稍等"},
    {"phrase": "hang on", "meaning": "坚持/等一下", "grammar": "hang on 坚持（口语）"},
    {"phrase": "cheer up", "meaning": "振作起来", "grammar": "cheer up 振作"},
    {"phrase": "feel down", "meaning": "心情低落", "grammar": "feel down = feel sad"},
    {"phrase": "lose my mind", "meaning": "失去理智", "grammar": "lose one's mind 失去理智"},
    {"phrase": "take my breath away", "meaning": "让我窒息/惊艳", "grammar": "take one's breath away 令人惊叹"},
    {"phrase": "sweep off my feet", "meaning": "让我神魂颠倒", "grammar": "sweep sb off their feet 让人倾倒"},

    # ---- 动作类 ----
    {"phrase": "hang around", "meaning": "闲逛/徘徊", "grammar": "hang around 在附近闲逛"},
    {"phrase": "figure out", "meaning": "弄清楚", "grammar": "figure sth out 弄明白"},
    {"phrase": "make up my mind", "meaning": "下定决心", "grammar": "make up one's mind 下定决心"},
    {"phrase": "take a chance", "meaning": "冒险/尝试", "grammar": "take a chance 冒险一试"},
    {"phrase": "take it easy", "meaning": "放轻松", "grammar": "take it easy = relax"},
    {"phrase": "show up", "meaning": "出现/露面", "grammar": "show up 出现"},
    {"phrase": "run away", "meaning": "逃跑", "grammar": "run away from sth 逃离"},
    {"phrase": "come along", "meaning": "一起来/出现", "grammar": "come along 跟着来"},
    {"phrase": "break down", "meaning": "崩溃/出故障", "grammar": "break down 崩溃/坏掉"},
    {"phrase": "look back", "meaning": "回头看/回顾", "grammar": "look back on sth 回顾"},
    {"phrase": "turn around", "meaning": "转身/改变", "grammar": "turn around 转身"},
    {"phrase": "pass by", "meaning": "经过/路过", "grammar": "pass by 经过"},
    {"phrase": "go on", "meaning": "继续", "grammar": "go on doing sth 继续做"},
    {"phrase": "carry on", "meaning": "继续/坚持", "grammar": "carry on 继续"},
    {"phrase": "stand by", "meaning": "支持/陪伴", "grammar": "stand by sb 支持某人"},
    {"phrase": "let go", "meaning": "放手", "grammar": "let go of sth 放手"},
    {"phrase": "hold back", "meaning": "克制/隐瞒", "grammar": "hold back 克制"},
    {"phrase": "wake up", "meaning": "醒来", "grammar": "wake up 醒来"},
    {"phrase": "get up", "meaning": "起床/站起来", "grammar": "get up 起床"},
    {"phrase": "set me free", "meaning": "让我自由", "grammar": "set sb free 释放某人"},
    {"phrase": "reach out", "meaning": "伸出手/联系", "grammar": "reach out to sb 联系某人"},
    {"phrase": "wrap up", "meaning": "包裹/结束", "grammar": "wrap up 包裹/完成"},

    # ---- 时间/状态 ----
    {"phrase": "right now", "meaning": "现在/立刻", "grammar": "right now = at this moment"},
    {"phrase": "from time to time", "meaning": "有时/偶尔", "grammar": "from time to time 偶尔"},
    {"phrase": "time after time", "meaning": "一次又一次", "grammar": "time after time 一再地"},
    {"phrase": "day and night", "meaning": "日日夜夜", "grammar": "day and night 日夜不停"},
    {"phrase": "once upon a time", "meaning": "从前", "grammar": "once upon a time 从前（故事开头）"},
    {"phrase": "in the end", "meaning": "最后", "grammar": "in the end = finally"},
    {"phrase": "at the end", "meaning": "在尽头", "grammar": "at the end of sth 在...的末尾"},
    {"phrase": "all the time", "meaning": "一直", "grammar": "all the time = always"},
    {"phrase": "for a while", "meaning": "一会儿", "grammar": "for a while 暂时"},
    {"phrase": "by the way", "meaning": "顺便说一下", "grammar": "by the way 顺便提一下"},
    {"phrase": "the other day", "meaning": "前几天", "grammar": "the other day 前几天"},
    {"phrase": "so far", "meaning": "到目前为止", "grammar": "so far = up to now"},
    {"phrase": "no longer", "meaning": "不再", "grammar": "no longer = not any more"},

    # ---- 常用短语 ----
    {"phrase": "a lot of", "meaning": "许多", "grammar": "a lot of = lots of（修饰可数/不可数名词）"},
    {"phrase": "kind of", "meaning": "有点/某种程度", "grammar": "kind of = sort of（口语）"},
    {"phrase": "sort of", "meaning": "有点", "grammar": "sort of = kind of（口语）"},
    {"phrase": "out of", "meaning": "从...出来/用完", "grammar": "out of sth 从...中/用完"},
    {"phrase": "instead of", "meaning": "而不是", "grammar": "instead of 而不是（介词短语）"},
    {"phrase": "as long as", "meaning": "只要", "grammar": "as long as = so long as 只要"},
    {"phrase": "because of", "meaning": "因为", "grammar": "because of + 名词/代词（介词短语）"},
    {"phrase": "in spite of", "meaning": "尽管", "grammar": "in spite of = despite 尽管"},
    {"phrase": "in front of", "meaning": "在...前面", "grammar": "in front of 在...前面"},
    {"phrase": "next to", "meaning": "在旁边", "grammar": "next to 在...旁边"},
    {"phrase": "close to", "meaning": "接近", "grammar": "be close to 接近"},
    {"phrase": "far from", "meaning": "远离", "grammar": "far from 远离"},
    {"phrase": "apart from", "meaning": "除了", "grammar": "apart from = besides 除了"},
    {"phrase": "due to", "meaning": "由于", "grammar": "due to = because of 由于"},
    {"phrase": "on my own", "meaning": "靠自己", "grammar": "on one's own = by oneself 独自"},
    {"phrase": "one more time", "meaning": "再来一次", "grammar": "one more time = once more"},
    {"phrase": "once again", "meaning": "再一次", "grammar": "once again = one more time"},
    {"phrase": "first of all", "meaning": "首先", "grammar": "first of all 首先"},
    {"phrase": "after all", "meaning": "毕竟/终究", "grammar": "after all 毕竟"},
    {"phrase": "above all", "meaning": "最重要的是", "grammar": "above all 最重要的是"},
    {"phrase": "all of a sudden", "meaning": "突然", "grammar": "all of a sudden = suddenly"},
    {"phrase": "more than", "meaning": "超过/不只是", "grammar": "more than 超过"},
    {"phrase": "less than", "meaning": "少于", "grammar": "less than 少于"},
    {"phrase": "other than", "meaning": "除了", "grammar": "other than = except 除了"},
    {"phrase": "rather than", "meaning": "而不是", "grammar": "rather than 而不是"},
    {"phrase": "would rather", "meaning": "宁愿", "grammar": "would rather do A than do B 宁愿做A不做B"},
    {"phrase": "nothing but", "meaning": "只是", "grammar": "nothing but = only 只是"},
    {"phrase": "anything but", "meaning": "绝不/一点也不", "grammar": "anything but 绝不是"},
    {"phrase": "something like", "meaning": "有点像", "grammar": "something like 大约/有点像"},
    {"phrase": "just the same", "meaning": "依然/同样", "grammar": "just the same = all the same 依然"},
    {"phrase": "for sure", "meaning": "确定地", "grammar": "for sure = certainly 确定地"},
    {"phrase": "to tell the truth", "meaning": "说实话", "grammar": "to tell the truth = honestly"},

    # ---- 婚恋/关系 ----
    {"phrase": "tie the knot", "meaning": "结婚", "grammar": "tie the knot 结婚（口语）"},
    {"phrase": "break up", "meaning": "分手", "grammar": "break up (with sb) 与某人分手"},
    {"phrase": "make up", "meaning": "和好/补妆", "grammar": "make up 和好/弥补"},
    {"phrase": "go out", "meaning": "出去/约会", "grammar": "go out (with sb) 与某人约会"},
    {"phrase": "settle down", "meaning": "安定下来", "grammar": "settle down 安定下来/安家"},

    # ---- 自然/天气 ----
    {"phrase": "pouring rain", "meaning": "倾盆大雨", "grammar": "pouring rain 大雨"},
    {"phrase": "clear up", "meaning": "放晴/清理", "grammar": "clear up (天气)放晴"},
    {"phrase": "come rain or shine", "meaning": "风雨无阻", "grammar": "come rain or shine = no matter what"},

    # ---- 思考/信念 ----
    {"phrase": "believe in", "meaning": "相信/信任", "grammar": "believe in sth/sb 相信...的存在/能力"},
    {"phrase": "in my eyes", "meaning": "在我眼中", "grammar": "in one's eyes 在某人看来"},
    {"phrase": "point of view", "meaning": "观点", "grammar": "from my point of view 在我看来"},
    {"phrase": "to be honest", "meaning": "老实说", "grammar": "to be honest = honestly 老实说"},
    {"phrase": "have no idea", "meaning": "不知道", "grammar": "have no idea = don't know"},
    {"phrase": "no wonder", "meaning": "难怪", "grammar": "no wonder = it's not surprising"},
    {"phrase": "make sense", "meaning": "有道理", "grammar": "make sense 说得通/有道理"},
    {"phrase": "to make matters worse", "meaning": "更糟的是", "grammar": "to make matters worse 更糟的是"},

    # ---- 歌词常用 ----
    {"phrase": "over and over", "meaning": "一遍又一遍", "grammar": "over and over 反复地"},
    {"phrase": "again and again", "meaning": "一次又一次", "grammar": "again and again 反复地"},
    {"phrase": "up and down", "meaning": "上上下下/到处", "grammar": "up and down 上上下下"},
    {"phrase": "back and forth", "meaning": "来回", "grammar": "back and forth 来来回回"},
    {"phrase": "here and there", "meaning": "到处", "grammar": "here and there 各处"},
    {"phrase": "now and then", "meaning": "偶尔", "grammar": "now and then = sometimes"},
    {"phrase": "sooner or later", "meaning": "迟早", "grammar": "sooner or later 迟早"},
    {"phrase": "little by little", "meaning": "一点一点地", "grammar": "little by little = gradually"},
    {"phrase": "step by step", "meaning": "一步一步", "grammar": "step by step 逐步地"},
    {"phrase": "side by side", "meaning": "肩并肩", "grammar": "side by side 肩并肩地"},
    {"phrase": "face to face", "meaning": "面对面", "grammar": "face to face 面对面地"},
    {"phrase": "hand in hand", "meaning": "手牵手", "grammar": "hand in hand 手拉手"},
    {"phrase": "word by word", "meaning": "逐词地", "grammar": "word by word 一个词一个词地"},
    {"phrase": "one by one", "meaning": "一个一个地", "grammar": "one by one 逐一地"},
    {"phrase": "all right", "meaning": "好吧/没关系", "grammar": "all right = OK"},
    {"phrase": "no matter what", "meaning": "无论怎样", "grammar": "no matter what = whatever 无论什么"},
    {"phrase": "no matter where", "meaning": "无论在哪", "grammar": "no matter where = wherever 无论哪里"},
    {"phrase": "no matter when", "meaning": "无论何时", "grammar": "no matter when = whenever 无论何时"},
    {"phrase": "no matter how", "meaning": "无论怎样", "grammar": "no matter how = however 无论怎样"},
    {"phrase": "nothing else matters", "meaning": "其他都不重要", "grammar": "nothing else = 没有别的"},
    {"phrase": "right here", "meaning": "就在这里", "grammar": "right here = exactly here"},
    {"phrase": "right there", "meaning": "就在那里", "grammar": "right there = exactly there"},
    {"phrase": "in my life", "meaning": "在我生命中", "grammar": "in one's life 在某人一生中"},
    {"phrase": "in my arms", "meaning": "在我怀里", "grammar": "in one's arms 在怀抱中"},
    {"phrase": "in my heart", "meaning": "在我心里", "grammar": "in one's heart 在心底"},
    {"phrase": "by my side", "meaning": "在我身边", "grammar": "by one's side 在某人身边"},
    {"phrase": "on my way", "meaning": "在途中", "grammar": "on one's way 在路上"},
    {"phrase": "to the top", "meaning": "到顶", "grammar": "to the top 到顶峰"},
    {"phrase": "from the bottom", "meaning": "从底部", "grammar": "from the bottom 从底部"},
    {"phrase": "like a fool", "meaning": "像个傻瓜", "grammar": "like a + 名词 = 像...一样"},
    {"phrase": "in the rain", "meaning": "在雨中", "grammar": "in the rain 在雨里"},
    {"phrase": "in the dark", "meaning": "在黑暗中", "grammar": "in the dark 在暗处/不知情"},
    {"phrase": "in the mirror", "meaning": "在镜子里", "grammar": "in the mirror 在镜子中"},
    {"phrase": "out of the blue", "meaning": "突然", "grammar": "out of the blue = suddenly 突然地"},
    {"phrase": "cry my eyes out", "meaning": "痛哭", "grammar": "cry one's eyes out 哭得死去活来"},
    {"phrase": "wasting time", "meaning": "浪费时间", "grammar": "waste time doing sth 浪费时间做某事"},
    {"phrase": "take my time", "meaning": "慢慢来", "grammar": "take one's time = don't rush"},
    {"phrase": "make it", "meaning": "成功/赶到", "grammar": "make it 成功/赶上"},
    {"phrase": "beating in my chest", "meaning": "在胸口跳动", "grammar": "heart beating = 心跳"},
    {"phrase": "shining like", "meaning": "像...一样闪耀", "grammar": "shining like = 闪耀如"},
    {"phrase": "call my name", "meaning": "叫我的名字", "grammar": "call one's name 呼唤名字"},
    {"phrase": "hold me tight", "meaning": "紧紧抱我", "grammar": "hold sb tight 紧紧抱住"},
    {"phrase": "hold me close", "meaning": "紧紧拥抱我", "grammar": "hold sb close 紧紧拥抱"},
    {"phrase": "stay with me", "meaning": "留在我身边", "grammar": "stay with sb 陪伴某人"},
    {"phrase": "gone too far", "meaning": "走得太远/太过分", "grammar": "go too far 过分/走极端"},
    {"phrase": "too fast", "meaning": "太快", "grammar": "too + adj/adv 太..."},
    {"phrase": "fall apart", "meaning": "崩溃/散架", "grammar": "fall apart 崩溃/瓦解"},
    {"phrase": "come true", "meaning": "实现", "grammar": "come true (梦想等)实现"},
    {"phrase": "meant to be", "meaning": "命中注定", "grammar": "be meant to be 注定"},
    {"phrase": "meant to say", "meaning": "本想说的是", "grammar": "mean to do sth 本打算做"},
    {"phrase": "start over", "meaning": "重新开始", "grammar": "start over = start again 重新开始"},
    {"phrase": "start again", "meaning": "重新开始", "grammar": "start again 重新开始"},
    {"phrase": "begin again", "meaning": "重新开始", "grammar": "begin again 重新开始"},
    {"phrase": "try again", "meaning": "再试一次", "grammar": "try again 再试一次"},
    {"phrase": "do my best", "meaning": "尽我所能", "grammar": "do one's best = try one's best 尽力"},
    {"phrase": "the way", "meaning": "方式/道路", "grammar": "the way (that) ... 的方式"},
    {"phrase": "along the way", "meaning": "沿途/在过程中", "grammar": "along the way 在途中"},
    {"phrase": "on the way", "meaning": "在路上", "grammar": "on the way 在路上/即将"},
    {"phrase": "in a way", "meaning": "在某种意义上", "grammar": "in a way 在某种程度上"},
    {"phrase": "the same", "meaning": "相同的", "grammar": "the same as 与...相同"},
    {"phrase": "the best", "meaning": "最好的", "grammar": "the best 最好的（最高级）"},
    {"phrase": "the rest", "meaning": "剩下的", "grammar": "the rest = the remaining 剩余的"},
    {"phrase": "at last", "meaning": "最后/终于", "grammar": "at last = finally 终于"},
    {"phrase": "at first", "meaning": "起初", "grammar": "at first = in the beginning 起初"},
    {"phrase": "at least", "meaning": "至少", "grammar": "at least 至少"},
    {"phrase": "at most", "meaning": "至多", "grammar": "at most 至多"},
    {"phrase": "all over", "meaning": "到处/结束", "grammar": "all over 到处/完全结束"},
    {"phrase": "all along", "meaning": "一直/始终", "grammar": "all along 一直/始终"},
    {"phrase": "all around", "meaning": "到处", "grammar": "all around = everywhere 到处"},
    {"phrase": "even if", "meaning": "即使", "grammar": "even if = even though 即使"},
    {"phrase": "even though", "meaning": "即使/尽管", "grammar": "even though 尽管（引导让步状语从句）"},
    {"phrase": "what if", "meaning": "如果...会怎样", "grammar": "what if 如果...怎么办"},
    {"phrase": "as if", "meaning": "好像", "grammar": "as if = as though 好像"},
    {"phrase": "only if", "meaning": "只有当", "grammar": "only if 只有在...条件下"},
    {"phrase": "but if", "meaning": "但如果", "grammar": "but if = but (conjunction) + if"},
    {"phrase": "so that", "meaning": "以便/所以", "grammar": "so that 以便（引导目的状语从句）"},
    {"phrase": "in order to", "meaning": "为了", "grammar": "in order to do sth 为了做某事"},
    {"phrase": "be supposed to", "meaning": "应该/被期望", "grammar": "be supposed to do sth 应该做"},
    {"phrase": "used to", "meaning": "过去常常", "grammar": "used to do sth 过去常做（现在不了）"},
    {"phrase": "get used to", "meaning": "习惯于", "grammar": "get used to doing sth 习惯于做某事"},
    {"phrase": "look forward to", "meaning": "期待", "grammar": "look forward to doing sth 期待做"},
    {"phrase": "be able to", "meaning": "能够", "grammar": "be able to do sth 能够做"},
    {"phrase": "have to", "meaning": "必须/不得不", "grammar": "have to do sth 不得不做"},
    {"phrase": "need to", "meaning": "需要", "grammar": "need to do sth 需要做"},
    {"phrase": "want to", "meaning": "想要", "grammar": "want to do sth 想要做"},
    {"phrase": "try to", "meaning": "试图/努力", "grammar": "try to do sth 尝试做"},
    {"phrase": "decide to", "meaning": "决定", "grammar": "decide to do sth 决定做"},
    {"phrase": "forget to", "meaning": "忘记做", "grammar": "forget to do sth 忘记去做"},
    {"phrase": "remember to", "meaning": "记得做", "grammar": "remember to do sth 记得去做"},
    {"phrase": "stop to", "meaning": "停下来去做", "grammar": "stop to do sth 停下（手中的事）去做"},
    {"phrase": "begin to", "meaning": "开始", "grammar": "begin to do sth 开始做"},
    {"phrase": "start to", "meaning": "开始", "grammar": "start to do sth 开始做"},
    {"phrase": "agree to", "meaning": "同意", "grammar": "agree to do sth 同意做"},
    {"phrase": "refuse to", "meaning": "拒绝", "grammar": "refuse to do sth 拒绝做"},
    {"phrase": "happen to", "meaning": "碰巧", "grammar": "happen to do sth 碰巧做"},
    {"phrase": "seem to", "meaning": "似乎", "grammar": "seem to do sth 似乎做"},
    {"phrase": "turn out", "meaning": "结果是", "grammar": "turn out to be 结果是"},
    {"phrase": "find out", "meaning": "发现/查明", "grammar": "find out 发现真相/查明"},
    {"phrase": "work out", "meaning": "解决/锻炼", "grammar": "work out 解决/算出"},
    {"phrase": "think about", "meaning": "考虑", "grammar": "think about sth 考虑某事"},
    {"phrase": "worry about", "meaning": "担心", "grammar": "worry about sth 为...担心"},
    {"phrase": "talk about", "meaning": "谈论", "grammar": "talk about sth 谈论某事"},
    {"phrase": "care about", "meaning": "关心", "grammar": "care about sth 关心/在乎"},
    {"phrase": "know about", "meaning": "了解", "grammar": "know about sth 了解某事"},
    {"phrase": "dream about", "meaning": "梦到", "grammar": "dream about sth 梦见"},
    {"phrase": "laugh about", "meaning": "因...而笑", "grammar": "laugh about sth 因...发笑"},
    {"phrase": "wonder why", "meaning": "想知道为什么", "grammar": "wonder + 疑问词 想知道..."},
    {"phrase": "wonder how", "meaning": "想知道怎么", "grammar": "wonder + 疑问词"},
    {"phrase": "wonder if", "meaning": "想知道是否", "grammar": "wonder if 想知道是否"},
    {"phrase": "there's nothing", "meaning": "什么都没有", "grammar": "there's nothing = 没有什么"},
    {"phrase": "it's just", "meaning": "这只是", "grammar": "it's just = 这只是"},
    {"phrase": "i don't know", "meaning": "我不知道", "grammar": "I don't know = I have no idea"},
    {"phrase": "i can't believe", "meaning": "我不敢相信", "grammar": "can't believe 难以置信"},
    {"phrase": "can't stop", "meaning": "停不下来", "grammar": "can't stop doing sth 停不下来"},
    {"phrase": "won't let", "meaning": "不会让", "grammar": "won't = will not 不会"},
    {"phrase": "don't want", "meaning": "不想", "grammar": "don't want to do 不想做"},
    {"phrase": "don't need", "meaning": "不需要", "grammar": "don't need to do 不需要做"},
    {"phrase": "don't have", "meaning": "没有", "grammar": "don't have = lack 缺乏"},
    {"phrase": "don't know", "meaning": "不知道", "grammar": "don't know = be unaware 不知道"},
    {"phrase": "doesn't matter", "meaning": "没关系", "grammar": "it doesn't matter 没关系"},
    {"phrase": "never mind", "meaning": "没关系/别介意", "grammar": "never mind = it's OK"},
    {"phrase": "no way", "meaning": "不可能", "grammar": "no way = impossible 不可能"},
    {"phrase": "of course", "meaning": "当然", "grammar": "of course = certainly"},
    {"phrase": "for sure", "meaning": "确定", "grammar": "for sure = certainly"},
    {"phrase": "to be honest", "meaning": "说实话", "grammar": "to be honest = honestly"},
    {"phrase": "so far away", "meaning": "那么遥远", "grammar": "so far = this far 这么远"},
    {"phrase": "long ago", "meaning": "很久以前", "grammar": "long ago = a long time ago"},
    {"phrase": "long time", "meaning": "很长时间", "grammar": "a long time 很长时间"},
    {"phrase": "every time", "meaning": "每次", "grammar": "every time 每次/每当"},
    {"phrase": "the first time", "meaning": "第一次", "grammar": "the first time 第一次"},
    {"phrase": "next time", "meaning": "下次", "grammar": "next time 下次"},
    {"phrase": "last time", "meaning": "上次", "grammar": "last time 上次"},
    {"phrase": "this time", "meaning": "这次", "grammar": "this time 这次"},
    {"phrase": "same time", "meaning": "同时", "grammar": "at the same time 同时"},
    {"phrase": "right now", "meaning": "现在", "grammar": "right now = immediately 现在"},
    {"phrase": "just now", "meaning": "刚才", "grammar": "just now = a moment ago 刚才"},
    {"phrase": "from now on", "meaning": "从现在起", "grammar": "from now on 从今以后"},
    {"phrase": "ever since", "meaning": "自从", "grammar": "ever since 自从...以来"},
    {"phrase": "far away", "meaning": "遥远", "grammar": "far away = distant 遥远的"},
    {"phrase": "long way", "meaning": "很长的路", "grammar": "a long way 很长一段距离"},
    {"phrase": "close to", "meaning": "接近", "grammar": "be close to 靠近"},
    {"phrase": "meant for", "meaning": "注定属于", "grammar": "be meant for 为...而存在"},
    {"phrase": "too late", "meaning": "太迟了", "grammar": "too late 太晚了"},
    {"phrase": "too much", "meaning": "太多", "grammar": "too much 太多（修饰不可数名词）"},
    {"phrase": "so much", "meaning": "如此多", "grammar": "so much 这么多"},
    {"phrase": "so many", "meaning": "如此多", "grammar": "so many 这么多（可数名词）"},
    {"phrase": "so long", "meaning": "那么久", "grammar": "so long = goodbye 再见"},
    {"phrase": "so sad", "meaning": "如此悲伤", "grammar": "so + adj 如此..."},
    {"phrase": "such a", "meaning": "如此一个", "grammar": "such a/an + adj + noun 如此...的一个"},
    {"phrase": "what a", "meaning": "多么", "grammar": "what a/an + adj + noun 多么...的"},
    {"phrase": "looking for", "meaning": "寻找", "grammar": "look for 寻找（强调过程）"},
    {"phrase": "waiting for", "meaning": "等待", "grammar": "wait for 等待"},
    {"phrase": "asking for", "meaning": "请求", "grammar": "ask for 请求/要求"},
    {"phrase": "paying for", "meaning": "为...付出", "grammar": "pay for 为...付钱/付出代价"},
    {"phrase": "known for", "meaning": "因...而闻名", "grammar": "be known for 因...闻名"},
    {"phrase": "singing along", "meaning": "跟着唱", "grammar": "sing along 跟着唱"},
    {"phrase": "go wrong", "meaning": "出问题", "grammar": "go wrong 出错/出毛病"},
    {"phrase": "do wrong", "meaning": "做错", "grammar": "do wrong 做错事"},
    {"phrase": "strong enough", "meaning": "足够强", "grammar": "adj + enough 足够..."},
    {"phrase": "good enough", "meaning": "足够好", "grammar": "adj + enough 足够..."},
    {"phrase": "old enough", "meaning": "足够老/大", "grammar": "adj + enough 足够..."},
    {"phrase": "ready for", "meaning": "准备好", "grammar": "be ready for 为...做好准备"},
    {"phrase": "sorry for", "meaning": "为...抱歉", "grammar": "be sorry for 为...感到抱歉"},
    {"phrase": "famous for", "meaning": "因...出名", "grammar": "be famous for 因...而出名"},
    {"phrase": "late for", "meaning": "迟到", "grammar": "be late for 迟到"},
    {"phrase": "afraid of", "meaning": "害怕", "grammar": "be afraid of sth/sb 害怕"},
    {"phrase": "proud of", "meaning": "为...骄傲", "grammar": "be proud of 为...自豪"},
    {"phrase": "tired of", "meaning": "厌倦", "grammar": "be tired of 对...厌倦"},
    {"phrase": "full of", "meaning": "充满", "grammar": "be full of 充满"},
    {"phrase": "made of", "meaning": "由...制成", "grammar": "be made of 由...制成（看得出材料）"},
    {"phrase": "dream of", "meaning": "梦想", "grammar": "dream of doing sth 梦想做某事"},
    {"phrase": "think of", "meaning": "想到", "grammar": "think of 想到/想起"},
    {"phrase": "hear of", "meaning": "听说", "grammar": "hear of 听说（间接）"},
    {"phrase": "speak of", "meaning": "谈到", "grammar": "speak of 谈到"},
    {"phrase": "die for", "meaning": "为...而死/极度渴望", "grammar": "die for 为...而死"},
    {"phrase": "fight for", "meaning": "为...而战", "grammar": "fight for 为...而战"},
    {"phrase": "hope for", "meaning": "期望", "grammar": "hope for sth 期望得到"},
    {"phrase": "wish for", "meaning": "希望", "grammar": "wish for sth 希望得到"},
]


# ============================================================
# API 获取歌词和翻译
# ============================================================
def search_netease_id(song_name, artist=""):
    """通过网易云搜索API查找歌曲ID"""
    query = f"{song_name} {artist}".strip()
    api_url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&offset=0&limit=5"
    try:
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("result") and data["result"].get("songs"):
                for s in data["result"]["songs"]:
                    artists = ", ".join(a["name"] for a in s["artists"])
                    # 优先匹配艺术家名称
                    if artist and artist.lower() in artists.lower():
                        return s["id"], artists
                # 没有精确匹配就取第一个
                first = data["result"]["songs"][0]
                artists = ", ".join(a["name"] for a in first["artists"])
                return first["id"], artists
    except Exception as e:
        print(f"[WARN] 搜索失败: {e}")
    return None, None


def is_english_text(text):
    """判断文本是否主要是英文（ASCII字符占多数）"""
    # 计算ASCII字符占比
    ascii_count = sum(1 for c in text if ord(c) < 128)
    # 跳过标点和空白后检查
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return True  # 没有字母，按英文处理
    ascii_alpha = sum(1 for c in alpha if ord(c) < 128)
    return ascii_alpha / len(alpha) > 0.5


def parse_lyric_lines(raw_lyric):
    """解析歌词，返回按时间戳组织的列表"""
    lines = []
    for line in raw_lyric.split("\n"):
        line = line.strip()
        if not line:
            continue
        ts_match = re.match(r"\[(\d{2}:\d{2}\.\d{1,3})\]", line)
        if not ts_match:
            continue
        ts = ts_match.group(1)
        text = re.sub(r"\[\d{2}:\d{2}\.\d{1,3}\]", "", line).strip()
        # 跳过标签行
        if not text or text.startswith(("作词", "作曲", "编曲", "混音", "制作人", "by:", "By:", "offset")):
            continue
        if len(text) < 2:
            continue
        lines.append((ts, text))
    return lines


def fetch_lyrics(netease_id):
    """通过网易云API获取歌词和中文翻译，返回 (英文字幕列表, 中文字幕列表)
    智能判断：如果是英文歌用lrc作主歌词，如果是中文歌用tlyric作主歌词（英文翻译）
    """
    api_url = f"https://music.163.com/api/song/lyric?id={netease_id}&lv=1&tv=1"
    try:
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.163.com"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        lrc_data = data.get("lrc", {}).get("lyric", "")
        tlyric_data = data.get("tlyric", {}).get("lyric", "")

        # 解析两套歌词
        lrc_lines = parse_lyric_lines(lrc_data) if lrc_data else []
        tlyric_lines = parse_lyric_lines(tlyric_data) if tlyric_data else []

        # 建立时间戳到文本的映射
        lrc_map = {ts: text for ts, text in lrc_lines}
        tlyric_map = {ts: text for ts, text in tlyric_lines}

        # 收集所有时间戳
        all_ts = sorted(set(list(lrc_map.keys()) + list(tlyric_map.keys())))

        # 判断原歌词是英文还是非英文
        # 采样前10行检查
        sample_texts = [text for ts, text in lrc_lines[:10]]
        is_english_song = all(is_english_text(t) for t in sample_texts if t)

        if is_english_song:
            # 英文歌：lrc是英文，tlyric是中文翻译
            en_lyrics = [lrc_map.get(ts, "") for ts in all_ts]
            zh_lyrics = [tlyric_map.get(ts, "") for ts in all_ts]
        else:
            # 非英文歌（如中文歌）：tlyric是英文翻译，lrc是中文原文
            en_lyrics = [tlyric_map.get(ts, lrc_map.get(ts, "")) for ts in all_ts]
            zh_lyrics = [lrc_map.get(ts, "") for ts in all_ts]

        # 过滤空行
        result = [(e, z) for e, z in zip(en_lyrics, zh_lyrics) if e.strip()]

        if not result:
            return [], []

        return list(zip(*result)) if result else ([], [])

    except Exception as e:
        print(f"[WARN] 获取歌词失败: {e}")
        return [], []


def get_lyrics_with_fallback(song_name, artist, netease_id):
    """获取歌词，如果指定ID失败则通过搜索查找"""
    # 先尝试指定的ID
    en, zh = fetch_lyrics(netease_id)
    if en:
        return en, zh, netease_id

    # 指定ID失败，通过搜索查找
    print(f"  [WARN] ID:{netease_id} 无歌词，搜索: {song_name} - {artist}")
    found_id, found_artist = search_netease_id(song_name, artist)
    if found_id:
        print(f"  [INFO] 搜索到ID:{found_id} ({found_artist})")
        en, zh = fetch_lyrics(found_id)
        if en:
            return en, zh, found_id

    return [], [], None


CF_WORKER = "quiet-term-cc2f.zjunxcr.workers.dev"

def fetch_mp3_url(netease_id):
    """通过第三方API获取网易云音乐MP3直链，并转为 Cloudflare Worker HTTPS 代理地址"""
    api_url = f"https://api.byfuns.top/1/?id={netease_id}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            mp3_url = resp.read().decode("utf-8").strip()
            if mp3_url.startswith("http://m801.music.126.net/"):
                # 用 Cloudflare Worker 把 HTTP 转成 HTTPS，手机可内嵌播放
                audio_path = mp3_url[len("http://"):]  # 去掉 "http://" 剩 "m801.music.126.net/..."
                return f"https://{CF_WORKER}/proxy/{audio_path}"
            elif mp3_url.startswith("http"):
                # 其他 HTTP 源同样处理
                audio_path = mp3_url[len("http://"):]
                return f"https://{CF_WORKER}/proxy/{audio_path}"
            elif mp3_url.startswith("https"):
                # 已经是 HTTPS 直接返回
                return mp3_url
    except Exception as e:
        print(f"[WARN] 获取MP3链接失败: {e}")
    return None


# ============================================================
# 自动检测歌词中的生词
# ============================================================
def extract_words(text):
    """从英文文本中提取所有英文单词（小写）"""
    return set(re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text.lower()))


def find_hard_words(lyrics_lines, basic_words=None):
    """
    找出歌词中所有非基础词汇的"生词"
    返回: [(word, count)] 按出现频率降序
    """
    if basic_words is None:
        basic_words = ALL_BASIC_WORDS

    # 收集所有歌词中的单词
    all_words = set()
    for line in lyrics_lines:
        words = extract_words(line)
        # 过滤掉太短的词（1-2个字母的基本不需要标注）
        all_words.update(w for w in words if len(w) > 2)

    # 找出不在基础词表中的词
    hard = all_words - basic_words

    # 过滤掉一些不需要标注的词
    skip = {"nt", "ll", "ve", "re", "d", "m", "s", "t", "don", "doesn",
            "didn", "wasn", "weren", "couldn", "wouldn", "shouldn", "ain",
            "gonna", "wanna", "gotta", "kinda", "sorta", "outta", "dunno",
            "ya", "ya", "ol", "ooh", "ah", "oh", "hey", "yeah", "yeh",
            "na", "da", "la", "mm", "hm", "uh", "em", "ba", "eh", "oo",
            "imma", "tryna", "bout", "cause", "till", "round", "bout"}
    hard = hard - skip

    # 统计词频
    word_count = {}
    for line in lyrics_lines:
        words = extract_words(line)
        for w in words:
            if w in hard:
                word_count[w] = word_count.get(w, 0) + 1

    # 按频率降序排列
    return sorted(word_count.items(), key=lambda x: x[1], reverse=True)


# ============================================================
# 自动匹配歌词中的俚语/地道表达
# ============================================================
def find_slang_in_lyrics(lyrics_lines):
    """在歌词中查找俚语/地道表达"""
    # 把所有歌词合成一个文本用于匹配
    full_text = " ".join(lyrics_lines).lower()
    found = []

    for entry in SLANG_DB:
        phrase_lower = entry["phrase"].lower()
        if phrase_lower in full_text:
            # 记录找到的俚语
            found.append(entry)

    return found


# ============================================================
# 选择今日歌曲（动态选择，去重）
# ============================================================
def get_used_songs():
    """读取已使用过的歌曲记录（从GitHub Actions的memory中）"""
    import os
    mem_path = os.path.join(os.path.dirname(__file__), ".codebuddy", "automations", "automation", "memory.md")
    if os.path.exists(mem_path):
        try:
            with open(mem_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 查找 ## 已用歌曲 部分或 song_history 行
            used = set()
            for line in content.split("\n"):
                if line.strip().startswith("song_history:"):
                    # 解析歌曲名列表
                    songs_str = line.split("song_history:", 1)[1].strip()
                    for s in songs_str.split(","):
                        s = s.strip().strip("'\"")
                        if s:
                            used.add(s)
            return used
        except:
            pass
    return set()


def select_daily_song(level=None, exclude=None):
    """
    动态选择一首歌曲
    level: 1=入门, 2=初级, 3=中级, None=随机
    exclude: 需要排除的歌曲名集合
    """
    import hashlib

    if exclude is None:
        exclude = set()

    # 根据level筛选歌曲
    if level:
        pool = [s for s in SONG_LIBRARY if s["level"] == level and s["name"] not in exclude]
    else:
        pool = [s for s in SONG_LIBRARY if s["name"] not in exclude]

    if not pool:
        # 如果筛选后没有歌曲，回退到全部歌曲
        pool = [s for s in SONG_LIBRARY if s["name"] not in exclude]

    if not pool:
        # 所有歌曲都用过了，重新开始
        pool = SONG_LIBRARY

    # 用日期做种子选择，同一天选同一首
    from datetime import date
    today = date.today().isoformat()
    day_seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
    return pool[day_seed % len(pool)]


# ============================================================
# 生成歌曲学习HTML（供 generate-today-words.py 调用）
# ============================================================
def generate_auto_song_html(svg_speaker):
    """
    自动选择歌曲并生成HTML
    返回: (html_str, song_info_dict)
    """
    import hashlib
    from datetime import date

    # 获取已用歌曲
    used = get_used_songs()

    # 动态选择（不带level限制，让系统自然轮换）
    song = select_daily_song(exclude=used)

    print(f"  [歌曲] 今日推荐: {song['name']} - {song['artist']} (难度{song['level']})")

    # 获取歌词（带搜索备选）
    en_lyrics, zh_lyrics, actual_id = get_lyrics_with_fallback(
        song["name"], song["artist"], song["netease_id"]
    )
    if not en_lyrics:
        print(f"  [WARN] 歌词获取失败，跳过歌曲: {song['name']}")
        return None, None

    # 用实际获取到的ID获取MP3
    mp3_id = actual_id or song["netease_id"]

    # 限制歌词行数（最多30行，避免太长）
    max_lines = 30
    if len(en_lyrics) > max_lines:
        en_lyrics = en_lyrics[:max_lines]
        zh_lyrics = zh_lyrics[:max_lines]

    # 检测生词
    hard_words = find_hard_words(en_lyrics)
    hard_word_set = set(w for w, _ in hard_words)

    # 检测俚语
    found_slang = find_slang_in_lyrics(en_lyrics)
    slang_phrases = {s["phrase"].lower() for s in found_slang}

    # 生成每行歌词HTML（图片样式：行内标注俚语+生词）
    lyrics_html = ""
    for i, en_line in enumerate(en_lyrics):
        zh_line = zh_lyrics[i] if i < len(zh_lyrics) else ""

        # 收集该行所有的俚语和生词标注
        note_items = []

        # 检测俚语
        for slang in found_slang:
            if slang["phrase"].lower() in en_line.lower():
                phrase_safe = slang["phrase"].replace("'", "\\'")
                note_items.append(f'<span class="lyric-note slang-note">💡 {slang["phrase"]} /{slang["meaning"]}/ <button onclick="speakWord(this,\'{phrase_safe}\')">{svg_speaker}</button></span>')

        # 检测生词（简化标注）
        line_words = extract_words(en_line)
        line_hard = [w for w in line_words if w in hard_word_set and len(w) > 2]
        seen = set()
        unique_hard = []
        for w in line_hard:
            if w not in seen:
                seen.add(w)
                unique_hard.append(w)

        for hw in unique_hard[:5]:  # 每行最多标5个生词
            hw_safe = hw.replace("'", "\\'")
            note_items.append(f'<span class="lyric-note hard-note"><b>{hw}</b> <button onclick="speakWord(this,\'{hw_safe}\')">{svg_speaker}</button></span>')

        # 合并标注
        notes_html = ""
        if note_items:
            notes_html = '<div class="lyric-notes">' + " ".join(note_items) + '</div>'

        lyrics_html += f'''
      <div class="lyric-line">
        <div class="lyric-en">{en_line}</div>
        <div class="lyric-zh">{zh_line}</div>
        {notes_html}
      </div>'''

    # 生词总览（现在只在行内标注，删除总览）
    hard_overview_html = ""
    slang_overview_html = ""

    # ============== 添加生词拼读区块 ==============
    # 收集所有生词，获取音标
    all_hard_words = []
    for word, count in hard_words[:20]:  # 最多20个生词
        phonetic = get_phonetic(word)
        syll = syllabify(word)
        all_hard_words.append({
            "word": word,
            "ipa": phonetic["ipa"],
            "syllables": syll,
            "pos": phonetic["pos"],
            "definition": phonetic["definition"]
        })
        time.sleep(0.1)  # 避免请求过快

    vocab_phonetic_html = ""
    if all_hard_words:
        entries = []
        for item in all_hard_words:
            word_safe = item["word"].replace("'", "\\'")
            ipa_str = f" {item['ipa']}" if item['ipa'] else ""
            pos_str = f" {item['pos']}." if item['pos'] else ""
            def_str = f" {item['definition']}" if item['definition'] else ""
            entries.append(f'<p class="phonetic-entry"><strong>{item["word"]}</strong>{ipa_str} {item["syllables"]}{pos_str}{def_str} <button onclick="speakWord(this,\'{word_safe}\')">{svg_speaker}</button></p>')
        vocab_phonetic_html = f'''
    <div class="vocab-phonetic">
      <h4 class="vocab-phonetic-title">📝 生词拼读</h4>
      {"".join(entries)}
    </div>'''

    # ============== 添加重点句型解析 ==============
    # 从歌词中选择几句有代表性的作为重点句型
    key_sentences = []
    for i, en_line in enumerate(en_lyrics):
        # 选择有完整意思、比较短或语法有代表性的行
        clean_line = en_line.strip()
        if len(clean_line) > 5 and len(clean_line) < 60 and not clean_line.startswith("["):
            zh_line = zh_lyrics[i] if i < len(zh_lyrics) else ""
            # 获取该句的音标
            words_in_line = list(extract_words(clean_line))
            sentence_phonetic = ""
            for w in words_in_line[:3]:  # 只取前3个词的音标
                p = get_phonetic(w)
                if p["ipa"]:
                    sentence_phonetic = p["ipa"]
                    break
            
            key_sentences.append({
                "en": clean_line,
                "zh": zh_line,
                "ipa": sentence_phonetic
            })
            time.sleep(0.1)
            if len(key_sentences) >= 3:  # 最多3句
                break

    key_patterns_html = ""
    if key_sentences:
        pattern_items = []
        for item in key_sentences:
            en_safe = item["en"].replace("'", "\\'")
            ipa_str = f"<p class=\"pattern-ipa\">/{item['ipa']}/</p>" if item['ipa'] else ""
            pattern_items.append(f'''
      <div class="pattern-item">
        <p class="pattern-quote">"{item['en']}"</p>
        {ipa_str}
        <p class="pattern-syllables">{item['en']} <button onclick="speakWord(this,\'{en_safe}\')">{svg_speaker}</button></p>
        <p class="pattern-translation">{item['zh']}</p>
      </div>''')
        key_patterns_html = f'''
    <div class="key-patterns">
      <h4 class="key-patterns-title">🎯 重点句型解析（点击🔊听发音）</h4>
      {"".join(pattern_items)}
    </div>'''

    # 播放器：内嵌优先 + 备用链接
    player_html = f'''
    <div class="song-player">
      <audio id="song-audio" src="https://quiet-term-cc2f.zjunxcr.workers.dev/proxy/{mp3_id}.mp3" controls preload="none" style="width:100%;border-radius:10px;">
      </audio>
      <div class="player-fallback">
        🎧 播放失败？<a href="https://music.163.com/song?id={mp3_id}" target="_blank">点击前往网易云音乐收听</a>
      </div>
    </div>'''

    # 难度标签
    level_labels = {1: "🌟 入门级", 2: "⭐ 初级", 3: "⭐⭐ 中级"}
    level_label = level_labels.get(song["level"], "⭐⭐ 中级")

    html = f'''
<div class="bonus-section song-day">
  <div class="bonus-title">🎵 兴趣加餐 · 听歌学英语</div>
  <div class="bonus-content">
    <div class="song-header">
      <div class="song-name">{song["name"]} <span class="song-year">({song["year"]})</span></div>
      <div class="song-artist">🎤 {song["artist"]}</div>
      <div class="song-tense">
        <span class="tense-badge">{song["tense"]}</span>
        <span class="tense-en">{song["tense_en"]}</span>
        <span class="level-badge">{level_label}</span>
      </div>
      <div class="tense-rule">📌 {song["tense_rule"]}</div>
    </div>
    {player_html}'''

    # 歌词区域
    html += f'''
    <div class="lyrics-box">
      <div class="lyrics-title">🎶 歌词</div>
      {lyrics_html}
    </div>'''

    # 生词拼读区块
    html += vocab_phonetic_html

    # 重点句型解析
    html += key_patterns_html

    html += f'''
    <div class="bonus-tip">
      <strong>🎧 学习建议：</strong>先完整听两遍感受旋律，再看歌词跟读。标注的俚语和生词点击🔊听发音。
    </div>
  </div>
</div>'''

    song_info = {
        "name": song["name"],
        "artist": song["artist"],
        "level": song["level"],
    }

    return html, song_info


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    SVG_SPEAKER = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M19.07 4.93a10 10 0 010 14.14M15.54 8.46a5 5 0 010 7.07"/></svg>'

    html, info = generate_auto_song_html(SVG_SPEAKER)
    if html:
        print(f"歌曲: {info['name']} - {info['artist']} (难度{info['level']})")
        print(f"HTML长度: {len(html)}")
        print(html[:200])
    else:
        print("生成失败")
