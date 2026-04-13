"""
每日英语单词生成器 v3 - 完全自动化版
核心改进：
1. 内建200+词库，自动随机抽取（7 NZ日常 + 3 雅思移民）
2. 自动去重：读取 memory.md 中已用过的单词
3. 兴趣加餐按星期轮换：
   - 周一/三/五：英文歌曲推荐（从歌曲库动态选择）
   - 周二/四/六：老友记风格场景对话（从对话库动态选择）
   - 周日：轻松复习版（回顾本周单词）
4. HTML模板参考 2026-04-03 示例，手机友好
5. 使用 speechSynthesis 实现点击发音（不依赖edge-tts）
"""

import hashlib
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = Path(__file__).parent
TODAY = datetime.now().strftime('%Y-%m-%d')
TODAY_DATE = datetime.now()
WEEKDAY = TODAY_DATE.weekday()  # 0=周一 ... 6=周日
WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
OUTPUT = BASE_DIR / f"每日英语单词_{TODAY}.html"

# 导入歌曲数据库
from songs_db import SONGS_DB


# ============================================================
# 大词库：200+ 单词，分类标注
# ============================================================
WORD_BANK = {
    "nz": [
        # ---- 租房 ----
        {"word": "tenancy", "phonetic": "/ˈtenənsi/", "syllable": "ten · an · cy", "pos": "n.",
         "meaning": "租约；租赁期",
         "example": "Make sure you read the tenancy agreement carefully before signing.",
         "example_cn": "签字前一定要仔细阅读租赁协议。", "scene": "🏠 租房签约",
         "grammar": "祈使句：Make sure + 主从结构，表示叮嘱",
         "sentence_words": [
             {"word": "agreement", "phonetic": "/əˈɡriːmənt/", "syllable": "a·gree·ment", "meaning": "n. 协议；合同"},
             {"word": "carefully", "phonetic": "/ˈkeəfəli/", "syllable": "care·ful·ly", "meaning": "adv. 仔细地"},
             {"word": "signing", "phonetic": "/ˈsaɪnɪŋ/", "syllable": "sign·ing", "meaning": "v. 签字（现在分词）"},
             {"word": "read", "phonetic": "/riːd/", "syllable": "read", "meaning": "v. 阅读；读（read过去式仍写read）"},
         ]},
        {"word": "bond", "phonetic": "/bɒnd/", "syllable": "bond", "pos": "n.",
         "meaning": "押金（租房）",
         "example": "The bond is four weeks' rent. You'll get it back if there's no damage.",
         "example_cn": "押金是四周的租金。如果没有损坏，你会拿回来的。", "scene": "🏠 租房签约",
         "grammar": "主系表结构 + 条件句：if there's no damage（如果没有损坏）",
         "sentence_words": [
             {"word": "damage", "phonetic": "/ˈdæmɪdʒ/", "syllable": "dam·age", "meaning": "n. 损坏；损害"},
             {"word": "rent", "phonetic": "/rent/", "syllable": "rent", "meaning": "n. 租金"},
             {"word": "weeks", "phonetic": "/wiːks/", "syllable": "weeks", "meaning": "n. 周（week的复数）"},
         ]},
        {"word": "landlord", "phonetic": "/ˈlændlɔːd/", "syllable": "land · lord", "pos": "n.",
         "meaning": "房东",
         "example": "My landlord is pretty chill about fixing things.",
         "example_cn": "我房东对修东西的事挺随和的。", "scene": "🏠 租房",
         "grammar": "一般现在时：is + 形容词，表示当前状态；be chill about = 对...随和",
         "sentence_words": [
             {"word": "chill", "phonetic": "/tʃɪl/", "syllable": "chill", "meaning": "adj. 随和的；放松的（口语）"},
             {"word": "fixing", "phonetic": "/ˈfɪksɪŋ/", "syllable": "fix·ing", "meaning": "v. 修理（现在分词）"},
             {"word": "pretty", "phonetic": "/ˈprɪti/", "syllable": "pret·ty", "meaning": "adv. 挺；相当（口语）"},
         ]},
        {"word": "flatmate", "phonetic": "/ˈflætmeɪt/", "syllable": "flat · mate", "pos": "n.",
         "meaning": "室友；合租伙伴",
         "example": "My flatmate is moving out next month.",
         "example_cn": "我室友下个月要搬走了。", "scene": "🏠 合租生活",
         "grammar": "现在进行时表将来：is moving out，+时间状语 next month 表近期计划",
         "sentence_words": [
             {"word": "moving out", "phonetic": "/ˈmuːvɪŋ aʊt/", "syllable": "mov·ing out", "meaning": "v. 搬出去（move out 短语动词）"},
             {"word": "month", "phonetic": "/mʌnθ/", "syllable": "month", "meaning": "n. 月；月份"},
         ]},
        {"word": "inspection", "phonetic": "/ɪnˈspekʃn/", "syllable": "in · spec · tion", "pos": "n.",
         "meaning": "检查（租房定期检查）",
         "example": "The property inspection is next Thursday. Just tidy up a bit.",
         "example_cn": "房子检查在下周四。稍微收拾一下就行。", "scene": "🏠 租房检查",
         "grammar": "主系表结构 + 祈使句：Just tidy up（只需收拾一下）",
         "sentence_words": [
             {"word": "property", "phonetic": "/ˈprɒpəti/", "syllable": "prop·er·ty", "meaning": "n. 房产；物业"},
             {"word": "tidy up", "phonetic": "/ˈtaɪdi ʌp/", "syllable": "ti·dy up", "meaning": "v. 整理；收拾（短语动词）"},
             {"word": "Thursday", "phonetic": "/ˈθɜːzdeɪ/", "syllable": "Thurs·day", "meaning": "n. 周四"},
             {"word": "bit", "phonetic": "/bɪt/", "syllable": "bit", "meaning": "n. 一点；少量（a bit = 有点儿）"},
         ]},
        {"word": "notice", "phonetic": "/ˈnəʊtɪs/", "syllable": "no · tice", "pos": "n.",
         "meaning": "通知；提前通知（退租等）",
         "example": "You need to give 21 days' notice before moving out.",
         "example_cn": "搬走前需要提前21天通知房东。", "scene": "🏠 退租",
         "grammar": "need to + 动词原形：需要做某事；before + 动名词表时间先后",
         "sentence_words": [
             {"word": "give notice", "phonetic": "/ɡɪv ˈnəʊtɪs/", "syllable": "give no·tice", "meaning": "v. 提前通知（固定搭配）"},
             {"word": "moving out", "phonetic": "/ˈmuːvɪŋ aʊt/", "syllable": "mov·ing out", "meaning": "v. 搬出去"},
             {"word": "before", "phonetic": "/bɪˈfɔːr/", "syllable": "be·fore", "meaning": "prep. 在……之前"},
         ]},
        {"word": "furnished", "phonetic": "/ˈfɜːnɪʃt/", "syllable": "fur · nished", "pos": "adj.",
         "meaning": "带家具的",
         "example": "Is this flat fully furnished or do I need to buy my own stuff?",
         "example_cn": "这套公寓带全套家具吗，还是我需要自己买？", "scene": "🏠 租房",
         "grammar": "选择疑问句：Is...or do I need to...，两个选项并列",
         "sentence_words": [
             {"word": "flat", "phonetic": "/flæt/", "syllable": "flat", "meaning": "n. 公寓（英/NZ用法）"},
             {"word": "fully", "phonetic": "/ˈfʊli/", "syllable": "ful·ly", "meaning": "adv. 完全地；充分地"},
             {"word": "stuff", "phonetic": "/stʌf/", "syllable": "stuff", "meaning": "n. 东西；物品（口语）"},
             {"word": "buy", "phonetic": "/baɪ/", "syllable": "buy", "meaning": "v. 买；购买"},
             {"word": "own", "phonetic": "/əʊn/", "syllable": "own", "meaning": "adj. 自己的；pron. 自己的东西"},
         ]},
        {"word": "lease", "phonetic": "/liːs/", "syllable": "lease", "pos": "n.",
         "meaning": "租约",
         "example": "We signed a one-year lease on this place.",
         "example_cn": "我们签了一年的租约。", "scene": "🏠 租房签约",
         "grammar": "一般过去时：signed（sign 的过去式），表示已完成的动作",
         "sentence_words": [
             {"word": "signed", "phonetic": "/saɪnd/", "syllable": "signed", "meaning": "v. 签署（过去式）"},
             {"word": "one-year", "phonetic": "/wʌn jɪər/", "syllable": "one-year", "meaning": "adj. 一年期的（复合形容词）"},
             {"word": "place", "phonetic": "/pleɪs/", "syllable": "place", "meaning": "n. 地方；住所"},
         ]},

        # ---- 超市/购物 ----
        {"word": "dairy", "phonetic": "/ˈdeəri/", "syllable": "dai · ry", "pos": "n.",
         "meaning": "便利店（NZ特有叫法）",
         "example": "I'll grab some milk from the dairy down the road.",
         "example_cn": "我去路口便利店买点牛奶。", "scene": "🏪 日常购物",
         "grammar": "will + 动词原形（将来时）：I'll grab 表示说话时决定要做的事",
         "sentence_words": [
             {"word": "grab", "phonetic": "/ɡræb/", "syllable": "grab", "meaning": "v. 拿；取（口语常用）"},
             {"word": "milk", "phonetic": "/mɪlk/", "syllable": "milk", "meaning": "n. 牛奶"},
             {"word": "down the road", "phonetic": "/daʊn ðə rəʊd/", "syllable": "down the road", "meaning": "prep. 在路的尽头；不远处"},
             {"word": "road", "phonetic": "/rəʊd/", "syllable": "road", "meaning": "n. 路；道路"},
         ]},
        {"word": "queue", "phonetic": "/kjuː/", "syllable": "queue（单音节）", "pos": "n./v.",
         "meaning": "排队；队列",
         "example": "There's a long queue at the checkout. Let's use self-service.",
         "example_cn": "收银台排了好长的队。我们去自助结账吧。", "scene": "🏪 超市结账",
         "grammar": "There be 句型 + 祈使句（Let's...表示提建议）",
         "sentence_words": [
             {"word": "checkout", "phonetic": "/ˈtʃekaʊt/", "syllable": "check·out", "meaning": "n. 收银台；结账处"},
             {"word": "self-service", "phonetic": "/ˌself ˈsɜːvɪs/", "syllable": "self-ser·vice", "meaning": "n. 自助服务"},
             {"word": "long", "phonetic": "/lɒŋ/", "syllable": "long", "meaning": "adj. 长的（此处指队伍长）"},
         ]},
        {"word": "trolley", "phonetic": "/ˈtrɒli/", "syllable": "trol · ley", "pos": "n.",
         "meaning": "购物车（NZ/英式）",
         "example": "Can you grab a trolley? I forgot to get one.",
         "example_cn": "你能推一辆购物车吗？我忘了拿。", "scene": "🏪 超市",
         "grammar": "Can you...? 表示请求；I forgot to do sth. 忘记做某事",
         "sentence_words": [
             {"word": "forgot", "phonetic": "/fəˈɡɒt/", "syllable": "for·got", "meaning": "v. 忘记（forget 的过去式）"},
         ]},
        {"word": "receipt", "phonetic": "/rɪˈsiːt/", "syllable": "re · ceipt", "pos": "n.",
         "meaning": "收据；小票",
         "example": "Keep the receipt in case you need to return it.",
         "example_cn": "保留好小票，以防需要退货。", "scene": "🏪 购物退换",
         "grammar": "祈使句：Keep...；in case + 从句，表示以防万一",
         "sentence_words": [
             {"word": "keep", "phonetic": "/kiːp/", "syllable": "keep", "meaning": "v. 保留；保存"},
             {"word": "in case", "phonetic": "/ɪn keɪs/", "syllable": "in case", "meaning": "conj. 以防；万一（固定搭配）"},
             {"word": "return", "phonetic": "/rɪˈtɜːn/", "syllable": "re·turn", "meaning": "v. 退还；归还"},
         ]},
        {"word": "special", "phonetic": "/ˈspeʃl/", "syllable": "spe · cial", "pos": "n./adj.",
         "meaning": "特价商品；特别的",
         "example": "Mince is on special this week at Pak'nSave.",
         "example_cn": "这周Pak'nSave的肉末特价。", "scene": "🏪 超市促销",
         "grammar": "on special = 打折特价（NZ固定表达），一般现在时表当前状态",
         "sentence_words": [
             {"word": "mince", "phonetic": "/mɪns/", "syllable": "mince", "meaning": "n. 肉末；绞肉（NZ超市常见）"},
             {"word": "on special", "phonetic": "/ɒn ˈspeʃl/", "syllable": "on spe·cial", "meaning": "phrase. 特价中（NZ口语）"},
         ]},
        {"word": "eftpos", "phonetic": "/ˈeftɒs/", "syllable": "ef · tpos", "pos": "n.",
         "meaning": "电子刷卡机（NZ通用）",
         "example": "Can I pay by EFTPOS? I don't have any cash on me.",
         "example_cn": "我能刷卡吗？我没带现金。", "scene": "🏪 支付",
         "grammar": "Can I...? 表示请求许可；I don't have...on me（身上没有...）",
         "sentence_words": [
             {"word": "pay by", "phonetic": "/peɪ baɪ/", "syllable": "pay by", "meaning": "v. 以...方式支付（固定搭配）"},
             {"word": "cash", "phonetic": "/kæʃ/", "syllable": "cash", "meaning": "n. 现金"},
             {"word": "on me", "phonetic": "/ɒn miː/", "syllable": "on me", "meaning": "phrase. 随身携带（口语）"},
         ]},
        {"word": "produce", "phonetic": "/ˈprɒdjuːs/", "syllable": "pro · duce", "pos": "n.",
         "meaning": "农产品区（水果蔬菜）",
         "example": "The produce section is over there, next to the bakery.",
         "example_cn": "果蔬区在那边，面包房旁边。", "scene": "🏪 超市",
         "grammar": "主系表结构：is + 方位副词短语，表示位置",
         "sentence_words": [
             {"word": "section", "phonetic": "/ˈsekʃn/", "syllable": "sec·tion", "meaning": "n. 区域；部分"},
             {"word": "next to", "phonetic": "/nekst tuː/", "syllable": "next to", "meaning": "prep. 紧挨着；旁边"},
             {"word": "bakery", "phonetic": "/ˈbeɪkəri/", "syllable": "bak·er·y", "meaning": "n. 面包店；烘焙区"},
         ]},

        # ---- 医疗 ----
        {"word": "chemist", "phonetic": "/ˈkemɪst/", "syllable": "che · mist", "pos": "n.",
         "meaning": "药店",
         "example": "You can get that cream at any chemist.",
         "example_cn": "任何药店都能买到那个药膏。", "scene": "🏥 药店",
         "grammar": "情态动词 can + 动词原形，表示可能性；at any chemist（在任何药店）",
         "sentence_words": [
             {"word": "cream", "phonetic": "/kriːm/", "syllable": "cream", "meaning": "n. 药膏；乳霜"},
         ]},
        {"word": "prescription", "phonetic": "/prɪˈskrɪpʃn/", "syllable": "pre · scrip · tion", "pos": "n.",
         "meaning": "处方；药方",
         "example": "The doctor gave me a prescription for antibiotics.",
         "example_cn": "医生给我开了一剂抗生素处方。", "scene": "🏥 医院/药店",
         "grammar": "一般过去时：gave（give 的过去式）；give sb. sth. 双宾语结构",
         "sentence_words": [
             {"word": "doctor", "phonetic": "/ˈdɒktər/", "syllable": "doc·tor", "meaning": "n. 医生"},
             {"word": "antibiotics", "phonetic": "/ˌæntibaɪˈɒtɪks/", "syllable": "an·ti·bi·ot·ics", "meaning": "n. 抗生素（复数）"},
         ]},
        {"word": "GP", "phonetic": "/ˌdʒiː ˈpiː/", "syllable": "G · P", "pos": "n.",
         "meaning": "全科医生",
         "example": "You should go see a GP if it doesn't get better in a few days.",
         "example_cn": "如果过几天还不好，你应该去看全科医生。", "scene": "🏥 看病",
         "grammar": "should + 动词原形（建议）；if 条件句（如果...）",
         "sentence_words": [
             {"word": "get better", "phonetic": "/ɡet ˈbetər/", "syllable": "get bet·ter", "meaning": "v. 好转；康复（固定搭配）"},
             {"word": "in a few days", "phonetic": "/ɪn ə fjuː deɪz/", "syllable": "in a few days", "meaning": "phrase. 在几天内"},
         ]},
        {"word": "ACC", "phonetic": "/ˌeɪ siː ˈsiː/", "syllable": "A · C · C", "pos": "n.",
         "meaning": "事故赔偿公司（NZ特有）",
         "example": "If you get injured in NZ, ACC covers most of your medical costs.",
         "example_cn": "在新西兰受伤的话，ACC会覆盖大部分医疗费用。", "scene": "🏥 医疗保险",
         "grammar": "条件句：if + 一般现在时，主句用一般现在时（真实条件句）",
         "sentence_words": [
             {"word": "injured", "phonetic": "/ˈɪndʒəd/", "syllable": "in·jured", "meaning": "adj. 受伤的；v. 受伤（过去分词）"},
             {"word": "covers", "phonetic": "/ˈkʌvəz/", "syllable": "cov·ers", "meaning": "v. 覆盖；承担（第三人称单数）"},
             {"word": "medical costs", "phonetic": "/ˈmedɪkl kɒsts/", "syllable": "med·i·cal costs", "meaning": "n. 医疗费用"},
         ]},
        {"word": "appointment", "phonetic": "/əˈpɔɪntmənt/", "syllable": "ap · point · ment", "pos": "n.",
         "meaning": "预约",
         "example": "I've got a doctor's appointment at 2pm.",
         "example_cn": "我约了下午2点看医生。", "scene": "🏥 预约看病",
         "grammar": "现在完成时（口语）：I've got = I have got，表示当前拥有的安排",
         "sentence_words": [
             {"word": "doctor's", "phonetic": "/ˈdɒktəz/", "syllable": "doc·tor's", "meaning": "n. 医生的（所有格）"},
         ]},

        # ---- 交通 ----
        {"word": "bus lane", "phonetic": "/bʌs leɪn/", "syllable": "bus lane", "pos": "n.",
         "meaning": "公交专用道",
         "example": "Don't drive in the bus lane during rush hour.",
         "example_cn": "高峰时段不要开进公交专用道。", "scene": "🚌 交通出行",
         "grammar": "祈使句否定：Don't + 动词原形；during + 名词，表示在...期间",
         "sentence_words": [
             {"word": "drive", "phonetic": "/draɪv/", "syllable": "drive", "meaning": "v. 驾车；开车"},
             {"word": "rush hour", "phonetic": "/rʌʃ aʊər/", "syllable": "rush hour", "meaning": "n. 高峰时段；早晚高峰"},
         ]},
        {"word": "motorway", "phonetic": "/ˈməʊtəweɪ/", "syllable": "mo · tor · way", "pos": "n.",
         "meaning": "高速公路（NZ叫法）",
         "example": "Take the motorway south, it's faster than going through the city.",
         "example_cn": "走南边的高速吧，比穿城快。", "scene": "🚌 交通出行",
         "grammar": "祈使句：Take...；比较级：faster than（比...更快）",
         "sentence_words": [
             {"word": "south", "phonetic": "/saʊθ/", "syllable": "south", "meaning": "adv./n. 向南；南方"},
             {"word": "through", "phonetic": "/θruː/", "syllable": "through", "meaning": "prep. 穿过；经过"},
         ]},
        {"word": "roundabout", "phonetic": "/ˈraʊndəbaʊt/", "syllable": "round · a · bout", "pos": "n.",
         "meaning": "环岛；环形交叉路口",
         "example": "At the roundabout, take the second exit.",
         "example_cn": "在环岛走第二个出口。", "scene": "🚌 交通出行",
         "grammar": "祈使句：take the second exit（走第二个出口）；at + 名词，表示位置",
         "sentence_words": [
             {"word": "exit", "phonetic": "/ˈeksɪt/", "syllable": "ex·it", "meaning": "n. 出口；出路"},
             {"word": "second", "phonetic": "/ˈsekənd/", "syllable": "sec·ond", "meaning": "adj. 第二的（序数词）"},
         ]},
        {"word": "transfer", "phonetic": "/trænsˈfɜː/", "syllable": "trans · fer", "pos": "n./v.",
         "meaning": "换乘；转账",
         "example": "You need to transfer to Bus 70 at Britomart.",
         "example_cn": "你需要在Britomart换乘70路公交。", "scene": "🚌 换乘",
         "grammar": "need to + 动词原形：需要做某事；transfer to 换乘到（某路线）",
         "sentence_words": [
             {"word": "transfer to", "phonetic": "/trænsˈfɜː tuː/", "syllable": "trans·fer to", "meaning": "v. 换乘；转乘（固定搭配）"},
         ]},
        {"word": "AT HOP card", "phonetic": "/eɪ tiː hɒp kɑːd/", "syllable": "AT HOP card", "pos": "n.",
         "meaning": "奥克兰公交卡",
         "example": "Make sure you tag on and off with your AT HOP card.",
         "example_cn": "上下车记得刷AT HOP卡。", "scene": "🚌 公交通勤",
         "grammar": "祈使句：Make sure + 主从句；tag on and off（刷卡上下车）",
         "sentence_words": [
             {"word": "tag on", "phonetic": "/tæɡ ɒn/", "syllable": "tag on", "meaning": "v. 刷卡进站（NZ公交用语）"},
             {"word": "tag off", "phonetic": "/tæɡ ɒf/", "syllable": "tag off", "meaning": "v. 刷卡出站（NZ公交用语）"},
         ]},
        {"word": "carpark", "phonetic": "/ˈkɑːpɑːk/", "syllable": "car · park", "pos": "n.",
         "meaning": "停车场（NZ合写）",
         "example": "The carpark is full. Let's try the one around the corner.",
         "example_cn": "停车场满了。我们去拐角那个试试。", "scene": "🚌 停车",
         "grammar": "主系表：is full；Let's...（建议句型）；around the corner（拐角处）",
         "sentence_words": [
             {"word": "full", "phonetic": "/fʊl/", "syllable": "full", "meaning": "adj. 满的；满员"},
             {"word": "around the corner", "phonetic": "/əˈraʊnd ðə ˈkɔːnər/", "syllable": "a·round the cor·ner", "meaning": "phrase. 在拐角处；即将到来"},
         ]},

        # ---- NZ口语/俚语 ----
        {"word": "kiwi", "phonetic": "/ˈkiːwiː/", "syllable": "ki · wi", "pos": "n.",
         "meaning": "新西兰人（亲切自称）",
         "example": "Most kiwis love a good barbecue on the weekend.",
         "example_cn": "大多数新西兰人周末喜欢好好搞个烧烤。", "scene": "🗣️ NZ日常口语",
         "grammar": "一般现在时（习惯）：love + 动名词，表示经常性喜好",
         "sentence_words": [
             {"word": "barbecue", "phonetic": "/ˈbɑːbɪkjuː/", "syllable": "bar·be·cue", "meaning": "n. 烧烤（也缩写为 barbie）"},
             {"word": "weekend", "phonetic": "/ˌwiːkˈend/", "syllable": "week·end", "meaning": "n. 周末"},
         ]},
        {"word": "heaps", "phonetic": "/hiːps/", "syllable": "heaps", "pos": "adv./n.",
         "meaning": "很多；大量（口语）",
         "example": "There were heaps of people at the market today.",
         "example_cn": "今天集市上人超多。", "scene": "🗣️ NZ口语",
         "grammar": "There be 句型（过去时）：There were...，表示存在；heaps of = lots of",
         "sentence_words": [
             {"word": "market", "phonetic": "/ˈmɑːkɪt/", "syllable": "mar·ket", "meaning": "n. 集市；市场"},
             {"word": "heaps of", "phonetic": "/hiːps ɒv/", "syllable": "heaps of", "meaning": "phrase. 大量的（NZ口语）"},
         ]},
        {"word": "sweet as", "phonetic": "/swiːt æz/", "syllable": "sweet as", "pos": "phrase",
         "meaning": "太好了；没问题（NZ经典口语）",
         "example": "Can you pick me up at 5? — Sweet as, no worries.",
         "example_cn": "5点能来接我吗？——没问题，放心。", "scene": "🗣️ NZ口语",
         "grammar": "对话回应句：Sweet as 作感叹语；no worries（没关系）是NZ万能回应",
         "sentence_words": [
             {"word": "pick up", "phonetic": "/pɪk ʌp/", "syllable": "pick up", "meaning": "v. 开车来接（短语动词）"},
             {"word": "no worries", "phonetic": "/nəʊ ˈwʌriz/", "syllable": "no wor·ries", "meaning": "phrase. 没问题；不客气（NZ口语）"},
         ]},
        {"word": "no worries", "phonetic": "/nəʊ ˈwʌriz/", "syllable": "no wor · ries", "pos": "phrase",
         "meaning": "没事；不客气（NZ万能回应）",
         "example": "Thanks for the lift! — No worries, mate.",
         "example_cn": "谢谢捎我！——没事儿，哥们。", "scene": "🗣️ NZ口语",
         "grammar": "感谢与回应的对话句型；mate（哥们）是NZ/英国口语称呼",
         "sentence_words": [
             {"word": "lift", "phonetic": "/lɪft/", "syllable": "lift", "meaning": "n. 搭车；顺风车（英/NZ用法）"},
             {"word": "mate", "phonetic": "/meɪt/", "syllable": "mate", "meaning": "n. 哥们；朋友（NZ/英口语）"},
         ]},
        {"word": "ta", "phonetic": "/tɑː/", "syllable": "ta", "pos": "int.",
         "meaning": "谢谢（极口语，NZ/英）",
         "example": "Here's your coffee. — Ta!",
         "example_cn": "你的咖啡。——谢啦！", "scene": "🗣️ NZ口语",
         "grammar": "感叹语（单词句）：Ta = Thank you 的极简口语形式",
         "sentence_words": [
             {"word": "here's", "phonetic": "/hɪəz/", "syllable": "here's", "meaning": "这是...（Here is 的缩写）"},
         ]},
        {"word": "arvo", "phonetic": "/ɑːˈvəʊ/", "syllable": "ar · vo", "pos": "n.",
         "meaning": "下午（afternoon缩写）",
         "example": "Want to grab a coffee this arvo?",
         "example_cn": "今天下午想喝杯咖啡吗？", "scene": "🗣️ NZ口语",
         "grammar": "简短邀请句型：Want to do...?（想做...吗？）省略了主语 Do you",
         "sentence_words": [
             {"word": "grab a coffee", "phonetic": "/ɡræb ə ˈkɒfi/", "syllable": "grab a cof·fee", "meaning": "v. 去喝杯咖啡（口语）"},
         ]},
        {"word": "cheers", "phonetic": "/tʃɪəz/", "syllable": "cheers", "pos": "int.",
         "meaning": "谢谢；再见；干杯",
         "example": "Cheers for helping me move the sofa!",
         "example_cn": "谢谢你帮我搬沙发！", "scene": "🗣️ NZ口语",
         "grammar": "Cheers for + 动名词：感谢某人做了某事",
         "sentence_words": [
             {"word": "helping", "phonetic": "/ˈhelpɪŋ/", "syllable": "help·ing", "meaning": "v. 帮助（现在分词/动名词）"},
             {"word": "sofa", "phonetic": "/ˈsəʊfə/", "syllable": "so·fa", "meaning": "n. 沙发"},
             {"word": "move", "phonetic": "/muːv/", "syllable": "move", "meaning": "v. 移动；搬动"},
         ]},
        {"word": "mate", "phonetic": "/meɪt/", "syllable": "mate", "pos": "n.",
         "meaning": "哥们；朋友",
         "example": "Hey mate, how's it going?",
         "example_cn": "嘿哥们，最近怎么样？", "scene": "🗣️ NZ口语",
         "grammar": "问候句型：How's it going? = How are you?（最近怎样？）口语化问候",
         "sentence_words": [
             {"word": "how's it going", "phonetic": "/haʊz ɪt ˈɡəʊɪŋ/", "syllable": "how's it go·ing", "meaning": "phrase. 最近怎样？（口语问候）"},
         ]},
        {"word": "brekkie", "phonetic": "/ˈbreki/", "syllable": "brek · kie", "pos": "n.",
         "meaning": "早餐（breakfast缩写）",
         "example": "What do you want for brekkie? I'm making eggs.",
         "example_cn": "早餐想吃什么？我在煎鸡蛋。", "scene": "🗣️ NZ口语",
         "grammar": "疑问句：What do you want for...?；现在进行时：I'm making（正在做）",
         "sentence_words": [
             {"word": "making", "phonetic": "/ˈmeɪkɪŋ/", "syllable": "mak·ing", "meaning": "v. 制作；烹饪（现在分词）"},
             {"word": "eggs", "phonetic": "/eɡz/", "syllable": "eggs", "meaning": "n. 鸡蛋（复数）"},
         ]},
        {"word": "reckon", "phonetic": "/ˈrekən/", "syllable": "reck · on", "pos": "v.",
         "meaning": "觉得；认为（口语）",
         "example": "I reckon it'll rain this afternoon.",
         "example_cn": "我觉得今天下午会下雨。", "scene": "🗣️ NZ口语",
         "grammar": "I reckon + 宾语从句（口语化的 I think）；it'll = it will，将来时预测",
         "sentence_words": [
             {"word": "it'll", "phonetic": "/ɪtl/", "syllable": "it'll", "meaning": "it will 的缩写，将来时"},
             {"word": "rain", "phonetic": "/reɪn/", "syllable": "rain", "meaning": "v. 下雨；n. 雨"},
         ]},
        {"word": "beaut", "phonetic": "/bjuːt/", "syllable": "beaut", "pos": "n./adj.",
         "meaning": "好东西；太棒了",
         "example": "She's a beaut, your new car!",
         "example_cn": "你的新车真漂亮！", "scene": "🗣️ NZ口语",
         "grammar": "感叹句：She's a beaut（NZ口语，用she指代物品）；your new car 是补充说明",
         "sentence_words": [
             {"word": "new car", "phonetic": "/njuː kɑː/", "syllable": "new car", "meaning": "n. 新车"},
         ]},
        {"word": "stoked", "phonetic": "/stəʊkt/", "syllable": "stoked", "pos": "adj.",
         "meaning": "超兴奋；超开心",
         "example": "I'm stoked about the concert next week!",
         "example_cn": "我对下周的音乐会超期待！", "scene": "🗣️ NZ口语",
         "grammar": "be + 形容词：I'm stoked about，about 表示对...感到兴奋",
         "sentence_words": [
             {"word": "concert", "phonetic": "/ˈkɒnsət/", "syllable": "con·cert", "meaning": "n. 音乐会；演唱会"},
             {"word": "next week", "phonetic": "/nekst wiːk/", "syllable": "next week", "meaning": "n. 下周"},
         ]},

        # ---- 日常生活 ----
        {"word": "bin", "phonetic": "/bɪn/", "syllable": "bin", "pos": "n.",
         "meaning": "垃圾桶",
         "example": "Can you take the bins out tonight?",
         "example_cn": "你今晚能把垃圾倒了吗？", "scene": "🏠 日常生活",
         "grammar": "Can you...? 表示请求；take out 是短语动词，表示把...拿出去",
         "sentence_words": [
             {"word": "take out", "phonetic": "/teɪk aʊt/", "syllable": "take out", "meaning": "v. 拿出去；取出（短语动词）"},
             {"word": "tonight", "phonetic": "/təˈnaɪt/", "syllable": "to·night", "meaning": "adv. 今晚"},
         ]},
        {"word": "rubbish", "phonetic": "/ˈrʌbɪʃ/", "syllable": "rub · bish", "pos": "n.",
         "meaning": "垃圾",
         "example": "Rubbish day is Tuesday. Don't forget to put the bin out.",
         "example_cn": "垃圾日是周二。别忘了把垃圾桶推出去。", "scene": "🏠 日常生活",
         "grammar": "主系表结构 + 祈使句否定：Don't forget to do sth.（别忘了做某事）",
         "sentence_words": [
             {"word": "Tuesday", "phonetic": "/ˈtjuːzdeɪ/", "syllable": "Tues·day", "meaning": "n. 周二"},
             {"word": "put out", "phonetic": "/pʊt aʊt/", "syllable": "put out", "meaning": "v. 推出去；放到外面（短语动词）"},
         ]},
        {"word": "hire", "phonetic": "/ˈhaɪə/", "syllable": "hire", "pos": "v.",
         "meaning": "租用（租车、工具等）",
         "example": "We hired a car for the weekend trip to Rotorua.",
         "example_cn": "我们租了辆车周末去Rotorua玩。", "scene": "🚗 租车",
         "grammar": "一般过去时：hired（hire 的过去式），表示已完成的动作",
         "sentence_words": [
             {"word": "hired", "phonetic": "/ˈhaɪəd/", "syllable": "hired", "meaning": "v. 租用（过去式）"},
             {"word": "weekend trip", "phonetic": "/ˈwiːkend trɪp/", "syllable": "week·end trip", "meaning": "n. 周末旅行"},
         ]},
        {"word": "rate", "phonetic": "/reɪt/", "syllable": "rate", "pos": "n.",
         "meaning": "费率；税率（NZ有GST）",
         "example": "The GST rate in New Zealand is 15 percent.",
         "example_cn": "新西兰的消费税率是15%。", "scene": "🏦 税务/银行",
         "grammar": "主系表结构：The rate is + 数字，表示数值",
         "sentence_words": [
             {"word": "GST", "phonetic": "/ˌdʒiːesˈtiː/", "syllable": "G·S·T", "meaning": "n. 商品服务税（新西兰消费税）"},
             {"word": "percent", "phonetic": "/pəˈsent/", "syllable": "per·cent", "meaning": "n. 百分之..."},
         ]},
        {"word": "power", "phonetic": "/ˈpaʊə/", "syllable": "pow · er", "pos": "n.",
         "meaning": "电；电力",
         "example": "The power bill this month is way higher than last month.",
         "example_cn": "这个月的电费比上个月高多了。", "scene": "🏠 生活缴费",
         "grammar": "比较级：higher than...（比...高）；way 加强比较级语气",
         "sentence_words": [
             {"word": "power bill", "phonetic": "/ˈpaʊər bɪl/", "syllable": "pow·er bill", "meaning": "n. 电费账单"},
             {"word": "way higher", "phonetic": "/weɪ ˈhaɪər/", "syllable": "way high·er", "meaning": "phrase. 高多了（way 加强比较级）"},
         ]},
        {"word": "bach", "phonetic": "/bætʃ/", "syllable": "bach", "pos": "n.",
         "meaning": "度假小屋（NZ经典）",
         "example": "We're heading to our bach in Coromandel for the long weekend.",
         "example_cn": "长周末我们去Coromandel的度假屋。", "scene": "🏖️ 度假生活",
         "grammar": "现在进行时：We're heading to，表示即将出发的计划",
         "sentence_words": [
             {"word": "heading to", "phonetic": "/ˈhedɪŋ tuː/", "syllable": "head·ing to", "meaning": "v. 前往；出发去（口语）"},
             {"word": "long weekend", "phonetic": "/lɒŋ ˈwiːkend/", "syllable": "long week·end", "meaning": "n. 长周末（含公假）"},
         ]},
        {"word": "barbie", "phonetic": "/ˈbɑːbi/", "syllable": "bar · bie", "pos": "n.",
         "meaning": "烧烤（barbecue缩写）",
         "example": "Throw some sausages on the barbie, mate!",
         "example_cn": "放几根香肠上烤架，哥们！", "scene": "🍽️ 日常社交",
         "grammar": "祈使句：Throw...on...（把...放到...上）；mate 作感叹语",
         "sentence_words": [
             {"word": "throw", "phonetic": "/θrəʊ/", "syllable": "throw", "meaning": "v. 扔；放上去（口语）"},
             {"word": "sausages", "phonetic": "/ˈsɒsɪdʒɪz/", "syllable": "sau·sag·es", "meaning": "n. 香肠（复数）"},
         ]},
        {"word": "jandal", "phonetic": "/ˈdʒændl/", "syllable": "jan · dal", "pos": "n.",
         "meaning": "人字拖（NZ叫法）",
         "example": "I pretty much live in my jandals in summer.",
         "example_cn": "夏天我基本就穿人字拖。", "scene": "👟 日常穿着",
         "grammar": "一般现在时：I live in...（穿...度日）；pretty much = basically，表示几乎",
         "sentence_words": [
             {"word": "pretty much", "phonetic": "/ˈprɪti mʌtʃ/", "syllable": "pret·ty much", "meaning": "adv. 基本上；差不多"},
             {"word": "live in", "phonetic": "/lɪv ɪn/", "syllable": "live in", "meaning": "v. 穿着...度日（口语）"},
         ]},
        {"word": "tramping", "phonetic": "/ˈtræmpɪŋ/", "syllable": "tramp · ing", "pos": "n.",
         "meaning": "徒步旅行（NZ叫法）",
         "example": "We went tramping in the Tongariro Alpine Crossing last weekend.",
         "example_cn": "我们上周末去走了汤加里罗越山步道。", "scene": "🏔️ 户外活动",
         "grammar": "一般过去时：went（go 的过去式）；go + 动名词表示活动",
         "sentence_words": [
             {"word": "went", "phonetic": "/went/", "syllable": "went", "meaning": "v. 去（go 的过去式）"},
             {"word": "last weekend", "phonetic": "/lɑːst ˈwiːkend/", "syllable": "last week·end", "meaning": "n. 上个周末"},
         ]},
        {"word": "plug", "phonetic": "/plʌɡ/", "syllable": "plug", "pos": "n./v.",
         "meaning": "插头；插上",
         "example": "Do I need an adapter for NZ power plugs?",
         "example_cn": "新西兰的插头需要转接器吗？", "scene": "🔌 日常生活",
         "grammar": "一般现在时疑问句：Do I need...?，询问是否有需要",
         "sentence_words": [
             {"word": "adapter", "phonetic": "/əˈdæptər/", "syllable": "a·dap·ter", "meaning": "n. 适配器；转接器"},
             {"word": "power plugs", "phonetic": "/ˈpaʊər plʌɡz/", "syllable": "pow·er plugs", "meaning": "n. 电源插头（复数）"},
         ]},
        {"word": "radiator", "phonetic": "/ˈreɪdieɪtə/", "syllable": "ra · di · a · tor", "pos": "n.",
         "meaning": "暖气片",
         "example": "NZ houses can get really cold. You'll need a good radiator.",
         "example_cn": "新西兰的房子会很冷。你需要一个靠谱的暖气片。", "scene": "🏠 日常生活",
         "grammar": "情态动词 can：can get cold（会变冷）；will need（将会需要）",
         "sentence_words": [
             {"word": "get cold", "phonetic": "/ɡet kəʊld/", "syllable": "get cold", "meaning": "v. 变冷（get + 形容词，表状态变化）"},
             {"word": "really", "phonetic": "/ˈrɪəli/", "syllable": "re·al·ly", "meaning": "adv. 真的；非常"},
         ]},

        # ---- 学校/工作 ----
        {"word": "polytechnic", "phonetic": "/ˌpɒliˈteknɪk/", "syllable": "pol · y · tech · nic", "pos": "n.",
         "meaning": "理工学院",
         "example": "She's studying nursing at a polytechnic in Wellington.",
         "example_cn": "她在惠灵顿的一所理工学院学护理。", "scene": "🎓 学校教育",
         "grammar": "现在进行时：She's studying，表示正在进行的学习活动",
         "sentence_words": [
             {"word": "studying", "phonetic": "/ˈstʌdiɪŋ/", "syllable": "stud·y·ing", "meaning": "v. 学习（现在分词）"},
             {"word": "nursing", "phonetic": "/ˈnɜːsɪŋ/", "syllable": "nurs·ing", "meaning": "n. 护理学"},
         ]},
        {"word": "NCEA", "phonetic": "/ˈensiːeɪ/", "syllable": "N · C · E · A", "pos": "n.",
         "meaning": "新西兰国家教育证书",
         "example": "Most high school students in NZ work towards NCEA levels.",
         "example_cn": "新西兰大多数高中生都在读NCEA等级。", "scene": "🎓 学校教育",
         "grammar": "一般现在时：work towards（努力争取）+ 目标",
         "sentence_words": [
             {"word": "work towards", "phonetic": "/wɜːk təˈwɔːdz/", "syllable": "work to·wards", "meaning": "v. 努力争取；朝...努力"},
             {"word": "levels", "phonetic": "/ˈlevlz/", "syllable": "lev·els", "meaning": "n. 级别；等级（复数）"},
         ]},
        {"word": "deadline", "phonetic": "/ˈdedlaɪn/", "syllable": "dead · line", "pos": "n.",
         "meaning": "截止日期",
         "example": "The assignment deadline is next Friday.",
         "example_cn": "作业截止日期是下周五。", "scene": "🎓 学校/工作",
         "grammar": "主系表结构：The deadline is + 时间，表示截止时间",
         "sentence_words": [
             {"word": "assignment", "phonetic": "/əˈsaɪnmənt/", "syllable": "as·sign·ment", "meaning": "n. 作业；任务"},
             {"word": "next Friday", "phonetic": "/nekst ˈfraɪdeɪ/", "syllable": "next Fri·day", "meaning": "n. 下周五"},
         ]},
        {"word": "roster", "phonetic": "/ˈrɒstə/", "syllable": "ros · ter", "pos": "n.",
         "meaning": "排班表",
         "example": "Can you check the roster and tell me when I'm working next?",
         "example_cn": "能帮我看一下排班表吗？告诉我下次什么时候上班。", "scene": "💼 工作沟通",
         "grammar": "Can you...? 请求句；and 连接两个祈使动词：check...and tell...",
         "sentence_words": [
             {"word": "check", "phonetic": "/tʃek/", "syllable": "check", "meaning": "v. 查看；检查"},
             {"word": "working", "phonetic": "/ˈwɜːkɪŋ/", "syllable": "work·ing", "meaning": "v. 工作（现在分词）"},
         ]},
        {"word": "reference", "phonetic": "/ˈrefrəns/", "syllable": "ref · er · ence", "pos": "n.",
         "meaning": "推荐信；推荐人",
         "example": "Most employers here want at least two references.",
         "example_cn": "这里大多数雇主都要求至少两个推荐人。", "scene": "💼 求职",
         "grammar": "一般现在时（习惯）：want + 数量 + 名词；at least（至少）",
         "sentence_words": [
             {"word": "employers", "phonetic": "/ɪmˈplɔɪəz/", "syllable": "em·ploy·ers", "meaning": "n. 雇主（复数）"},
             {"word": "at least", "phonetic": "/æt liːst/", "syllable": "at least", "meaning": "adv. 至少"},
         ]},

        # ---- 银行/政府 ----
        {"word": "ASB", "phonetic": "/ˌeɪ es ˈbiː/", "syllable": "A · S · B", "pos": "n.",
         "meaning": "ASB银行（NZ四大银行之一）",
         "example": "I bank with ASB. Their app is pretty good.",
         "example_cn": "我在ASB银行开户。他们的App挺好用。", "scene": "🏦 银行开户",
         "grammar": "一般现在时（状态）：bank with（在...银行有账户）；is pretty good（很不错）",
         "sentence_words": [
             {"word": "bank with", "phonetic": "/bæŋk wɪð/", "syllable": "bank with", "meaning": "v. 在...银行有账户（固定搭配）"},
             {"word": "pretty good", "phonetic": "/ˈprɪti ɡʊd/", "syllable": "pret·ty good", "meaning": "adj. 相当不错（口语）"},
         ]},
        {"word": "IRD number", "phonetic": "/aɪ ɑː diː ˈnʌmbə/", "syllable": "IRD num · ber", "pos": "n.",
         "meaning": "税务局编号（NZ必备）",
         "example": "You need an IRD number to start working in New Zealand.",
         "example_cn": "在新西兰开始工作需要先申请IRD税号。", "scene": "🏦 政府/税务",
         "grammar": "need + 名词 + 不定式：need sth. to do，表示为了做某事需要某物",
         "sentence_words": [
             {"word": "start working", "phonetic": "/stɑːt ˈwɜːkɪŋ/", "syllable": "start work·ing", "meaning": "v. 开始工作（start + 动名词）"},
         ]},
        {"word": "WINZ", "phonetic": "/wɪnz/", "syllable": "WINZ", "pos": "n.",
         "meaning": "工作收入局（社会福利）",
         "example": "If you lose your job, you might be able to get help from WINZ.",
         "example_cn": "如果失业了，你可以找WINZ寻求帮助。", "scene": "🏦 政府服务",
         "grammar": "if 条件句 + might（可能）：might be able to（可能有能力）",
         "sentence_words": [
             {"word": "lose your job", "phonetic": "/luːz jɔː dʒɒb/", "syllable": "lose your job", "meaning": "v. 失业（固定搭配）"},
             {"word": "might be able to", "phonetic": "/maɪt biː ˈeɪbl tuː/", "syllable": "might be a·ble to", "meaning": "v. 可能能够（情态动词+be able to）"},
         ]},
    ],
    "ielts": [
        {"word": "eligible", "phonetic": "/ˈelɪdʒəbl/", "syllable": "el · i · gi · ble", "pos": "adj.",
         "meaning": "符合条件的；有资格的",
         "example": "You may be eligible for a work visa if you have a job offer.",
         "example_cn": "如果你有工作邀请，可能有资格申请工作签证。", "scene": "📋 签证申请",
         "grammar": "情态动词 may + 形容词：may be eligible for（可能有资格）；if 条件句",
         "sentence_words": [
             {"word": "work visa", "phonetic": "/wɜːk ˈviːzə/", "syllable": "work vi·sa", "meaning": "n. 工作签证"},
             {"word": "job offer", "phonetic": "/dʒɒb ˈɒfər/", "syllable": "job of·fer", "meaning": "n. 工作邀请；录用通知"},
         ]},
        {"word": "infrastructure", "phonetic": "/ˈɪnfrəstrʌktʃə/", "syllable": "in · fra · struc · ture", "pos": "n.",
         "meaning": "基础设施",
         "example": "Auckland is investing in public transport infrastructure.",
         "example_cn": "奥克兰正在大力投资公共交通基础设施。", "scene": "📝 雅思写作",
         "grammar": "现在进行时：is investing in（正在投资），表示持续进行的动作",
         "sentence_words": [
             {"word": "investing", "phonetic": "/ɪnˈvestɪŋ/", "syllable": "in·vest·ing", "meaning": "v. 投资（现在分词）"},
             {"word": "public transport", "phonetic": "/ˈpʌblɪk ˈtrænspɔːt/", "syllable": "pub·lic trans·port", "meaning": "n. 公共交通"},
         ]},
        {"word": "sustainability", "phonetic": "/səˌsteɪnəˈbɪləti/", "syllable": "sus · tain · a · bil · i · ty", "pos": "n.",
         "meaning": "可持续性",
         "example": "NZ has strong policies focused on sustainability.",
         "example_cn": "新西兰有以可持续发展为重点的政策。", "scene": "📝 雅思写作",
         "grammar": "一般现在时：has（拥有）+ 名词，表示当前的政策状态",
         "sentence_words": [
             {"word": "policies", "phonetic": "/ˈpɒlɪsiz/", "syllable": "pol·i·cies", "meaning": "n. 政策（复数）"},
             {"word": "focused on", "phonetic": "/ˈfəʊkəst ɒn/", "syllable": "fo·cused on", "meaning": "adj. 专注于；以...为重点（过去分词作后置定语）"},
         ]},
        {"word": "acknowledge", "phonetic": "/əkˈnɒlɪdʒ/", "syllable": "ac · knowl · edge", "pos": "v.",
         "meaning": "承认；致谢",
         "example": "It's important to acknowledge different cultural perspectives.",
         "example_cn": "承认不同的文化视角很重要。", "scene": "🎓 雅思口语/写作",
         "grammar": "It's + 形容词 + to do sth.：It's important to...（形式主语句型）",
         "sentence_words": [
             {"word": "cultural", "phonetic": "/ˈkʌltʃərəl/", "syllable": "cul·tur·al", "meaning": "adj. 文化的；文化上的"},
             {"word": "perspectives", "phonetic": "/pəˈspektɪvz/", "syllable": "per·spec·tives", "meaning": "n. 观点；视角（复数）"},
         ]},
        {"word": "migrate", "phonetic": "/maɪˈɡreɪt/", "syllable": "mi · grate", "pos": "v.",
         "meaning": "移民；迁徙",
         "example": "Many families migrate to NZ for better education.",
         "example_cn": "许多家庭为了更好的教育移民新西兰。", "scene": "📋 移民",
         "grammar": "一般现在时（习惯/普遍规律）：migrate to...for...，表示目的",
         "sentence_words": [
             {"word": "families", "phonetic": "/ˈfæmɪliz/", "syllable": "fam·i·lies", "meaning": "n. 家庭（复数）"},
             {"word": "better education", "phonetic": "/ˈbetər ˌedʒuˈkeɪʃn/", "syllable": "bet·ter ed·u·ca·tion", "meaning": "n. 更好的教育（比较级+名词）"},
         ]},
        {"word": "adapt", "phonetic": "/əˈdæpt/", "syllable": "a · dapt", "pos": "v.",
         "meaning": "适应；调整",
         "example": "It took me a few months to adapt to the NZ way of life.",
         "example_cn": "我花了几个月才适应新西兰的生活方式。", "scene": "📋 生活适应",
         "grammar": "It took + 时间 + to do：花了...时间做某事（固定句型）",
         "sentence_words": [
             {"word": "took", "phonetic": "/tʊk/", "syllable": "took", "meaning": "v. 花（take 的过去式）"},
             {"word": "way of life", "phonetic": "/weɪ əv laɪf/", "syllable": "way of life", "meaning": "n. 生活方式（固定搭配）"},
         ]},
        {"word": "resident", "phonetic": "/ˈrezɪdənt/", "syllable": "res · i · dent", "pos": "n./adj.",
         "meaning": "居民；居住的",
         "example": "Permanent residents have the right to vote in local elections.",
         "example_cn": "永久居民有权在地方选举中投票。", "scene": "📋 签证/移民",
         "grammar": "一般现在时（事实/权利）：have the right to do（有权做某事）",
         "sentence_words": [
             {"word": "permanent", "phonetic": "/ˈpɜːmənənt/", "syllable": "per·ma·nent", "meaning": "adj. 永久的；长期的"},
             {"word": "vote", "phonetic": "/vəʊt/", "syllable": "vote", "meaning": "v. 投票；参选"},
             {"word": "local elections", "phonetic": "/ˈləʊkl ɪˈlekʃnz/", "syllable": "lo·cal e·lec·tions", "meaning": "n. 地方选举"},
         ]},
        {"word": "income", "phonetic": "/ˈɪnkʌm/", "syllable": "in · come", "pos": "n.",
         "meaning": "收入",
         "example": "You need to declare all your income when filing your tax return.",
         "example_cn": "报税时需要申报所有收入。", "scene": "📋 税务/签证",
         "grammar": "need to + 动词原形；when + 动名词（filing），表示时间",
         "sentence_words": [
             {"word": "declare", "phonetic": "/dɪˈkleər/", "syllable": "de·clare", "meaning": "v. 申报；声明"},
             {"word": "filing", "phonetic": "/ˈfaɪlɪŋ/", "syllable": "fil·ing", "meaning": "v. 提交；申报（动名词）"},
             {"word": "tax return", "phonetic": "/tæks rɪˈtɜːn/", "syllable": "tax re·turn", "meaning": "n. 报税表；税务申报"},
         ]},
        {"word": "opportunity", "phonetic": "/ˌɒpəˈtjuːnəti/", "syllable": "op · por · tu · ni · ty", "pos": "n.",
         "meaning": "机会",
         "example": "Studying abroad gives you great opportunities.",
         "example_cn": "出国留学给你很好的机会。", "scene": "🎓 留学申请",
         "grammar": "动名词作主语：Studying abroad（出国留学）+ 谓语 gives",
         "sentence_words": [
             {"word": "studying abroad", "phonetic": "/ˈstʌdiɪŋ əˈbrɔːd/", "syllable": "stud·y·ing a·broad", "meaning": "v. 出国留学（动名词短语）"},
             {"word": "great", "phonetic": "/ɡreɪt/", "syllable": "great", "meaning": "adj. 很好的；巨大的"},
         ]},
        {"word": "previous", "phonetic": "/ˈpriːviəs/", "syllable": "pre · vi · ous", "pos": "adj.",
         "meaning": "以前的；先前的",
         "example": "What was your previous address?",
         "example_cn": "你以前的地址是什么？", "scene": "📋 表格填写",
         "grammar": "一般过去时疑问句：What was...? 询问过去的信息",
         "sentence_words": [
             {"word": "address", "phonetic": "/əˈdres/", "syllable": "ad·dress", "meaning": "n. 地址"},
         ]},
        {"word": "accommodation", "phonetic": "/əˌkɒməˈdeɪʃn/", "syllable": "ac · com · mo · da · tion", "pos": "n.",
         "meaning": "住宿；住处",
         "example": "Finding affordable accommodation in Auckland is quite hard.",
         "example_cn": "在奥克兰找到便宜的住处挺难的。", "scene": "🏠 租房/雅思",
         "grammar": "动名词作主语：Finding...（找...）是主语；quite hard（相当难）作表语",
         "sentence_words": [
             {"word": "affordable", "phonetic": "/əˈfɔːdəbl/", "syllable": "af·ford·a·ble", "meaning": "adj. 负担得起的；价格合理的"},
             {"word": "quite", "phonetic": "/kwaɪt/", "syllable": "quite", "meaning": "adv. 相当；非常"},
         ]},
        {"word": "settle", "phonetic": "/ˈsetl/", "syllable": "set · tle", "pos": "v.",
         "meaning": "安顿；定居",
         "example": "It takes time to settle into a new country.",
         "example_cn": "在一个新国家安顿下来需要时间。", "scene": "📋 移民生活",
         "grammar": "It takes + 名词 + to do：需要...来做某事（形式主语句型）",
         "sentence_words": [
             {"word": "takes time", "phonetic": "/teɪks taɪm/", "syllable": "takes time", "meaning": "v. 需要时间（固定搭配）"},
             {"word": "settle into", "phonetic": "/ˈsetl ˈɪntuː/", "syllable": "set·tle in·to", "meaning": "v. 融入；安顿下来（短语动词）"},
         ]},
        {"word": "certificate", "phonetic": "/səˈtɪfɪkət/", "syllable": "cer · ti · fi · cate", "pos": "n.",
         "meaning": "证书；证明",
         "example": "You need a police certificate for your visa application.",
         "example_cn": "签证申请需要无犯罪证明。", "scene": "📋 签证材料",
         "grammar": "need + 名词（宾语）+ for + 名词：需要某物用于某事",
         "sentence_words": [
             {"word": "police certificate", "phonetic": "/pəˈliːs səˈtɪfɪkət/", "syllable": "po·lice cer·tif·i·cate", "meaning": "n. 无犯罪记录证明"},
             {"word": "visa application", "phonetic": "/ˈviːzə ˌæplɪˈkeɪʃn/", "syllable": "vi·sa ap·pli·ca·tion", "meaning": "n. 签证申请"},
         ]},
        {"word": "fluent", "phonetic": "/ˈfluːənt/", "syllable": "flu · ent", "pos": "adj.",
         "meaning": "流利的",
         "example": "She's fluent in both English and Mandarin.",
         "example_cn": "她的英语和普通话都很流利。", "scene": "🎓 雅思口语",
         "grammar": "be + 形容词：is fluent in（在...方面很流利）；both...and...（两者都）",
         "sentence_words": [
             {"word": "fluent in", "phonetic": "/ˈfluːənt ɪn/", "syllable": "flu·ent in", "meaning": "adj. 精通；流利（固定搭配）"},
             {"word": "Mandarin", "phonetic": "/ˈmændərɪn/", "syllable": "Man·da·rin", "meaning": "n. 普通话；官话"},
         ]},
        {"word": "diverse", "phonetic": "/daɪˈvɜːs/", "syllable": "di · verse", "pos": "adj.",
         "meaning": "多元的；多样化的",
         "example": "NZ is a diverse society with people from many cultures.",
         "example_cn": "新西兰是一个多元文化的社会。", "scene": "📝 雅思写作",
         "grammar": "主系表结构：is a + 形容词 + 名词；with + 名词短语作后置定语",
         "sentence_words": [
             {"word": "society", "phonetic": "/səˈsaɪəti/", "syllable": "so·ci·e·ty", "meaning": "n. 社会"},
             {"word": "cultures", "phonetic": "/ˈkʌltʃəz/", "syllable": "cul·tures", "meaning": "n. 文化（复数）"},
         ]},
        {"word": "contribute", "phonetic": "/kənˈtrɪbjuːt/", "syllable": "con · trib · ute", "pos": "v.",
         "meaning": "贡献；捐助",
         "example": "Volunteering is a great way to contribute to the community.",
         "example_cn": "做志愿者是回馈社区的好方式。", "scene": "📝 雅思写作",
         "grammar": "动名词作主语：Volunteering is a way to...（...是...的方式）",
         "sentence_words": [
             {"word": "volunteering", "phonetic": "/ˌvɒlənˈtɪərɪŋ/", "syllable": "vol·un·teer·ing", "meaning": "v. 做志愿者（动名词）"},
             {"word": "community", "phonetic": "/kəˈmjuːnəti/", "syllable": "com·mu·ni·ty", "meaning": "n. 社区；团体"},
         ]},
        {"word": "require", "phonetic": "/rɪˈkwaɪə/", "syllable": "re · quire", "pos": "v.",
         "meaning": "需要；要求",
         "example": "The visa application requires several supporting documents.",
         "example_cn": "签证申请需要几份支持材料。", "scene": "📋 签证申请",
         "grammar": "一般现在时：requires（第三人称单数）+ 宾语；several（几个）",
         "sentence_words": [
             {"word": "supporting documents", "phonetic": "/səˈpɔːtɪŋ ˈdɒkjuménts/", "syllable": "sup·port·ing doc·u·ments", "meaning": "n. 支持性文件；证明材料"},
             {"word": "several", "phonetic": "/ˈsevrəl/", "syllable": "sev·er·al", "meaning": "adj. 几个；若干"},
         ]},
        {"word": "temporary", "phonetic": "/ˈtemprəri/", "syllable": "tem · po · ra · ry", "pos": "adj.",
         "meaning": "临时的；暂时的",
         "example": "I'm on a temporary work visa right now.",
         "example_cn": "我现在持临时工作签证。", "scene": "📋 签证",
         "grammar": "be on + 名词：be on a visa（持有签证）；right now（现在）",
         "sentence_words": [
             {"word": "on a visa", "phonetic": "/ɒn ə ˈviːzə/", "syllable": "on a vi·sa", "meaning": "phrase. 持有签证（固定搭配）"},
             {"word": "right now", "phonetic": "/raɪt naʊ/", "syllable": "right now", "meaning": "adv. 现在；此刻（口语）"},
         ]},
        {"word": "minimum", "phonetic": "/ˈmɪnɪməm/", "syllable": "min · i · mum", "pos": "n./adj.",
         "meaning": "最低限度；最低的",
         "example": "The minimum wage in NZ is reviewed every year.",
         "example_cn": "新西兰的最低工资每年都会审核。", "scene": "💼 工作/生活",
         "grammar": "被动语态：is reviewed（被审核）；every year（每年）",
         "sentence_words": [
             {"word": "wage", "phonetic": "/weɪdʒ/", "syllable": "wage", "meaning": "n. 工资；薪酬"},
             {"word": "reviewed", "phonetic": "/rɪˈvjuːd/", "syllable": "re·viewed", "meaning": "v. 审查；审核（被动语态）"},
         ]},
        {"word": "essential", "phonetic": "/ɪˈsenʃl/", "syllable": "es · sen · tial", "pos": "adj.",
         "meaning": "必不可少的；核心的",
         "example": "English is essential for working in most NZ companies.",
         "example_cn": "英语在大多数新西兰公司工作是必不可少的。", "scene": "📝 雅思写作",
         "grammar": "主系表结构：is essential for...（对...来说是必要的）",
         "sentence_words": [
             {"word": "for working in", "phonetic": "/fɔː ˈwɜːkɪŋ ɪn/", "syllable": "for work·ing in", "meaning": "prep. 对于在...工作（for + 动名词）"},
             {"word": "companies", "phonetic": "/ˈkʌmpəniz/", "syllable": "com·pa·nies", "meaning": "n. 公司（复数）"},
         ]},
        {"word": "application", "phonetic": "/ˌæplɪˈkeɪʃn/", "syllable": "ap · pli · ca · tion", "pos": "n.",
         "meaning": "申请；申请表",
         "example": "Submit your visa application at least two months in advance.",
         "example_cn": "至少提前两个月提交签证申请。", "scene": "📋 签证申请",
         "grammar": "祈使句：Submit...；at least two months in advance（提前至少两个月）",
         "sentence_words": [
             {"word": "submit", "phonetic": "/səbˈmɪt/", "syllable": "sub·mit", "meaning": "v. 提交；递交"},
             {"word": "in advance", "phonetic": "/ɪn ədˈvɑːns/", "syllable": "in ad·vance", "meaning": "adv. 提前；预先（固定搭配）"},
         ]},
        {"word": "duration", "phonetic": "/djʊˈreɪʃn/", "syllable": "du · ra · tion", "pos": "n.",
         "meaning": "持续时间；期限",
         "example": "The duration of this course is two semesters.",
         "example_cn": "这门课的时长是两个学期。", "scene": "🎓 学校/雅思",
         "grammar": "主系表结构：The duration of...is...（...的时长是...）",
         "sentence_words": [
             {"word": "course", "phonetic": "/kɔːs/", "syllable": "course", "meaning": "n. 课程"},
             {"word": "semesters", "phonetic": "/sɪˈmestəz/", "syllable": "se·mes·ters", "meaning": "n. 学期（复数，一年两学期）"},
         ]},
        {"word": "approximately", "phonetic": "/əˈprɒksɪmətli/", "syllable": "ap · prox · i · mate · ly", "pos": "adv.",
         "meaning": "大约；大概",
         "example": "The processing time is approximately four to six weeks.",
         "example_cn": "处理时间大约是四到六周。", "scene": "📋 签证/雅思写作",
         "grammar": "主系表结构：The...time is + 副词 + 数量，用副词 approximately 修饰",
         "sentence_words": [
             {"word": "processing time", "phonetic": "/ˈprəʊsesɪŋ taɪm/", "syllable": "pro·cess·ing time", "meaning": "n. 处理时间；审批时间"},
         ]},
        {"word": "recommend", "phonetic": "/ˌrekəˈmend/", "syllable": "re · com · mend", "pos": "v.",
         "meaning": "推荐；建议",
         "example": "I highly recommend the Italian restaurant on Queen Street.",
         "example_cn": "我强烈推荐Queen Street上那家意大利餐厅。", "scene": "🗣️ 雅思口语",
         "grammar": "一般现在时：I recommend...（我推荐...）；highly 加强推荐语气",
         "sentence_words": [
             {"word": "highly", "phonetic": "/ˈhaɪli/", "syllable": "high·ly", "meaning": "adv. 高度；强烈地"},
             {"word": "Italian", "phonetic": "/ɪˈtæliən/", "syllable": "I·tal·ian", "meaning": "adj. 意大利的；n. 意大利人"},
             {"word": "restaurant", "phonetic": "/ˈrestrɒnt/", "syllable": "res·tau·rant", "meaning": "n. 餐厅；饭店"},
         ]},
        {"word": "enrol", "phonetic": "/ɪnˈrəʊl/", "syllable": "en · rol", "pos": "v.",
         "meaning": "注册；报名",
         "example": "You need to enrol before the semester starts.",
         "example_cn": "你需要在学期开始前完成注册。", "scene": "🎓 学校教育",
         "grammar": "need to + 动词原形；before + 从句，表示时间先后",
         "sentence_words": [
             {"word": "semester", "phonetic": "/sɪˈmestər/", "syllable": "se·mes·ter", "meaning": "n. 学期"},
             {"word": "starts", "phonetic": "/stɑːts/", "syllable": "starts", "meaning": "v. 开始（第三人称单数）"},
         ]},
        {"word": "tuition", "phonetic": "/tjuˈɪʃn/", "syllable": "tu · i · tion", "pos": "n.",
         "meaning": "学费",
         "example": "International students pay higher tuition fees than locals.",
         "example_cn": "国际学生的学费比本地生高。", "scene": "🎓 学校/签证",
         "grammar": "比较级：pay higher...than...（比...付更多）",
         "sentence_words": [
             {"word": "international students", "phonetic": "/ˌɪntəˈnæʃnəl ˈstjuːdənts/", "syllable": "in·ter·na·tion·al stu·dents", "meaning": "n. 国际学生（复数）"},
             {"word": "locals", "phonetic": "/ˈləʊkəlz/", "syllable": "lo·cals", "meaning": "n. 本地人（复数口语）"},
         ]},
        {"word": "community", "phonetic": "/kəˈmjuːnəti/", "syllable": "com · mu · ni · ty", "pos": "n.",
         "meaning": "社区",
         "example": "Getting involved in the local community helps you settle in faster.",
         "example_cn": "参与当地社区活动能帮你更快安顿下来。", "scene": "📋 移民生活",
         "grammar": "动名词作主语：Getting involved in...（参与...）+ helps（帮助）",
         "sentence_words": [
             {"word": "getting involved", "phonetic": "/ˈɡetɪŋ ɪnˈvɒlvd/", "syllable": "get·ting in·volved", "meaning": "v. 参与；融入（动名词短语）"},
             {"word": "settle in", "phonetic": "/ˈsetl ɪn/", "syllable": "set·tle in", "meaning": "v. 安顿下来；适应（短语动词）"},
             {"word": "faster", "phonetic": "/ˈfɑːstər/", "syllable": "fast·er", "meaning": "adv. 更快（比较级）"},
         ]},
    ],
}


# ============================================================
# 去重：读取已使用的单词
# ============================================================
def load_used_words():
    """从 memory.md 中提取已使用过的单词"""
    memory_path = BASE_DIR / ".codebuddy" / "automations" / "automation" / "memory.md"
    if not memory_path.exists():
        return set()

    content = memory_path.read_text(encoding='utf-8')
    used = set()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('- ') and ':' in line:
            # 格式: - 2026-04-03: word1, word2, ...
            date_part, words_part = line.split(':', 1)
            words = [w.strip().lower() for w in words_part.split(',') if w.strip()]
            used.update(words)
    return used


def save_used_words(today_words):
    """将今天的单词追加到 memory.md"""
    memory_path = BASE_DIR / ".codebuddy" / "automations" / "automation" / "memory.md"
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    if not memory_path.exists():
        memory_path.write_text("# 每日英语单词 - 自动化执行记录\n\n", encoding='utf-8')

    content = memory_path.read_text(encoding='utf-8')
    word_list = ', '.join(w['word'] for w in today_words)

    # 追加到单词去重记录
    new_line = f"- {TODAY}: {word_list}\n"
    # 插入到 "## 单词去重记录" 之后（如果存在）
    marker = "## 单词去重记录\n"
    if marker in content:
        content = content.replace(marker, marker + new_line, 1)
    else:
        content += "\n## 单词去重记录\n" + new_line

    memory_path.write_text(content, encoding='utf-8')


# ============================================================
# 随机选取今日单词
# ============================================================
def select_todays_words():
    """从词库随机选取10个词（7 NZ + 3 雅思），避免重复"""
    used = load_used_words()

    # 过滤已使用的词
    nz_pool = [w for w in WORD_BANK["nz"] if w["word"].lower() not in used]
    ielts_pool = [w for w in WORD_BANK["ielts"] if w["word"].lower() not in used]

    # 如果去重后不够，从全池补充
    if len(nz_pool) < 7:
        all_nz_words = set(w["word"].lower() for w in WORD_BANK["nz"])
        extra_nz = [w for w in WORD_BANK["nz"] if w["word"].lower() in all_nz_words - set(w["word"].lower() for w in nz_pool)]
        random.shuffle(extra_nz)
        nz_pool.extend(extra_nz)
    if len(ielts_pool) < 3:
        all_ielts_words = set(w["word"].lower() for w in WORD_BANK["ielts"])
        extra_ielts = [w for w in WORD_BANK["ielts"] if w["word"].lower() in all_ielts_words - set(w["word"].lower() for w in ielts_pool)]
        random.shuffle(extra_ielts)
        ielts_pool.extend(extra_ielts)

    random.shuffle(nz_pool)
    random.shuffle(ielts_pool)

    nz_words = nz_pool[:7]
    ielts_words = ielts_pool[:3]

    # 为每个词添加type标记
    for w in nz_words:
        w["type"] = "nz"
    for w in ielts_words:
        w["type"] = "ielts"

    # 合并并随机打乱前7个和后3个的顺序（保持类型不变）
    all_words = nz_words + ielts_words
    return all_words


# ============================================================
# 兴趣加餐：对话库（老友记风格）
# ============================================================
DIALOGUES = [
    {
        "scene": "☕ 咖啡馆偶遇",
        "lines": [
            ("A", "Hey! Fancy seeing you here!", "嘿！真巧在这儿碰到你！"),
            ("B", "Oh hey! I was just grabbing a coffee before work.", "哦嘿！我上班前过来买杯咖啡。"),
            ("A", "Same here. Mind if I join you?", "我也是。介意我一起坐吗？"),
            ("B", "Not at all! Actually, I'm glad I ran into you.", "完全不介意！其实我很高兴碰到你。"),
            ("A", "Really? What's up?", "真的吗？怎么了？"),
            ("B", "I need your advice on something...", "我需要你帮我出出主意..."),
        ],
        "expressions": [
            {"en": "Fancy seeing you here!", "phonetic": "/ˈfænsi ˈsiːɪŋ juː hɪər/", "syllable": "Fan·cy see·ing you here", "cn": "真巧在这儿碰到你！（惊喜偶遇）"},
            {"en": "Mind if I join you?", "phonetic": "/maɪnd ɪf aɪ dʒɔɪn juː/", "syllable": "Mind if I join you?", "cn": "介意我一起吗？（礼貌询问）"},
            {"en": "I ran into you", "phonetic": "/aɪ ræn ˈɪntuː juː/", "syllable": "I ran in·to you", "cn": "我碰到你了（run into = 偶遇）"},
        ]
    },
    {
        "scene": "🍕 约饭",
        "lines": [
            ("A", "I'm starving. Wanna grab a bite?", "我饿死了。去吃点东西？"),
            ("B", "Sure! What are you in the mood for?", "好啊！你想吃什么？"),
            ("A", "How about that new pizza place?", "那家新开的披萨店怎么样？"),
            ("B", "Oh, I've been wanting to try that!", "哦，我一直想去试试！"),
            ("A", "Great! My treat this time.", "太好了！这次我请客。"),
            ("B", "No way, let's go Dutch.", "不行，我们AA吧。"),
        ],
        "expressions": [
            {"en": "Wanna grab a bite?", "phonetic": "/ˈwɒnə ɡræb ə baɪt/", "syllable": "Wan·na grab a bite?", "cn": "去吃点东西？（Wanna = Want to，bite = 一口食物）"},
            {"en": "What are you in the mood for?", "phonetic": "/wɒt ɑː juː ɪn ðə muːd fɔː/", "syllable": "What are you in the mood for?", "cn": "你想吃什么？/你想干嘛？（in the mood for）"},
            {"en": "go Dutch", "phonetic": "/ɡəʊ dʌtʃ/", "syllable": "go Dutch", "cn": "AA制（各自付账）"},
        ]
    },
    {
        "scene": "🏠 合租室友日常",
        "lines": [
            ("A", "Dude, we need to talk about the dishes.", "兄弟，我们得聊聊碗的事儿。"),
            ("B", "Oh no, did I leave them in the sink again?", "哦不，我又把碗扔水槽里了？"),
            ("A", "It's been three days, man.", "都三天了，哥们儿。"),
            ("B", "My bad! I'll do them right after this show.", "我的错！这集看完我就去洗。"),
            ("A", "You said that yesterday.", "你昨天也是这么说的。"),
            ("B", "Okay okay, I'm getting up now...", "好好好，我现在就去..."),
        ],
        "expressions": [
            {"en": "My bad!", "phonetic": "/maɪ bæd/", "syllable": "My bad!", "cn": "我的错！（口语化道歉）"},
            {"en": "right after", "phonetic": "/raɪt ˈɑːftər/", "syllable": "right af·ter", "cn": "……之后马上（表示立即行动）"},
            {"en": "You said that yesterday.", "phonetic": "/juː sed ðæt ˈjestədeɪ/", "syllable": "You said that yes·ter·day.", "cn": "你昨天也是这么说的。（吐槽专用）"},
        ]
    },
    {
        "scene": "💼 上班闲聊",
        "lines": [
            ("A", "How was your weekend?", "你周末过得怎么样？"),
            ("B", "Pretty good! I went hiking with some friends.", "挺好的！和朋友去徒步了。"),
            ("A", "Nice! Where did you go?", "不错！去了哪儿？"),
            ("B", "We drove down to the Waitakere Ranges. The views were amazing.", "我们开车去了Waitakere山脉，风景超棒。"),
            ("A", "I need to get out more. I just stayed home all weekend.", "我得出去走走。我整个周末都宅在家里。"),
            ("B", "Next time you should come with us!", "下次你跟我们一起去吧！"),
        ],
        "expressions": [
            {"en": "Pretty good!", "phonetic": "/ˈprɪti ɡʊd/", "syllable": "Pret·ty good!", "cn": "挺好的！（比Just good更热情的回应）"},
            {"en": "I need to get out more.", "phonetic": "/aɪ niːd tə ɡet aʊt mɔː/", "syllable": "I need to get out more.", "cn": "我得出去多走走/多社交。（常用自嘲）"},
            {"en": "You should come with us!", "phonetic": "/juː ʃʊd kʌm wɪð ʌs/", "syllable": "You should come with us!", "cn": "你应该跟我们一起去！（热情邀请）"},
        ]
    },
    {
        "scene": "🛒 超市偶遇",
        "lines": [
            ("A", "Hey! Long time no see!", "嘿！好久不见！"),
            ("B", "Oh my God, hi! How have you been?", "天哪，嗨！你最近怎么样？"),
            ("A", "Not bad, just moved to a new flat. Still unpacking.", "还行，刚搬了新家。还在拆箱子。"),
            ("B", "That's exciting! Which area?", "太棒了！哪个区？"),
            ("A", "Mt Eden. It's close to work and there's a good cafe nearby.", "Mt Eden。离工作近，附近还有家不错的咖啡馆。"),
            ("B", "You should check out the farmer's market on Sunday. It's great.", "你应该去看看周日的农贸市场，非常好。"),
        ],
        "expressions": [
            {"en": "Long time no see!", "phonetic": "/lɒŋ taɪm nəʊ siː/", "syllable": "Long time no see!", "cn": "好久不见！（经典口语问候）"},
            {"en": "How have you been?", "phonetic": "/haʊ hæv juː biːn/", "syllable": "How have you been?", "cn": "你最近怎么样？（比How are you更关注对方状态）"},
            {"en": "You should check out...", "phonetic": "/juː ʃʊd tʃek aʊt/", "syllable": "You should check out...", "cn": "你应该去看看/试试……（推荐用句）"},
        ]
    },
    {
        "scene": "📞 电话约见面",
        "lines": [
            ("A", "Hey, are you free this Saturday?", "嘿，这周六有空吗？"),
            ("B", "Let me check... Yeah, I think I'm free in the afternoon.", "我看一下……嗯，下午应该有空。"),
            ("A", "Awesome! Want to catch a movie?", "太好了！想去看电影吗？"),
            ("B", "Sure! What's on?", "好啊！有什么在上映？"),
            ("A", "There's a new Marvel film. Want to go to the 3pm session?", "有部新的漫威电影。去看下午3点的场次？"),
            ("B", "Sounds good! Let's meet at the cinema at 2:45.", "听起来不错！2点45在电影院见。"),
        ],
        "expressions": [
            {"en": "Are you free this Saturday?", "phonetic": "/ɑː juː friː ðɪs ˈsætədeɪ/", "syllable": "Are you free this Sat·ur·day?", "cn": "这周六有空吗？（约人必备句型）"},
            {"en": "What's on?", "phonetic": "/wɒts ɒn/", "syllable": "What's on?", "cn": "有什么在上映？/有什么活动？（万能问句）"},
            {"en": "Sounds good!", "phonetic": "/saʊndz ɡʊd/", "syllable": "Sounds good!", "cn": "听起来不错！（轻松同意）"},
        ]
    },
]


# ============================================================
# 兴趣加餐：生成函数
# ============================================================
def generate_bonus(today_words):
    """根据星期几生成兴趣加餐"""
    if WEEKDAY in [1, 3, 5]:  # 周二、四、六 → 老友记对话
        return generate_dialogue_bonus()
    elif WEEKDAY == 6:  # 周日 → 轻松复习
        return generate_review_bonus(today_words)
    else:  # 周一、三、五 → 英文歌曲
        return generate_song_bonus()


def generate_dialogue_bonus():
    """生成老友记风格对话兴趣加餐"""
    # 基于日期确定性选择对话（同一周内不同）
    day_seed = int(hashlib.md5(TODAY.encode()).hexdigest(), 16)
    d = DIALOGUES[day_seed % len(DIALOGUES)]

    lines_html = ""
    for speaker, text, trans in d["lines"]:
        text_safe = text.replace("'", "\\'")
        lines_html += f'''
        <div class="dialogue-line">
          <div class="dialogue-en-row">
            <span class="speaker">{speaker}:</span>
            <span class="dialogue-text">{text}</span>
          </div>
          <div class="dialogue-cn">{trans}</div>
          <button class="dialogue-speak-btn" onclick="speakSentence(this,'{text_safe}')">
            <svg viewBox="0 0 24 24" width="12" height="12"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>
            听这句
          </button>
        </div>'''

    expr_html = ""
    for ex in d["expressions"]:
        ex_safe = ex['en'].replace("'", "\\'")
        phonetic = ex.get('phonetic', '')
        syllable = ex.get('syllable', '')
        syllable_html = f'<span class="ex-syllable">{syllable}</span>' if syllable else ''
        phonetic_html = f'<div class="ex-phonetic">{phonetic}</div>' if phonetic else ''
        expr_html += f'''
        <div class="expression-card">
          <div class="ex-header">
            <span class="ex-en">"{ex['en']}"</span>
            <button class="ex-speak" onclick="speakWord(this,'{ex_safe}')">{SVG_SPEAKER}</button>
          </div>
          {phonetic_html}
          <div class="ex-meta">{syllable_html}</div>
          <div class="ex-cn">{ex['cn']}</div>
        </div>'''

    return f'''
<div class="bonus-section friends-day">
  <div class="bonus-title">☕ 兴趣加餐 · 老友记风格对话</div>
  <div class="bonus-content">
    <div class="scene-title">{d['scene']}</div>
    <div class="dialogue-box">
      {lines_html}
    </div>
    <div class="expressions-box">
      <div class="expressions-title">🗣️ 可直接套用的口语表达（点击🔊听发音）</div>
      {expr_html}
    </div>
    <div class="bonus-tip">
      <strong>💡 学习建议：</strong>大声朗读对话3遍，然后遮住英文只看中文试着翻译，最后模仿语气跟读。把这些表达用到今天的聊天里！
    </div>
  </div>
</div>'''


def generate_song_bonus():
    """生成英文歌曲兴趣加餐（从歌曲库动态选择）"""
    song_keys = list(SONGS_DB.keys())
    # 用日期种子选择，保证同一天选同一首歌，不同天选不同的
    day_seed = int(hashlib.md5(TODAY.encode()).hexdigest(), 16)
    song_key = song_keys[day_seed % len(song_keys)]
    song = SONGS_DB[song_key]

    # 尝试获取MP3直链，失败则回退到搜索链接
    import urllib.parse
    search_query = urllib.parse.quote(f"{song['name']} {song['artist']}")
    netease_search_url = f"https://music.163.com/#/search/m/?s={search_query}"
    print(f"  [音频] 歌曲: {song['name']} - {song['artist']}")

    mp3_url = None
    if song.get('netease_id'):
        from songs_db import fetch_mp3_url
        mp3_url = fetch_mp3_url(song['netease_id'])
        if mp3_url:
            print(f"  [音频] MP3链接获取成功: {mp3_url[:60]}...")
        else:
            print(f"  [音频] MP3链接获取失败，使用搜索链接作为备选")

    if mp3_url:
        # 成功获取MP3：使用 <audio> 内嵌播放器 + 搜索链接备选
        player_html = f'''
    <div class="song-player">
      <audio controls preload="metadata" style="width:100%;border-radius:8px;">
        <source src="{mp3_url}" type="audio/mpeg">
        您的浏览器不支持音频播放
      </audio>
      <div class="song-play-hint">🎧 播放失败？<a href="{netease_search_url}" target="_blank" rel="noopener" style="color:#1e88e5;">点击前往网易云音乐收听</a></div>
    </div>'''
    else:
        # 获取MP3失败：显示搜索跳转按钮
        player_html = f'''
    <div class="song-player">
      <a class="song-play-btn" href="{netease_search_url}" target="_blank" rel="noopener">
        🎧 点击前往网易云音乐收听
      </a>
      <div class="song-play-hint">👉 打开链接后点击播放即可收听完整歌曲</div>
    </div>'''

    # 歌词HTML
    lyrics_html = ""
    for line in song["lyrics"]:
        en = line["en"]
        zh = line["zh"]
        slang_html = ""
        if line.get("slang"):
            for slang in line["slang"]:
                # 检查是否有生词拼读
                hard_words_html = ""
                if slang.get("hard_words"):
                    for hw in slang["hard_words"]:
                        hw_word = hw.get("word", "")
                        hw_phonetic = hw.get("phonetic", "")
                        hw_syllable = hw.get("syllable", "")
                        hw_note = hw.get("note", "")
                        hw_word_safe = hw_word.replace("'", "\\'")
                        syllable_span = f'<span class="hw-syllable">{hw_syllable}</span>' if hw_syllable else ''
                        hard_words_html += f'''
            <div class="hw-item">
              <span class="hw-word">{hw_word}</span>
              <span class="hw-phonetic">{hw_phonetic}</span>
              {syllable_span}
              <span class="hw-mean">{hw_note}</span>
              <button class="hw-speak" onclick="speakWord(this,'{hw_word_safe}')">{SVG_SPEAKER}</button>
            </div>'''
                if hard_words_html:
                    hard_words_block = f'''
        <div class="hard-words-box">
          <div class="hw-title">📝 生词拼读</div>
          {hard_words_html}
        </div>'''
                else:
                    hard_words_block = ""
                # 把 word 做成可发音的格式
                slang_word = slang["word"]
                slang_word_safe = slang_word.replace("'", "\\'")
                # 从 keywords 中查找匹配的音标
                slang_phonetic = ""
                slang_syllable = ""
                for kw in song.get("keywords", []):
                    # 模糊匹配：kw的phrase包含slang的word，或反之
                    if slang_word.lower() in kw["phrase"].lower() or kw["phrase"].lower() in slang_word.lower():
                        slang_phonetic = kw.get("phonetic", "")
                        slang_syllable = kw.get("syllable", "")
                        break
                slang_word_display = f'<b>{slang_word}</b>'
                if slang_phonetic:
                    slang_word_display += f' <span class="slang-phonetic">{slang_phonetic}</span>'
                if slang_syllable:
                    slang_word_display += f' <span class="slang-syllable">{slang_syllable}</span>'
                slang_word_display += f' <button class="slang-speak" onclick="speakWord(this,\'{slang_word_safe}\')">{SVG_SPEAKER}</button>'
                slang_html += f'<div class="slang-note">💡 {slang_word_display}: {slang["note"]}</div>{hard_words_block}'
        lyrics_html += f'''
      <div class="lyric-line">
        <div class="lyric-en">{en}</div>
        <div class="lyric-zh">{zh}</div>
        {slang_html}
      </div>'''

    # 关键词
    keywords_html = ""
    for kw in song["keywords"]:
        phrase_safe = kw["phrase"].replace("'", "\\'")
        syllable = kw.get("syllable", "")
        syllable_html = f'<span class="kw-syllable">{syllable}</span>' if syllable else ''
        keywords_html += f'''
      <div class="keyword-card">
        <div class="kw-header">
          <span class="kw-phrase">"{kw["phrase"]}"</span>
          <button class="kw-speak" onclick="speakWord(this,'{phrase_safe}')">{SVG_SPEAKER}</button>
        </div>
        <div class="kw-phonetic">{kw["phonetic"]}</div>
        <div class="kw-meta">
          {syllable_html}
          <span class="kw-grammar">📘 {kw["grammar"]}</span>
        </div>
        <div class="kw-mean">{kw["meaning"]}</div>
      </div>'''

    return f'''
<div class="bonus-section song-day">
  <div class="bonus-title">🎵 兴趣加餐 · 听歌学英语</div>
  <div class="bonus-content">
    <div class="song-header">
      <div class="song-name">{song["name"]} <span class="song-year">({song["year"]})</span></div>
      <div class="song-artist">🎤 {song["artist"]}</div>
      <div class="song-tense">
        <span class="tense-badge">{song["tense"]}</span>
        <span class="tense-en">{song["tense_en"]}</span>
      </div>
      <div class="tense-rule">📌 {song["tense_rule"]}</div>
    </div>
    {player_html}
    <div class="lyrics-box">
      <div class="lyrics-title">🎶 完整歌词（橙色标注为俚语/地道表达）</div>
      {lyrics_html}
    </div>
    <div class="keywords-box">
      <div class="keywords-title">🎯 重点句型解析（点击🔊听发音）</div>
      <div class="keywords-grid">
        {keywords_html}
      </div>
    </div>
    <div class="bonus-tip">
      <strong>🎧 学习建议：</strong>先完整听两遍感受旋律，再看歌词跟读，最后对照关键表达理解语法。每天一首歌，时态全搞懂！
    </div>
  </div>
</div>'''


def generate_review_bonus(today_words):
    """周日复习版：回顾本周最值得复习的词"""
    used = load_used_words()
    used_list = list(used)

    # 选取最近5个还没太熟的词（从已用词中取最后5-10个）
    review_words = used_list[-10:] if len(used_list) >= 10 else used_list
    random.shuffle(review_words)
    review_words = review_words[:5]

    # 从词库中找到这些词的详细信息
    review_details = []
    all_words = WORD_BANK["nz"] + WORD_BANK["ielts"]
    word_map = {w["word"].lower(): w for w in all_words}

    for w in review_words:
        if w in word_map:
            detail = word_map[w]
            w_safe = detail['word'].replace("'", "\\'")
            review_details.append(f'''
        <div class="review-item">
          <div class="review-word">
            <span class="rw-en">{detail['word']}</span>
            <span class="rw-phonetic">{detail['phonetic']}</span>
            <span class="rw-syllable">{detail['syllable']}</span>
            <button class="rw-speak" onclick="speakWord(this,'{w_safe}')">{SVG_SPEAKER}</button>
          </div>
          <div class="rw-mean">{detail['meaning']}</div>
          <div class="rw-example">"{detail['example']}"</div>
          <div class="rw-example-cn">{detail['example_cn']}</div>
        </div>''')

    # 生成一个小对话帮助回忆
    mini_dialogue = '''
        <div class="review-dialogue">
          <div class="rd-line"><b>A:</b> Hey, how's your English study going this week?</div>
          <div class="rd-cn">嘿，这周英语学得怎么样？</div>
          <div class="rd-line"><b>B:</b> Not bad! I learned some really useful words.</div>
          <div class="rd-cn">还不错！学了一些特别实用的词。</div>
          <div class="rd-line"><b>A:</b> Like what? Give me an example!</div>
          <div class="rd-cn">比如？给我举个例子！</div>
          <div class="rd-line"><b>B:</b> Hmm... try testing me!</div>
          <div class="rd-cn">嗯……你考考我吧！</div>
        </div>'''

    review_items_html = '\n'.join(review_details)

    return f'''
<div class="bonus-section review-day">
  <div class="bonus-title">🧠 兴趣加餐 · 轻松复习</div>
  <div class="bonus-content">
    <div class="review-intro">
      周末到了！轻松回顾一下这周学过的词，不用死记硬背，看看哪些你已经脱口而出了 😊
    </div>
    {mini_dialogue}
    <div class="review-list">
      {review_items_html}
    </div>
    <div class="bonus-tip">
      <strong>💡 复习建议：</strong>遮住英文，只看中文释义试着回忆单词怎么拼、怎么读。能回忆起来的就是你的了！回忆不起来的多看两遍就好。
    </div>
  </div>
</div>'''


# ============================================================
# HTML模板生成
# ============================================================
SVG_SPEAKER = '<svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>'


def build_inline_example(example, sentence_words):
    """
    把例句里的生词替换为高亮内联块（绿色 inline-word）。
    sentence_words: list of dict {word, phonetic, syllable, meaning}
    """
    result = example
    for sw in (sentence_words or []):
        w = sw['word']
        ph = sw.get('phonetic', '')
        # 用大小写不敏感替换，只替换首次出现
        import re
        pattern = re.compile(re.escape(w), re.IGNORECASE)
        inline = (f'<span class="inline-word">'
                  f'<span class="inline-text">{w}</span>'
                  f'<span class="inline-phonetic">{ph}</span>'
                  f'</span>')
        result = pattern.sub(inline, result, count=1)
    return result


def build_sentence_words_html(sentence_words):
    """生成例句生词列表区块 HTML"""
    if not sentence_words:
        return ''
    items = ''
    for sw in sentence_words:
        w_safe = sw['word'].replace("'", "\\'")
        items += f'''
      <div class="sw-item">
        <span class="sw-word">{sw['word']}</span>
        <span class="sw-phonetic">{sw.get('phonetic','')}</span>
        <span class="sw-syllable">{sw.get('syllable','')}</span>
        <span class="sw-mean">{sw.get('meaning','')}</span>
        <button class="sw-speak" onclick="speakWord(this,'{w_safe}')">{SVG_SPEAKER}</button>
      </div>'''
    return f'''
    <div class="sentence-words">
      <div class="sw-title">📝 例句生词</div>
      {items}
    </div>'''


def generate_word_card(w, index):
    """生成单个单词卡片HTML（04-09完整模板：句内高亮+语法标注+例句生词拼读）"""
    word_safe = w['word'].replace("'", "\\'")
    ex_safe = w['example'].replace("'", "\\'")
    pos_class = "nz" if w['type'] == 'nz' else "ielts"
    pos_label = "NZ日常" if w['type'] == 'nz' else "雅思核心"

    sentence_words = w.get('sentence_words', [])
    grammar = w.get('grammar', '')

    # 构建句内高亮例句
    inline_example = build_inline_example(w['example'], sentence_words)
    # 构建例句生词区块
    sw_html = build_sentence_words_html(sentence_words)
    # 语法标注
    grammar_html = f'<span class="grammar-tag">📝 语法：{grammar}</span>' if grammar else ''

    return f'''
<!-- {index} -->
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
      {SVG_SPEAKER}
      听发音
    </button>
  </div>
  <div class="scene-tag">{w['scene']}</div>
  <div class="meaning-cn">{w['meaning']}</div>
  <div class="example-block">
    <div class="example-en">"{inline_example}"</div>
    <div class="example-cn">{w['example_cn']}</div>
    <div class="example-actions">
      <button class="speak-ex-btn" onclick="speakSentence(this,'{ex_safe}')">
        {SVG_SPEAKER}
        听例句
      </button>
      {grammar_html}
    </div>
  </div>
  {sw_html}
</div>'''


# 完整CSS（参考04-03模板 + 兴趣加餐样式）
CSS = '''
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%);
      min-height: 100vh;
      font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
      padding: 20px 16px 40px;
      color: #263238;
    }
    header {
      text-align: center;
      margin-bottom: 28px;
      padding: 28px 20px 22px;
      background: linear-gradient(120deg, #43a047, #1e88e5);
      border-radius: 20px;
      color: #fff;
      box-shadow: 0 6px 24px rgba(30,136,229,0.25);
    }
    header .date-label { font-size: 15px; letter-spacing: 2px; opacity: 0.88; margin-bottom: 8px; }
    header h1 { font-size: 30px; font-weight: 800; letter-spacing: 4px; text-shadow: 0 2px 8px rgba(0,0,0,0.15); }
    header .subtitle { font-size: 13px; margin-top: 10px; opacity: 0.82; letter-spacing: 1px; }
    .tag-bar { display: flex; justify-content: center; gap: 10px; margin-bottom: 22px; flex-wrap: wrap; }
    .tag { font-size: 12px; padding: 4px 14px; border-radius: 20px; font-weight: 600; letter-spacing: 1px; }
    .tag-nz    { background: #c8e6c9; color: #2e7d32; }
    .tag-ielts { background: #bbdefb; color: #1565c0; }
    .card {
      background: #fff;
      border-radius: 18px;
      padding: 22px 20px 20px;
      margin-bottom: 18px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.08);
      position: relative;
      overflow: hidden;
    }
    .card::before { content: ''; position: absolute; top: 0; left: 0; width: 5px; height: 100%; border-radius: 18px 0 0 18px; }
    .card.nz::before    { background: linear-gradient(180deg, #43a047, #a5d6a7); }
    .card.ielts::before { background: linear-gradient(180deg, #1e88e5, #90caf9); }
    .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }
    .word-index { font-size: 13px; font-weight: 700; color: #9e9e9e; min-width: 26px; }
    .word-en { font-size: 28px; font-weight: 800; color: #1a237e; letter-spacing: 1px; }
    .pos-badge { font-size: 11px; padding: 2px 10px; border-radius: 10px; font-weight: 600; margin-left: auto; }
    .nz .pos-badge    { background: #e8f5e9; color: #2e7d32; }
    .ielts .pos-badge { background: #e3f2fd; color: #1565c0; }
    .phonetic-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-left: 36px; flex-wrap: wrap; }
    .phonetic { font-size: 17px; color: #757575; font-family: 'Segoe UI', Arial, sans-serif; letter-spacing: 1px; }
    .syllable { font-size: 14px; color: #ff6f00; font-weight: 700; background: #fff8e1; padding: 2px 10px; border-radius: 8px; letter-spacing: 2px; }
    .speak-btn {
      display: inline-flex; align-items: center; gap: 5px;
      background: linear-gradient(120deg, #43a047, #1e88e5); color: #fff;
      border: none; border-radius: 20px; padding: 6px 16px;
      font-size: 14px; font-weight: 600; cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
      box-shadow: 0 2px 8px rgba(30,136,229,0.25); letter-spacing: 1px;
    }
    .speak-btn:active { transform: scale(0.95); }
    .speak-btn.playing { background: linear-gradient(120deg, #fb8c00, #f4511e); }
    .speak-btn svg { width: 16px; height: 16px; fill: #fff; }
    .speak-ex-btn {
      display: inline-flex; align-items: center; gap: 4px;
      background: #e3f2fd; color: #1565c0; border: none;
      border-radius: 14px; padding: 6px 14px; font-size: 13px;
      font-weight: 600; cursor: pointer; transition: background 0.15s; margin-top: 6px;
    }
    .speak-ex-btn:hover { background: #bbdefb; }
    .speak-ex-btn svg { width: 14px; height: 14px; fill: #1565c0; }
    .meaning-cn { font-size: 20px; font-weight: 700; color: #37474f; margin-bottom: 12px; padding-left: 36px; }
    .scene-tag { font-size: 11px; display: inline-block; padding: 2px 8px; border-radius: 8px; background: #fff3e1; color: #e65100; margin-left: 36px; margin-bottom: 8px; font-weight: 600; }
    .example-block { background: #f5f7fa; border-radius: 12px; padding: 14px 16px; margin-left: 36px; }
    .example-en { font-size: 15px; color: #1a237e; font-style: italic; margin-bottom: 6px; line-height: 2; }
    .example-cn { font-size: 14px; color: #607d8b; line-height: 1.5; margin-bottom: 10px; }
    .example-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .grammar-tag { font-size: 12px; color: #7b1fa2; background: #f3e5f5; padding: 6px 12px; border-radius: 12px; font-weight: 600; }

    /* 句内生词高亮（绿色块：单词+音标） */
    .inline-word {
      display: inline-flex;
      flex-direction: column;
      align-items: center;
      background: #e8f5e9;
      border-radius: 8px;
      padding: 2px 8px;
      margin: 0 2px;
      vertical-align: bottom;
    }
    .inline-text {
      font-size: 15px;
      color: #2e7d32;
      font-weight: 700;
      font-style: normal;
    }
    .inline-phonetic {
      font-size: 11px;
      color: #e65100;
      font-weight: 600;
      font-style: normal;
    }

    /* 例句生词列表 */
    .sentence-words { margin: 12px 0 0 36px; background: #fff; border-radius: 12px; padding: 14px 16px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .sw-title { font-size: 14px; color: #666; font-weight: 600; margin-bottom: 12px; }
    .sw-item { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; padding: 8px 0; border-bottom: 1px dashed #eee; }
    .sw-item:last-child { border-bottom: none; margin-bottom: 0; }
    .sw-word { font-size: 18px; font-weight: 700; color: #1976d2; min-width: 70px; }
    .sw-phonetic { font-size: 14px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; }
    .sw-syllable { font-size: 13px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffcc80; }
    .sw-mean { font-size: 14px; color: #333; }
    .sw-speak {
      width: 28px; height: 28px; border-radius: 50%; border: none;
      background: #e3f2fd; color: #1976d2;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s; flex-shrink: 0; margin-left: 4px;
    }
    .sw-speak svg { width: 14px; height: 14px; fill: #1976d2; }
    .sw-speak:hover { background: #bbdefb; transform: scale(1.05); }
    .sw-speak:active { transform: scale(0.95); }
    .tip-bar { background: #fff8e1; border-left: 4px solid #ffca28; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #795548; margin-bottom: 20px; line-height: 1.6; }
    footer { text-align: center; margin-top: 32px; padding: 22px 16px; background: linear-gradient(120deg, #43a047, #1e88e5); border-radius: 18px; color: #fff; font-size: 18px; font-weight: 700; letter-spacing: 2px; box-shadow: 0 4px 16px rgba(30,136,229,0.2); line-height: 1.8; }
    footer span { display: block; font-size: 13px; font-weight: 400; margin-top: 6px; opacity: 0.85; }
    @media (max-width: 480px) { .word-en { font-size: 23px; } .meaning-cn { font-size: 18px; } }

    /* ===== 兴趣加餐 - 通用 ===== */
    .bonus-section {
      margin-top: 28px;
      padding: 24px 20px 22px;
      border-radius: 20px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.1);
    }
    .bonus-title {
      font-size: 22px;
      font-weight: 800;
      text-align: center;
      margin-bottom: 16px;
      letter-spacing: 2px;
    }
    .bonus-content { line-height: 1.8; }
    .bonus-tip {
      background: #f3e5f5;
      border-radius: 10px;
      padding: 12px 14px;
      margin-top: 16px;
      font-size: 13px;
      color: #6a1b9a;
      line-height: 1.7;
    }

    /* ===== 兴趣加餐 - 对话版 ===== */
    .friends-day {
      background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
      border: 2px dashed #ffb74d;
    }
    .friends-day .bonus-title { color: #e65100; }
    .scene-title { font-size: 16px; font-weight: 700; color: #e65100; margin-bottom: 12px; text-align: center; }
    .dialogue-box { background: #fff8e1; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .dialogue-line { margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #ffe0b2; }
    .dialogue-line:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .dialogue-en-row { margin-bottom: 4px; }
    .speaker { font-weight: 700; color: #e65100; }
    .dialogue-text { color: #333; font-style: italic; }
    .dialogue-cn { color: #777; font-size: 13px; margin-bottom: 6px; padding-left: 24px; }
    .dialogue-speak-btn {
      display: inline-flex; align-items: center; gap: 4px;
      background: #fff3e0; color: #e65100; border: 1px solid #ffcc80;
      border-radius: 12px; padding: 3px 10px; font-size: 11px;
      font-weight: 600; cursor: pointer; transition: all 0.15s;
      margin-left: 24px;
    }
    .dialogue-speak-btn:hover { background: #ffe0b2; }
    .dialogue-speak-btn svg { fill: #e65100; }
    .expressions-box { background: #e3f2fd; border-radius: 12px; padding: 14px; }
    .expressions-title { font-size: 14px; font-weight: 700; color: #1565c0; margin-bottom: 12px; }
    .expression-card { background: #fff; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
    .expression-card:last-child { margin-bottom: 0; }
    .ex-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .ex-en { font-size: 18px; font-weight: 700; color: #1976d2; }
    .ex-speak {
      width: 28px; height: 28px; border-radius: 50%; border: none;
      background: #e3f2fd; color: #1976d2;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s;
    }
    .ex-speak svg { width: 14px; height: 14px; fill: #1976d2; }
    .ex-speak:hover { background: #bbdefb; transform: scale(1.05); }
    .ex-speak:active { transform: scale(0.95); }
    .ex-phonetic { font-size: 14px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; margin-bottom: 6px; }
    .ex-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
    .ex-syllable { font-size: 13px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffcc80; }
    .ex-cn { color: #333; font-size: 14px; }

    /* ===== 兴趣加餐 - 歌曲版 ===== */
    .song-day {
      background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
      border: 2px dashed #66bb6a;
    }
    .song-day .bonus-title { color: #2e7d32; }
    .song-header { margin-bottom: 16px; text-align: center; }
    .song-name { font-size: 22px; font-weight: 800; color: #1b5e20; margin-bottom: 6px; }
    .song-year { font-size: 14px; color: #666; font-weight: 400; }
    .song-artist { font-size: 15px; color: #555; margin-bottom: 10px; }
    .song-tense { margin-bottom: 8px; }
    .tense-badge { background: #4caf50; color: #fff; font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-right: 8px; }
    .tense-en { font-size: 13px; color: #666; font-style: italic; }
    .tense-rule { font-size: 13px; color: #2e7d32; background: #e8f5e9; padding: 8px 12px; border-radius: 8px; margin-top: 8px; }
    .song-player { margin: 16px 0; }
    .song-player audio { width: 100%; border-radius: 8px; }
    .song-player .song-play-btn {
      display: inline-block;
      background: linear-gradient(135deg, #43a047, #1e88e5);
      color: #fff;
      text-decoration: none;
      padding: 14px 28px;
      border-radius: 30px;
      font-size: 16px;
      font-weight: 700;
      letter-spacing: 1px;
      box-shadow: 0 4px 16px rgba(30,136,229,0.3);
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .song-player .song-play-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(30,136,229,0.4); }
    .song-player .song-play-btn:active { transform: scale(0.97); }
    .song-player .song-play-hint { font-size: 12px; color: #888; margin-top: 10px; }
    .song-player-error { color: #e65100; font-size: 13px; text-align: center; padding: 12px; background: #fff3e0; border-radius: 8px; }
    .lyrics-box { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .lyrics-title { font-size: 14px; font-weight: 700; color: #2e7d32; margin-bottom: 12px; }
    .lyric-line { margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #e0e0e0; }
    .lyric-line:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .lyric-en { font-size: 15px; color: #333; font-weight: 500; margin-bottom: 4px; }
    .lyric-zh { font-size: 13px; color: #666; margin-bottom: 4px; }
    .slang-note { font-size: 12px; color: #e65100; background: #fff8e1; padding: 6px 10px; border-radius: 6px; margin-top: 4px; border-left: 3px solid #ffb74d; }
    .slang-phonetic { font-size: 11px; color: #888; font-family: 'Segoe UI', Arial, sans-serif; }
    .slang-syllable { font-size: 11px; color: #e65100; font-weight: 600; background: #fff3e0; padding: 1px 6px; border-radius: 4px; margin-left: 2px; }
    .slang-speak {
      width: 22px; height: 22px; border-radius: 50%; border: none;
      background: #ffe0b2; color: #e65100;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s; vertical-align: middle; margin-left: 2px;
    }
    .slang-speak svg { width: 11px; height: 11px; fill: #e65100; }
    .slang-speak:hover { background: #ffcc80; transform: scale(1.05); }
    /* 歌词生词拼读 */
    .hard-words-box { background: #e8f5e9; border-radius: 8px; padding: 8px 12px; margin-top: 4px; border: 1px solid #a5d6a7; }
    .hw-title { font-size: 12px; color: #2e7d32; font-weight: 700; margin-bottom: 6px; }
    .hw-item { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 4px 0; border-bottom: 1px dashed #c8e6c9; }
    .hw-item:last-child { border-bottom: none; }
    .hw-word { font-size: 15px; font-weight: 700; color: #2e7d32; }
    .hw-phonetic { font-size: 12px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; }
    .hw-syllable { font-size: 11px; color: #e65100; font-weight: 600; background: #fff3e0; padding: 1px 6px; border-radius: 4px; }
    .hw-mean { font-size: 12px; color: #333; }
    .hw-speak {
      width: 24px; height: 24px; border-radius: 50%; border: none;
      background: #c8e6c9; color: #2e7d32;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s; flex-shrink: 0;
    }
    .hw-speak svg { width: 12px; height: 12px; fill: #2e7d32; }
    .hw-speak:hover { background: #a5d6a7; transform: scale(1.05); }
    .keywords-box { background: #f3e5f5; border-radius: 12px; padding: 14px; }
    .keywords-title { font-size: 14px; font-weight: 700; color: #6a1b9a; margin-bottom: 12px; }
    .keywords-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
    .keyword-card { background: #fff; border-radius: 10px; padding: 12px 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
    .kw-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
    .kw-phrase { font-size: 16px; font-weight: 700; color: #1976d2; }
    .kw-speak {
      width: 26px; height: 26px; border-radius: 50%; border: none;
      background: #e3f2fd; color: #1976d2; font-size: 11px;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
      transition: all 0.2s;
    }
    .kw-speak:hover { background: #bbdefb; }
    .kw-phonetic { font-size: 13px; color: #666; font-family: 'Segoe UI', Arial, sans-serif; margin-bottom: 6px; }
    .kw-grammar { font-size: 12px; color: #5e35b1; background: #ede7f6; padding: 3px 10px; border-radius: 6px; display: inline-block; margin-bottom: 6px; }
    .kw-mean { font-size: 13px; color: #333; }

    /* ===== 兴趣加餐 - 复习版 ===== */
    .review-day {
      background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
      border: 2px dashed #7986cb;
    }
    .review-day .bonus-title { color: #283593; }
    .review-intro { font-size: 14px; color: #37474f; margin-bottom: 16px; text-align: center; }
    .review-dialogue { background: #fff; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px; }
    .rd-line { font-size: 14px; color: #333; margin-bottom: 4px; font-style: italic; }
    .rd-cn { font-size: 13px; color: #777; margin-bottom: 8px; padding-left: 20px; }
    .review-list { background: #fff; border-radius: 12px; padding: 14px; }
    .review-item { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed #e0e0e0; }
    .review-item:last-child { border-bottom: none; margin-bottom: 0; }
    .review-word { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .rw-en { font-size: 18px; font-weight: 700; color: #1a237e; }
    .rw-phonetic { font-size: 14px; color: #757575; }
    .rw-speak {
      width: 26px; height: 26px; border-radius: 50%; border: none;
      background: #e8eaf6; color: #283593;
      cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
    }
    .rw-speak svg { width: 13px; height: 13px; fill: #283593; }
    .rw-speak:hover { background: #c5cae9; }
    .rw-syllable { font-size: 13px; color: #e65100; font-weight: 600; background: #fff8e1; padding: 2px 8px; border-radius: 6px; border: 1px solid #ffcc80; margin-left: 6px; }
    .rw-mean { font-size: 14px; color: #37474f; margin-bottom: 4px; }
    .rw-example { font-size: 13px; color: #1a237e; font-style: italic; margin-bottom: 2px; }
    .rw-example-cn { font-size: 12px; color: #607d8b; }
'''


def generate_html(words, bonus_html):
    """生成完整HTML"""
    date_display = f'{TODAY_DATE.year}年{TODAY_DATE.month}月{TODAY_DATE.day}日'
    weekday_cn = WEEKDAY_NAMES[WEEKDAY]

    words_html = ""
    for i, w in enumerate(words, 1):
        words_html += generate_word_card(w, i)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>每日英语单词 · {TODAY}</title>
  <style>{CSS}</style>
</head>
<body>
<header>
  <div class="date-label">📅 {date_display} · {weekday_cn}</div>
  <h1>📖 每日英语单词</h1>
  <div class="subtitle">🇳🇿 新西兰生活口语 &nbsp;+&nbsp; 🎓 雅思移民备考</div>
</header>

<div class="tag-bar">
  <span class="tag tag-nz">🟢 新西兰日常 × 7</span>
  <span class="tag tag-ielts">🔵 雅思核心 × 3</span>
</div>

<div class="tip-bar">
  🔊 点击 <strong>「听发音」</strong> 朗读单词，点击 <strong>「听例句」</strong> 朗读完整例句（语速较慢，方便跟读）<br>
  橙色音节为拼读分解，帮助记忆发音规律。
</div>

{words_html}

{bonus_html}

<footer>
  🌱 每天进步一点点，语言的大门就会为你敞开！
  <span>坚持学习，你的新西兰生活已在路上 🇳🇿</span>
</footer>

<script>
  const synth = window.speechSynthesis;
  let voices = [];
  function loadVoices() {{ voices = synth.getVoices(); }}
  if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = loadVoices;
  loadVoices();

  function getEnglishVoice() {{
    const preferred = ['en-NZ','en-AU','en-GB','en-US'];
    for (const lang of preferred) {{
      const v = voices.find(v => v.lang === lang);
      if (v) return v;
    }}
    return voices.find(v => v.lang.startsWith('en')) || null;
  }}

  function speak(text, btn, rate) {{
    if (!synth) {{ alert('请使用 Chrome 或 Edge 浏览器打开以获得最佳体验。'); return; }}
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    const voice = getEnglishVoice();
    if (voice) utter.voice = voice;
    utter.lang  = 'en-NZ';
    utter.rate  = rate;
    utter.pitch = 1;
    if (btn) {{
      btn.classList.add('playing');
      utter.onend   = () => btn.classList.remove('playing');
      utter.onerror = () => btn.classList.remove('playing');
    }}
    synth.speak(utter);
  }}

  function speakWord(btn, word)    {{ speak(word, btn, 0.5); }}
  function speakSentence(btn, sen) {{ speak(sen, btn, 0.3); }}
</script>

</body>
</html>'''


# ============================================================
# 主流程
# ============================================================
if __name__ == "__main__":
    print(f"[*] 每日英语单词生成器 v3")
    print(f"[*] 日期: {TODAY} ({WEEKDAY_NAMES[WEEKDAY]})")
    print(f"[*] 正在从词库选取今日10词...")

    # 1. 选取单词
    words = select_todays_words()
    print(f"[*] 选取完成，已排除 {len(load_used_words())} 个已用词")

    print(f"\n[*] 今日 10 词：")
    for i, w in enumerate(words, 1):
        tag = "🟢" if w['type'] == 'nz' else "🔵"
        print(f"  {tag} {i:02d}. {w['word']} ({w['meaning']})")

    # 2. 生成兴趣加餐
    print(f"\n[*] 生成兴趣加餐...", end="")
    bonus_html = generate_bonus(words)
    if WEEKDAY in [0, 2, 4]:
        print(" 🎵 英文歌曲")
    elif WEEKDAY in [1, 3, 5]:
        print(" ☕ 老友记对话")
    else:
        print(" 🧠 轻松复习")

    # 3. 生成完整HTML
    print(f"\n[*] 生成HTML文件...")
    final_html = generate_html(words, bonus_html)
    OUTPUT.write_text(final_html, encoding='utf-8')
    print(f"[OK] 已生成: {OUTPUT}")
    print(f"     文件大小: {OUTPUT.stat().st_size / 1024:.1f} KB")

    # 4. 保存去重记录
    save_used_words(words)
    print(f"[OK] 去重记录已更新")

    print(f"\n[*] ✅ 完成！下一步：运行 embed-daily-words-audio.py 嵌入音频，然后运行 send-all-v2.py 推送")
