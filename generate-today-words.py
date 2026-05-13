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

import random
import re
import pathlib
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 始终使用北京时间（UTC+8），避免 GitHub Actions 在 UTC 时区导致星期几判断偏差
_BJT = timezone(timedelta(hours=8))
BASE_DIR = Path(__file__).parent
TODAY = datetime.now(_BJT).strftime('%Y-%m-%d')
TODAY_DATE = datetime.now(_BJT)
WEEKDAY = TODAY_DATE.weekday()  # 0=周一 ... 6=周日（基于北京时间）
WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
OUTPUT = BASE_DIR / f"每日英语单词_{TODAY}.html"

# 导入歌曲数据库（使用自动歌曲系统）
import auto_songs


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
             {"word": "tenancy", "phonetic": "/ˈtenənsi/", "syllable": "ten·an·cy", "meaning": "n. 租赁"}
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
             {"word": "bond", "phonetic": "/bɒnd/", "syllable": "bond", "meaning": "n. 押金"}
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
            {"word": "landlord", "phonetic": "/ˈlændlɔːd/", "syllable": "land·lord", "meaning": "n. 房东"},
            {"word": "things", "phonetic": "/θɪŋz/", "syllable": "things", "meaning": "n. 东西（复数）"}
         ]},
        {"word": "flatmate", "phonetic": "/ˈflætmeɪt/", "syllable": "flat · mate", "pos": "n.",
         "meaning": "室友；合租伙伴",
         "example": "My flatmate is moving out next month.",
         "example_cn": "我室友下个月要搬走了。", "scene": "🏠 合租生活",
         "grammar": "现在进行时表将来：is moving out，+时间状语 next month 表近期计划",
         "sentence_words": [
             {"word": "moving out", "phonetic": "/ˈmuːvɪŋ aʊt/", "syllable": "mov·ing out", "meaning": "v. 搬出去（move out 短语动词）"},
             {"word": "month", "phonetic": "/mʌnθ/", "syllable": "month", "meaning": "n. 月；月份"},
             {"word": "flatmate", "phonetic": "/ˈflætmeɪt/", "syllable": "flat·mate", "meaning": "n. 合租室友"},
             {"word": "moving", "phonetic": "/ˈmuːvɪŋ/", "syllable": "mov·ing", "meaning": "v. 搬家（现在分词/动名词）"}
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
             {"word": "inspection", "phonetic": "/ɪnˈspekʃn/", "syllable": "in·spec·tion", "meaning": "n. 检查；视察"},
             {"word": "tidy", "phonetic": "/ˈtaɪdi/", "syllable": "ti·dy", "meaning": "v./adj. 整理；整洁的"}
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
             {"word": "days", "phonetic": "/deɪz/", "syllable": "days", "meaning": "n. 天（复数）"},
             {"word": "moving", "phonetic": "/ˈmuːvɪŋ/", "syllable": "mov·ing", "meaning": "v. 搬家（现在分词/动名词）"},
             {"word": "notice", "phonetic": "/ˈnəʊtɪs/", "syllable": "no·tice", "meaning": "n. 通知；提前告知"}
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
             {"word": "furnished", "phonetic": "/ˈfɜːnɪʃt/", "syllable": "fur·nished", "meaning": "adj. 配备家具的"}
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
             {"word": "lease", "phonetic": "/liːs/", "syllable": "lease", "meaning": "n. 租约；租期"}
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
             {"word": "dairy", "phonetic": "/ˈdeəri/", "syllable": "dai·ry", "meaning": "n. 便利店（NZ用法）"}
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
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "queue", "phonetic": "/kjuː/", "syllable": "queue", "meaning": "n. 排队；队伍"}
         ]},
        {"word": "trolley", "phonetic": "/ˈtrɒli/", "syllable": "trol · ley", "pos": "n.",
         "meaning": "购物车（NZ/英式）",
         "example": "Can you grab a trolley? I forgot to get one.",
         "example_cn": "你能推一辆购物车吗？我忘了拿。", "scene": "🏪 超市",
         "grammar": "Can you...? 表示请求；I forgot to do sth. 忘记做某事",
         "sentence_words": [
             {"word": "forgot", "phonetic": "/fəˈɡɒt/", "syllable": "for·got", "meaning": "v. 忘记（forget 的过去式）"},
             {"word": "grab", "phonetic": "/ɡræb/", "syllable": "grab", "meaning": "v. 拿；取（口语常用）"},
             {"word": "trolley", "phonetic": "/ˈtrɒli/", "syllable": "trol·ley", "meaning": "n. 购物车"}
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
             {"word": "receipt", "phonetic": "/rɪˈsiːt/", "syllable": "re·ceipt", "meaning": "n. 收据；小票"}
         ]},
        {"word": "special", "phonetic": "/ˈspeʃl/", "syllable": "spe · cial", "pos": "n./adj.",
         "meaning": "特价商品；特别的",
         "example": "Mince is on special this week at Pak'nSave.",
         "example_cn": "这周Pak'nSave的肉末特价。", "scene": "🏪 超市促销",
         "grammar": "on special = 打折特价（NZ固定表达），一般现在时表当前状态",
         "sentence_words": [
             {"word": "mince", "phonetic": "/mɪns/", "syllable": "mince", "meaning": "n. 肉末；绞肉（NZ超市常见）"},
             {"word": "on special", "phonetic": "/ɒn ˈspeʃl/", "syllable": "on spe·cial", "meaning": "phrase. 特价中（NZ口语）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "pak'nsave", "phonetic": "/ˌpæk ən ˈseɪv/", "syllable": "Pak'nSave", "meaning": "n. 纽村平价超市名"},
             {"word": "special", "phonetic": "/ˈspeʃl/", "syllable": "spe·cial", "meaning": "adj. 特价的；特别的"}
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
             {"word": "eftpos", "phonetic": "/ˈeftpɒs/", "syllable": "EFT·POS", "meaning": "n. 电子刷卡支付系统"}
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
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "chemist", "phonetic": "/ˈkemɪst/", "syllable": "chem·ist", "meaning": "n. 药房；药剂师"}
         ]},
        {"word": "prescription", "phonetic": "/prɪˈskrɪpʃn/", "syllable": "pre · scrip · tion", "pos": "n.",
         "meaning": "处方；药方",
         "example": "The doctor gave me a prescription for antibiotics.",
         "example_cn": "医生给我开了一剂抗生素处方。", "scene": "🏥 医院/药店",
         "grammar": "一般过去时：gave（give 的过去式）；give sb. sth. 双宾语结构",
         "sentence_words": [
             {"word": "doctor", "phonetic": "/ˈdɒktər/", "syllable": "doc·tor", "meaning": "n. 医生"},
             {"word": "antibiotics", "phonetic": "/ˌæntibaɪˈɒtɪks/", "syllable": "an·ti·bi·ot·ics", "meaning": "n. 抗生素（复数）"},
             {"word": "prescription", "phonetic": "/prɪˈskrɪpʃn/", "syllable": "pre·scrip·tion", "meaning": "n. 处方"}
         ]},
        {"word": "GP", "phonetic": "/ˌdʒiː ˈpiː/", "syllable": "G · P", "pos": "n.",
         "meaning": "全科医生",
         "example": "You should go see a GP if it doesn't get better in a few days.",
         "example_cn": "如果过几天还不好，你应该去看全科医生。", "scene": "🏥 看病",
         "grammar": "should + 动词原形（建议）；if 条件句（如果...）",
         "sentence_words": [
             {"word": "get better", "phonetic": "/ɡet ˈbetər/", "syllable": "get bet·ter", "meaning": "v. 好转；康复（固定搭配）"},
             {"word": "in a few days", "phonetic": "/ɪn ə fjuː deɪz/", "syllable": "in a few days", "meaning": "phrase. 在几天内"},
             {"word": "better", "phonetic": "/ˈbetər/", "syllable": "bet·ter", "meaning": "adj./adv. 更好的"},
             {"word": "days", "phonetic": "/deɪz/", "syllable": "days", "meaning": "n. 天（复数）"},
             {"word": "gp", "phonetic": "/ˌdʒiː ˈpiː/", "syllable": "GP", "meaning": "n. 全科医生（General Practitioner）"}
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
             {"word": "acc", "phonetic": "/ˌeɪ siː ˈsiː/", "syllable": "ACC", "meaning": "n. 新西兰意外伤害赔偿局"},
             {"word": "costs", "phonetic": "/kɒsts/", "syllable": "costs", "meaning": "n. 费用（复数）"},
             {"word": "medical", "phonetic": "/ˈmedɪkl/", "syllable": "med·i·cal", "meaning": "adj. 医疗的"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"}
         ]},
        {"word": "appointment", "phonetic": "/əˈpɔɪntmənt/", "syllable": "ap · point · ment", "pos": "n.",
         "meaning": "预约",
         "example": "I've got a doctor's appointment at 2pm.",
         "example_cn": "我约了下午2点看医生。", "scene": "🏥 预约看病",
         "grammar": "现在完成时（口语）：I've got = I have got，表示当前拥有的安排",
         "sentence_words": [
             {"word": "doctor's", "phonetic": "/ˈdɒktəz/", "syllable": "doc·tor's", "meaning": "n. 医生的（所有格）"},
             {"word": "appointment", "phonetic": "/əˈpɔɪntmənt/", "syllable": "ap·point·ment", "meaning": "n. 预约"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "pm", "phonetic": "/ˌpiː ˈem/", "syllable": "PM", "meaning": "n./abbr. 下午（Post Meridiem）"}
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
             {"word": "lane", "phonetic": "/leɪn/", "syllable": "lane", "meaning": "n. 车道"},
             {"word": "rush", "phonetic": "/rʌʃ/", "syllable": "rush", "meaning": "n./adj. 高峰；匆忙的"}
         ]},
        {"word": "motorway", "phonetic": "/ˈməʊtəweɪ/", "syllable": "mo · tor · way", "pos": "n.",
         "meaning": "高速公路（NZ叫法）",
         "example": "Take the motorway south, it's faster than going through the city.",
         "example_cn": "走南边的高速吧，比穿城快。", "scene": "🚌 交通出行",
         "grammar": "祈使句：Take...；比较级：faster than（比...更快）",
         "sentence_words": [
             {"word": "south", "phonetic": "/saʊθ/", "syllable": "south", "meaning": "adv./n. 向南；南方"},
             {"word": "through", "phonetic": "/θruː/", "syllable": "through", "meaning": "prep. 穿过；经过"},
             {"word": "city", "phonetic": "/ˈsɪti/", "syllable": "cit·y", "meaning": "n. 城市"},
             {"word": "faster", "phonetic": "/ˈfɑːstər/", "syllable": "fas·ter", "meaning": "adv. 更快地"},
             {"word": "motorway", "phonetic": "/ˈməʊtəweɪ/", "syllable": "mo·tor·way", "meaning": "n. 高速公路"}
         ]},
        {"word": "roundabout", "phonetic": "/ˈraʊndəbaʊt/", "syllable": "round · a · bout", "pos": "n.",
         "meaning": "环岛；环形交叉路口",
         "example": "At the roundabout, take the second exit.",
         "example_cn": "在环岛走第二个出口。", "scene": "🚌 交通出行",
         "grammar": "祈使句：take the second exit（走第二个出口）；at + 名词，表示位置",
         "sentence_words": [
             {"word": "exit", "phonetic": "/ˈeksɪt/", "syllable": "ex·it", "meaning": "n. 出口；出路"},
             {"word": "second", "phonetic": "/ˈsekənd/", "syllable": "sec·ond", "meaning": "adj. 第二的（序数词）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "roundabout", "phonetic": "/ˈraʊndəbaʊt/", "syllable": "round·a·bout", "meaning": "n. 环岛（交通）"}
         ]},
        {"word": "transfer", "phonetic": "/trænsˈfɜː/", "syllable": "trans · fer", "pos": "n./v.",
         "meaning": "换乘；转账",
         "example": "You need to transfer to Bus 70 at Britomart.",
         "example_cn": "你需要在Britomart换乘70路公交。", "scene": "🚌 换乘",
         "grammar": "need to + 动词原形：需要做某事；transfer to 换乘到（某路线）",
         "sentence_words": [
             {"word": "transfer to", "phonetic": "/trænsˈfɜː tuː/", "syllable": "trans·fer to", "meaning": "v. 换乘；转乘（固定搭配）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "britomart", "phonetic": "/ˈbrɪtəmɑːt/", "syllable": "Bri·to·mart", "meaning": "n. 奥克兰市中心交通枢纽"},
             {"word": "transfer", "phonetic": "/trænsˈfɜːr/", "syllable": "trans·fer", "meaning": "v. 换乘；转车"}
         ]},
        {"word": "AT HOP card", "phonetic": "/eɪ tiː hɒp kɑːd/", "syllable": "AT HOP card", "pos": "n.",
         "meaning": "奥克兰公交卡",
         "example": "Make sure you tag on and off with your AT HOP card.",
         "example_cn": "上下车记得刷AT HOP卡。", "scene": "🚌 公交通勤",
         "grammar": "祈使句：Make sure + 主从句；tag on and off（刷卡上下车）",
         "sentence_words": [
             {"word": "tag on", "phonetic": "/tæɡ ɒn/", "syllable": "tag on", "meaning": "v. 刷卡进站（NZ公交用语）"},
             {"word": "tag off", "phonetic": "/tæɡ ɒf/", "syllable": "tag off", "meaning": "v. 刷卡出站（NZ公交用语）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "card", "phonetic": "/kɑːd/", "syllable": "card", "meaning": "n. 卡"},
             {"word": "hop", "phonetic": "/hɒp/", "syllable": "hop", "meaning": "n. 跳（AT HOP = 奥克兰公交卡）"},
             {"word": "tag", "phonetic": "/tæɡ/", "syllable": "tag", "meaning": "v. 刷卡；贴标签"}
         ]},
        {"word": "carpark", "phonetic": "/ˈkɑːpɑːk/", "syllable": "car · park", "pos": "n.",
         "meaning": "停车场（NZ合写）",
         "example": "The carpark is full. Let's try the one around the corner.",
         "example_cn": "停车场满了。我们去拐角那个试试。", "scene": "🚌 停车",
         "grammar": "主系表：is full；Let's...（建议句型）；around the corner（拐角处）",
         "sentence_words": [
             {"word": "full", "phonetic": "/fʊl/", "syllable": "full", "meaning": "adj. 满的；满员"},
             {"word": "around the corner", "phonetic": "/əˈraʊnd ðə ˈkɔːnər/", "syllable": "a·round the cor·ner", "meaning": "phrase. 在拐角处；即将到来"},
             {"word": "around", "phonetic": "/əˈraʊnd/", "syllable": "a·round", "meaning": "adv./prep. 在附近；围绕"},
             {"word": "carpark", "phonetic": "/ˈkɑːpɑːk/", "syllable": "car·park", "meaning": "n. 停车场"},
             {"word": "corner", "phonetic": "/ˈkɔːnər/", "syllable": "cor·ner", "meaning": "n. 拐角；角落"}
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
             {"word": "kiwis", "phonetic": "/ˈkiːwiːz/", "syllable": "ki·wis", "meaning": "n. 新西兰人（复数）"}
         ]},
        {"word": "heaps", "phonetic": "/hiːps/", "syllable": "heaps", "pos": "adv./n.",
         "meaning": "很多；大量（口语）",
         "example": "There were heaps of people at the market today.",
         "example_cn": "今天集市上人超多。", "scene": "🗣️ NZ口语",
         "grammar": "There be 句型（过去时）：There were...，表示存在；heaps of = lots of",
         "sentence_words": [
             {"word": "market", "phonetic": "/ˈmɑːkɪt/", "syllable": "mar·ket", "meaning": "n. 集市；市场"},
             {"word": "heaps of", "phonetic": "/hiːps ɒv/", "syllable": "heaps of", "meaning": "phrase. 大量的（NZ口语）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "heaps", "phonetic": "/hiːps/", "syllable": "heaps", "meaning": "adv. 大量；很多（NZ口语）"},
             {"word": "people", "phonetic": "/ˈpiːpl/", "syllable": "peo·ple", "meaning": "n. 人们"},
             {"word": "today", "phonetic": "/təˈdeɪ/", "syllable": "to·day", "meaning": "n. 今天"}
         ]},
        {"word": "sweet as", "phonetic": "/swiːt æz/", "syllable": "sweet as", "pos": "phrase",
         "meaning": "太好了；没问题（NZ经典口语）",
         "example": "Can you pick me up at 5? — Sweet as, no worries.",
         "example_cn": "5点能来接我吗？——没问题，放心。", "scene": "🗣️ NZ口语",
         "grammar": "对话回应句：Sweet as 作感叹语；no worries（没关系）是NZ万能回应",
         "sentence_words": [
             {"word": "pick up", "phonetic": "/pɪk ʌp/", "syllable": "pick up", "meaning": "v. 开车来接（短语动词）"},
             {"word": "no worries", "phonetic": "/nəʊ ˈwʌriz/", "syllable": "no wor·ries", "meaning": "phrase. 没问题；不客气（NZ口语）"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "sweet", "phonetic": "/swiːt/", "syllable": "sweet", "meaning": "adj. 太好了；没问题（NZ口语）"}
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
             {"word": "coffee", "phonetic": "/ˈkɒfi/", "syllable": "cof·fee", "meaning": "n. 咖啡"},
             {"word": "ta", "phonetic": "/tɑː/", "syllable": "ta", "meaning": "interj. 谢了！（口语）"}
         ]},
        {"word": "arvo", "phonetic": "/ɑːˈvəʊ/", "syllable": "ar · vo", "pos": "n.",
         "meaning": "下午（afternoon缩写）",
         "example": "Want to grab a coffee this arvo?",
         "example_cn": "今天下午想喝杯咖啡吗？", "scene": "🗣️ NZ口语",
         "grammar": "简短邀请句型：Want to do...?（想做...吗？）省略了主语 Do you",
         "sentence_words": [
             {"word": "grab a coffee", "phonetic": "/ɡræb ə ˈkɒfi/", "syllable": "grab a cof·fee", "meaning": "v. 去喝杯咖啡（口语）"},
             {"word": "arvo", "phonetic": "/ˈɑːvəʊ/", "syllable": "ar·vo", "meaning": "n. 下午（AU/NZ俚语）"},
             {"word": "coffee", "phonetic": "/ˈkɒfi/", "syllable": "cof·fee", "meaning": "n. 咖啡"},
             {"word": "grab", "phonetic": "/ɡræb/", "syllable": "grab", "meaning": "v. 拿；取（口语常用）"}
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
             {"word": "mate", "phonetic": "/meɪt/", "syllable": "mate", "meaning": "n. 伙计；哥们"}
         ]},
        {"word": "brekkie", "phonetic": "/ˈbreki/", "syllable": "brek · kie", "pos": "n.",
         "meaning": "早餐（breakfast缩写）",
         "example": "What do you want for brekkie? I'm making eggs.",
         "example_cn": "早餐想吃什么？我在煎鸡蛋。", "scene": "🗣️ NZ口语",
         "grammar": "疑问句：What do you want for...?；现在进行时：I'm making（正在做）",
         "sentence_words": [
             {"word": "making", "phonetic": "/ˈmeɪkɪŋ/", "syllable": "mak·ing", "meaning": "v. 制作；烹饪（现在分词）"},
             {"word": "eggs", "phonetic": "/eɡz/", "syllable": "eggs", "meaning": "n. 鸡蛋（复数）"},
             {"word": "brekkie", "phonetic": "/ˈbreki/", "syllable": "brek·kie", "meaning": "n. 早餐（AU/NZ俚语）"},
             {"word": "i'm", "phonetic": "/aɪm/", "syllable": "I'm", "meaning": "abbr. I am 的缩写"}
         ]},
        {"word": "reckon", "phonetic": "/ˈrekən/", "syllable": "reck · on", "pos": "v.",
         "meaning": "觉得；认为（口语）",
         "example": "I reckon it'll rain this afternoon.",
         "example_cn": "我觉得今天下午会下雨。", "scene": "🗣️ NZ口语",
         "grammar": "I reckon + 宾语从句（口语化的 I think）；it'll = it will，将来时预测",
         "sentence_words": [
             {"word": "it'll", "phonetic": "/ɪtl/", "syllable": "it'll", "meaning": "it will 的缩写，将来时"},
             {"word": "rain", "phonetic": "/reɪn/", "syllable": "rain", "meaning": "v. 下雨；n. 雨"},
             {"word": "reckon", "phonetic": "/ˈrekən/", "syllable": "reck·on", "meaning": "v. 认为；觉得（口语）"}
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
             {"word": "i'm", "phonetic": "/aɪm/", "syllable": "I'm", "meaning": "abbr. I am 的缩写"},
             {"word": "stoked", "phonetic": "/stəʊkt/", "syllable": "stoked", "meaning": "adj. 非常兴奋；超开心"}
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
             {"word": "weekend", "phonetic": "/ˌwiːkˈend/", "syllable": "week·end", "meaning": "n. 周末"}
         ]},
        {"word": "rate", "phonetic": "/reɪt/", "syllable": "rate", "pos": "n.",
         "meaning": "费率；税率（NZ有GST）",
         "example": "The GST rate in New Zealand is 15 percent.",
         "example_cn": "新西兰的消费税率是15%。", "scene": "🏦 税务/银行",
         "grammar": "主系表结构：The rate is + 数字，表示数值",
         "sentence_words": [
             {"word": "GST", "phonetic": "/ˌdʒiːesˈtiː/", "syllable": "G·S·T", "meaning": "n. 商品服务税（新西兰消费税）"},
             {"word": "percent", "phonetic": "/pəˈsent/", "syllable": "per·cent", "meaning": "n. 百分之..."},
             {"word": "rate", "phonetic": "/reɪt/", "syllable": "rate", "meaning": "n. 费率；比率"}
         ]},
        {"word": "power", "phonetic": "/ˈpaʊə/", "syllable": "pow · er", "pos": "n.",
         "meaning": "电；电力",
         "example": "The power bill this month is way higher than last month.",
         "example_cn": "这个月的电费比上个月高多了。", "scene": "🏠 生活缴费",
         "grammar": "比较级：higher than...（比...高）；way 加强比较级语气",
         "sentence_words": [
             {"word": "power bill", "phonetic": "/ˈpaʊər bɪl/", "syllable": "pow·er bill", "meaning": "n. 电费账单"},
             {"word": "way higher", "phonetic": "/weɪ ˈhaɪər/", "syllable": "way high·er", "meaning": "phrase. 高多了（way 加强比较级）"},
             {"word": "higher", "phonetic": "/ˈhaɪər/", "syllable": "high·er", "meaning": "adj. 更高的"}
         ]},
        {"word": "bach", "phonetic": "/bætʃ/", "syllable": "bach", "pos": "n.",
         "meaning": "度假小屋（NZ经典）",
         "example": "We're heading to our bach in Coromandel for the long weekend.",
         "example_cn": "长周末我们去Coromandel的度假屋。", "scene": "🏖️ 度假生活",
         "grammar": "现在进行时：We're heading to，表示即将出发的计划",
         "sentence_words": [
             {"word": "heading to", "phonetic": "/ˈhedɪŋ tuː/", "syllable": "head·ing to", "meaning": "v. 前往；出发去（口语）"},
             {"word": "long weekend", "phonetic": "/lɒŋ ˈwiːkend/", "syllable": "long week·end", "meaning": "n. 长周末（含公假）"},
             {"word": "weekend", "phonetic": "/ˌwiːkˈend/", "syllable": "week·end", "meaning": "n. 周末"}
         ]},
        {"word": "barbie", "phonetic": "/ˈbɑːbi/", "syllable": "bar · bie", "pos": "n.",
         "meaning": "烧烤（barbecue缩写）",
         "example": "Throw some sausages on the barbie, mate!",
         "example_cn": "放几根香肠上烤架，哥们！", "scene": "🍽️ 日常社交",
         "grammar": "祈使句：Throw...on...（把...放到...上）；mate 作感叹语",
         "sentence_words": [
             {"word": "throw", "phonetic": "/θrəʊ/", "syllable": "throw", "meaning": "v. 扔；放上去（口语）"},
             {"word": "sausages", "phonetic": "/ˈsɒsɪdʒɪz/", "syllable": "sau·sag·es", "meaning": "n. 香肠（复数）"},
             {"word": "mate", "phonetic": "/meɪt/", "syllable": "mate", "meaning": "n. 伙计；哥们"}
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
             {"word": "tramping", "phonetic": "/ˈtræmpɪŋ/", "syllable": "tramp·ing", "meaning": "n. 徒步旅行（NZ用法）"},
             {"word": "weekend", "phonetic": "/ˌwiːkˈend/", "syllable": "week·end", "meaning": "n. 周末"}
         ]},
        {"word": "plug", "phonetic": "/plʌɡ/", "syllable": "plug", "pos": "n./v.",
         "meaning": "插头；插上",
         "example": "Do I need an adapter for NZ power plugs?",
         "example_cn": "新西兰的插头需要转接器吗？", "scene": "🔌 日常生活",
         "grammar": "一般现在时疑问句：Do I need...?，询问是否有需要",
         "sentence_words": [
             {"word": "adapter", "phonetic": "/əˈdæptər/", "syllable": "a·dap·ter", "meaning": "n. 适配器；转接器"},
             {"word": "power plugs", "phonetic": "/ˈpaʊər plʌɡz/", "syllable": "pow·er plugs", "meaning": "n. 电源插头（复数）"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"}
         ]},
        {"word": "radiator", "phonetic": "/ˈreɪdieɪtə/", "syllable": "ra · di · a · tor", "pos": "n.",
         "meaning": "暖气片",
         "example": "NZ houses can get really cold. You'll need a good radiator.",
         "example_cn": "新西兰的房子会很冷。你需要一个靠谱的暖气片。", "scene": "🏠 日常生活",
         "grammar": "情态动词 can：can get cold（会变冷）；will need（将会需要）",
         "sentence_words": [
             {"word": "get cold", "phonetic": "/ɡet kəʊld/", "syllable": "get cold", "meaning": "v. 变冷（get + 形容词，表状态变化）"},
             {"word": "really", "phonetic": "/ˈrɪəli/", "syllable": "re·al·ly", "meaning": "adv. 真的；非常"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"}
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
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"}
         ]},
        {"word": "NCEA", "phonetic": "/ˈensiːeɪ/", "syllable": "N · C · E · A", "pos": "n.",
         "meaning": "新西兰国家教育证书",
         "example": "Most high school students in NZ work towards NCEA levels.",
         "example_cn": "新西兰大多数高中生都在读NCEA等级。", "scene": "🎓 学校教育",
         "grammar": "一般现在时：work towards（努力争取）+ 目标",
         "sentence_words": [
             {"word": "work towards", "phonetic": "/wɜːk təˈwɔːdz/", "syllable": "work to·wards", "meaning": "v. 努力争取；朝...努力"},
             {"word": "levels", "phonetic": "/ˈlevlz/", "syllable": "lev·els", "meaning": "n. 级别；等级（复数）"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"},
             {"word": "students", "phonetic": "/ˈstjuːdənts/", "syllable": "stu·dents", "meaning": "n. 学生（复数）"},
             {"word": "work", "phonetic": "/wɜːk/", "syllable": "work", "meaning": "n./v. 工作"}
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
             {"word": "i'm", "phonetic": "/aɪm/", "syllable": "I'm", "meaning": "abbr. I am 的缩写"}
         ]},
        {"word": "reference", "phonetic": "/ˈrefrəns/", "syllable": "ref · er · ence", "pos": "n.",
         "meaning": "推荐信；推荐人",
         "example": "Most employers here want at least two references.",
         "example_cn": "这里大多数雇主都要求至少两个推荐人。", "scene": "💼 求职",
         "grammar": "一般现在时（习惯）：want + 数量 + 名词；at least（至少）",
         "sentence_words": [
             {"word": "employers", "phonetic": "/ɪmˈplɔɪəz/", "syllable": "em·ploy·ers", "meaning": "n. 雇主（复数）"},
             {"word": "at least", "phonetic": "/æt liːst/", "syllable": "at least", "meaning": "adv. 至少"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "least", "phonetic": "/liːst/", "syllable": "least", "meaning": "n./adj. 最少；最小的"}
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
             {"word": "working", "phonetic": "/ˈwɜːkɪŋ/", "syllable": "work·ing", "meaning": "v. 工作（现在分词/动名词）"}
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

        # ---- 餐饮/咖啡 ----
        {"word": "flat white", "phonetic": "/flæt waɪt/", "syllable": "flat white", "pos": "n.",
         "meaning": "馥芮白（NZ特产咖啡）",
         "example": "I'll have a flat white, please. Extra hot.",
         "example_cn": "我要一杯馥芮白，少冰/热一点。", "scene": "☕ 咖啡店",
         "grammar": "一般将来时：will have（将要喝）；extra hot（额外热 = 少冰 NZ说法）",
         "sentence_words": [
             {"word": "extra hot", "phonetic": "/ˈekstrə hɒt/", "syllable": "ex·tra hot", "meaning": "phrase. 热一点；少冰（NZ咖啡用语）"},
             {"word": "flat white", "phonetic": "/flæt waɪt/", "syllable": "flat white", "meaning": "n. 馥芮白（NZ咖啡名）"},
             {"word": "please", "phonetic": "/pliːz/", "syllable": "please", "meaning": "int. 请（礼貌用语）"}
         ]},
        {"word": "takeaway", "phonetic": "/ˈteɪkəweɪ/", "syllable": "take · a · way", "pos": "n.",
         "meaning": "外卖；外带食物",
         "example": "Let's get some takeaway for dinner tonight.",
         "example_cn": "今晚我们点外卖吧。", "scene": "🍽️ 外卖",
         "grammar": "let's = let us 的缩写，表示建议；for dinner（晚餐）",
         "sentence_words": [
             {"word": "dinner", "phonetic": "/ˈdɪnər/", "syllable": "din·ner", "meaning": "n. 晚餐；正餐"},
             {"word": "tonight", "phonetic": "/təˈnaɪt/", "syllable": "to·night", "meaning": "n./adv. 今晚"},
             {"word": "takeaway", "phonetic": "/ˈteɪkəweɪ/", "syllable": "take·a·way", "meaning": "n. 外卖；外带"}
         ]},
        {"word": "brew", "phonetic": "/bruː/", "syllable": "brew", "pos": "n.",
         "meaning": "一杯咖啡（咖啡店用语）",
         "example": "What can I get you? — Just a brew, thanks.",
         "example_cn": "您要什么？——一杯咖啡就行，谢谢。", "scene": "☕ 咖啡店",
         "grammar": "简略回答：Just a brew = I'll have a brew；thanks = thank you",
         "sentence_words": [
             {"word": "brew", "phonetic": "/bruː/", "syllable": "brew", "meaning": "n. 一杯咖啡（NZ俚语）"},
             {"word": "thanks", "phonetic": "/θæŋks/", "syllable": "thanks", "meaning": "int. 谢谢（= thank you）"}
         ]},

        # ---- 互联网/手机 ----
        {"word": "broadband", "phonetic": "/ˈbrɔːdbænd/", "syllable": "broad · band", "pos": "n.",
         "meaning": "宽带网络",
         "example": "How's the broadband speed at your place?",
         "example_cn": "你那里的网速怎么样？", "scene": "📶 宽带网络",
         "grammar": "How's = How is 的缩写；at your place（在你那里）",
         "sentence_words": [
             {"word": "speed", "phonetic": "/spiːd/", "syllable": "speed", "meaning": "n. 速度；速率"},
             {"word": "broadband", "phonetic": "/ˈbrɔːdbænd/", "syllable": "broad·band", "meaning": "n. 宽带"},
             {"word": "place", "phonetic": "/pleɪs/", "syllable": "place", "meaning": "n. 地方；住处"}
         ]},
        {"word": "prepay", "phonetic": "/ˈpriːpeɪ/", "syllable": "pre · pay", "pos": "n./v.",
         "meaning": "预付费手机套餐",
         "example": "I'm on prepay. It's cheaper if you don't use much data.",
         "example_cn": "我用的是预付费套餐。如果你流量用得不多，这个更划算。", "scene": "📱 手机套餐",
         "grammar": "be on prepay = 使用预付费套餐；比较句：cheaper if...",
         "sentence_words": [
             {"word": "data", "phonetic": "/ˈdeɪtə/", "syllable": "da·ta", "meaning": "n. 流量；数据"},
             {"word": "cheaper", "phonetic": "/ˈtʃiːpər/", "syllable": "cheap·er", "meaning": "adj. 更便宜的（cheap比较级）"},
             {"word": "prepay", "phonetic": "/ˈpriːpeɪ/", "syllable": "pre·pay", "meaning": "n. 预付费"}
         ]},

        # ---- 天气/自然 ----
        {"word": "forecast", "phonetic": "/ˈfɔːkɑːst/", "syllable": "fore · cast", "pos": "n./v.",
         "meaning": "天气预报",
         "example": "The forecast says it's going to pour this weekend.",
         "example_cn": "天气预报说这周末要下大雨。", "scene": "🌤️ 天气",
         "grammar": "一般现在时（客观陈述）：The forecast says（天气预报说）；be going to（将）",
         "sentence_words": [
             {"word": "pour", "phonetic": "/pɔːr/", "syllable": "pour", "meaning": "v. 倾盆大雨；倒（水）"},
             {"word": "weekend", "phonetic": "/ˌwiːkˈend/", "syllable": "week·end", "meaning": "n. 周末"},
             {"word": "forecast", "phonetic": "/ˈfɔːkɑːst/", "syllable": "fore·cast", "meaning": "n. 天气预报"}
         ]},
        {"word": "sunny", "phonetic": "/ˈsʌni/", "syllable": "sun · ny", "pos": "adj.",
         "meaning": "晴天；阳光明媚",
         "example": "It's a beautiful sunny day. Let's go to the beach!",
         "example_cn": "今天阳光明媚，我们去海滩吧！", "scene": "🌤️ 天气",
         "grammar": "主系表：It's + adj. + n.；感叹句：Let's do...（让我们做...）",
         "sentence_words": [
             {"word": "beautiful", "phonetic": "/ˈbjuːtɪfl/", "syllable": "beau·ti·ful", "meaning": "adj. 美丽的；美好的"},
             {"word": "beach", "phonetic": "/biːtʃ/", "syllable": "beach", "meaning": "n. 海滩；沙滩"},
             {"word": "sunny", "phonetic": "/ˈsʌni/", "syllable": "sun·ny", "meaning": "adj. 晴朗的；阳光明媚的"}
         ]},

        # ---- 社区/邻居 ----
        {"word": "neighbour", "phonetic": "/ˈneɪbə/", "syllable": "neigh · bour", "pos": "n.",
         "meaning": "邻居",
         "example": "Our neighbour brought over a plate of cookies.",
         "example_cn": "我们邻居送了一盘饼干过来。", "scene": "👥 邻里",
         "grammar": "一般过去时：brought（bring的过去式）；brought over（送过来）",
         "sentence_words": [
             {"word": "brought over", "phonetic": "/brɔːt ˈəʊvər/", "syllable": "brought o·ver", "meaning": "v. 送过来（bring over的过去式）"},
             {"word": "plate", "phonetic": "/pleɪt/", "syllable": "plate", "meaning": "n. 盘子；一盘"},
             {"word": "cookies", "phonetic": "/ˈkʊkiz/", "syllable": "cook·ies", "meaning": "n. 饼干；曲奇（复数）"},
             {"word": "neighbour", "phonetic": "/ˈneɪbə/", "syllable": "neigh·bour", "meaning": "n. 邻居"}
         ]},
        {"word": "community", "phonetic": "/kəˈmjuːnəti/", "syllable": "com · mu · ni · ty", "pos": "n.",
         "meaning": "社区；群体",
         "example": "There's a great sense of community in this neighbourhood.",
         "example_cn": "这个社区的归属感很强。", "scene": "🏘️ 社区",
         "grammar": "There be 句型：There's a...；sense of community（社区归属感）",
         "sentence_words": [
             {"word": "neighbourhood", "phonetic": "/ˈneɪbəhʊd/", "syllable": "neigh·bour·hood", "meaning": "n. 社区；街道"},
             {"word": "community", "phonetic": "/kəˈmjuːnəti/", "syllable": "com·mu·ni·ty", "meaning": "n. 社区；共同体"}
         ]},

        # ---- 健身/休闲 ----
        {"word": "gym", "phonetic": "/dʒɪm/", "syllable": "gym", "pos": "n.",
         "meaning": "健身房",
         "example": "I signed up for the gym near my flat.",
         "example_cn": "我在住的附近办了健身卡。", "scene": "🏋️ 健身",
         "grammar": "一般过去时：signed up（报名）；near my flat（我公寓附近）",
         "sentence_words": [
             {"word": "signed up", "phonetic": "/saɪnd ʌp/", "syllable": "signed up", "meaning": "v. 报名；注册（sign up的过去式）"},
             {"word": "near", "phonetic": "/nɪər/", "syllable": "near", "meaning": "prep. 在...附近"},
             {"word": "gym", "phonetic": "/dʒɪm/", "syllable": "gym", "meaning": "n. 健身房"}
         ]},
        {"word": "trail", "phonetic": "/treɪl/", "syllable": "trail", "pos": "n.",
         "meaning": "徒步道；山间小路",
         "example": "There are some amazing trails up in the hills.",
         "example_cn": "山里有一些超棒的徒步道。", "scene": "🥾 徒步",
         "grammar": "There be 句型（复数）：There are...；up in the hills（山里面）",
         "sentence_words": [
             {"word": "trails", "phonetic": "/treɪlz/", "syllable": "trails", "meaning": "n. 徒步道；小路（复数）"},
             {"word": "hills", "phonetic": "/hɪlz/", "syllable": "hills", "meaning": "n. 山丘；小山（复数）"},
             {"word": "trail", "phonetic": "/treɪl/", "syllable": "trail", "meaning": "n. 徒步道；山野小径"}
         ]},

        # ---- 学校/孩子 ----
        {"word": "enrol", "phonetic": "/ɪnˈrəʊl/", "syllable": "en · rol", "pos": "v.",
         "meaning": "注册；报名（课程）",
         "example": "You need to enrol your child before the school term starts.",
         "example_cn": "你需要在开学前给孩子报名注册。", "scene": "🏫 学校报名",
         "grammar": "need to + 动词原形：需要做某事；before + 时间状语",
         "sentence_words": [
             {"word": "child", "phonetic": "/tʃaɪld/", "syllable": "child", "meaning": "n. 孩子"},
             {"word": "term", "phonetic": "/tɜːm/", "syllable": "term", "meaning": "n. 学期"},
             {"word": "enrol", "phonetic": "/ɪnˈrəʊl/", "syllable": "en·rol", "meaning": "v. 注册；入学；报名"}
         ]},
        {"word": "uniform", "phonetic": "/ˈjuːnɪfɔːm/", "syllable": "uni · form", "pos": "n.",
         "meaning": "校服；制服",
         "example": "The kids need to wear a school uniform every day.",
         "example_cn": "孩子们每天都要穿校服。", "scene": "🏫 学校",
         "grammar": "need to + 动词原形；every day（每天）频率副词",
         "sentence_words": [
             {"word": "kids", "phonetic": "/kɪdz/", "syllable": "kids", "meaning": "n. 孩子们（kid的复数，口语）"},
             {"word": "wear", "phonetic": "/weər/", "syllable": "wear", "meaning": "v. 穿（衣服）"},
             {"word": "uniform", "phonetic": "/ˈjuːnɪfɔːm/", "syllable": "u·ni·form", "meaning": "n. 校服；制服"}
         ]},

        # ---- 宠物 ----
        {"word": "vet", "phonetic": "/vet/", "syllable": "vet", "pos": "n.",
         "meaning": "兽医",
         "example": "My cat needs to see a vet. She's been off her food.",
         "example_cn": "我的猫要去看兽医。她这几天都不吃东西。", "scene": "🐱 宠物",
         "grammar": "needs to + 动词原形；现在完成进行时：has been doing（一直...）",
         "sentence_words": [
             {"word": "cat", "phonetic": "/kæt/", "syllable": "cat", "meaning": "n. 猫"},
             {"word": "off her food", "phonetic": "/ɒf hɜː fuːd/", "syllable": "off her food", "meaning": "phrase. 不吃东西；食欲不佳"},
             {"word": "vet", "phonetic": "/vet/", "syllable": "vet", "meaning": "n. 兽医"}
         ]},

        # ---- 紧急/报警 ----
        {"word": "emergency", "phonetic": "/ɪˈmɜːdʒənsi/", "syllable": "e · mer · gen · cy", "pos": "n.",
         "meaning": "紧急情况",
         "example": "In an emergency, call 111 straight away.",
         "example_cn": "遇到紧急情况，立刻拨打111。", "scene": "🚨 紧急电话",
         "grammar": "In an emergency（介词短语作状语）；call + 数字（打电话）",
         "sentence_words": [
             {"word": "emergency", "phonetic": "/ɪˈmɜːdʒənsi/", "syllable": "e·mer·gen·cy", "meaning": "n. 紧急情况；突发事件"},
             {"word": "straight away", "phonetic": "/streɪt əˈweɪ/", "syllable": "straight a·way", "meaning": "adv. 立刻；马上"}
         ]},

        # ---- 护照/身份 ----
        {"word": "passport", "phonetic": "/ˈpɑːspɔːt/", "syllable": "pass · port", "pos": "n.",
         "meaning": "护照",
         "example": "Make sure your passport is valid for at least six months.",
         "example_cn": "确保你的护照有效期至少还有六个月。", "scene": "🛂 护照",
         "grammar": "Make sure + 从句（确保...）；for at least six months（至少六个月）",
         "sentence_words": [
             {"word": "valid", "phonetic": "/ˈvælɪd/", "syllable": "val·id", "meaning": "adj. 有效的"},
             {"word": "passport", "phonetic": "/ˈpɑːspɔːt/", "syllable": "pass·port", "meaning": "n. 护照"},
             {"word": "months", "phonetic": "/mʌnθs/", "syllable": "months", "meaning": "n. 月（month的复数）"}
         ]},

        # ---- 购物/折扣 ----
        {"word": "refund", "phonetic": "/ˈriːfʌnd/", "syllable": "re · fund", "pos": "n./v.",
         "meaning": "退款；退换",
         "example": "Can I get a refund if the item doesn't fit?",
         "example_cn": "如果东西不合身，我可以退款吗？", "scene": "🛍️ 购物退换",
         "grammar": "一般疑问句：Can I...?；if 条件句（如果...）",
         "sentence_words": [
             {"word": "item", "phonetic": "/ˈaɪtəm/", "syllable": "i·tem", "meaning": "n. 商品；物品"},
             {"word": "fit", "phonetic": "/fɪt/", "syllable": "fit", "meaning": "v. 合适；合身"},
             {"word": "refund", "phonetic": "/ˈriːfʌnd/", "syllable": "re·fund", "meaning": "n. 退款；v. 退款"}
         ]},
        {"word": "bargain", "phonetic": "/ˈbɑːɡɪn/", "syllable": "bar · gain", "pos": "n.",
         "meaning": "便宜货；特价商品",
         "example": "These shoes are a real bargain at that price.",
         "example_cn": "这个价格的鞋子真的很划算。", "scene": "🛍️ 购物",
         "grammar": "主系表：are + a real bargain（是很划算的买卖）；at that price（那个价格）",
         "sentence_words": [
             {"word": "shoes", "phonetic": "/ʃuːz/", "syllable": "shoes", "meaning": "n. 鞋子（shoe的复数）"},
             {"word": "bargain", "phonetic": "/ˈbɑːɡɪn/", "syllable": "bar·gain", "meaning": "n. 便宜货；特价品"},
             {"word": "price", "phonetic": "/praɪs/", "syllable": "price", "meaning": "n. 价格"}
         ]},
        {"word": "secondhand", "phonetic": "/ˌsekəndˈhænd/", "syllable": "sec · ond · hand", "pos": "adj.",
         "meaning": "二手的",
         "example": "I got this bike secondhand. It was really cheap.",
         "example_cn": "这辆自行车是二手买的，真的很便宜。", "scene": "🛍️ 二手购物",
         "grammar": "一般过去时：got（买，get的过去式）；It was + adj.（过去状态）",
         "sentence_words": [
             {"word": "bike", "phonetic": "/baɪk/", "syllable": "bike", "meaning": "n. 自行车"},
             {"word": "cheap", "phonetic": "/tʃiːp/", "syllable": "cheap", "meaning": "adj. 便宜的"},
             {"word": "secondhand", "phonetic": "/ˌsekəndˈhænd/", "syllable": "sec·ond·hand", "meaning": "adj. 二手的；用过的"}
         ]},

        # ---- NZ职场 ----
        {"word": "hourly rate", "phonetic": "/ˈaʊəli reɪt/", "syllable": "hour · ly rate", "pos": "n.",
         "meaning": "时薪",
         "example": "What's the hourly rate for this job?",
         "example_cn": "这份工作的时薪是多少？", "scene": "💼 薪资",
         "grammar": "What + be动词 + the + n.?（提问）；What's = What is",
         "sentence_words": [
             {"word": "hourly", "phonetic": "/ˈaʊəli/", "syllable": "hour·ly", "meaning": "adj. 每小时的"},
             {"word": "rate", "phonetic": "/reɪt/", "syllable": "rate", "meaning": "n. 比率；工资标准"},
             {"word": "job", "phonetic": "/dʒɒb/", "syllable": "job", "meaning": "n. 工作；岗位"}
         ]},
        {"word": "shift", "phonetic": "/ʃɪft/", "syllable": "shift", "pos": "n.",
         "meaning": "班次；轮班",
         "example": "I'm on the early shift this week. It starts at 6am.",
         "example_cn": "这周我上早班，6点开始。", "scene": "💼 上班",
         "grammar": "be on + n.（在...班次）；一般现在时（固定日程）",
         "sentence_words": [
             {"word": "shift", "phonetic": "/ʃɪft/", "syllable": "shift", "meaning": "n. 班次；轮班"},
             {"word": "early shift", "phonetic": "/ˈɜːli ʃɪft/", "syllable": "ear·ly shift", "meaning": "n. 早班"},
             {"word": "starts", "phonetic": "/stɑːts/", "syllable": "starts", "meaning": "v. 开始（第三人称单数）"}
         ]},
        {"word": "overtime", "phonetic": "/ˈəʊvətaɪm/", "syllable": "o · ver · time", "pos": "n.",
         "meaning": "加班",
         "example": "We get paid extra for overtime work.",
         "example_cn": "加班有额外工资。", "scene": "💼 薪资",
         "grammar": "被动语态：get paid（被支付）；extra for（额外获得...）",
         "sentence_words": [
             {"word": "overtime", "phonetic": "/ˈəʊvətaɪm/", "syllable": "o·ver·time", "meaning": "n. 加班；超时"}
         ]},

        # ---- 移民/签证 ----
        {"word": "citizenship", "phonetic": "/ˈsɪtɪzənʃɪp/", "syllable": "cit · i · zen · ship", "pos": "n.",
         "meaning": "公民身份；国籍",
         "example": "After living here for five years, you can apply for citizenship.",
         "example_cn": "在这里住满五年后，你可以申请入籍。", "scene": "🛂 移民",
         "grammar": "After + 动名词/时间名词（...之后）；can + 动词原形（可以）",
         "sentence_words": [
             {"word": "citizenship", "phonetic": "/ˈsɪtɪzənʃɪp/", "syllable": "cit·i·zen·ship", "meaning": "n. 公民身份；国籍"}
         ]},
        {"word": "resident", "phonetic": "/ˈrezɪdənt/", "syllable": "res · i · dent", "pos": "n.",
         "meaning": "居民",
         "example": "As a permanent resident, you have most of the same rights as a citizen.",
         "example_cn": "作为永久居民，你享有和公民几乎同等的权利。", "scene": "🛂 签证",
         "grammar": "As + 身份（作为...）；the same...as（和...一样）",
         "sentence_words": [
             {"word": "permanent", "phonetic": "/ˈpɜːmənənt/", "syllable": "per·ma·nent", "meaning": "adj. 永久的；长期的"},
             {"word": "resident", "phonetic": "/ˈrezɪdənt/", "syllable": "res·i·dent", "meaning": "n. 居民；住户"}
         ]},
        {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi · sa", "pos": "n.",
         "meaning": "签证",
         "example": "Your student visa allows you to work up to 20 hours per week.",
         "example_cn": "你的学生签证允许你每周工作最多20小时。", "scene": "🛂 签证",
         "grammar": "一般现在时（规定）；allow + sb. + to do（允许某人做）",
         "sentence_words": [
             {"word": "student visa", "phonetic": "/ˈstjuːdnt ˈviːzə/", "syllable": "stu·dent vi·sa", "meaning": "n. 学生签证"},
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"}
         ]},

        # ---- NZ生活其他 ----
        {"word": "chur", "phonetic": "/tʃɜː/", "syllable": "chur", "pos": "int.",
         "meaning": "谢谢（NZ特有俚语）",
         "example": "Chur, bro! That was a sick wave!",
         "example_cn": "谢啦兄弟！那个冲浪太帅了！", "scene": "🗣️ NZ俚语",
         "grammar": "感叹句；bro（brother的缩写，NZ口语）；sick（太棒了，slang）",
         "sentence_words": [
             {"word": "chur", "phonetic": "/tʃɜːr/", "syllable": "chur", "meaning": "int. 谢谢（NZ毛利语来源俚语）"},
             {"word": "bro", "phonetic": "/brəʊ/", "syllable": "bro", "meaning": "n. 兄弟；伙计（brother的口语缩写）"},
             {"word": "sick", "phonetic": "/sɪk/", "syllable": "sick", "meaning": "adj. 太棒了（NZ俚语，正面意思）"}
         ]},
        {"word": "choice", "phonetic": "/tʃɔɪs/", "syllable": "choice", "pos": "adj.",
         "meaning": "太棒了；绝妙（NZ俚语）",
         "example": "That fish and chips was choice, mate!",
         "example_cn": "那个炸鱼薯条太绝了老兄！", "scene": "🗣️ NZ口语",
         "grammar": "名词作形容词用（NZ特有用法）；mate（伙计，NZ常用）",
         "sentence_words": [
             {"word": "choice", "phonetic": "/tʃɔɪs/", "syllable": "choice", "meaning": "adj. 太棒了（NZ俚语）"}
         ]},
        {"word": "keen", "phonetic": "/kiːn/", "syllable": "keen", "pos": "adj.",
         "meaning": "想；想要（NZ口语 = want）",
         "example": "Are you keen for a drink after work?",
         "example_cn": "下班后想喝一杯吗？", "scene": "🗣️ NZ口语",
         "grammar": "be keen for = 想/要（keen = want 的NZ用法）；after work（下班后）",
         "sentence_words": [
             {"word": "keen", "phonetic": "/kiːn/", "syllable": "keen", "meaning": "adj. 想；要（NZ口语=want）"}
         ]},
        {"word": "fridge", "phonetic": "/frɪdʒ/", "syllable": "fridge", "pos": "n.",
         "meaning": "冰箱（NZ/英式）",
         "example": "The milk's in the fridge. Help yourself.",
         "example_cn": "牛奶在冰箱里，随便喝。", "scene": "🏠 日常",
         "grammar": "主系表：The milk's = The milk is；Help yourself（随便用）",
         "sentence_words": [
             {"word": "fridge", "phonetic": "/frɪdʒ/", "syllable": "fridge", "meaning": "n. 冰箱（英/NZ用法）"}
         ]},
        {"word": "sparky", "phonetic": "/ˈspɑːki/", "syllable": "spar · ky", "pos": "n.",
         "meaning": "电工（NZ口语）",
         "example": "We need to call a sparky. The power's not working.",
         "example_cn": "得叫个电工了，电不通了。", "scene": "🔧 维修",
         "grammar": "need to + 动词原形；The power's not working（电不工作了）",
         "sentence_words": [
             {"word": "sparky", "phonetic": "/ˈspɑːki/", "syllable": "spar·ky", "meaning": "n. 电工（NZ俚语）"}
         ]},
        {"word": "scroggin", "phonetic": "/ˈskrɒɡɪn/", "syllable": "scrog · gin", "pos": "n.",
         "meaning": "能量棒；坚果干果混合零食",
         "example": "I always pack some scroggin for the hike.",
         "example_cn": "徒步的时候我总会带一些能量棒零食。", "scene": "🥾 徒步/零食",
         "grammar": "一般现在时（习惯）；pack some（打包一些）；for the hike（为了徒步）",
         "sentence_words": [
             {"word": "scroggin", "phonetic": "/ˈskrɒɡɪn/", "syllable": "scrog·gin", "meaning": "n. 能量坚果混合零食（NZ特有）"}
         ]},
        {"word": "recycle", "phonetic": "/rɪˈsaɪkl/", "syllable": "re · cy · cle", "pos": "v.",
         "meaning": "回收利用；垃圾分类",
         "example": "Remember to put the glass bottles in the recycle bin.",
         "example_cn": "记得把玻璃瓶放进回收桶。", "scene": "♻️ 环保",
         "grammar": "remember to + 动词原形（记得做...）；put...in（把...放进）",
         "sentence_words": [
             {"word": "recycle", "phonetic": "/rɪˈsaɪkl/", "syllable": "re·cy·cle", "meaning": "v. 回收利用；垃圾分类"}
         ]},

        # ---- 扩充词汇 ----
        {"word": "she'll be right", "phonetic": "/\u0283i\u02d0l bi ra\u026at/", "syllable": "she'll be right", "pos": "phrase",
         "meaning": "\u6ca1\u4e8b\u7684\uff1b\u4f1a\u597d\u7684\uff08NZ\u7ecf\u5178\u53e3\u8bed\uff09",
         "example": "Don't stress about the exam, she'll be right.", "example_cn": "\u522b\u4e3a\u8003\u8bd5\u7126\u8651\uff0c\u6ca1\u4e8b\u7684\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u53e3\u8bed\u7701\u7565\u53e5",
         "sentence_words": [
             {"word": "stress", "phonetic": "/stres/", "syllable": "stress", "meaning": "v. \u7126\u8651\uff1b\u7d27\u5f20"},
             {"word": "exam", "phonetic": "/\u026a\u0261\u02c8z\u00e6m/", "syllable": "ex\u00b7am", "meaning": "n. \u8003\u8bd5"}
         ]},
        {"word": "yeah nah", "phonetic": "/je\u0259 n\u0251\u02d0/", "syllable": "yeah nah", "pos": "phrase",
         "meaning": "\u4e0d\uff1b\u4e0d\u592a\u786e\u5b9a\uff08NZ\u77db\u76fe\u8868\u8fbe\uff0c\u5b9e\u9645\u5426\u5b9a\uff09",
         "example": "Are you keen to come? Yeah nah, I'm pretty tired tonight.", "example_cn": "\u4f60\u60f3\u6765\u5417\uff1f\u7b97\u4e86\u5427\uff0c\u4eca\u665a\u633a\u7d2f\u7684\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "yeah nah = polite no",
         "sentence_words": [
             {"word": "keen", "phonetic": "/ki\u02d0n/", "syllable": "keen", "meaning": "adj. \u6709\u5174\u8da3\u7684"},
             {"word": "tired", "phonetic": "/ta\u026a\u0259d/", "syllable": "tired", "meaning": "adj. \u7d2f\u7684"}
         ]},
        {"word": "hard case", "phonetic": "/h\u0251\u02d0d ke\u026as/", "syllable": "hard case", "pos": "n.",
         "meaning": "\u6709\u8da3\u7684\u4eba\uff1b\u641e\u7b11\u7684\u4eba\uff08NZ\u53e3\u8bed\uff09",
         "example": "Dave's a hard case, he always cracks everyone up.", "example_cn": "Dave\u8fd9\u4eba\u8d85\u641e\u7b11\uff0c\u603b\u80fd\u8ba9\u6240\u6709\u4eba\u4e50\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u540d\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "cracks up", "phonetic": "/kr\u00e6ks \u028cp/", "syllable": "cracks up", "meaning": "v. \u8ba9\u4eba\u53d1\u7b11"}
         ]},
        {"word": "piece of piss", "phonetic": "/pi\u02d0s \u0259v p\u026as/", "syllable": "piece of piss", "pos": "phrase",
         "meaning": "\u5c0f\u83dc\u4e00\u789f\uff1b\u592a\u7b80\u5355\u4e86\uff08NZ\u53e3\u8bed\uff09",
         "example": "The test was a piece of piss, finished in ten minutes.", "example_cn": "\u90a3\u8003\u8bd5\u592a\u7b80\u5355\u4e86\uff0c\u5341\u5206\u949f\u641e\u5b9a\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u53e3\u8bed\u77ed\u8bed",
         "sentence_words": [
             {"word": "finished", "phonetic": "/\u02c8f\u026an\u026a\u0283t/", "syllable": "fin\u00b7ished", "meaning": "v. \u5b8c\u6210"},
             {"word": "test", "phonetic": "/test/", "syllable": "test", "meaning": "n. \u6d4b\u8bd5"}
         ]},
        {"word": "gutted", "phonetic": "/\u02c8\u0261\u028ct\u026ad/", "syllable": "gut\u00b7ted", "pos": "adj.",
         "meaning": "\u975e\u5e38\u5931\u671b\uff1b\u5d29\u6e83\uff08NZ/UK\u53e3\u8bed\uff09",
         "example": "I was absolutely gutted when they cancelled the game.", "example_cn": "\u4ed6\u4eec\u53d6\u6d88\u6bd4\u8d5b\u65f6\u6211\u7b80\u76f4\u5d29\u6e83\u4e86\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u5f62\u5bb9\u8bcd\u7528\u6cd5",
         "sentence_words": [
             {"word": "cancelled", "phonetic": "/\u02c8k\u00e6ns\u0259ld/", "syllable": "can\u00b7celled", "meaning": "v. \u53d6\u6d88"},
             {"word": "absolutely", "phonetic": "/\u02c8\u00e6bs\u0259lu\u02d0tli/", "syllable": "ab\u00b7so\u00b7lute\u00b7ly", "meaning": "adv. \u7edd\u5bf9\u5730"}
         ]},
        {"word": "piker", "phonetic": "/\u02c8pa\u026ak\u0259/", "syllable": "pi\u00b7ker", "pos": "n.",
         "meaning": "\u80c6\u5c0f\u9b3c\uff1b\u653e\u9e3d\u5b50\u7684\u4eba\uff08NZ\u53e3\u8bed\uff09",
         "example": "Don't be a piker, come to the party with us!", "example_cn": "\u522b\u505a\u80c6\u5c0f\u9b3c\uff0c\u8ddf\u6211\u4eec\u53bb\u6d3e\u5bf9\uff01", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "party", "phonetic": "/\u02c8p\u0251\u02d0ti/", "syllable": "par\u00b7ty", "meaning": "n. \u6d3e\u5bf9"}
         ]},
        {"word": "pull your socks up", "phonetic": "/p\u028al j\u0254\u02d0 s\u0252ks \u028cp/", "syllable": "pull your socks up", "pos": "phrase",
         "meaning": "\u632f\u4f5c\u8d77\u6765\uff1b\u52a0\u628a\u52b2",
         "example": "You need to pull your socks up if you want to pass this course.", "example_cn": "\u5982\u679c\u4f60\u8981\u8fc7\u8fd9\u95e8\u8bfe\uff0c\u5f97\u52a0\u628a\u52b2\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u7948\u4f7f\u53e5+\u6761\u4ef6\u53e5",
         "sentence_words": [
             {"word": "pass", "phonetic": "/p\u0251\u02d0s/", "syllable": "pass", "meaning": "v. \u901a\u8fc7"},
             {"word": "course", "phonetic": "/k\u0254\u02d0s/", "syllable": "course", "meaning": "n. \u8bfe\u7a0b"}
         ]},
        {"word": "munted", "phonetic": "/\u02c8m\u028cnt\u026ad/", "syllable": "mun\u00b7ted", "pos": "adj.",
         "meaning": "\u574f\u6389\u7684\uff1b\u641e\u7838\u7684\uff08NZ\u53e3\u8bed\uff09",
         "example": "My phone screen is completely munted after dropping it.", "example_cn": "\u624b\u673a\u6454\u4e86\u540e\u5c4f\u5e55\u5f7b\u5e95\u788e\u4e86\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "is munted = is broken",
         "sentence_words": [
             {"word": "screen", "phonetic": "/skri\u02d0n/", "syllable": "screen", "meaning": "n. \u5c4f\u5e55"},
             {"word": "dropping", "phonetic": "/\u02c8dr\u0252p\u026a\u014b/", "syllable": "drop\u00b7ping", "meaning": "v. \u6389\u843d"}
         ]},
        {"word": "wop-wops", "phonetic": "/w\u0252p w\u0252ps/", "syllable": "wop-wops", "pos": "n.",
         "meaning": "\u504f\u50fb\u4e61\u4e0b\uff08NZ\u53e3\u8bed\uff09",
         "example": "They bought a house out in the wop-wops.", "example_cn": "\u4ed6\u4eec\u5728\u5f88\u504f\u7684\u4e61\u4e0b\u4e70\u4e86\u623f\u5b50\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u4ecb\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "countryside", "phonetic": "/\u02c8k\u028cntrisa\u026ad/", "syllable": "coun\u00b7try\u00b7side", "meaning": "n. \u4e61\u4e0b"}
         ]},
        {"word": "togs", "phonetic": "/t\u0252\u0261z/", "syllable": "togs", "pos": "n.",
         "meaning": "\u6cf3\u8863\uff08NZ/AU\u53e3\u8bed\uff09",
         "example": "Don't forget to bring your togs to the beach.", "example_cn": "\u53bb\u6d77\u8fb9\u522b\u5fd8\u4e86\u5e26\u6cf3\u8863\u3002", "scene": "\ud83c\udfd6\ufe0f \u5ea6\u5047",
         "grammar": "\u540d\u8bcd\u590d\u6570",
         "sentence_words": [
             {"word": "beach", "phonetic": "/bi\u02d0t\u0283/", "syllable": "beach", "meaning": "n. \u6d77\u6ee9"}
         ]},
        {"word": "chilly bin", "phonetic": "/\u02c8t\u0283\u026ali b\u026an/", "syllable": "chil\u00b7ly bin", "pos": "n.",
         "meaning": "\u4fdd\u6e29\u7bb1\uff1b\u51b0\u76d2\uff08NZ\u7279\u6709\uff09",
         "example": "Grab the chilly bin, we're having a BBQ.", "example_cn": "\u62ff\u4e0a\u4fdd\u6e29\u7bb1\uff0c\u6211\u4eec\u53bb\u70e7\u70e4\u3002", "scene": "\ud83c\udfd6\ufe0f \u5ea6\u5047\u751f\u6d3b",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "BBQ", "phonetic": "/\u02ccbi\u02d0bi\u02d0\u02c8kju\u02d0/", "syllable": "B-B-Q", "meaning": "n. \u70e7\u70e4"}
         ]},
        {"word": "L&P", "phonetic": "/el \u0259nd pi\u02d0/", "syllable": "L and P", "pos": "n.",
         "meaning": "Lemon & Paeroa\uff08NZ\u56fd\u6c11\u996e\u6599\uff09",
         "example": "You haven't tried L&P? It's a classic Kiwi drink.", "example_cn": "\u4f60\u6ca1\u8bd5\u8fc7L&P\uff1f\u90a3\u662f\u65b0\u897f\u5170\u7ecf\u5178\u996e\u6599\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u53cd\u95ee\u53e5",
         "sentence_words": [
             {"word": "classic", "phonetic": "/\u02c8kl\u00e6s\u026ak/", "syllable": "clas\u00b7sic", "meaning": "adj. \u7ecf\u5178\u7684"}
         ]},
        {"word": "banger", "phonetic": "/\u02c8b\u00e6\u014b\u0259/", "syllable": "ban\u00b7ger", "pos": "n.",
         "meaning": "\u8d85\u68d2\u7684\u6b4c\u66f2/\u7535\u5f71\uff08\u53e3\u8bed\uff09",
         "example": "That new song by Six60 is an absolute banger.", "example_cn": "Six60\u90a3\u9996\u65b0\u6b4c\u7edd\u4e86\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u540d\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "absolute", "phonetic": "/\u02c8\u00e6bs\u0259lu\u02d0t/", "syllable": "ab\u00b7so\u00b7lute", "meaning": "adj. \u7edd\u5bf9\u7684"}
         ]},
        {"word": "smoko", "phonetic": "/\u02c8sm\u0259\u028ak\u0259\u028a/", "syllable": "smo\u00b7ko", "pos": "n.",
         "meaning": "\u5de5\u95f4\u4f11\u606f\uff1b\u8336\u6b47\uff08NZ\u84dd\u9886\u5e38\u7528\uff09",
         "example": "Let's have a smoko \u2014 I'm knackered.", "example_cn": "\u6b47\u4f1a\u513f\u5427\u2014\u2014\u6211\u7d2f\u6b7b\u4e86\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "let's+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "knackered", "phonetic": "/\u02c8n\u00e6k\u0259d/", "syllable": "knack\u00b7ered", "meaning": "adj. \u7d2f\u574f\u4e86\u7684"}
         ]},
        {"word": "op shop", "phonetic": "/\u0252p \u0283\u0252p/", "syllable": "op shop", "pos": "n.",
         "meaning": "\u4e8c\u624b\u6148\u5584\u5546\u5e97",
         "example": "I found this cool jacket at the op shop for only $15.", "example_cn": "\u6211\u5728\u4e8c\u624b\u5e97\u627e\u5230\u8fd9\u4ef6\u5916\u5957\uff0c\u624d15\u5757\u3002", "scene": "\ud83d\udecd\ufe0f \u4e8c\u624b\u8d2d\u7269",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "jacket", "phonetic": "/\u02c8d\u0292\u00e6k\u026at/", "syllable": "jack\u00b7et", "meaning": "n. \u5916\u5957"}
         ]},
        {"word": "docket", "phonetic": "/\u02c8d\u0252k\u026at/", "syllable": "dock\u00b7et", "pos": "n.",
         "meaning": "\u5c0f\u7968\uff1b\u6536\u636e\uff08NZ\u53e3\u8bed\uff09",
         "example": "Keep your docket in case you need to return it.", "example_cn": "\u7559\u7740\u5c0f\u7968\uff0c\u4e07\u4e00\u8981\u9000\u8d27\u3002", "scene": "\ud83d\udecd\ufe0f \u8d2d\u7269\u9000\u6362",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "return", "phonetic": "/r\u026a\u02c8t\u025c\u02d0n/", "syllable": "re\u00b7turn", "meaning": "v. \u9000\u8d27"}
         ]},
        {"word": "lolly", "phonetic": "/\u02c8l\u0252li/", "syllable": "lol\u00b7ly", "pos": "n.",
         "meaning": "\u7cd6\u679c\uff08NZ/AU\u7528\u6cd5\uff09",
         "example": "The kids always want lollies when we go to the dairy.", "example_cn": "\u6bcf\u6b21\u53bb\u4fbf\u5229\u5e97\u5b69\u5b50\u4eec\u90fd\u60f3\u8981\u7cd6\u679c\u3002", "scene": "\ud83c\udfea \u8d85\u5e02",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "kids", "phonetic": "/k\u026adz/", "syllable": "kids", "meaning": "n. \u5b69\u5b50\u4eec"}
         ]},
        {"word": "pottle", "phonetic": "/\u02c8p\u0252t\u0259l/", "syllable": "pot\u00b7tle", "pos": "n.",
         "meaning": "\u5c0f\u5bb9\u5668\uff1b\u5c0f\u5305\u88c5\uff08NZ\u91cf\u8bcd\uff09",
         "example": "Can I get a pottle of sour cream, please?", "example_cn": "\u8bf7\u7ed9\u6211\u4e00\u5c0f\u76d2\u9178\u5976\u6cb9\u3002", "scene": "\ud83c\udfea \u8d85\u5e02",
         "grammar": "\u793c\u8c8c\u7528\u8bed",
         "sentence_words": [
             {"word": "sour cream", "phonetic": "/sa\u028a\u0259 kri\u02d0m/", "syllable": "sour cream", "meaning": "n. \u9178\u5976\u6cb9"}
         ]},
        {"word": "sausage sizzle", "phonetic": "/\u02c8s\u0252s\u026ad\u0292 \u02c8s\u026az\u0259l/", "syllable": "sau\u00b7sage siz\u00b7zle", "pos": "n.",
         "meaning": "\u9999\u80a0\u70e7\u70e4\u4e49\u5356\uff08NZ\u793e\u533a\u6d3b\u52a8\uff09",
         "example": "There's a sausage sizzle outside the warehouse this Saturday.", "example_cn": "\u8fd9\u5468\u516dWarehouse\u95e8\u53e3\u6709\u9999\u80a0\u70e7\u70e4\u4e49\u5356\u3002", "scene": "\ud83e\udd7e \u5f92\u6b65",
         "grammar": "there be",
         "sentence_words": [
             {"word": "fundraising", "phonetic": "/f\u028cnd\u02c8re\u026az\u026a\u014b/", "syllable": "fund\u00b7rais\u00b7ing", "meaning": "n. \u7b79\u6b3e"}
         ]},
        {"word": "pie", "phonetic": "/pa\u026a/", "syllable": "pie", "pos": "n.",
         "meaning": "\u8089\u6d3e\uff08NZ\u56fd\u6c11\u5c0f\u5403\uff09",
         "example": "Grab a pie and a coffee for lunch.", "example_cn": "\u5348\u9910\u4e70\u4e2a\u8089\u6d3e\u548c\u5496\u5561\u3002", "scene": "\ud83c\udf7d\ufe0f \u5916\u5356",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "quick and easy", "phonetic": "/kw\u026ak \u00e6nd \u02c8i\u02d0zi/", "syllable": "quick and ea\u00b7sy", "meaning": "phrase \u5feb\u6377\u65b9\u4fbf"}
         ]},
        {"word": "hot chips", "phonetic": "/h\u0252t t\u0283\u026aps/", "syllable": "hot chips", "pos": "n.",
         "meaning": "\u70b8\u85af\u6761\uff08NZ\u53e3\u8bed\uff09",
         "example": "Nothing beats hot chips on the beach after a swim.", "example_cn": "\u6e38\u5b8c\u6cf3\u5728\u6d77\u8fb9\u5403\u70ed\u85af\u6761\uff0c\u6ca1\u6709\u6bd4\u8fd9\u66f4\u723d\u7684\u3002", "scene": "\ud83c\udfd6\ufe0f \u5ea6\u5047",
         "grammar": "nothing beats",
         "sentence_words": [
             {"word": "beats", "phonetic": "/bi\u02d0ts/", "syllable": "beats", "meaning": "v. \u80dc\u8fc7"},
             {"word": "swim", "phonetic": "/sw\u026am/", "syllable": "swim", "meaning": "n. \u6e38\u6cf3"}
         ]},
        {"word": "pavlova", "phonetic": "/p\u00e6v\u02c8l\u0259\u028av\u0259/", "syllable": "pav\u00b7lo\u00b7va", "pos": "n.",
         "meaning": "\u5e15\u8299\u6d1b\u5a03\u86cb\u7cd5\uff08NZ\u7ecf\u5178\u751c\u70b9\uff09",
         "example": "Mum made a pavlova for Christmas dessert.", "example_cn": "\u5988\u5988\u505a\u4e86\u5e15\u8299\u6d1b\u5a03\u5f53\u5723\u8bde\u751c\u70b9\u3002", "scene": "\ud83c\udf7d\ufe0f \u5916\u5356",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "dessert", "phonetic": "/d\u026a\u02c8z\u025c\u02d0t/", "syllable": "des\u00b7sert", "meaning": "n. \u751c\u70b9"}
         ]},
        {"word": "hangi", "phonetic": "/\u02c8h\u028c\u014bi/", "syllable": "han\u00b7gi", "pos": "n.",
         "meaning": "\u6bdb\u5229\u5730\u7089\u6599\u7406",
         "example": "We went to a hangi on the marae \u2014 the food was amazing.", "example_cn": "\u6211\u4eec\u53bb\u6bdb\u5229\u4f1a\u5802\u5403\u5730\u7089\u6599\u7406\u2014\u2014\u592a\u7f8e\u5473\u4e86\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "marae", "phonetic": "/\u02c8m\u00e6re\u026a/", "syllable": "ma\u00b7rae", "meaning": "n. \u6bdb\u5229\u4f1a\u5802"}
         ]},
        {"word": "numpty", "phonetic": "/\u02c8n\u028cmpti/", "syllable": "num\u00b7pty", "pos": "n.",
         "meaning": "\u7b28\u86cb\uff1b\u50bb\u74dc\uff08NZ/UK\u53e3\u8bed\uff09",
         "example": "I locked my keys in the car \u2014 what a numpty!", "example_cn": "\u6211\u628a\u94a5\u5319\u9501\u8f66\u91cc\u4e86\u2014\u2014\u592a\u8822\u4e86\uff01", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u611f\u53f9\u53e5",
         "sentence_words": [
             {"word": "locked", "phonetic": "/l\u0252kt/", "syllable": "locked", "meaning": "v. \u9501\u4e0a"}
         ]},
        {"word": "skite", "phonetic": "/ska\u026at/", "syllable": "skite", "pos": "v.",
         "meaning": "\u5439\u725b\uff1b\u70ab\u8000\uff08NZ\u65b9\u8a00\uff09",
         "example": "He's always skiting about how much money he makes.", "example_cn": "\u4ed6\u603b\u5728\u5439\u81ea\u5df1\u6323\u591a\u5c11\u94b1\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "always", "phonetic": "/\u02c8\u0254\u02d0lwe\u026az/", "syllable": "al\u00b7ways", "meaning": "adv. \u603b\u662f"}
         ]},
        {"word": "dosh", "phonetic": "/d\u0252\u0283/", "syllable": "dosh", "pos": "n.",
         "meaning": "\u94b1\uff1b\u73b0\u91d1\uff08NZ/UK\u4fda\u8bed\uff09",
         "example": "I don't have enough dosh for that concert ticket.", "example_cn": "\u6211\u6ca1\u90a3\u4e48\u591a\u94b1\u4e70\u6f14\u5531\u4f1a\u95e8\u7968\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "don't have",
         "sentence_words": [
             {"word": "enough", "phonetic": "/\u026a\u02c8n\u028cf/", "syllable": "e\u00b7nough", "meaning": "adj. \u8db3\u591f\u7684"}
         ]},
        {"word": "hoon", "phonetic": "/hu\u02d0n/", "syllable": "hoon", "pos": "n.",
         "meaning": "\u9c81\u83bd\u9a7e\u9a76\u8005\uff1b\u98d9\u8f66\u65cf",
         "example": "Some hoon in a modified car was doing burnouts.", "example_cn": "\u6709\u4e2a\u5f00\u6539\u88c5\u8f66\u7684\u98d9\u8f66\u65cf\u5728\u70e7\u80ce\u3002", "scene": "\ud83d\ude97 \u79df\u8f66",
         "grammar": "\u8fc7\u53bb\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "modified", "phonetic": "/\u02c8m\u0252d\u026afa\u026ad/", "syllable": "mod\u00b7i\u00b7fied", "meaning": "adj. \u6539\u88c5\u7684"},
             {"word": "burnout", "phonetic": "/\u02c8b\u025c\u02d0na\u028at/", "syllable": "burn\u00b7out", "meaning": "n. \u70e7\u80ce"}
         ]},
        {"word": "tinnie", "phonetic": "/\u02c8t\u026ani/", "syllable": "tin\u00b7nie", "pos": "n.",
         "meaning": "\u5564\u9152\u7f50\uff1b\u5c0f\u94dd\u8247\uff08\u53e3\u8bed\uff09",
         "example": "Chuck us a tinnie from the chilly bin, mate.", "example_cn": "\u54e5\u4eec\uff0c\u4ece\u51b0\u76d2\u91cc\u7ed9\u6211\u6254\u7f50\u5564\u9152\u3002", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u53e3\u8bed\u7528\u6cd5",
         "sentence_words": [
             {"word": "chuck", "phonetic": "/t\u0283\u028ck/", "syllable": "chuck", "meaning": "v. \u6254"}
         ]},
        {"word": "kia ora", "phonetic": "/ki a \u02c8\u0254\u02d0r\u0259/", "syllable": "ki\u00b7a o\u00b7ra", "pos": "phrase",
         "meaning": "\u4f60\u597d\uff08\u6bdb\u5229\u8bed\u95ee\u5019\u8bed\uff09",
         "example": "Kia ora! How's it going?", "example_cn": "\u4f60\u597d\uff01\u6700\u8fd1\u600e\u4e48\u6837\uff1f", "scene": "\ud83d\udde3\ufe0f NZ\u53e3\u8bed",
         "grammar": "\u6bdb\u5229\u8bed",
         "sentence_words": [
             {"word": "how's it going", "phonetic": "/ha\u028az \u026at \u02c8\u0261\u0259\u028a\u026a\u014b/", "syllable": "how's it go\u00b7ing", "meaning": "phrase \u600e\u4e48\u6837\uff1f"}
         ]},
        {"word": "poncho", "phonetic": "/\u02c8p\u0252nt\u0283\u0259\u028a/", "syllable": "pon\u00b7cho", "pos": "n.",
         "meaning": "\u6597\u7bf7\u96e8\u8863",
         "example": "It's bucketing down \u2014 grab your poncho.", "example_cn": "\u5916\u9762\u4e0b\u5927\u96e8\u2014\u2014\u62ff\u4e0a\u96e8\u62ab\u3002", "scene": "\ud83c\udf24\ufe0f \u5929\u6c14",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "bucketing down", "phonetic": "/\u02c8b\u028ck\u026at\u026a\u014b da\u028an/", "syllable": "buck\u00b7et\u00b7ing down", "meaning": "phrase \u4e0b\u503e\u76c6\u5927\u96e8"}
         ]},
        {"word": "nor'wester", "phonetic": "/n\u0254\u02d0\u02c8w\u025bst\u0259/", "syllable": "nor'-wes\u00b7ter", "pos": "n.",
         "meaning": "\u897f\u5317\u98ce\uff08\u57fa\u7763\u57ce\u7279\u6709\uff09",
         "example": "The nor'wester makes Christchurch really hot and windy.", "example_cn": "\u897f\u5317\u98ce\u8ba9\u57fa\u7763\u57ce\u53c8\u70ed\u53c8\u98ce\u5927\u3002", "scene": "\ud83c\udf24\ufe0f \u5929\u6c14",
         "grammar": "\u4f7f\u5f79\u52a8\u8bcd",
         "sentence_words": [
             {"word": "windy", "phonetic": "/\u02c8w\u026andi/", "syllable": "win\u00b7dy", "meaning": "adj. \u98ce\u5927\u7684"}
         ]},
        {"word": "long black", "phonetic": "/l\u0252\u014b bl\u00e6k/", "syllable": "long black", "pos": "n.",
         "meaning": "\u957f\u9ed1\u5496\u5561\uff08\u6fb3\u65b0\u7279\u6709\uff09",
         "example": "I'll just have a long black, thanks.", "example_cn": "\u6211\u8981\u4e00\u676f\u957f\u9ed1\u5496\u5561\uff0c\u8c22\u8c22\u3002", "scene": "\u2615 \u5496\u5561\u5e97",
         "grammar": "\u70b9\u5355\u7528\u8bed",
         "sentence_words": [
             {"word": "espresso", "phonetic": "/e\u02c8spres\u0259\u028a/", "syllable": "es\u00b7pres\u00b7so", "meaning": "n. \u6d53\u7f29\u5496\u5561"}
         ]},
        {"word": "short black", "phonetic": "/\u0283\u0254\u02d0t bl\u00e6k/", "syllable": "short black", "pos": "n.",
         "meaning": "\u77ed\u9ed1\u5496\u5561\uff1b\u7eaf\u6d53\u7f29",
         "example": "Can I get a double short black to go?", "example_cn": "\u4e00\u676f\u53cc\u4efd\u6d53\u7f29\u5e26\u8d70\u3002", "scene": "\u2615 \u5496\u5561\u5e97",
         "grammar": "to go = \u6253\u5305",
         "sentence_words": [
             {"word": "double", "phonetic": "/\u02c8d\u028cb\u0259l/", "syllable": "dou\u00b7ble", "meaning": "adj. \u53cc\u4efd\u7684"}
         ]},
        {"word": "trim flat white", "phonetic": "/tr\u026am fl\u00e6t wa\u026at/", "syllable": "trim flat white", "pos": "n.",
         "meaning": "\u8131\u8102\u5976\u767d\u5496\u5561\uff08NZ\u7ecf\u5178\uff09",
         "example": "One trim flat white, please.", "example_cn": "\u4e00\u676f\u8131\u8102\u767d\u5496\u5561\uff0c\u8c22\u8c22\u3002", "scene": "\u2615 \u5496\u5561\u5e97",
         "grammar": "\u540d\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "trim milk", "phonetic": "/tr\u026am m\u026alk/", "syllable": "trim milk", "meaning": "n. \u8131\u8102\u725b\u5976"}
         ]},
        {"word": "babycino", "phonetic": "/\u02ccbe\u026abis\u026a\u02c8n\u0259\u028a/", "syllable": "ba\u00b7by\u00b7ci\u00b7no", "pos": "n.",
         "meaning": "\u513f\u7ae5\u70ed\u53ef\u53ef\u5976\u6ce1",
         "example": "Can my kid have a babycino with a marshmallow?", "example_cn": "\u80fd\u7ed9\u6211\u5b69\u5b50\u6765\u4e00\u676f\u5e26\u68c9\u82b1\u7cd6\u7684\u513f\u7ae5\u5976\u6ce1\u5417\uff1f", "scene": "\u2615 \u5496\u5561\u5e97",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "marshmallow", "phonetic": "/\u02ccm\u0251\u02d0\u0283\u02c8m\u00e6l\u0259\u028a/", "syllable": "marsh\u00b7mal\u00b7low", "meaning": "n. \u68c9\u82b1\u7cd6"}
         ]},
        {"word": "morning tea", "phonetic": "/\u02c8m\u0254\u02d0n\u026a\u014b ti\u02d0/", "syllable": "morn\u00b7ing tea", "pos": "n.",
         "meaning": "\u4e0a\u5348\u8336\u6b47\uff08NZ\u5de5\u4f5c\u6587\u5316\uff09",
         "example": "Let's grab a morning tea at the cafe.", "example_cn": "\u53bb\u5496\u5561\u9986\u559d\u4e2a\u4e0a\u5348\u8336\u3002", "scene": "\u2615 \u5496\u5561\u5e97",
         "grammar": "let's+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "across the road", "phonetic": "/\u0259\u02c8kr\u0252s \u00f0\u0259 r\u0259\u028ad/", "syllable": "a\u00b7cross the road", "meaning": "phrase \u9a6c\u8def\u5bf9\u9762"}
         ]},
        {"word": "on special", "phonetic": "/\u0252n \u02c8spe\u0283\u0259l/", "syllable": "on spe\u00b7cial", "pos": "phrase",
         "meaning": "\u7279\u4ef7\uff1b\u6253\u6298\u4e2d",
         "example": "These avocados are on special this week.", "example_cn": "\u8fd9\u4e9b\u725b\u6cb9\u679c\u8fd9\u5468\u7279\u4ef7\u3002", "scene": "\ud83c\udfea \u8d85\u5e02\u4fc3\u9500",
         "grammar": "\u4ecb\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "avocados", "phonetic": "/\u02cc\u00e6v\u0259\u02c8k\u0251\u02d0d\u0259\u028az/", "syllable": "a\u00b7vo\u00b7ca\u00b7dos", "meaning": "n. \u725b\u6cb9\u679c"}
         ]},
        {"word": "chip packet", "phonetic": "/t\u0283\u026ap \u02c8p\u00e6k\u026at/", "syllable": "chip pack\u00b7et", "pos": "n.",
         "meaning": "\u85af\u7247\u888b",
         "example": "Can you grab a couple of chip packets?", "example_cn": "\u4f60\u80fd\u4e70\u51e0\u5305\u85af\u7247\u5417\uff1f", "scene": "\ud83c\udfea \u8d85\u5e02",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "couple of", "phonetic": "/\u02c8k\u028cp\u0259l \u0259v/", "syllable": "cou\u00b7ple of", "meaning": "phrase \u51e0\u4e2a"}
         ]},
        {"word": "paywave", "phonetic": "/\u02c8pe\u026awe\u026av/", "syllable": "pay\u00b7wave", "pos": "n./v.",
         "meaning": "\u975e\u63a5\u89e6\u5f0f\u652f\u4ed8",
         "example": "You can just paywave it, no PIN needed under $200.", "example_cn": "\u76f4\u63a5\u5237\u5c31\u884c\uff0c200\u4ee5\u4e0b\u4e0d\u7528\u5bc6\u7801\u3002", "scene": "\ud83c\udfea \u652f\u4ed8",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "PIN", "phonetic": "/p\u026an/", "syllable": "PIN", "meaning": "n. \u5bc6\u7801"}
         ]},
        {"word": "flybuys", "phonetic": "/\u02c8fla\u026ab\u028c\u026az/", "syllable": "fly\u00b7buys", "pos": "n.",
         "meaning": "Fly Buys\u79ef\u5206",
         "example": "Do you collect Fly Buys?", "example_cn": "\u4f60\u96c6Fly Buys\u79ef\u5206\u5417\uff1f", "scene": "\ud83c\udfea \u8d85\u5e02\u4fc3\u9500",
         "grammar": "\u4e00\u822c\u7591\u95ee\u53e5",
         "sentence_words": [
             {"word": "collect", "phonetic": "/k\u0259\u02c8lekt/", "syllable": "col\u00b7lect", "meaning": "v. \u6536\u96c6"}
         ]},
        {"word": "nappy", "phonetic": "/\u02c8n\u00e6pi/", "syllable": "nap\u00b7py", "pos": "n.",
         "meaning": "\u7eb8\u5c3f\u88e4\uff08NZ/AU\u7528\u6cd5\uff09",
         "example": "Can you grab a box of nappies?", "example_cn": "\u80fd\u4e70\u4e00\u7bb1\u7eb8\u5c3f\u88e4\u5417\uff1f", "scene": "\ud83c\udfea \u8d85\u5e02",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "box", "phonetic": "/b\u0252ks/", "syllable": "box", "meaning": "n. \u76d2"}
         ]},
        {"word": "give way", "phonetic": "/\u0261\u026av we\u026a/", "syllable": "give way", "pos": "phrase",
         "meaning": "\u8ba9\u8def\uff1b\u8ba9\u884c\uff08NZ\u4ea4\u901a\u6807\u5fd7\uff09",
         "example": "At a Give Way sign, you must slow down.", "example_cn": "\u5728\u8ba9\u884c\u6807\u5fd7\u5904\u5fc5\u987b\u51cf\u901f\u3002", "scene": "\ud83d\ude8c \u4ea4\u901a\u51fa\u884c",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "slow down", "phonetic": "/sl\u0259\u028a da\u028an/", "syllable": "slow down", "meaning": "v. \u51cf\u901f"},
             {"word": "traffic", "phonetic": "/\u02c8tr\u00e6f\u026ak/", "syllable": "traf\u00b7fic", "meaning": "n. \u4ea4\u901a"}
         ]},
        {"word": "toll road", "phonetic": "/t\u0259\u028al r\u0259\u028ad/", "syllable": "toll road", "pos": "n.",
         "meaning": "\u6536\u8d39\u516c\u8def",
         "example": "The toll road is faster but costs more.", "example_cn": "\u6536\u8d39\u516c\u8def\u66f4\u5feb\u4f46\u66f4\u8d35\u3002", "scene": "\ud83d\ude8c \u4ea4\u901a\u51fa\u884c",
         "grammar": "\u6bd4\u8f83\u7ea7",
         "sentence_words": [
             {"word": "costs", "phonetic": "/k\u0252sts/", "syllable": "costs", "meaning": "v. \u82b1\u8d39"}
         ]},
        {"word": "campervan", "phonetic": "/\u02c8k\u00e6mp\u0259v\u00e6n/", "syllable": "cam\u00b7per\u00b7van", "pos": "n.",
         "meaning": "\u9732\u8425\u8f66\uff1b\u623f\u8f66",
         "example": "We hired a campervan and drove around the South Island.", "example_cn": "\u6211\u4eec\u79df\u4e86\u623f\u8f66\u73af\u5357\u5c9b\u81ea\u9a7e\u3002", "scene": "\ud83d\ude97 \u79df\u8f66",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "hired", "phonetic": "/\u02c8ha\u026a\u0259d/", "syllable": "hired", "meaning": "v. \u79df\u7528"},
             {"word": "South Island", "phonetic": "/sa\u028a\u03b8 \u02c8a\u026al\u0259nd/", "syllable": "South Is\u00b7land", "meaning": "n. \u5357\u5c9b"}
         ]},
        {"word": "wof", "phonetic": "/d\u028cb\u0259lju\u02d0 \u0259\u028a ef/", "syllable": "W-O-F", "pos": "n.",
         "meaning": "\u8f66\u8f86\u5e74\u68c0\uff08Warrant of Fitness\uff09",
         "example": "Your WOF expires next month.", "example_cn": "\u4f60\u8f66\u5e74\u68c0\u4e0b\u4e2a\u6708\u5230\u671f\u3002", "scene": "\ud83d\ude97 \u79df\u8f66",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "expires", "phonetic": "/\u026ak\u02c8spa\u026a\u0259z/", "syllable": "ex\u00b7pires", "meaning": "v. \u5230\u671f"}
         ]},
        {"word": "rego", "phonetic": "/\u02c8re\u0261\u0259\u028a/", "syllable": "re\u00b7go", "pos": "n.",
         "meaning": "\u8f66\u8f86\u6ce8\u518c\uff08registration\u53e3\u8bed\uff09",
         "example": "The rego on my car costs about $700 a year.", "example_cn": "\u6211\u8f66\u6ce8\u518c\u8d39\u4e00\u5e74\u5927\u6982700\u5757\u3002", "scene": "\ud83d\ude97 \u79df\u8f66",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "registration", "phonetic": "/\u02ccred\u0292\u026a\u02c8stre\u026a\u0283\u0259n/", "syllable": "reg\u00b7is\u00b7tra\u00b7tion", "meaning": "n. \u6ce8\u518c"}
         ]},
        {"word": "footpath", "phonetic": "/\u02c8f\u028atp\u0251\u02d0\u03b8/", "syllable": "foot\u00b7path", "pos": "n.",
         "meaning": "\u4eba\u884c\u9053\uff08NZ\u7528\u6cd5\uff09",
         "example": "Watch out for the uneven footpath.", "example_cn": "\u5c0f\u5fc3\u4e0d\u5e73\u7684\u4eba\u884c\u9053\u3002", "scene": "\ud83d\ude8c \u4ea4\u901a\u51fa\u884c",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "uneven", "phonetic": "/\u028cn\u02c8i\u02d0v\u0259n/", "syllable": "un\u00b7e\u00b7ven", "meaning": "adj. \u4e0d\u5e73\u7684"}
         ]},
        {"word": "pram", "phonetic": "/pr\u00e6m/", "syllable": "pram", "pos": "n.",
         "meaning": "\u5a74\u513f\u8f66\uff08NZ/UK\u7528\u6cd5\uff09",
         "example": "The pram won't fit through that narrow gate.", "example_cn": "\u5a74\u513f\u8f66\u8fc7\u4e0d\u4e86\u90a3\u4e2a\u7a84\u95e8\u3002", "scene": "\ud83d\ude8c \u4ea4\u901a\u51fa\u884c",
         "grammar": "won't = will not",
         "sentence_words": [
             {"word": "narrow", "phonetic": "/\u02c8n\u00e6r\u0259\u028a/", "syllable": "nar\u00b7row", "meaning": "adj. \u7a84\u7684"}
         ]},
        {"word": "Snapper", "phonetic": "/\u02c8sn\u00e6p\u0259/", "syllable": "Snap\u00b7per", "pos": "n.",
         "meaning": "Snapper\u516c\u4ea4\u5361\uff08\u60e0\u7075\u987f\uff09",
         "example": "Tag on with your Snapper card.", "example_cn": "\u5237Snapper\u5361\u4e0a\u8f66\u3002", "scene": "\ud83d\ude8c \u516c\u4ea4\u901a\u52e4",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "tag on", "phonetic": "/t\u00e6\u0261 \u0252n/", "syllable": "tag on", "meaning": "v. \u5237\u5361\u4e0a\u8f66"}
         ]},
        {"word": "term deposit", "phonetic": "/t\u025c\u02d0m d\u026a\u02c8p\u0252z\u026at/", "syllable": "term de\u00b7pos\u00b7it", "pos": "n.",
         "meaning": "\u5b9a\u671f\u5b58\u6b3e",
         "example": "I put some savings into a 6-month term deposit.", "example_cn": "\u6211\u653e\u4e866\u4e2a\u6708\u5b9a\u671f\u3002", "scene": "\ud83c\udfe6 \u94f6\u884c\u5f00\u6237",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "savings", "phonetic": "/\u02c8se\u026av\u026a\u014bz/", "syllable": "sav\u00b7ings", "meaning": "n. \u5b58\u6b3e"}
         ]},
        {"word": "kiwisaver", "phonetic": "/\u02ccki\u02d0wi\u02d0\u02c8se\u026av\u0259/", "syllable": "ki\u00b7wi\u00b7sa\u00b7ver", "pos": "n.",
         "meaning": "KiwiSaver\u9000\u4f11\u50a8\u84c4\u8ba1\u5212",
         "example": "You should contribute at least 3% to KiwiSaver.", "example_cn": "KiwiSaver\u81f3\u5c11\u5e94\u4ea43%\u3002", "scene": "\ud83d\udcbc \u85aa\u8d44",
         "grammar": "\u60c5\u6001\u52a8\u8bcd",
         "sentence_words": [
             {"word": "contribute", "phonetic": "/k\u0259n\u02c8tr\u026abju\u02d0t/", "syllable": "con\u00b7trib\u00b7ute", "meaning": "v. \u7f34\u7eb3"}
         ]},
        {"word": "annual leave", "phonetic": "/\u02c8\u00e6nju\u0259l li\u02d0v/", "syllable": "an\u00b7nu\u00b7al leave", "pos": "n.",
         "meaning": "\u5e74\u5047\uff08NZ\u6cd5\u5b9a4\u5468\uff09",
         "example": "I've got two weeks of annual leave coming up.", "example_cn": "\u6211\u6709\u4e24\u5468\u5e74\u5047\u8981\u4f11\u4e86\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "coming up", "phonetic": "/\u02c8k\u028cm\u026a\u014b \u028cp/", "syllable": "com\u00b7ing up", "meaning": "phrase \u5373\u5c06\u5230\u6765"}
         ]},
        {"word": "bank fee", "phonetic": "/b\u00e6\u014bk fi\u02d0/", "syllable": "bank fee", "pos": "n.",
         "meaning": "\u94f6\u884c\u624b\u7eed\u8d39",
         "example": "Check your bank fees \u2014 they can add up.", "example_cn": "\u770b\u770b\u4f60\u7684\u624b\u7eed\u8d39\u2014\u2014\u7d2f\u79ef\u8d77\u6765\u4e0d\u5c11\u3002", "scene": "\ud83c\udfe6 \u7a0e\u52a1/\u94f6\u884c",
         "grammar": "can add up",
         "sentence_words": [
             {"word": "add up", "phonetic": "/\u00e6d \u028cp/", "syllable": "add up", "meaning": "v. \u7d2f\u79ef"}
         ]},
        {"word": "pension", "phonetic": "/\u02c8pen\u0283\u0259n/", "syllable": "pen\u00b7sion", "pos": "n.",
         "meaning": "\u517b\u8001\u91d1\uff08NZ Super\uff09",
         "example": "NZ Super is paid to people over 65.", "example_cn": "NZ Super\u53d1\u7ed965\u5c81\u4ee5\u4e0a\u4eba\u7fa4\u3002", "scene": "\ud83c\udfe6 \u653f\u5e9c\u670d\u52a1",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "superannuation", "phonetic": "/\u02ccsu\u02d0p\u0259\u02ccr\u00e6nju\u02c8e\u026a\u0283\u0259n/", "syllable": "su\u00b7per\u00b7an\u00b7nu\u00b7a\u00b7tion", "meaning": "n. \u517b\u8001\u91d1"}
         ]},
        {"word": "section", "phonetic": "/\u02c8sek\u0283\u0259n/", "syllable": "sec\u00b7tion", "pos": "n.",
         "meaning": "\u5730\u5757\uff1b\u5b85\u57fa\u5730\uff08NZ\u623f\u4ea7\u7528\u8bed\uff09",
         "example": "They bought a section and are building a house.", "example_cn": "\u4ed6\u4eec\u4e70\u4e86\u4e00\u5757\u5730\uff0c\u6b63\u5728\u5efa\u623f\u3002", "scene": "\ud83c\udfe0 \u79df\u623f",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "building", "phonetic": "/\u02c8b\u026ald\u026a\u014b/", "syllable": "build\u00b7ing", "meaning": "v. \u5efa\u9020"}
         ]},
        {"word": "sleepout", "phonetic": "/\u02c8sli\u02d0pa\u028at/", "syllable": "sleep\u00b7out", "pos": "n.",
         "meaning": "\u72ec\u7acb\u5c0f\u5c4b\uff08\u9644\u5728\u4e3b\u5c4b\u5916\uff09",
         "example": "I'm renting the sleepout at the back of the property.", "example_cn": "\u6211\u79df\u4e86\u623f\u5b50\u540e\u9762\u7684\u72ec\u7acb\u5c0f\u5c4b\u3002", "scene": "\ud83c\udfe0 \u5408\u79df\u751f\u6d3b",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "property", "phonetic": "/\u02c8pr\u0252p\u0259ti/", "syllable": "prop\u00b7er\u00b7ty", "meaning": "n. \u623f\u4ea7"}
         ]},
        {"word": "water rate", "phonetic": "/\u02c8w\u0254\u02d0t\u0259 re\u026at/", "syllable": "wa\u00b7ter rate", "pos": "n.",
         "meaning": "\u6c34\u8d39\uff08NZ\u5355\u72ec\u8ba1\u8d39\uff09",
         "example": "Water rates in Auckland are quite high.", "example_cn": "\u5965\u514b\u5170\u6c34\u8d39\u76f8\u5f53\u9ad8\u3002", "scene": "\ud83c\udfe0 \u751f\u6d3b\u7f34\u8d39",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "rate", "phonetic": "/re\u026at/", "syllable": "rate", "meaning": "n. \u8d39\u7387"}
         ]},
        {"word": "rates", "phonetic": "/re\u026ats/", "syllable": "rates", "pos": "n.",
         "meaning": "\u5e02\u653f\u7a0e\uff08NZ\u623f\u4e3b\u5e74\u5ea6\u8d39\u7528\uff09",
         "example": "Rates are due at the end of August.", "example_cn": "\u5e02\u653f\u7a0e8\u6708\u5e95\u5230\u671f\u3002", "scene": "\ud83c\udfe0 \u751f\u6d3b\u7f34\u8d39",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "due", "phonetic": "/dju\u02d0/", "syllable": "due", "meaning": "adj. \u5230\u671f\u7684"}
         ]},
        {"word": "body corporate", "phonetic": "/\u02c8b\u0252di \u02c8k\u0254\u02d0p\u0259r\u0259t/", "syllable": "body cor\u00b7po\u00b7rate", "pos": "n.",
         "meaning": "\u7269\u4e1a\u7ba1\u7406\u59d4\u5458\u4f1a",
         "example": "Our body corporate fee is $400 per quarter.", "example_cn": "\u6211\u4eec\u7269\u4e1a\u8d39\u6bcf\u5b63\u5ea6400\u5757\u3002", "scene": "\ud83c\udfe0 \u79df\u623f",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "quarter", "phonetic": "/\u02c8kw\u0254\u02d0t\u0259/", "syllable": "quar\u00b7ter", "meaning": "n. \u5b63\u5ea6"}
         ]},
        {"word": "open home", "phonetic": "/\u02c8\u0259\u028ap\u0259n h\u0259\u028am/", "syllable": "o\u00b7pen home", "pos": "n.",
         "meaning": "\u5f00\u653e\u770b\u623f\uff08NZ\u623f\u4ea7\u7528\u8bed\uff09",
         "example": "There's an open home this Saturday from 1 to 1:30pm.", "example_cn": "\u8fd9\u5468\u516d\u4e0b\u53481\u70b9\u52301\u70b9\u534a\u5f00\u653e\u770b\u623f\u3002", "scene": "\ud83c\udfe0 \u79df\u623f",
         "grammar": "there be",
         "sentence_words": [
             {"word": "auction", "phonetic": "/\u02c8\u0254\u02d0k\u0283\u0259n/", "syllable": "auc\u00b7tion", "meaning": "n. \u62cd\u5356"}
         ]},
        {"word": "fixture", "phonetic": "/\u02c8f\u026akst\u0283\u0259/", "syllable": "fix\u00b7ture", "pos": "n.",
         "meaning": "\u56fa\u5b9a\u8bbe\u65bd\uff08\u4e0d\u53ef\u79fb\u52a8\u7269\u54c1\uff09",
         "example": "The oven and dishwasher are fixtures.", "example_cn": "\u70e4\u7bb1\u548c\u6d17\u7897\u673a\u662f\u56fa\u5b9a\u8bbe\u65bd\u3002", "scene": "\ud83c\udfe0 \u79df\u623f\u68c0\u67e5",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "oven", "phonetic": "/\u02c8\u028cv\u0259n/", "syllable": "o\u00b7ven", "meaning": "n. \u70e4\u7bb1"},
             {"word": "dishwasher", "phonetic": "/\u02c8d\u026a\u0283w\u0252\u0283\u0259/", "syllable": "dish\u00b7wash\u00b7er", "meaning": "n. \u6d17\u7897\u673a"}
         ]},
        {"word": "chattels", "phonetic": "/\u02c8t\u0283\u00e6t\u0259lz/", "syllable": "chat\u00b7tels", "pos": "n.",
         "meaning": "\u52a8\u4ea7\uff1b\u53ef\u79fb\u52a8\u7269\u54c1",
         "example": "The curtains are chattels \u2014 you can take them.", "example_cn": "\u7a97\u5e18\u662f\u52a8\u4ea7\u2014\u2014\u53ef\u4ee5\u5e26\u8d70\u3002", "scene": "\ud83c\udfe0 \u9000\u79df",
         "grammar": "can take",
         "sentence_words": [
             {"word": "curtains", "phonetic": "/\u02c8k\u025c\u02d0t\u0259nz/", "syllable": "cur\u00b7tains", "meaning": "n. \u7a97\u5e18"},
             {"word": "blinds", "phonetic": "/bla\u026andz/", "syllable": "blinds", "meaning": "n. \u767e\u53f6\u7a97"}
         ]},
        {"word": "CV", "phonetic": "/\u02ccsi\u02d0\u02c8vi\u02d0/", "syllable": "C-V", "pos": "n.",
         "meaning": "\u7b80\u5386\uff08Curriculum Vitae\uff09",
         "example": "Make sure your CV is up to date before applying.", "example_cn": "\u7533\u8bf7\u524d\u786e\u4fdd\u7b80\u5386\u662f\u6700\u65b0\u7684\u3002", "scene": "\ud83d\udcbc \u6c42\u804c",
         "grammar": "make sure",
         "sentence_words": [
             {"word": "up to date", "phonetic": "/\u028cp tu de\u026at/", "syllable": "up to date", "meaning": "phrase \u6700\u65b0\u7684"},
             {"word": "applying", "phonetic": "/\u0259\u02c8pla\u026a\u026a\u014b/", "syllable": "ap\u00b7ply\u00b7ing", "meaning": "v. \u7533\u8bf7"}
         ]},
        {"word": "gap", "phonetic": "/\u0261\u00e6p/", "syllable": "gap", "pos": "n.",
         "meaning": "\u7a7a\u767d\u671f\uff08\u7b80\u5386\u7a7a\u7a97\u671f\uff09",
         "example": "Employers might ask about the gap in your CV.", "example_cn": "\u96c7\u4e3b\u53ef\u80fd\u4f1a\u95ee\u7b80\u5386\u4e0a\u7684\u7a7a\u767d\u671f\u3002", "scene": "\ud83d\udcbc \u6c42\u804c",
         "grammar": "might ask",
         "sentence_words": [
             {"word": "employers", "phonetic": "/\u026am\u02c8pl\u0254\u026a\u0259z/", "syllable": "em\u00b7ploy\u00b7ers", "meaning": "n. \u96c7\u4e3b"}
         ]},
        {"word": "casual", "phonetic": "/\u02c8k\u00e6\u0292u\u0259l/", "syllable": "cas\u00b7u\u00b7al", "pos": "adj.",
         "meaning": "\u517c\u804c\u7684\uff1b\u4e34\u65f6\u5de5",
         "example": "I'm working casual hours \u2014 about 20 a week.", "example_cn": "\u6211\u505a\u4e34\u65f6\u5de5\u2014\u2014\u5927\u6982\u4e00\u546820\u5c0f\u65f6\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "hours", "phonetic": "/\u02c8a\u028a\u0259z/", "syllable": "hours", "meaning": "n. \u5de5\u65f6"}
         ]},
        {"word": "pharmacy", "phonetic": "/\u02c8f\u0251\u02d0m\u0259si/", "syllable": "phar\u00b7ma\u00b7cy", "pos": "n.",
         "meaning": "\u836f\u623f",
         "example": "The pharmacy closes at 5pm on Saturdays.", "example_cn": "\u836f\u623f\u5468\u516d5\u70b9\u5173\u95e8\u3002", "scene": "\ud83c\udfe5 \u836f\u5e97",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "closes", "phonetic": "/\u02c8kl\u0259\u028az\u026az/", "syllable": "clo\u00b7ses", "meaning": "v. \u5173\u95e8"}
         ]},
        {"word": "subsidised", "phonetic": "/\u02c8s\u028cbs\u026ada\u026azd/", "syllable": "sub\u00b7si\u00b7dised", "pos": "adj.",
         "meaning": "\u6709\u8865\u8d34\u7684",
         "example": "Most doctor visits are subsidised if you're a resident.", "example_cn": "\u5c45\u6c11\u591a\u6570\u770b\u75c5\u6709\u8865\u8d34\u3002", "scene": "\ud83c\udfe5 \u9884\u7ea6\u770b\u75c5",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "subsidy", "phonetic": "/\u02c8s\u028cbs\u026adi/", "syllable": "sub\u00b7sid\u00b7y", "meaning": "n. \u8865\u8d34"}
         ]},
        {"word": "potluck", "phonetic": "/\u02ccp\u0252t\u02c8l\u028ck/", "syllable": "pot\u00b7luck", "pos": "n.",
         "meaning": "\u767e\u4e50\u9910\uff08\u6bcf\u4eba\u5e26\u4e00\u9053\u83dc\uff09",
         "example": "We're having a potluck dinner on Friday.", "example_cn": "\u5468\u4e94\u641e\u767e\u4e50\u9910\u3002", "scene": "\ud83d\udc65 \u90bb\u91cc",
         "grammar": "\u73b0\u5728\u8fdb\u884c\u65f6",
         "sentence_words": [
             {"word": "dish", "phonetic": "/d\u026a\u0283/", "syllable": "dish", "meaning": "n. \u4e00\u9053\u83dc"}
         ]},
        {"word": "bring a plate", "phonetic": "/br\u026a\u014b \u0259 ple\u026at/", "syllable": "bring a plate", "pos": "phrase",
         "meaning": "\u5e26\u98df\u7269\u6765\u5206\u4eab\uff08NZ\u805a\u4f1a\u7528\u8bed\uff09",
         "example": "Just bring a plate when you come.", "example_cn": "\u6765\u7684\u65f6\u5019\u5e26\u70b9\u5403\u7684\u5c31\u884c\u3002", "scene": "\ud83d\udc65 \u90bb\u91cc",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "join", "phonetic": "/d\u0292\u0254\u026an/", "syllable": "join", "meaning": "v. \u53c2\u52a0"}
         ]},
        {"word": "uni", "phonetic": "/\u02c8ju\u02d0ni/", "syllable": "u\u00b7ni", "pos": "n.",
         "meaning": "\u5927\u5b66\uff08university\u53e3\u8bed\u7f29\u5199\uff09",
         "example": "She's at uni in Wellington studying law.", "example_cn": "\u5979\u5728\u60e0\u7075\u987f\u5927\u5b66\u8bfb\u6cd5\u5f8b\u3002", "scene": "\ud83c\udf93 \u5b66\u6821\u6559\u80b2",
         "grammar": "\u53e3\u8bed\u7f29\u5199",
         "sentence_words": [
             {"word": "Wellington", "phonetic": "/\u02c8wel\u026a\u014bt\u0259n/", "syllable": "Wel\u00b7ling\u00b7ton", "meaning": "n. \u60e0\u7075\u987f"}
         ]},
        {"word": "assignment", "phonetic": "/\u0259\u02c8sa\u026anm\u0259nt/", "syllable": "as\u00b7sign\u00b7ment", "pos": "n.",
         "meaning": "\u4f5c\u4e1a\uff1b\u8bfe\u9898",
         "example": "The assignment is due next Friday.", "example_cn": "\u4f5c\u4e1a\u4e0b\u5468\u4e94\u4ea4\u3002", "scene": "\ud83c\udf93 \u5b66\u6821/\u5de5\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "due", "phonetic": "/dju\u02d0/", "syllable": "due", "meaning": "adj. \u5230\u671f\u7684"}
         ]},
        {"word": "soft plastic", "phonetic": "/s\u0252ft \u02c8pl\u00e6st\u026ak/", "syllable": "soft plas\u00b7tic", "pos": "n.",
         "meaning": "\u8f6f\u5851\u6599\uff08NZ\u6307\u5b9a\u56de\u6536\uff09",
         "example": "Soft plastics go in the special bin.", "example_cn": "\u8f6f\u5851\u6599\u653e\u4e13\u7528\u56de\u6536\u7bb1\u3002", "scene": "\u267b\ufe0f \u73af\u4fdd",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "recycle", "phonetic": "/ri\u02d0\u02c8sa\u026ak\u0259l/", "syllable": "re\u00b7cy\u00b7cle", "meaning": "v. \u56de\u6536"}
         ]},
        {"word": "kerbside", "phonetic": "/\u02c8k\u025c\u02d0bsa\u026ad/", "syllable": "kerb\u00b7side", "pos": "adj.",
         "meaning": "\u8def\u8fb9\u7684",
         "example": "Kerbside recycling is collected every Tuesday.", "example_cn": "\u6bcf\u5468\u4e8c\u6536\u8def\u8fb9\u53ef\u56de\u6536\u7269\u3002", "scene": "\u267b\ufe0f \u73af\u4fdd",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "collected", "phonetic": "/k\u0259\u02c8lekt\u026ad/", "syllable": "col\u00b7lected", "meaning": "v. \u6536\u96c6"}
         ]},
        {"word": "gumboots", "phonetic": "/\u02c8\u0261\u028cmbu\u02d0ts/", "syllable": "gum\u00b7boots", "pos": "n.",
         "meaning": "\u96e8\u9774\uff1b\u6a61\u80f6\u9774",
         "example": "Grab your gumboots, it's pretty muddy.", "example_cn": "\u7a7f\u4e0a\u96e8\u9774\uff0c\u5916\u9762\u633a\u6ce5\u6cde\u3002", "scene": "\ud83c\udf24\ufe0f \u5929\u6c14",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "muddy", "phonetic": "/\u02c8m\u028cdi/", "syllable": "mud\u00b7dy", "meaning": "adj. \u6ce5\u6cde\u7684"}
         ]},
        {"word": "torch", "phonetic": "/t\u0254\u02d0t\u0283/", "syllable": "torch", "pos": "n.",
         "meaning": "\u624b\u7535\u7b52\uff08NZ/UK\u7528\u6cd5\uff09",
         "example": "Take a torch if you're walking the dog at night.", "example_cn": "\u665a\u4e0a\u905b\u72d7\u5e26\u4e2a\u624b\u7535\u7b52\u3002", "scene": "\ud83d\udc15 \u5ba0\u7269",
         "grammar": "\u7948\u4f7f\u53e5+\u6761\u4ef6\u53e5",
         "sentence_words": [
             {"word": "walking the dog", "phonetic": "/\u02c8w\u0254\u02d0k\u026a\u014b \u00f0\u0259 d\u0252\u0261/", "syllable": "walk\u00b7ing the dog", "meaning": "phrase \u905b\u72d7"}
         ]},
        {"word": "duvet", "phonetic": "/\u02c8dju\u02d0ve\u026a/", "syllable": "du\u00b7vet", "pos": "n.",
         "meaning": "\u7fbd\u7ed2\u88ab\uff08NZ\u5e38\u7528\uff09",
         "example": "I need a thicker duvet \u2014 it's getting cold.", "example_cn": "\u6211\u9700\u8981\u66f4\u539a\u7684\u88ab\u5b50\u2014\u2014\u8d8a\u6765\u8d8a\u51b7\u4e86\u3002", "scene": "\ud83c\udfe0 \u65e5\u5e38\u751f\u6d3b",
         "grammar": "need to",
         "sentence_words": [
             {"word": "thicker", "phonetic": "/\u02c8\u03b8\u026ak\u0259/", "syllable": "thick\u00b7er", "meaning": "adj. \u66f4\u539a\u7684"}
         ]},
        {"word": "heat pump", "phonetic": "/hi\u02d0t p\u028cmp/", "syllable": "heat pump", "pos": "n.",
         "meaning": "\u7a7a\u8c03/\u6696\u901a\uff08NZ\u53ebheat pump\uff09",
         "example": "We got a heat pump installed \u2014 huge difference.", "example_cn": "\u6211\u4eec\u88c5\u4e86\u7a7a\u8c03\u2014\u2014\u5dee\u522b\u592a\u5927\u4e86\u3002", "scene": "\ud83c\udfe0 \u65e5\u5e38\u751f\u6d3b",
         "grammar": "\u4f7f\u5f79\u52a8\u8bcd",
         "sentence_words": [
             {"word": "installed", "phonetic": "/\u026an\u02c8st\u0254\u02d0ld/", "syllable": "in\u00b7stalled", "meaning": "v. \u5b89\u88c5"}
         ]},
        {"word": "text", "phonetic": "/tekst/", "syllable": "text", "pos": "v./n.",
         "meaning": "\u53d1\u77ed\u4fe1",
         "example": "Just text me when you're on your way.", "example_cn": "\u4f60\u51fa\u53d1\u65f6\u7ed9\u6211\u53d1\u77ed\u4fe1\u3002", "scene": "\ud83d\udcf1 \u624b\u673a\u5957\u9910",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "on your way", "phonetic": "/\u0252n j\u0254\u02d0 we\u026a/", "syllable": "on your way", "meaning": "phrase \u5728\u8def\u4e0a"}
         ]},
        {"word": "data cap", "phonetic": "/\u02c8de\u026at\u0259 k\u00e6p/", "syllable": "da\u00b7ta cap", "pos": "n.",
         "meaning": "\u6d41\u91cf\u4e0a\u9650",
         "example": "We've hit our data cap \u2014 internet is super slow.", "example_cn": "\u6d41\u91cf\u7528\u5b8c\u4e86\u2014\u2014\u7f51\u8d85\u6162\u3002", "scene": "\ud83d\udcf6 \u5bbd\u5e26\u7f51\u7edc",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "internet", "phonetic": "/\u02c8\u026ant\u0259net/", "syllable": "in\u00b7ter\u00b7net", "meaning": "n. \u4e92\u8054\u7f51"}
         ]},
        {"word": "glowing", "phonetic": "/\u02c8\u0261l\u0259\u028a\u026a\u014b/", "syllable": "glow\u00b7ing", "pos": "adj.",
         "meaning": "\u53d1\u5149\u7684\uff08\u5899\u58c1\u9709\u83cc\u8ff9\u8c61\uff09",
         "example": "There's a glowing patch on the ceiling \u2014 might be a leak.", "example_cn": "\u5929\u82b1\u677f\u4e0a\u6709\u5757\u53d1\u4eae\u2014\u2014\u53ef\u80fd\u6f0f\u6c34\u3002", "scene": "\ud83d\udd27 \u7ef4\u4fee",
         "grammar": "there be",
         "sentence_words": [
             {"word": "leak", "phonetic": "/li\u02d0k/", "syllable": "leak", "meaning": "n. \u6f0f\u6c34"},
             {"word": "ceiling", "phonetic": "/\u02c8si\u02d0l\u026a\u014b/", "syllable": "ceil\u00b7ing", "meaning": "n. \u5929\u82b1\u677f"}
         ]},
        {"word": "DIY", "phonetic": "/di\u02d0 a\u026a wa\u026a/", "syllable": "D-I-Y", "pos": "n./adj.",
         "meaning": "\u81ea\u5df1\u52a8\u624b\u505a\uff08NZ\u6587\u5316\uff09",
         "example": "He fixed the fence himself, full DIY.", "example_cn": "\u4ed6\u81ea\u5df1\u4fee\u597d\u4e86\u6805\u680f\uff0c\u5b8c\u5168DIY\u3002", "scene": "\ud83d\udd27 \u7ef4\u4fee",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "handy", "phonetic": "/\u02c8h\u00e6ndi/", "syllable": "hand\u00b7y", "meaning": "adj. \u624b\u5de7\u7684"}
         ]},
        {"word": "mitre 10", "phonetic": "/\u02c8ma\u026at\u0259 ten/", "syllable": "mi\u00b7tre 10", "pos": "n.",
         "meaning": "Mitre 10 MEGA\uff08NZ\u4e94\u91d1\u8fde\u9501\uff09",
         "example": "I need to pop into Mitre 10 to get some paint.", "example_cn": "\u6211\u5f97\u53bbMitre 10\u4e70\u70b9\u6cb9\u6f06\u3002", "scene": "\ud83d\udd27 \u7ef4\u4fee",
         "grammar": "need to pop into",
         "sentence_words": [
             {"word": "paint", "phonetic": "/pe\u026ant/", "syllable": "paint", "meaning": "n. \u6cb9\u6f06"}
         ]},
        {"word": "INZ", "phonetic": "/a\u026a en ze\u026a/", "syllable": "I-N-Z", "pos": "n.",
         "meaning": "\u65b0\u897f\u5170\u79fb\u6c11\u5c40",
         "example": "Submit your application through the INZ portal.", "example_cn": "\u901a\u8fc7\u79fb\u6c11\u5c40\u5b98\u7f51\u63d0\u4ea4\u7533\u8bf7\u3002", "scene": "\ud83d\udec2 \u7b7e\u8bc1",
         "grammar": "\u7948\u4f7f\u53e5",
         "sentence_words": [
             {"word": "portal", "phonetic": "/\u02c8p\u0254\u02d0t\u0259l/", "syllable": "por\u00b7tal", "meaning": "n. \u7f51\u4e0a\u5165\u53e3"},
             {"word": "submit", "phonetic": "/s\u0259b\u02c8m\u026at/", "syllable": "sub\u00b7mit", "meaning": "v. \u63d0\u4ea4"}
         ]},
        {"word": "e-visa", "phonetic": "/\u02c8i\u02d0 vi\u02d0z\u0259/", "syllable": "e-vi\u00b7sa", "pos": "n.",
         "meaning": "\u7535\u5b50\u7b7e\u8bc1",
         "example": "Your e-visa will be emailed once approved.", "example_cn": "\u7b7e\u8bc1\u6279\u51c6\u540e\u7535\u5b50\u7b7e\u8bc1\u53d1\u5230\u4f60\u90ae\u7bb1\u3002", "scene": "\ud83d\udec2 \u7b7e\u8bc1",
         "grammar": "\u4e00\u822c\u5c06\u6765\u65f6",
         "sentence_words": [
             {"word": "approved", "phonetic": "/\u0259\u02c8pru\u02d0vd/", "syllable": "ap\u00b7proved", "meaning": "v. \u6279\u51c6"}
         ]},
        {"word": "expression of interest", "phonetic": "/\u026ak\u02c8spre\u0283\u0259n \u0259v \u02c8\u026antr\u0259st/", "syllable": "ex\u00b7pres\u00b7sion of in\u00b7ter\u00b7est", "pos": "n.",
         "meaning": "\u610f\u5411\u7533\u8bf7\uff08EOI\uff09",
         "example": "The EOI pool is drawn every two weeks.", "example_cn": "EOI\u6c60\u6bcf\u4e24\u5468\u62bd\u4e00\u6b21\u3002", "scene": "\ud83d\udec2 \u79fb\u6c11",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "pool", "phonetic": "/pu\u02d0l/", "syllable": "pool", "meaning": "n. \u5019\u9009\u6c60"}
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
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"},
             {"word": "work", "phonetic": "/wɜːk/", "syllable": "work", "meaning": "n./v. 工作"}
         ]},
        {"word": "infrastructure", "phonetic": "/ˈɪnfrəstrʌktʃə/", "syllable": "in · fra · struc · ture", "pos": "n.",
         "meaning": "基础设施",
         "example": "Auckland is investing in public transport infrastructure.",
         "example_cn": "奥克兰正在大力投资公共交通基础设施。", "scene": "📝 雅思写作",
         "grammar": "现在进行时：is investing in（正在投资），表示持续进行的动作",
         "sentence_words": [
             {"word": "investing", "phonetic": "/ɪnˈvestɪŋ/", "syllable": "in·vest·ing", "meaning": "v. 投资（现在分词）"},
             {"word": "public transport", "phonetic": "/ˈpʌblɪk ˈtrænspɔːt/", "syllable": "pub·lic trans·port", "meaning": "n. 公共交通"},
             {"word": "auckland", "phonetic": "/ˈɔːklənd/", "syllable": "Auck·land", "meaning": "n. 奥克兰（新西兰最大城市）"}
         ]},
        {"word": "sustainability", "phonetic": "/səˌsteɪnəˈbɪləti/", "syllable": "sus · tain · a · bil · i · ty", "pos": "n.",
         "meaning": "可持续性",
         "example": "NZ has strong policies focused on sustainability.",
         "example_cn": "新西兰有以可持续发展为重点的政策。", "scene": "📝 雅思写作",
         "grammar": "一般现在时：has（拥有）+ 名词，表示当前的政策状态",
         "sentence_words": [
             {"word": "policies", "phonetic": "/ˈpɒlɪsiz/", "syllable": "pol·i·cies", "meaning": "n. 政策（复数）"},
             {"word": "focused on", "phonetic": "/ˈfəʊkəst ɒn/", "syllable": "fo·cused on", "meaning": "adj. 专注于；以...为重点（过去分词作后置定语）"},
             {"word": "focused", "phonetic": "/ˈfəʊkəst/", "syllable": "fo·cused", "meaning": "adj. 专注的；聚焦于"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"},
             {"word": "sustainability", "phonetic": "/səˌsteɪnəˈbɪləti/", "syllable": "sus·tain·a·bil·i·ty", "meaning": "n. 可持续性"}
         ]},
        {"word": "acknowledge", "phonetic": "/əkˈnɒlɪdʒ/", "syllable": "ac · knowl · edge", "pos": "v.",
         "meaning": "承认；致谢",
         "example": "It's important to acknowledge different cultural perspectives.",
         "example_cn": "承认不同的文化视角很重要。", "scene": "🎓 雅思口语/写作",
         "grammar": "It's + 形容词 + to do sth.：It's important to...（形式主语句型）",
         "sentence_words": [
             {"word": "cultural", "phonetic": "/ˈkʌltʃərəl/", "syllable": "cul·tur·al", "meaning": "adj. 文化的；文化上的"},
             {"word": "perspectives", "phonetic": "/pəˈspektɪvz/", "syllable": "per·spec·tives", "meaning": "n. 观点；视角（复数）"},
             {"word": "acknowledge", "phonetic": "/əkˈnɒlɪdʒ/", "syllable": "ac·know·ledge", "meaning": "v. 承认；认可"}
         ]},
        {"word": "migrate", "phonetic": "/maɪˈɡreɪt/", "syllable": "mi · grate", "pos": "v.",
         "meaning": "移民；迁徙",
         "example": "Many families migrate to NZ for better education.",
         "example_cn": "许多家庭为了更好的教育移民新西兰。", "scene": "📋 移民",
         "grammar": "一般现在时（习惯/普遍规律）：migrate to...for...，表示目的",
         "sentence_words": [
             {"word": "families", "phonetic": "/ˈfæmɪliz/", "syllable": "fam·i·lies", "meaning": "n. 家庭（复数）"},
             {"word": "better education", "phonetic": "/ˈbetər ˌedʒuˈkeɪʃn/", "syllable": "bet·ter ed·u·ca·tion", "meaning": "n. 更好的教育（比较级+名词）"},
             {"word": "better", "phonetic": "/ˈbetər/", "syllable": "bet·ter", "meaning": "adj./adv. 更好的"},
             {"word": "education", "phonetic": "/ˌedʒuˈkeɪʃn/", "syllable": "ed·u·ca·tion", "meaning": "n. 教育"},
             {"word": "migrate", "phonetic": "/maɪˈɡreɪt/", "syllable": "mi·grate", "meaning": "v. 移居；迁移"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"}
         ]},
        {"word": "adapt", "phonetic": "/əˈdæpt/", "syllable": "a · dapt", "pos": "v.",
         "meaning": "适应；调整",
         "example": "It took me a few months to adapt to the NZ way of life.",
         "example_cn": "我花了几个月才适应新西兰的生活方式。", "scene": "📋 生活适应",
         "grammar": "It took + 时间 + to do：花了...时间做某事（固定句型）",
         "sentence_words": [
             {"word": "took", "phonetic": "/tʊk/", "syllable": "took", "meaning": "v. 花（take 的过去式）"},
             {"word": "way of life", "phonetic": "/weɪ əv laɪf/", "syllable": "way of life", "meaning": "n. 生活方式（固定搭配）"},
             {"word": "adapt", "phonetic": "/əˈdæpt/", "syllable": "a·dapt", "meaning": "v. 适应"},
             {"word": "months", "phonetic": "/mʌnθs/", "syllable": "months", "meaning": "n. 月（复数）"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"}
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
             {"word": "elections", "phonetic": "/ɪˈlekʃnz/", "syllable": "e·lec·tions", "meaning": "n. 选举（复数）"},
             {"word": "local", "phonetic": "/ˈləʊkl/", "syllable": "lo·cal", "meaning": "adj. 当地的"},
             {"word": "residents", "phonetic": "/ˈrezɪdənts/", "syllable": "res·i·dents", "meaning": "n. 居民（复数）"}
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
             {"word": "income", "phonetic": "/ˈɪnkʌm/", "syllable": "in·come", "meaning": "n. 收入"},
             {"word": "tax", "phonetic": "/tæks/", "syllable": "tax", "meaning": "n. 税"}
         ]},
        {"word": "opportunity", "phonetic": "/ˌɒpəˈtjuːnəti/", "syllable": "op · por · tu · ni · ty", "pos": "n.",
         "meaning": "机会",
         "example": "Studying abroad gives you great opportunities.",
         "example_cn": "出国留学给你很好的机会。", "scene": "🎓 留学申请",
         "grammar": "动名词作主语：Studying abroad（出国留学）+ 谓语 gives",
         "sentence_words": [
             {"word": "studying abroad", "phonetic": "/ˈstʌdiɪŋ əˈbrɔːd/", "syllable": "stud·y·ing a·broad", "meaning": "v. 出国留学（动名词短语）"},
             {"word": "great", "phonetic": "/ɡreɪt/", "syllable": "great", "meaning": "adj. 很好的；巨大的"},
             {"word": "abroad", "phonetic": "/əˈbrɔːd/", "syllable": "a·broad", "meaning": "adv. 在国外"},
             {"word": "gives", "phonetic": "/ɡɪvz/", "syllable": "gives", "meaning": "v. 给（第三人称单数）"},
             {"word": "opportunities", "phonetic": "/ˌɒpəˈtjuːnɪtiz/", "syllable": "op·por·tu·ni·ties", "meaning": "n. 机会（复数）"},
             {"word": "studying", "phonetic": "/ˈstʌdiɪŋ/", "syllable": "stud·y·ing", "meaning": "v. 学习（现在分词）"}
         ]},
        {"word": "previous", "phonetic": "/ˈpriːviəs/", "syllable": "pre · vi · ous", "pos": "adj.",
         "meaning": "以前的；先前的",
         "example": "What was your previous address?",
         "example_cn": "你以前的地址是什么？", "scene": "📋 表格填写",
         "grammar": "一般过去时疑问句：What was...? 询问过去的信息",
         "sentence_words": [
             {"word": "address", "phonetic": "/əˈdres/", "syllable": "ad·dress", "meaning": "n. 地址"},
             {"word": "previous", "phonetic": "/ˈpriːviəs/", "syllable": "pre·vi·ous", "meaning": "adj. 以前的；之前的"}
         ]},
        {"word": "accommodation", "phonetic": "/əˌkɒməˈdeɪʃn/", "syllable": "ac · com · mo · da · tion", "pos": "n.",
         "meaning": "住宿；住处",
         "example": "Finding affordable accommodation in Auckland is quite hard.",
         "example_cn": "在奥克兰找到便宜的住处挺难的。", "scene": "🏠 租房/雅思",
         "grammar": "动名词作主语：Finding...（找...）是主语；quite hard（相当难）作表语",
         "sentence_words": [
             {"word": "affordable", "phonetic": "/əˈfɔːdəbl/", "syllable": "af·ford·a·ble", "meaning": "adj. 负担得起的；价格合理的"},
             {"word": "quite", "phonetic": "/kwaɪt/", "syllable": "quite", "meaning": "adv. 相当；非常"},
             {"word": "accommodation", "phonetic": "/əˌkɒməˈdeɪʃn/", "syllable": "ac·com·mo·da·tion", "meaning": "n. 住宿"},
             {"word": "auckland", "phonetic": "/ˈɔːklənd/", "syllable": "Auck·land", "meaning": "n. 奥克兰（新西兰最大城市）"},
             {"word": "finding", "phonetic": "/ˈfaɪndɪŋ/", "syllable": "find·ing", "meaning": "v. 找到（现在分词）"}
         ]},
        {"word": "settle", "phonetic": "/ˈsetl/", "syllable": "set · tle", "pos": "v.",
         "meaning": "安顿；定居",
         "example": "It takes time to settle into a new country.",
         "example_cn": "在一个新国家安顿下来需要时间。", "scene": "📋 移民生活",
         "grammar": "It takes + 名词 + to do：需要...来做某事（形式主语句型）",
         "sentence_words": [
             {"word": "takes time", "phonetic": "/teɪks taɪm/", "syllable": "takes time", "meaning": "v. 需要时间（固定搭配）"},
             {"word": "settle into", "phonetic": "/ˈsetl ˈɪntuː/", "syllable": "set·tle in·to", "meaning": "v. 融入；安顿下来（短语动词）"},
             {"word": "settle", "phonetic": "/ˈsetl/", "syllable": "set·tle", "meaning": "v. 安顿；定居"},
             {"word": "takes", "phonetic": "/teɪks/", "syllable": "takes", "meaning": "v. 花费（第三人称单数）"}
         ]},
        {"word": "certificate", "phonetic": "/səˈtɪfɪkət/", "syllable": "cer · ti · fi · cate", "pos": "n.",
         "meaning": "证书；证明",
         "example": "You need a police certificate for your visa application.",
         "example_cn": "签证申请需要无犯罪证明。", "scene": "📋 签证材料",
         "grammar": "need + 名词（宾语）+ for + 名词：需要某物用于某事",
         "sentence_words": [
             {"word": "police certificate", "phonetic": "/pəˈliːs səˈtɪfɪkət/", "syllable": "po·lice cer·tif·i·cate", "meaning": "n. 无犯罪记录证明"},
             {"word": "visa application", "phonetic": "/ˈviːzə ˌæplɪˈkeɪʃn/", "syllable": "vi·sa ap·pli·ca·tion", "meaning": "n. 签证申请"},
             {"word": "application", "phonetic": "/ˌæplɪˈkeɪʃn/", "syllable": "ap·pli·ca·tion", "meaning": "n. 申请"},
             {"word": "certificate", "phonetic": "/sərˈtɪfɪkət/", "syllable": "cer·tif·i·cate", "meaning": "n. 证书"},
             {"word": "police", "phonetic": "/pəˈliːs/", "syllable": "po·lice", "meaning": "n. 警察"},
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"}
         ]},
        {"word": "fluent", "phonetic": "/ˈfluːənt/", "syllable": "flu · ent", "pos": "adj.",
         "meaning": "流利的",
         "example": "She's fluent in both English and Mandarin.",
         "example_cn": "她的英语和普通话都很流利。", "scene": "🎓 雅思口语",
         "grammar": "be + 形容词：is fluent in（在...方面很流利）；both...and...（两者都）",
         "sentence_words": [
             {"word": "fluent in", "phonetic": "/ˈfluːənt ɪn/", "syllable": "flu·ent in", "meaning": "adj. 精通；流利（固定搭配）"},
             {"word": "Mandarin", "phonetic": "/ˈmændərɪn/", "syllable": "Man·da·rin", "meaning": "n. 普通话；官话"},
             {"word": "both", "phonetic": "/bəʊθ/", "syllable": "both", "meaning": "pron./adj. 两者都"},
             {"word": "english", "phonetic": "/ˈɪŋɡlɪʃ/", "syllable": "Eng·lish", "meaning": "n. 英语"},
             {"word": "fluent", "phonetic": "/ˈfluːənt/", "syllable": "flu·ent", "meaning": "adj. 流利的"}
         ]},
        {"word": "diverse", "phonetic": "/daɪˈvɜːs/", "syllable": "di · verse", "pos": "adj.",
         "meaning": "多元的；多样化的",
         "example": "NZ is a diverse society with people from many cultures.",
         "example_cn": "新西兰是一个多元文化的社会。", "scene": "📝 雅思写作",
         "grammar": "主系表结构：is a + 形容词 + 名词；with + 名词短语作后置定语",
         "sentence_words": [
             {"word": "society", "phonetic": "/səˈsaɪəti/", "syllable": "so·ci·e·ty", "meaning": "n. 社会"},
             {"word": "cultures", "phonetic": "/ˈkʌltʃəz/", "syllable": "cul·tures", "meaning": "n. 文化（复数）"},
             {"word": "diverse", "phonetic": "/daɪˈvɜːs/", "syllable": "di·verse", "meaning": "adj. 多样的；多元化的"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"},
             {"word": "people", "phonetic": "/ˈpiːpl/", "syllable": "peo·ple", "meaning": "n. 人们"}
         ]},
        {"word": "contribute", "phonetic": "/kənˈtrɪbjuːt/", "syllable": "con · trib · ute", "pos": "v.",
         "meaning": "贡献；捐助",
         "example": "Volunteering is a great way to contribute to the community.",
         "example_cn": "做志愿者是回馈社区的好方式。", "scene": "📝 雅思写作",
         "grammar": "动名词作主语：Volunteering is a way to...（...是...的方式）",
         "sentence_words": [
             {"word": "volunteering", "phonetic": "/ˌvɒlənˈtɪərɪŋ/", "syllable": "vol·un·teer·ing", "meaning": "v. 做志愿者（动名词）"},
             {"word": "community", "phonetic": "/kəˈmjuːnəti/", "syllable": "com·mu·ni·ty", "meaning": "n. 社区；团体"},
             {"word": "contribute", "phonetic": "/kənˈtrɪbjuːt/", "syllable": "con·trib·ute", "meaning": "v. 贡献；做贡献"},
             {"word": "great", "phonetic": "/ɡreɪt/", "syllable": "great", "meaning": "adj. 很好的；很棒的"}
         ]},
        {"word": "require", "phonetic": "/rɪˈkwaɪə/", "syllable": "re · quire", "pos": "v.",
         "meaning": "需要；要求",
         "example": "The visa application requires several supporting documents.",
         "example_cn": "签证申请需要几份支持材料。", "scene": "📋 签证申请",
         "grammar": "一般现在时：requires（第三人称单数）+ 宾语；several（几个）",
         "sentence_words": [
             {"word": "supporting documents", "phonetic": "/səˈpɔːtɪŋ ˈdɒkjuménts/", "syllable": "sup·port·ing doc·u·ments", "meaning": "n. 支持性文件；证明材料"},
             {"word": "several", "phonetic": "/ˈsevrəl/", "syllable": "sev·er·al", "meaning": "adj. 几个；若干"},
             {"word": "application", "phonetic": "/ˌæplɪˈkeɪʃn/", "syllable": "ap·pli·ca·tion", "meaning": "n. 申请"},
             {"word": "documents", "phonetic": "/ˈdɒkjumənts/", "syllable": "doc·u·ments", "meaning": "n. 文件（复数）"},
             {"word": "requires", "phonetic": "/rɪˈkwaɪəz/", "syllable": "re·quires", "meaning": "v. 要求（第三人称单数）"},
             {"word": "supporting", "phonetic": "/səˈpɔːtɪŋ/", "syllable": "sup·port·ing", "meaning": "adj. 支持的；辅助的"},
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"}
         ]},
        {"word": "temporary", "phonetic": "/ˈtemprəri/", "syllable": "tem · po · ra · ry", "pos": "adj.",
         "meaning": "临时的；暂时的",
         "example": "I'm on a temporary work visa right now.",
         "example_cn": "我现在持临时工作签证。", "scene": "📋 签证",
         "grammar": "be on + 名词：be on a visa（持有签证）；right now（现在）",
         "sentence_words": [
             {"word": "on a visa", "phonetic": "/ɒn ə ˈviːzə/", "syllable": "on a vi·sa", "meaning": "phrase. 持有签证（固定搭配）"},
             {"word": "right now", "phonetic": "/raɪt naʊ/", "syllable": "right now", "meaning": "adv. 现在；此刻（口语）"},
             {"word": "i'm", "phonetic": "/aɪm/", "syllable": "I'm", "meaning": "abbr. I am 的缩写"},
             {"word": "temporary", "phonetic": "/ˈtemprəri/", "syllable": "tem·po·rary", "meaning": "adj. 临时的"},
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"},
             {"word": "work", "phonetic": "/wɜːk/", "syllable": "work", "meaning": "n./v. 工作"}
         ]},
        {"word": "minimum", "phonetic": "/ˈmɪnɪməm/", "syllable": "min · i · mum", "pos": "n./adj.",
         "meaning": "最低限度；最低的",
         "example": "The minimum wage in NZ is reviewed every year.",
         "example_cn": "新西兰的最低工资每年都会审核。", "scene": "💼 工作/生活",
         "grammar": "被动语态：is reviewed（被审核）；every year（每年）",
         "sentence_words": [
             {"word": "wage", "phonetic": "/weɪdʒ/", "syllable": "wage", "meaning": "n. 工资；薪酬"},
             {"word": "reviewed", "phonetic": "/rɪˈvjuːd/", "syllable": "re·viewed", "meaning": "v. 审查；审核（被动语态）"},
             {"word": "every", "phonetic": "/ˈevri/", "syllable": "ev·ery", "meaning": "adj. 每一（个）"},
             {"word": "minimum", "phonetic": "/ˈmɪnɪməm/", "syllable": "min·i·mum", "meaning": "adj. 最低的；最小的"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"},
             {"word": "year", "phonetic": "/jɪər/", "syllable": "year", "meaning": "n. 年"}
         ]},
        {"word": "essential", "phonetic": "/ɪˈsenʃl/", "syllable": "es · sen · tial", "pos": "adj.",
         "meaning": "必不可少的；核心的",
         "example": "English is essential for working in most NZ companies.",
         "example_cn": "英语在大多数新西兰公司工作是必不可少的。", "scene": "📝 雅思写作",
         "grammar": "主系表结构：is essential for...（对...来说是必要的）",
         "sentence_words": [
             {"word": "for working in", "phonetic": "/fɔː ˈwɜːkɪŋ ɪn/", "syllable": "for work·ing in", "meaning": "prep. 对于在...工作（for + 动名词）"},
             {"word": "companies", "phonetic": "/ˈkʌmpəniz/", "syllable": "com·pa·nies", "meaning": "n. 公司（复数）"},
             {"word": "english", "phonetic": "/ˈɪŋɡlɪʃ/", "syllable": "Eng·lish", "meaning": "n. 英语"},
             {"word": "essential", "phonetic": "/ɪˈsenʃl/", "syllable": "es·sen·tial", "meaning": "adj. 必要的；必不可少的"},
             {"word": "nz", "phonetic": "/ˌen ˈzed/", "syllable": "NZ", "meaning": "n. 新西兰（New Zealand缩写）"},
             {"word": "working", "phonetic": "/ˈwɜːkɪŋ/", "syllable": "work·ing", "meaning": "v. 工作（现在分词/动名词）"}
         ]},
        {"word": "application", "phonetic": "/ˌæplɪˈkeɪʃn/", "syllable": "ap · pli · ca · tion", "pos": "n.",
         "meaning": "申请；申请表",
         "example": "Submit your visa application at least two months in advance.",
         "example_cn": "至少提前两个月提交签证申请。", "scene": "📋 签证申请",
         "grammar": "祈使句：Submit...；at least two months in advance（提前至少两个月）",
         "sentence_words": [
             {"word": "submit", "phonetic": "/səbˈmɪt/", "syllable": "sub·mit", "meaning": "v. 提交；递交"},
             {"word": "in advance", "phonetic": "/ɪn ədˈvɑːns/", "syllable": "in ad·vance", "meaning": "adv. 提前；预先（固定搭配）"},
             {"word": "advance", "phonetic": "/ədˈvɑːns/", "syllable": "ad·vance", "meaning": "n./adv. 提前"},
             {"word": "application", "phonetic": "/ˌæplɪˈkeɪʃn/", "syllable": "ap·pli·ca·tion", "meaning": "n. 申请"},
             {"word": "at", "phonetic": "/æt/", "syllable": "at", "meaning": "prep. 在（此处人名At）"},
             {"word": "least", "phonetic": "/liːst/", "syllable": "least", "meaning": "n./adj. 最少；最小的"},
             {"word": "months", "phonetic": "/mʌnθs/", "syllable": "months", "meaning": "n. 月（复数）"},
             {"word": "visa", "phonetic": "/ˈviːzə/", "syllable": "vi·sa", "meaning": "n. 签证"}
         ]},
        {"word": "duration", "phonetic": "/djʊˈreɪʃn/", "syllable": "du · ra · tion", "pos": "n.",
         "meaning": "持续时间；期限",
         "example": "The duration of this course is two semesters.",
         "example_cn": "这门课的时长是两个学期。", "scene": "🎓 学校/雅思",
         "grammar": "主系表结构：The duration of...is...（...的时长是...）",
         "sentence_words": [
             {"word": "course", "phonetic": "/kɔːs/", "syllable": "course", "meaning": "n. 课程"},
             {"word": "semesters", "phonetic": "/sɪˈmestəz/", "syllable": "se·mes·ters", "meaning": "n. 学期（复数，一年两学期）"},
             {"word": "duration", "phonetic": "/djʊˈreɪʃn/", "syllable": "du·ra·tion", "meaning": "n. 期间；持续时间"}
         ]},
        {"word": "approximately", "phonetic": "/əˈprɒksɪmətli/", "syllable": "ap · prox · i · mate · ly", "pos": "adv.",
         "meaning": "大约；大概",
         "example": "The processing time is approximately four to six weeks.",
         "example_cn": "处理时间大约是四到六周。", "scene": "📋 签证/雅思写作",
         "grammar": "主系表结构：The...time is + 副词 + 数量，用副词 approximately 修饰",
         "sentence_words": [
             {"word": "processing time", "phonetic": "/ˈprəʊsesɪŋ taɪm/", "syllable": "pro·cess·ing time", "meaning": "n. 处理时间；审批时间"},
             {"word": "approximately", "phonetic": "/əˈprɒksɪmətli/", "syllable": "ap·prox·i·mate·ly", "meaning": "adv. 大约；约"},
             {"word": "processing", "phonetic": "/ˈprəʊsesɪŋ/", "syllable": "pro·cess·ing", "meaning": "n./v. 处理；审核"},
             {"word": "weeks", "phonetic": "/wiːks/", "syllable": "weeks", "meaning": "n. 周（复数）"}
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
             {"word": "queen", "phonetic": "/kwiːn/", "syllable": "Queen", "meaning": "n. 女王（此处为街名）"},
             {"word": "recommend", "phonetic": "/ˌrekəˈmend/", "syllable": "rec·om·mend", "meaning": "v. 推荐"},
             {"word": "street", "phonetic": "/striːt/", "syllable": "street", "meaning": "n. 街道"}
         ]},
        {"word": "enrol", "phonetic": "/ɪnˈrəʊl/", "syllable": "en · rol", "pos": "v.",
         "meaning": "注册；报名",
         "example": "You need to enrol before the semester starts.",
         "example_cn": "你需要在学期开始前完成注册。", "scene": "🎓 学校教育",
         "grammar": "need to + 动词原形；before + 从句，表示时间先后",
         "sentence_words": [
             {"word": "semester", "phonetic": "/sɪˈmestər/", "syllable": "se·mes·ter", "meaning": "n. 学期"},
             {"word": "starts", "phonetic": "/stɑːts/", "syllable": "starts", "meaning": "v. 开始（第三人称单数）"},
             {"word": "enrol", "phonetic": "/ɪnˈrəʊl/", "syllable": "en·rol", "meaning": "v. 注册；报名"}
         ]},
        {"word": "tuition", "phonetic": "/tjuˈɪʃn/", "syllable": "tu · i · tion", "pos": "n.",
         "meaning": "学费",
         "example": "International students pay higher tuition fees than locals.",
         "example_cn": "国际学生的学费比本地生高。", "scene": "🎓 学校/签证",
         "grammar": "比较级：pay higher...than...（比...付更多）",
         "sentence_words": [
             {"word": "international students", "phonetic": "/ˌɪntəˈnæʃnəl ˈstjuːdənts/", "syllable": "in·ter·na·tion·al stu·dents", "meaning": "n. 国际学生（复数）"},
             {"word": "locals", "phonetic": "/ˈləʊkəlz/", "syllable": "lo·cals", "meaning": "n. 本地人（复数口语）"},
             {"word": "fees", "phonetic": "/fiːz/", "syllable": "fees", "meaning": "n. 费用（复数）"},
             {"word": "higher", "phonetic": "/ˈhaɪər/", "syllable": "high·er", "meaning": "adj. 更高的"},
             {"word": "international", "phonetic": "/ˌɪntəˈnæʃənl/", "syllable": "in·ter·na·tion·al", "meaning": "adj. 国际的"},
             {"word": "students", "phonetic": "/ˈstjuːdənts/", "syllable": "stu·dents", "meaning": "n. 学生（复数）"},
             {"word": "tuition", "phonetic": "/tjuˈɪʃn/", "syllable": "tu·i·tion", "meaning": "n. 学费"}
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
             {"word": "community", "phonetic": "/kəˈmjuːnɪti/", "syllable": "com·mu·ni·ty", "meaning": "n. 社区"},
             {"word": "helps", "phonetic": "/helps/", "syllable": "helps", "meaning": "v. 帮助（第三人称单数）"},
             {"word": "involved", "phonetic": "/ɪnˈvɒlvd/", "syllable": "in·volved", "meaning": "adj. 参与的"},
             {"word": "local", "phonetic": "/ˈləʊkl/", "syllable": "lo·cal", "meaning": "adj. 当地的"},
             {"word": "settle", "phonetic": "/ˈsetl/", "syllable": "set·tle", "meaning": "v. 安顿；定居"}
         ]},

        # ---- 教育 ----
        {"word": "bachelor", "phonetic": "/ˈbætʃələr/", "syllable": "bach · e · lor", "pos": "n.",
         "meaning": "学士学位",
         "example": "She earned a bachelor's degree in Accounting.",
         "example_cn": "她获得了会计学学士学位。", "scene": "📚 大学",
         "grammar": "一般过去时：earned（earn的过去式）；degree in（...学位）",
         "sentence_words": [
             {"word": "earned", "phonetic": "/ɜːnd/", "syllable": "earned", "meaning": "v. 获得（过去式）"},
             {"word": "degree", "phonetic": "/dɪˈɡriː/", "syllable": "de·gree", "meaning": "n. 学位"},
             {"word": "accounting", "phonetic": "/əˈkaʊntɪŋ/", "syllable": "ac·count·ing", "meaning": "n. 会计学"}
         ]},
        {"word": "lecture", "phonetic": "/ˈlektʃər/", "syllable": "lec · ture", "pos": "n.",
         "meaning": "讲座；大课",
         "example": "The lecture starts at 9am sharp. Don't be late.",
         "example_cn": "讲座9点整开始，别迟到。", "scene": "📚 大学",
         "grammar": "一般现在时（固定安排）；sharp（整点）",
         "sentence_words": [
             {"word": "sharp", "phonetic": "/ʃɑːp/", "syllable": "sharp", "meaning": "adv. 整点地"},
             {"word": "late", "phonetic": "/leɪt/", "syllable": "late", "meaning": "adj. 迟到的"},
             {"word": "lecture", "phonetic": "/ˈlektʃər/", "syllable": "lec·ture", "meaning": "n. 讲座；大课"}
         ]},
        {"word": "assignment", "phonetic": "/əˈsaɪnmənt/", "syllable": "as · sign · ment", "pos": "n.",
         "meaning": "作业；任务",
         "example": "I need to finish this assignment before the deadline.",
         "example_cn": "我得在截止日期前完成这项作业。", "scene": "📚 学习",
         "grammar": "need to + 动词原形；before + 时间",
         "sentence_words": [
             {"word": "assignment", "phonetic": "/əˈsaɪnmənt/", "syllable": "as·sign·ment", "meaning": "n. 作业；任务"}
         ]},
        {"word": "scholarship", "phonetic": "/ˈskɒləʃɪp/", "syllable": "schol · ar · ship", "pos": "n.",
         "meaning": "奖学金",
         "example": "She won a scholarship to study at university.",
         "example_cn": "她获得了大学奖学金。", "scene": "📚 留学",
         "grammar": "一般过去时：won（win的过去式）；to study（不定式表目的）",
         "sentence_words": [
             {"word": "won", "phonetic": "/wʌn/", "syllable": "won", "meaning": "v. 赢得（win的过去式）"},
             {"word": "scholarship", "phonetic": "/ˈskɒləʃɪp/", "syllable": "schol·ar·ship", "meaning": "n. 奖学金"}
         ]},
        {"word": "semester", "phonetic": "/sɪˈmestər/", "syllable": "se · mes · ter", "pos": "n.",
         "meaning": "学期",
         "example": "The new semester starts in February.",
         "example_cn": "新学期2月开始。", "scene": "📚 学校",
         "grammar": "一般现在时（固定日程）；in + 月份（在一月）",
         "sentence_words": [
             {"word": "semester", "phonetic": "/sɪˈmestər/", "syllable": "se·mes·ter", "meaning": "n. 学期"}
         ]},

        # ---- 健康 ----
        {"word": "symptom", "phonetic": "/ˈsɪmptəm/", "syllable": "symp · tom", "pos": "n.",
         "meaning": "症状",
         "example": "Common symptoms include a fever and a dry cough.",
         "example_cn": "常见症状包括发烧和干咳。", "scene": "🏥 健康",
         "grammar": "一般现在时（医学描述）；include + 名词（包括）",
         "sentence_words": [
             {"word": "symptom", "phonetic": "/ˈsɪmptəm/", "syllable": "symp·tom", "meaning": "n. 症状"},
             {"word": "fever", "phonetic": "/ˈfiːvər/", "syllable": "fe·ver", "meaning": "n. 发烧"},
             {"word": "cough", "phonetic": "/kɒf/", "syllable": "cough", "meaning": "n./v. 咳嗽"}
         ]},
        {"word": "exercise", "phonetic": "/ˈeksəsaɪz/", "syllable": "ex · er · cise", "pos": "n./v.",
         "meaning": "锻炼；运动",
         "example": "Regular exercise is good for both physical and mental health.",
         "example_cn": "经常锻炼对身心健康都有好处。", "scene": "🏥 健康",
         "grammar": "主系表结构：is good for（对...有好处）；both...and...（两者都）",
         "sentence_words": [
             {"word": "regular", "phonetic": "/ˈreɡjələr/", "syllable": "reg·u·lar", "meaning": "adj. 经常的；有规律的"},
             {"word": "physical", "phonetic": "/ˈfɪzɪkl/", "syllable": "phys·i·cal", "meaning": "adj. 身体的"},
             {"word": "mental", "phonetic": "/ˈmentl/", "syllable": "men·tal", "meaning": "adj. 精神的；心理的"},
             {"word": "health", "phonetic": "/helθ/", "syllable": "health", "meaning": "n. 健康"},
             {"word": "exercise", "phonetic": "/ˈeksəsaɪz/", "syllable": "ex·er·cise", "meaning": "n./v. 锻炼；运动"}
         ]},
        {"word": "balanced", "phonetic": "/ˈbælənst/", "syllable": "bal · anced", "pos": "adj.",
         "meaning": "均衡的",
         "example": "A balanced diet includes plenty of vegetables and fruits.",
         "example_cn": "均衡饮食应包含大量蔬菜和水果。", "scene": "🏥 饮食健康",
         "grammar": "一般现在时（健康建议）；includes + 名词（包含）",
         "sentence_words": [
             {"word": "diet", "phonetic": "/ˈdaɪət/", "syllable": "di·et", "meaning": "n. 饮食"},
             {"word": "vegetables", "phonetic": "/ˈvedʒtəblz/", "syllable": "veg·e·ta·bles", "meaning": "n. 蔬菜（复数）"},
             {"word": "fruits", "phonetic": "/fruːts/", "syllable": "fruits", "meaning": "n. 水果（复数）"},
             {"word": "balanced", "phonetic": "/ˈbælənst/", "syllable": "bal·anced", "meaning": "adj. 均衡的"}
         ]},
        {"word": "stress", "phonetic": "/stres/", "syllable": "stress", "pos": "n.",
         "meaning": "压力",
         "example": "Too much stress can lead to serious health problems.",
         "example_cn": "压力过大会导致严重的健康问题。", "scene": "🏥 心理健康",
         "grammar": "Too much + n.（太多...）；can lead to（会导致）",
         "sentence_words": [
             {"word": "lead to", "phonetic": "/liːd tuː/", "syllable": "lead to", "meaning": "v. 导致（固定搭配）"},
             {"word": "serious", "phonetic": "/ˈsɪəriəs/", "syllable": "se·ri·ous", "meaning": "adj. 严重的"},
             {"word": "stress", "phonetic": "/stres/", "syllable": "stress", "meaning": "n. 压力；紧张"}
         ]},
        {"word": "recover", "phonetic": "/rɪˈkʌvər/", "syllable": "re · cov · er", "pos": "v.",
         "meaning": "恢复；康复",
         "example": "It takes time to recover from a major illness.",
         "example_cn": "大病之后需要时间恢复。", "scene": "🏥 康复",
         "grammar": "It takes time to do（做...需要时间）；to recover（不定式）",
         "sentence_words": [
             {"word": "recover", "phonetic": "/rɪˈkʌvər/", "syllable": "re·cov·er", "meaning": "v. 恢复；康复"}
         ]},

        # ---- 环境/科技 ----
        {"word": "climate change", "phonetic": "/ˈklaɪmɪt tʃeɪndʒ/", "syllable": "cli·mate change", "pos": "n.",
         "meaning": "气候变化",
         "example": "Climate change is one of the biggest challenges facing humanity.",
         "example_cn": "气候变化是人类面临的最大挑战之一。", "scene": "🌍 环境",
         "grammar": "主系表：is one of + the + 最高级 + 复数名词（是...最...之一）",
         "sentence_words": [
             {"word": "biggest", "phonetic": "/ˈbɪɡɪst/", "syllable": "big·gest", "meaning": "adj. 最大的（最高级）"},
             {"word": "challenge", "phonetic": "/ˈtʃælɪndʒ/", "syllable": "chal·lenge", "meaning": "n. 挑战"},
             {"word": "humanity", "phonetic": "/hjuːˈmænəti/", "syllable": "hu·man·i·ty", "meaning": "n. 人类"},
             {"word": "climate", "phonetic": "/ˈklaɪmɪt/", "syllable": "cli·mate", "meaning": "n. 气候"}
         ]},
        {"word": "renewable", "phonetic": "/rɪˈnjuːəbl/", "syllable": "re · new · a · ble", "pos": "adj.",
         "meaning": "可再生的",
         "example": "NZ has great potential for renewable energy like solar and wind.",
         "example_cn": "新西兰在太阳能、风能等可再生能源方面潜力巨大。", "scene": "🌍 环保/能源",
         "grammar": "一般现在时（客观描述）；potential for（...的潜力）",
         "sentence_words": [
             {"word": "potential", "phonetic": "/pəˈtenʃl/", "syllable": "po·ten·tial", "meaning": "n. 潜力；可能性"},
             {"word": "renewable", "phonetic": "/rɪˈnjuːəbl/", "syllable": "re·new·a·ble", "meaning": "adj. 可再生的"}
         ]},
        {"word": "technology", "phonetic": "/tekˈnɒlədʒi/", "syllable": "tech · nol · o · gy", "pos": "n.",
         "meaning": "科技",
         "example": "Technology has changed the way we communicate and work.",
         "example_cn": "科技改变了我们交流和工作方式。", "scene": "💻 科技",
         "grammar": "现在完成时：has changed（已经改变）；the way we...（我们...的方式）",
         "sentence_words": [
             {"word": "technology", "phonetic": "/tekˈnɒlədʒi/", "syllable": "tech·nol·o·gy", "meaning": "n. 科技；技术"}
         ]},
        {"word": "artificial", "phonetic": "/ˌɑːtɪˈfɪʃl/", "syllable": "ar · ti · fi · cial", "pos": "adj.",
         "meaning": "人工的；人造的",
         "example": "Artificial intelligence is transforming many industries.",
         "example_cn": "人工智能正在改变许多行业。", "scene": "💻 AI",
         "grammar": "现在进行时：is transforming（正在改变）；many industries（许多行业）",
         "sentence_words": [
             {"word": "artificial intelligence", "phonetic": "/ˌɑːtɪˈfɪʃl ɪnˈtelɪdʒəns/", "syllable": "ar·ti·fi·cial in·tel·li·gence", "meaning": "n. 人工智能"},
             {"word": "artificial", "phonetic": "/ˌɑːtɪˈfɪʃl/", "syllable": "ar·ti·fi·cial", "meaning": "adj. 人工的；人造的"}
         ]},
        {"word": "digital", "phonetic": "/ˈdɪdʒɪtl/", "syllable": "dig · i · tal", "pos": "adj.",
         "meaning": "数字化的",
         "example": "Digital skills are becoming essential in today's job market.",
         "example_cn": "数字技能在当今就业市场变得越来越重要。", "scene": "💻 数字化",
         "grammar": "现在进行时（趋势）：are becoming；essential（必不可少的）",
         "sentence_words": [
             {"word": "essential", "phonetic": "/ɪˈsenʃl/", "syllable": "es·sen·tial", "meaning": "adj. 必不可少的；必要的"},
             {"word": "digital", "phonetic": "/ˈdɪdʒɪtl/", "syllable": "dig·i·tal", "meaning": "adj. 数字化的"}
         ]},

        # ---- 工作/职业 ----
        {"word": "experience", "phonetic": "/ɪkˈspɪəriəns/", "syllable": "ex · pe · ri · ence", "pos": "n.",
         "meaning": "经验；经历",
         "example": "Previous experience in customer service is preferred.",
         "example_cn": "有客户服务经验者优先。", "scene": "💼 求职",
         "grammar": "Previous + n.（之前的...）；is preferred（更受欢迎）",
         "sentence_words": [
             {"word": "previous", "phonetic": "/ˈpriːviəs/", "syllable": "pre·vi·ous", "meaning": "adj. 之前的"},
             {"word": "customer service", "phonetic": "/ˈkʌstəmər ˈsɜːvɪs/", "syllable": "cus·to·mer ser·vice", "meaning": "n. 客户服务"},
             {"word": "preferred", "phonetic": "/prɪˈfɜːd/", "syllable": "pre·ferred", "meaning": "adj. 首选的；更受欢迎的"},
             {"word": "experience", "phonetic": "/ɪkˈspɪəriəns/", "syllable": "ex·pe·ri·ence", "meaning": "n. 经验；经历"}
         ]},
        {"word": "salary", "phonetic": "/ˈsæləri/", "syllable": "sal · a · ry", "pos": "n.",
         "meaning": "薪水",
         "example": "The salary for this position is negotiable depending on experience.",
         "example_cn": "这个职位的薪资可以根据经验协商。", "scene": "💼 薪资",
         "grammar": "主系表：is negotiable（可以协商）；depending on（取决于）",
         "sentence_words": [
             {"word": "negotiable", "phonetic": "/nɪˈɡəʊʃiəbl/", "syllable": "ne·go·ti·a·ble", "meaning": "adj. 可协商的"},
             {"word": "salary", "phonetic": "/ˈsæləri/", "syllable": "sal·a·ry", "meaning": "n. 薪水（通常指月薪/年薪）"}
         ]},
        {"word": "interview", "phonetic": "/ˈɪntəvjuː/", "syllable": "in · ter · view", "pos": "n./v.",
         "meaning": "面试",
         "example": "I have a job interview tomorrow morning.",
         "example_cn": "我明天上午有个工作面试。", "scene": "💼 面试",
         "grammar": "一般现在时（已有安排）；tomorrow morning（明天下午）",
         "sentence_words": [
             {"word": "interview", "phonetic": "/ˈɪntəvjuː/", "syllable": "in·ter·view", "meaning": "n. 面试；v. 面试"}
         ]},
        {"word": "qualification", "phonetic": "/ˌkwɒlɪfɪˈkeɪʃn/", "syllable": "qual · i · fi · ca · tion", "pos": "n.",
         "meaning": "资格；资质",
         "example": "What qualifications do I need for this job?",
         "example_cn": "这份工作需要什么资质？", "scene": "💼 求职",
         "grammar": "What + do + 主语 + need + for?（需要什么...?）",
         "sentence_words": [
             {"word": "qualification", "phonetic": "/ˌkwɒlɪfɪˈkeɪʃn/", "syllable": "qual·i·fi·ca·tion", "meaning": "n. 资格；资质；证书"}
         ]},
        {"word": "promotion", "phonetic": "/prəˈməʊʃn/", "syllable": "pro · mo · tion", "pos": "n.",
         "meaning": "晋升；推广",
         "example": "Hard work can lead to promotion and better pay.",
         "example_cn": "努力工作可以带来晋升和更好的报酬。", "scene": "💼 职业发展",
         "grammar": "can + 动词原形（可能）；lead to（导致）",
         "sentence_words": [
             {"word": "promotion", "phonetic": "/prəˈməʊʃn/", "syllable": "pro·mo·tion", "meaning": "n. 晋升；升职"}
         ]},
        {"word": "retire", "phonetic": "/rɪˈtaɪər/", "syllable": "re · tire", "pos": "v.",
         "meaning": "退休",
         "example": "Many people look forward to retiring at 65.",
         "example_cn": "许多人都期待着65岁退休。", "scene": "💼 退休",
         "grammar": "现在进行时（期待）：are looking forward to；at 65（65岁时）",
         "sentence_words": [
             {"word": "retire", "phonetic": "/rɪˈtaɪər/", "syllable": "re·tire", "meaning": "v. 退休"}
         ]},

        # ---- 城市/旅游 ----
        {"word": "tourism", "phonetic": "/ˈtʊərɪzəm/", "syllable": "tour · ism", "pos": "n.",
         "meaning": "旅游业",
         "example": "Tourism is a major source of income for NZ.",
         "example_cn": "旅游业是新西兰的主要收入来源。", "scene": "🌏 旅游",
         "grammar": "主系表：is a major source of（是...的主要来源）",
         "sentence_words": [
             {"word": "source", "phonetic": "/sɔːs/", "syllable": "source", "meaning": "n. 来源"},
             {"word": "income", "phonetic": "/ˈɪnkʌm/", "syllable": "in·come", "meaning": "n. 收入"},
             {"word": "tourism", "phonetic": "/ˈtʊərɪzəm/", "syllable": "tour·ism", "meaning": "n. 旅游业"}
         ]},
        {"word": "attraction", "phonetic": "/əˈtrækʃn/", "syllable": "at · trac · tion", "pos": "n.",
         "meaning": "景点；吸引力",
         "example": "Rotorua is one of NZ's top tourist attractions.",
         "example_cn": "罗托鲁瓦是新西兰最热门的旅游景点之一。", "scene": "🌏 旅游",
         "grammar": "主系表：is one of + the top + 复数名词（是...最...之一）",
         "sentence_words": [
             {"word": "tourist", "phonetic": "/ˈtʊərɪst/", "syllable": "tour·ist", "meaning": "n. 游客"},
             {"word": "attraction", "phonetic": "/əˈtrækʃn/", "syllable": "at·trac·tion", "meaning": "n. 景点；吸引力"}
         ]},
        {"word": "convenient", "phonetic": "/kənˈviːniənt/", "syllable": "con · ve · nient", "pos": "adj.",
         "meaning": "方便的；便利的",
         "example": "Living close to public transport is very convenient.",
         "example_cn": "住得离公共交通近很方便。", "scene": "🏘️ 住房",
         "grammar": "动名词作主语：Living close to...（住得离...近）",
         "sentence_words": [
             {"word": "convenient", "phonetic": "/kənˈviːniənt/", "syllable": "con·ve·nient", "meaning": "adj. 方便的；便利的"}
         ]},

        # ---- 社会/家庭 ----
        {"word": "generation", "phonetic": "/ˌdʒenəˈreɪʃn/", "syllable": "gen · er · a · tion", "pos": "n.",
         "meaning": "一代人",
         "example": "Each generation faces different challenges and opportunities.",
         "example_cn": "每一代人都面临不同的挑战和机遇。", "scene": "👨‍👩‍👧 社会",
         "grammar": "Each + 单数名词（每一...）；different challenges（不同的挑战）",
         "sentence_words": [
             {"word": "generation", "phonetic": "/ˌdʒenəˈreɪʃn/", "syllable": "gen·er·a·tion", "meaning": "n. 一代人；代际"}
         ]},
        {"word": "divorce", "phonetic": "/dɪˈvɔːs/", "syllable": "di · vorce", "pos": "n./v.",
         "meaning": "离婚",
         "example": "The divorce rate has been increasing in many countries.",
         "example_cn": "许多国家的离婚率一直在上升。", "scene": "👨‍👩‍👧 家庭",
         "grammar": "现在完成进行时：has been increasing（一直在上升）",
         "sentence_words": [
             {"word": "divorce", "phonetic": "/dɪˈvɔːs/", "syllable": "di·vorce", "meaning": "n. 离婚；v. 离婚"}
         ]},
        {"word": "population", "phonetic": "/ˌpɒpjuˈleɪʃn/", "syllable": "pop · u · la · tion", "pos": "n.",
         "meaning": "人口",
         "example": "The aging population puts pressure on healthcare systems.",
         "example_cn": "人口老龄化给医疗系统带来压力。", "scene": "👥 社会",
         "grammar": "主系表：puts pressure on（给...带来压力）；aging（老龄化的）",
         "sentence_words": [
             {"word": "aging", "phonetic": "/ˈeɪdʒɪŋ/", "syllable": "a·ging", "meaning": "adj. 老龄化的"},
             {"word": "pressure", "phonetic": "/ˈpreʃər/", "syllable": "pres·sure", "meaning": "n. 压力"},
             {"word": "population", "phonetic": "/ˌpɒpjuˈleɪʃn/", "syllable": "pop·u·la·tion", "meaning": "n. 人口"}
         ]},
        {"word": "multicultural", "phonetic": "/ˌmʌltiˈkʌltʃərəl/", "syllable": "mul · ti · cul · tu · ral", "pos": "adj.",
         "meaning": "多元文化的",
         "example": "NZ is a multicultural society with people from many backgrounds.",
         "example_cn": "新西兰是一个多元文化社会，有着来自不同背景的人们。", "scene": "🌏 社会",
         "grammar": "主系表；with people from many backgrounds（有着不同背景的人）",
         "sentence_words": [
             {"word": "multicultural", "phonetic": "/ˌmʌltiˈkʌltʃərəl/", "syllable": "mul·ti·cul·tu·ral", "meaning": "adj. 多元文化的"}
         ]},

        # ---- 扩充词汇 ----
        {"word": "sponsor", "phonetic": "/\u02c8sp\u0252ns\u0259/", "syllable": "spon\u00b7sor", "pos": "v./n.",
         "meaning": "\u62c5\u4fdd\uff1b\u8d44\u52a9\uff08\u7b7e\u8bc1\u62c5\u4fdd\u4eba\uff09",
         "example": "Your employer needs to sponsor your work visa.", "example_cn": "\u4f60\u7684\u96c7\u4e3b\u9700\u8981\u4e3a\u5de5\u4f5c\u7b7e\u8bc1\u505a\u62c5\u4fdd\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1\u7533\u8bf7",
         "grammar": "need to+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "employer", "phonetic": "/\u026am\u02c8pl\u0254\u026a\u0259/", "syllable": "em\u00b7ploy\u00b7er", "meaning": "n. \u96c7\u4e3b"}
         ]},
        {"word": "dependant", "phonetic": "/d\u026a\u02c8pend\u0259nt/", "syllable": "de\u00b7pen\u00b7dant", "pos": "n.",
         "meaning": "\u53d7\u517b\u4eba\uff1b\u5bb6\u5c5e",
         "example": "You can include your dependants on the same application.", "example_cn": "\u4f60\u53ef\u4ee5\u5728\u540c\u4e00\u7533\u8bf7\u4e2d\u5305\u542b\u5bb6\u5c5e\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1\u7533\u8bf7",
         "grammar": "can include",
         "sentence_words": [
             {"word": "application", "phonetic": "/\u02cc\u00e6pl\u026a\u02c8ke\u026a\u0283\u0259n/", "syllable": "ap\u00b7pli\u00b7ca\u00b7tion", "meaning": "n. \u7533\u8bf7"}
         ]},
        {"word": "deport", "phonetic": "/d\u026a\u02c8p\u0254\u02d0t/", "syllable": "de\u00b7port", "pos": "v.",
         "meaning": "\u9a71\u9010\u51fa\u5883",
         "example": "People who overstay may be deported.", "example_cn": "\u903e\u671f\u6ede\u7559\u7684\u4eba\u53ef\u80fd\u88ab\u9a71\u9010\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "overstay", "phonetic": "/\u02cc\u0259\u028av\u0259\u02c8ste\u026a/", "syllable": "o\u00b7ver\u00b7stay", "meaning": "v. \u903e\u671f\u6ede\u7559"}
         ]},
        {"word": "permanent", "phonetic": "/\u02c8p\u025c\u02d0m\u0259n\u0259nt/", "syllable": "per\u00b7ma\u00b7nent", "pos": "adj.",
         "meaning": "\u6c38\u4e45\u7684",
         "example": "After 5 years you can apply for permanent residency.", "example_cn": "5\u5e74\u540e\u53ef\u7533\u8bf7\u6c38\u4e45\u5c45\u7559\u6743\u3002", "scene": "\ud83d\udccb \u79fb\u6c11",
         "grammar": "can apply for",
         "sentence_words": [
             {"word": "residency", "phonetic": "/\u02c8rez\u026ad\u0259nsi/", "syllable": "res\u00b7i\u00b7den\u00b7cy", "meaning": "n. \u5c45\u7559\u6743"}
         ]},
        {"word": "quota", "phonetic": "/\u02c8kw\u0259\u028at\u0259/", "syllable": "quo\u00b7ta", "pos": "n.",
         "meaning": "\u914d\u989d\uff1b\u540d\u989d",
         "example": "The skilled migrant category has an annual quota.", "example_cn": "\u6280\u672f\u79fb\u6c11\u7c7b\u522b\u6709\u5e74\u5ea6\u914d\u989d\u3002", "scene": "\ud83d\udccb \u79fb\u6c11",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "annual", "phonetic": "/\u02c8\u00e6nju\u0259l/", "syllable": "an\u00b7nu\u00b7al", "meaning": "adj. \u5e74\u5ea6\u7684"}
         ]},
        {"word": "assessment", "phonetic": "/\u0259\u02c8sesm\u0259nt/", "syllable": "as\u00b7sess\u00b7ment", "pos": "n.",
         "meaning": "\u8bc4\u4f30\uff1b\u5ba1\u6838",
         "example": "Your overseas qualification needs a NZQA assessment.", "example_cn": "\u6d77\u5916\u5b66\u5386\u9700\u8981NZQA\u8ba4\u8bc1\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1\u6750\u6599",
         "grammar": "need to",
         "sentence_words": [
             {"word": "qualification", "phonetic": "/\u02cckw\u0252l\u026af\u026a\u02c8ke\u026a\u0283\u0259n/", "syllable": "qual\u00b7i\u00b7fi\u00b7ca\u00b7tion", "meaning": "n. \u5b66\u5386"}
         ]},
        {"word": "predominantly", "phonetic": "/pr\u026a\u02c8d\u0252m\u026an\u0259ntli/", "syllable": "pre\u00b7dom\u00b7i\u00b7nant\u00b7ly", "pos": "adv.",
         "meaning": "\u4e3b\u8981\u5730",
         "example": "The population is predominantly in urban areas.", "example_cn": "\u4eba\u53e3\u4e3b\u8981\u96c6\u4e2d\u5728\u57ce\u5e02\u5730\u533a\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u88ab\u52a8+\u526f\u8bcd",
         "sentence_words": [
             {"word": "concentrated", "phonetic": "/\u02c8k\u0252ns\u0259ntre\u026at\u026ad/", "syllable": "con\u00b7cen\u00b7tra\u00b7ted", "meaning": "adj. \u96c6\u4e2d\u7684"},
             {"word": "urban", "phonetic": "/\u02c8\u025c\u02d0b\u0259n/", "syllable": "ur\u00b7ban", "meaning": "adj. \u57ce\u5e02\u7684"}
         ]},
        {"word": "deteriorate", "phonetic": "/d\u026a\u02c8t\u026a\u0259ri\u0259re\u026at/", "syllable": "de\u00b7te\u00b7ri\u00b7o\u00b7rate", "pos": "v.",
         "meaning": "\u6076\u5316\uff1b\u53d8\u574f",
         "example": "Air quality has deteriorated significantly.", "example_cn": "\u7a7a\u6c14\u8d28\u91cf\u663e\u8457\u6076\u5316\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "significantly", "phonetic": "/s\u026a\u0261\u02c8n\u026af\u026ak\u0259ntli/", "syllable": "sig\u00b7nif\u00b7i\u00b7cant\u00b7ly", "meaning": "adv. \u663e\u8457\u5730"}
         ]},
        {"word": "inevitable", "phonetic": "/\u026an\u02c8ev\u026at\u0259b\u0259l/", "syllable": "in\u00b7ev\u00b7i\u00b7ta\u00b7ble", "pos": "adj.",
         "meaning": "\u4e0d\u53ef\u907f\u514d\u7684",
         "example": "Climate change is an inevitable consequence.", "example_cn": "\u6c14\u5019\u53d8\u5316\u662f\u5fc5\u7136\u7ed3\u679c\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u540d\u8bcd\u77ed\u8bed",
         "sentence_words": [
             {"word": "consequence", "phonetic": "/\u02c8k\u0252ns\u026akw\u0259ns/", "syllable": "con\u00b7se\u00b7quence", "meaning": "n. \u7ed3\u679c"}
         ]},
        {"word": "mitigate", "phonetic": "/\u02c8m\u026at\u026a\u0261e\u026at/", "syllable": "mit\u00b7i\u00b7gate", "pos": "v.",
         "meaning": "\u7f13\u89e3\uff1b\u51cf\u8f7b",
         "example": "Governments must take action to mitigate climate effects.", "example_cn": "\u653f\u5e9c\u5fc5\u987b\u884c\u52a8\u7f13\u89e3\u6c14\u5019\u5f71\u54cd\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "must+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "effects", "phonetic": "/\u026a\u02c8fekts/", "syllable": "ef\u00b7fects", "meaning": "n. \u5f71\u54cd"}
         ]},
        {"word": "demographic", "phonetic": "/\u02ccdem\u0259\u02c8\u0261r\u00e6f\u026ak/", "syllable": "de\u00b7mo\u00b7graph\u00b7ic", "pos": "n./adj.",
         "meaning": "\u4eba\u53e3\u7edf\u8ba1",
         "example": "Demographic changes have led to an ageing population.", "example_cn": "\u4eba\u53e3\u7ed3\u6784\u53d8\u5316\u5bfc\u81f4\u8001\u9f84\u5316\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "ageing", "phonetic": "/\u02c8e\u026ad\u0292\u026a\u014b/", "syllable": "ag\u00b7ing", "meaning": "adj. \u8001\u9f84\u5316\u7684"}
         ]},
        {"word": "phenomenon", "phonetic": "/f\u026a\u02c8n\u0252m\u026an\u0259n/", "syllable": "phe\u00b7nom\u00b7e\u00b7non", "pos": "n.",
         "meaning": "\u73b0\u8c61",
         "example": "Globalisation is a phenomenon that has reshaped societies.", "example_cn": "\u5168\u7403\u5316\u662f\u91cd\u5851\u793e\u4f1a\u7684\u73b0\u8c61\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "reshaped", "phonetic": "/ri\u02d0\u02c8\u0283e\u026apt/", "syllable": "re\u00b7shaped", "meaning": "v. \u91cd\u5851"},
             {"word": "globalisation", "phonetic": "/\u02cc\u0261l\u0259\u028ab\u0259la\u026a\u02c8ze\u026a\u0283\u0259n/", "syllable": "glo\u00b7bal\u00b7i\u00b7sa\u00b7tion", "meaning": "n. \u5168\u7403\u5316"}
         ]},
        {"word": "comprehensive", "phonetic": "/\u02cck\u0252mpr\u026a\u02c8hens\u026av/", "syllable": "com\u00b7pre\u00b7hen\u00b7sive", "pos": "adj.",
         "meaning": "\u5168\u9762\u7684\uff1b\u7efc\u5408\u7684",
         "example": "A comprehensive approach is needed.", "example_cn": "\u9700\u8981\u5168\u9762\u7684\u65b9\u6cd5\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "address", "phonetic": "/\u0259\u02c8dres/", "syllable": "ad\u00b7dress", "meaning": "v. \u5904\u7406\uff1b\u89e3\u51b3"}
         ]},
        {"word": "substantial", "phonetic": "/s\u0259b\u02c8st\u00e6n\u0283\u0259l/", "syllable": "sub\u00b7stan\u00b7tial", "pos": "adj.",
         "meaning": "\u5927\u91cf\u7684\uff1b\u91cd\u5927\u7684",
         "example": "There has been a substantial increase in housing prices.", "example_cn": "\u623f\u4ef7\u6709\u4e86\u5927\u5e45\u4e0a\u6da8\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "increase", "phonetic": "/\u02c8\u026ankri\u02d0s/", "syllable": "in\u00b7crease", "meaning": "n. \u589e\u957f"}
         ]},
        {"word": "subsequent", "phonetic": "/\u02c8s\u028cbs\u026akw\u0259nt/", "syllable": "sub\u00b7se\u00b7quent", "pos": "adj.",
         "meaning": "\u968f\u540e\u7684\uff1b\u540e\u6765\u7684",
         "example": "The subsequent investigation revealed new evidence.", "example_cn": "\u968f\u540e\u7684\u8c03\u67e5\u53d1\u73b0\u4e86\u65b0\u8bc1\u636e\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "investigation", "phonetic": "/\u026an\u02ccvest\u026a\u02c8\u0261e\u026a\u0283\u0259n/", "syllable": "in\u00b7ves\u00b7ti\u00b7ga\u00b7tion", "meaning": "n. \u8c03\u67e5"}
         ]},
        {"word": "perceive", "phonetic": "/p\u0259\u02c8si\u02d0v/", "syllable": "per\u00b7ceive", "pos": "v.",
         "meaning": "\u8ba4\u4e3a\uff1b\u611f\u77e5",
         "example": "Education is perceived as the key to social mobility.", "example_cn": "\u6559\u80b2\u88ab\u89c6\u4e3a\u793e\u4f1a\u6d41\u52a8\u7684\u5173\u952e\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "social mobility", "phonetic": "/\u02c8s\u0259\u028a\u0283\u0259l m\u0259\u028a\u02c8b\u026al\u0259ti/", "syllable": "so\u00b7cial mo\u00b7bi\u00b7li\u00b7ty", "meaning": "n. \u793e\u4f1a\u6d41\u52a8"}
         ]},
        {"word": "biodiversity", "phonetic": "/\u02ccba\u026a\u0259\u028ada\u026a\u02c8v\u025c\u02d0s\u0259ti/", "syllable": "bi\u00b7o\u00b7di\u00b7ver\u00b7si\u00b7ty", "pos": "n.",
         "meaning": "\u751f\u7269\u591a\u6837\u6027",
         "example": "NZ is known for its unique biodiversity.", "example_cn": "NZ\u4ee5\u72ec\u7279\u7684\u751f\u7269\u591a\u6837\u6027\u8457\u79f0\u3002", "scene": "\ud83c\udf0d \u73af\u5883",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "unique", "phonetic": "/ju\u02d0\u02c8ni\u02d0k/", "syllable": "u\u00b7nique", "meaning": "adj. \u72ec\u7279\u7684"}
         ]},
        {"word": "deforestation", "phonetic": "/di\u02d0\u02ccf\u0252r\u026a\u02c8ste\u026a\u0283\u0259n/", "syllable": "de\u00b7for\u00b7es\u00b7ta\u00b7tion", "pos": "n.",
         "meaning": "\u780d\u4f10\u68ee\u6797",
         "example": "Deforestation contributes to global warming.", "example_cn": "\u780d\u4f10\u68ee\u6797\u52a0\u5267\u4e86\u5168\u7403\u53d8\u6696\u3002", "scene": "\ud83c\udf0d \u73af\u5883",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "contributes to", "phonetic": "/k\u0259n\u02c8tr\u026abju\u02d0ts tu\u02d0/", "syllable": "con\u00b7tributes to", "meaning": "v. \u5bfc\u81f4"}
         ]},
        {"word": "emission", "phonetic": "/\u026a\u02c8m\u026a\u0283\u0259n/", "syllable": "e\u00b7mis\u00b7sion", "pos": "n.",
         "meaning": "\u6392\u653e\uff08\u5c24\u6307\u6e29\u5ba4\u6c14\u4f53\uff09",
         "example": "NZ has committed to reducing carbon emissions by 2050.", "example_cn": "NZ\u627f\u8bfa2050\u5e74\u524d\u51cf\u5c11\u78b3\u6392\u653e\u3002", "scene": "\ud83c\udf0d \u73af\u4fdd/\u80fd\u6e90",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "carbon", "phonetic": "/\u02c8k\u0251\u02d0b\u0259n/", "syllable": "car\u00b7bon", "meaning": "n. \u78b3"},
             {"word": "committed", "phonetic": "/k\u0259\u02c8m\u026at\u026ad/", "syllable": "com\u00b7mit\u00b7ted", "meaning": "v. \u627f\u8bfa"}
         ]},
        {"word": "fluctuate", "phonetic": "/\u02c8fl\u028ckt\u0283ue\u026at/", "syllable": "fluc\u00b7tu\u00b7ate", "pos": "v.",
         "meaning": "\u6ce2\u52a8\uff1b\u8d77\u4f0f",
         "example": "Exchange rates fluctuate depending on market conditions.", "example_cn": "\u6c47\u7387\u968f\u5e02\u573a\u6761\u4ef6\u6ce2\u52a8\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "exchange rate", "phonetic": "/\u026aks\u02c8t\u0283e\u026and\u0292 re\u026at/", "syllable": "ex\u00b7change rate", "meaning": "n. \u6c47\u7387"}
         ]},
        {"word": "surplus", "phonetic": "/\u02c8s\u025c\u02d0pl\u0259s/", "syllable": "sur\u00b7plus", "pos": "n./adj.",
         "meaning": "\u76c8\u4f59\uff1b\u8fc7\u5269\u7684",
         "example": "The country reported a trade surplus last quarter.", "example_cn": "\u8be5\u56fd\u4e0a\u5b63\u5ea6\u62a5\u544a\u4e86\u8d38\u6613\u76c8\u4f59\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "trade", "phonetic": "/tre\u026ad/", "syllable": "trade", "meaning": "n. \u8d38\u6613"}
         ]},
        {"word": "curriculum", "phonetic": "/k\u0259\u02c8r\u026akj\u0259l\u0259m/", "syllable": "cur\u00b7ric\u00b7u\u00b7lum", "pos": "n.",
         "meaning": "\u8bfe\u7a0b\u4f53\u7cfb",
         "example": "The school offers a broad curriculum including arts and sciences.", "example_cn": "\u5b66\u6821\u63d0\u4f9b\u5305\u62ec\u827a\u672f\u548c\u79d1\u5b66\u7684\u5e7f\u6cdb\u8bfe\u7a0b\u3002", "scene": "\ud83c\udf93 \u5b66\u6821\u6559\u80b2",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "broad", "phonetic": "/br\u0254\u02d0d/", "syllable": "broad", "meaning": "adj. \u5e7f\u6cdb\u7684"}
         ]},
        {"word": "plagiarism", "phonetic": "/\u02c8ple\u026ad\u0292\u0259r\u026az\u0259m/", "syllable": "pla\u00b7gia\u00b7rism", "pos": "n.",
         "meaning": "\u6284\u88ad\uff1b\u527d\u7a83",
         "example": "Plagiarism is a serious academic offence in NZ universities.", "example_cn": "\u6284\u88ad\u662fNZ\u5927\u5b66\u4e25\u91cd\u7684\u5b66\u672f\u8fdd\u89c4\u3002", "scene": "\ud83c\udf93 \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "academic offence", "phonetic": "/\u02cc\u00e6k\u0259\u02c8dem\u026ak \u0259\u02c8fens/", "syllable": "ac\u00b7a\u00b7dem\u00b7ic of\u00b7fence", "meaning": "n. \u5b66\u672f\u8fdd\u89c4"}
         ]},
        {"word": "tuition fees", "phonetic": "/tju\u02c8\u026a\u0283\u0259n fi\u02d0z/", "syllable": "tu\u00b7i\u00b7tion fees", "pos": "n.",
         "meaning": "\u5b66\u8d39",
         "example": "International tuition fees in NZ are around $30,000 per year.", "example_cn": "NZ\u56fd\u9645\u5b66\u751f\u5b66\u8d39\u7ea6\u6bcf\u5e743\u4e07\u3002", "scene": "\ud83d\udcda \u7559\u5b66\u8d39\u7528",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "international", "phonetic": "/\u02cc\u026ant\u0259\u02c8n\u00e6\u0283\u0259n\u0259l/", "syllable": "in\u00b7ter\u00b7na\u00b7tion\u00b7al", "meaning": "adj. \u56fd\u9645\u7684"}
         ]},
        {"word": "tutorial", "phonetic": "/tju\u02d0\u02c8t\u0254\u02d0ri\u0259l/", "syllable": "tu\u00b7to\u00b7ri\u00b7al", "pos": "n.",
         "meaning": "\u8f85\u5bfc\u8bfe\uff1b\u5c0f\u73ed\u8bfe",
         "example": "I have a chemistry tutorial every Wednesday afternoon.", "example_cn": "\u6211\u6bcf\u5468\u4e09\u4e0b\u5348\u6709\u5316\u5b66\u8f85\u5bfc\u8bfe\u3002", "scene": "\ud83d\udcda \u5b66\u4e60",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "chemistry", "phonetic": "/\u02c8kem\u026astri/", "syllable": "chem\u00b7is\u00b7try", "meaning": "n. \u5316\u5b66"}
         ]},
        {"word": "dissertation", "phonetic": "/\u02ccd\u026as\u0259\u02c8te\u026a\u0283\u0259n/", "syllable": "dis\u00b7ser\u00b7ta\u00b7tion", "pos": "n.",
         "meaning": "\u5b66\u4f4d\u8bba\u6587",
         "example": "My dissertation focuses on NZ immigration policy.", "example_cn": "\u6211\u7684\u8bba\u6587\u7814\u7a76\u65b0\u897f\u5170\u79fb\u6c11\u653f\u7b56\u3002", "scene": "\ud83d\udcda \u5927\u5b66",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "focuses on", "phonetic": "/\u02c8f\u0259\u028ak\u0259s\u026az \u0252n/", "syllable": "fo\u00b7cus\u00b7es on", "meaning": "v. \u4e13\u6ce8\u4e8e"}
         ]},
        {"word": "credential", "phonetic": "/kr\u026a\u02c8den\u0283\u0259l/", "syllable": "cre\u00b7den\u00b7tial", "pos": "n.",
         "meaning": "\u8d44\u683c\u8bc1\u4e66\uff1b\u51ed\u8bc1",
         "example": "Your professional credentials need to be verified by NZQA.", "example_cn": "\u4f60\u7684\u4e13\u4e1a\u8d44\u8d28\u9700\u8981NZQA\u8ba4\u8bc1\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1\u6750\u6599",
         "grammar": "need to be+\u8fc7\u53bb\u5206\u8bcd",
         "sentence_words": [
             {"word": "verified", "phonetic": "/\u02c8ver\u026afa\u026ad/", "syllable": "ver\u00b7i\u00b7fied", "meaning": "v. \u8ba4\u8bc1"}
         ]},
        {"word": "accommodate", "phonetic": "/\u0259\u02c8k\u0252m\u0259de\u026at/", "syllable": "ac\u00b7com\u00b7mo\u00b7date", "pos": "v.",
         "meaning": "\u5bb9\u7eb3\uff1b\u63d0\u4f9b\u4f4f\u5bbf",
         "example": "The university can accommodate over 5,000 international students.", "example_cn": "\u5927\u5b66\u80fd\u5bb9\u7eb35000\u591a\u540d\u56fd\u9645\u5b66\u751f\u3002", "scene": "\ud83d\udcda \u5927\u5b66",
         "grammar": "\u60c5\u6001\u52a8\u8bcd+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "international students", "phonetic": "/\u02cc\u026ant\u0259\u02c8n\u00e6\u0283\u0259n\u0259l \u02c8stju\u02d0d\u0259nts/", "syllable": "in\u00b7ter\u00b7na\u00b7tion\u00b7al stu\u00b7dents", "meaning": "n. \u56fd\u9645\u5b66\u751f"}
         ]},
        {"word": "expenditure", "phonetic": "/\u026ak\u02c8spend\u026at\u0283\u0259/", "syllable": "ex\u00b7pen\u00b7di\u00b7ture", "pos": "n.",
         "meaning": "\u652f\u51fa\uff1b\u82b1\u8d39",
         "example": "Government expenditure on healthcare has increased steadily.", "example_cn": "\u653f\u5e9c\u5728\u533b\u7597\u4e0a\u7684\u652f\u51fa\u7a33\u6b65\u589e\u957f\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "healthcare", "phonetic": "/\u02c8hel\u03b8ke\u0259/", "syllable": "health\u00b7care", "meaning": "n. \u533b\u7597"}
         ]},
        {"word": "inequality", "phonetic": "/\u02cc\u026an\u026a\u02c8kw\u0252l\u0259ti/", "syllable": "in\u00b7e\u00b7qual\u00b7i\u00b7ty", "pos": "n.",
         "meaning": "\u4e0d\u5e73\u7b49",
         "example": "Income inequality remains a significant issue in NZ.", "example_cn": "\u6536\u5165\u4e0d\u5e73\u7b49\u4ecd\u662fNZ\u7684\u91cd\u8981\u95ee\u9898\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "income", "phonetic": "/\u02c8\u026ank\u028cm/", "syllable": "in\u00b7come", "meaning": "n. \u6536\u5165"}
         ]},
        {"word": "assimilate", "phonetic": "/\u0259\u02c8s\u026am\u026ale\u026at/", "syllable": "as\u00b7sim\u00b7i\u00b7late", "pos": "v.",
         "meaning": "\u540c\u5316\uff1b\u878d\u5165",
         "example": "New migrants often struggle to assimilate into the local culture.", "example_cn": "\u65b0\u79fb\u6c11\u5e38\u5e38\u96be\u4ee5\u878d\u5165\u5f53\u5730\u6587\u5316\u3002", "scene": "\ud83d\udccb \u79fb\u6c11\u751f\u6d3b",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "migrant", "phonetic": "/\u02c8ma\u026a\u0261r\u0259nt/", "syllable": "mi\u00b7grant", "meaning": "n. \u79fb\u6c11"}
         ]},
        {"word": "entrepreneur", "phonetic": "/\u02cc\u0252ntr\u0259pr\u0259\u02c8n\u025c\u02d0/", "syllable": "en\u00b7tre\u00b7pre\u00b7neur", "pos": "n.",
         "meaning": "\u4f01\u4e1a\u5bb6\uff1b\u521b\u4e1a\u8005",
         "example": "The government offers grants for young entrepreneurs.", "example_cn": "\u653f\u5e9c\u4e3a\u5e74\u8f7b\u521b\u4e1a\u8005\u63d0\u4f9b\u8d44\u52a9\u3002", "scene": "\ud83d\udcbc \u804c\u4e1a\u53d1\u5c55",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "grants", "phonetic": "/\u0261r\u0251\u02d0nts/", "syllable": "grants", "meaning": "n. \u8d44\u52a9\uff1b\u62e8\u6b3e"}
         ]},
        {"word": "freelance", "phonetic": "/\u02c8fri\u02d0l\u0251\u02d0ns/", "syllable": "free\u00b7lance", "pos": "adj./v.",
         "meaning": "\u81ea\u7531\u804c\u4e1a\u7684",
         "example": "More people are choosing freelance work over traditional employment.", "example_cn": "\u8d8a\u6765\u8d8a\u591a\u4eba\u9009\u62e9\u81ea\u7531\u804c\u4e1a\u800c\u975e\u4f20\u7edf\u5c31\u4e1a\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c/\u751f\u6d3b",
         "grammar": "\u6bd4\u8f83\u7ed3\u6784",
         "sentence_words": [
             {"word": "traditional", "phonetic": "/tr\u0259\u02c8d\u026a\u0283\u0259n\u0259l/", "syllable": "tra\u00b7di\u00b7tion\u00b7al", "meaning": "adj. \u4f20\u7edf\u7684"}
         ]},
        {"word": "remuneration", "phonetic": "/r\u026a\u02ccmju\u02d0n\u0259\u02c8re\u026a\u0283\u0259n/", "syllable": "re\u00b7mu\u00b7ner\u00b7a\u00b7tion", "pos": "n.",
         "meaning": "\u62a5\u916c\uff1b\u85aa\u916c",
         "example": "The remuneration package includes salary, super and health insurance.", "example_cn": "\u85aa\u916c\u5305\u5305\u62ec\u5de5\u8d44\u3001\u517b\u8001\u91d1\u548c\u533b\u7597\u4fdd\u9669\u3002", "scene": "\ud83d\udcbc \u85aa\u8d44",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "salary", "phonetic": "/\u02c8s\u00e6l\u0259ri/", "syllable": "sal\u00b7a\u00b7ry", "meaning": "n. \u5de5\u8d44"},
             {"word": "insurance", "phonetic": "/\u026an\u02c8\u0283\u028a\u0259r\u0259ns/", "syllable": "in\u00b7sur\u00b7ance", "meaning": "n. \u4fdd\u9669"}
         ]},
        {"word": "probation", "phonetic": "/pr\u0259\u02c8be\u026a\u0283\u0259n/", "syllable": "pro\u00b7ba\u00b7tion", "pos": "n.",
         "meaning": "\u8bd5\u7528\u671f",
         "example": "You'll be on a 3-month probation period.", "example_cn": "\u4f60\u5c06\u67093\u4e2a\u6708\u7684\u8bd5\u7528\u671f\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u4e00\u822c\u5c06\u6765\u65f6",
         "sentence_words": [
             {"word": "period", "phonetic": "/\u02c8p\u026a\u0259ri\u0259d/", "syllable": "pe\u00b7ri\u00b7od", "meaning": "n. \u671f\u95f4"}
         ]},
        {"word": "redundancy", "phonetic": "/r\u026a\u02c8d\u028cnd\u0259nsi/", "syllable": "re\u00b7dun\u00b7dan\u00b7cy", "pos": "n.",
         "meaning": "\u88c1\u5458\uff1b\u5197\u4f59",
         "example": "He was made redundant when the company downsized.", "example_cn": "\u516c\u53f8\u7f29\u7f16\u65f6\u4ed6\u88ab\u88c1\u4e86\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "downsized", "phonetic": "/\u02c8da\u028ansa\u026azd/", "syllable": "down\u00b7sized", "meaning": "v. \u7f29\u7f16"}
         ]},
        {"word": "inflation", "phonetic": "/\u026an\u02c8fle\u026a\u0283\u0259n/", "syllable": "in\u00b7fla\u00b7tion", "pos": "n.",
         "meaning": "\u901a\u8d27\u81a8\u80c0",
         "example": "Inflation in NZ reached 7.3% last year.", "example_cn": "NZ\u53bb\u5e74\u901a\u80c0\u7387\u8fbe\u52307.3%\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "reached", "phonetic": "/ri\u02d0t\u0283t/", "syllable": "reached", "meaning": "v. \u8fbe\u5230"}
         ]},
        {"word": "census", "phonetic": "/\u02c8sens\u0259s/", "syllable": "cen\u00b7sus", "pos": "n.",
         "meaning": "\u4eba\u53e3\u666e\u67e5",
         "example": "The NZ census is conducted every five years.", "example_cn": "NZ\u4eba\u53e3\u666e\u67e5\u6bcf\u4e94\u5e74\u8fdb\u884c\u4e00\u6b21\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "conducted", "phonetic": "/k\u0259n\u02c8d\u028ckt\u026ad/", "syllable": "con\u00b7duc\u00b7ted", "meaning": "v. \u8fdb\u884c"}
         ]},
        {"word": "adolescent", "phonetic": "/\u02cc\u00e6d\u0259\u02c8les\u0259nt/", "syllable": "ad\u00b7o\u00b7les\u00b7cent", "pos": "n./adj.",
         "meaning": "\u9752\u5c11\u5e74\uff1b\u9752\u6625\u671f\u7684",
         "example": "Adolescent mental health is a growing concern in NZ.", "example_cn": "\u9752\u5c11\u5e74\u5fc3\u7406\u5065\u5eb7\u662fNZ\u65e5\u76ca\u5173\u6ce8\u7684\u95ee\u9898\u3002", "scene": "\ud83c\udfe5 \u5fc3\u7406\u5065\u5eb7",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "mental health", "phonetic": "/\u02c8ment\u0259l hel\u03b8/", "syllable": "men\u00b7tal health", "meaning": "n. \u5fc3\u7406\u5065\u5eb7"}
         ]},
        {"word": "nutrient", "phonetic": "/\u02c8nju\u02d0tri\u0259nt/", "syllable": "nu\u00b7tri\u00b7ent", "pos": "n.",
         "meaning": "\u8425\u517b\u7d20",
         "example": "A balanced diet provides all essential nutrients.", "example_cn": "\u5747\u8861\u996e\u98df\u63d0\u4f9b\u6240\u6709\u5fc5\u9700\u8425\u517b\u7d20\u3002", "scene": "\ud83c\udfe5 \u996e\u98df\u5065\u5eb7",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "balanced diet", "phonetic": "/\u02c8b\u00e6l\u0259nst \u02c8da\u026a\u0259t/", "syllable": "bal\u00b7anced di\u00b7et", "meaning": "n. \u5747\u8861\u996e\u98df"}
         ]},
        {"word": "sedentary", "phonetic": "/\u02c8sed\u0259nt\u0259ri/", "syllable": "sed\u00b7en\u00b7tar\u00b7y", "pos": "adj.",
         "meaning": "\u4e45\u5750\u7684",
         "example": "A sedentary lifestyle increases the risk of heart disease.", "example_cn": "\u4e45\u5750\u7684\u751f\u6d3b\u65b9\u5f0f\u589e\u52a0\u5fc3\u810f\u75c5\u98ce\u9669\u3002", "scene": "\ud83c\udfe5 \u5065\u5eb7",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "lifestyle", "phonetic": "/\u02c8la\u026afsta\u026al/", "syllable": "life\u00b7style", "meaning": "n. \u751f\u6d3b\u65b9\u5f0f"}
         ]},
        {"word": "rehabilitation", "phonetic": "/\u02ccri\u02d0h\u0259\u02ccb\u026al\u026a\u02c8te\u026a\u0283\u0259n/", "syllable": "re\u00b7ha\u00b7bil\u00b7i\u00b7ta\u00b7tion", "pos": "n.",
         "meaning": "\u5eb7\u590d\uff1b\u6062\u590d",
         "example": "ACC provides rehabilitation services for accident victims.", "example_cn": "ACC\u4e3a\u610f\u5916\u53d7\u5bb3\u8005\u63d0\u4f9b\u5eb7\u590d\u670d\u52a1\u3002", "scene": "\ud83c\udfe5 \u5eb7\u590d",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "services", "phonetic": "/\u02c8s\u025c\u02d0v\u026as\u026az/", "syllable": "ser\u00b7vic\u00b7es", "meaning": "n. \u670d\u52a1"}
         ]},
        {"word": "wellbeing", "phonetic": "/wel\u02c8bi\u02d0\u026a\u014b/", "syllable": "well\u00b7be\u00b7ing", "pos": "n.",
         "meaning": "\u798f\u7949\uff1b\u5065\u5eb7",
         "example": "The government has launched a wellbeing budget.", "example_cn": "\u653f\u5e9c\u63a8\u51fa\u4e86\u798f\u7949\u9884\u7b97\u3002", "scene": "\ud83c\udfe5 \u5fc3\u7406\u5065\u5eb7",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "budget", "phonetic": "/\u02c8b\u028cd\u0292\u026at/", "syllable": "bud\u00b7get", "meaning": "n. \u9884\u7b97"}
         ]},
        {"word": "pedestrian", "phonetic": "/p\u0259\u02c8destri\u0259n/", "syllable": "pe\u00b7des\u00b7tri\u00b7an", "pos": "n./adj.",
         "meaning": "\u884c\u4eba\uff1b\u6b65\u884c\u7684",
         "example": "Pedestrian safety is a priority in urban planning.", "example_cn": "\u884c\u4eba\u5b89\u5168\u662f\u57ce\u5e02\u89c4\u5212\u7684\u4f18\u5148\u4e8b\u9879\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "priority", "phonetic": "/pra\u026a\u02c8\u0252r\u0259ti/", "syllable": "pri\u00b7or\u00b7i\u00b7ty", "meaning": "n. \u4f18\u5148\u4e8b\u9879"}
         ]},
        {"word": "commute", "phonetic": "/k\u0259\u02c8mju\u02d0t/", "syllable": "com\u00b7mute", "pos": "v./n.",
         "meaning": "\u901a\u52e4",
         "example": "The average commute time in Auckland is about 30 minutes.", "example_cn": "\u5965\u514b\u5170\u5e73\u5747\u901a\u52e4\u65f6\u95f4\u7ea630\u5206\u949f\u3002", "scene": "\ud83d\ude8c \u4ea4\u901a\u51fa\u884c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "average", "phonetic": "/\u02c8\u00e6v\u0259r\u026ad\u0292/", "syllable": "av\u00b7er\u00b7age", "meaning": "adj. \u5e73\u5747\u7684"}
         ]},
        {"word": "conservation", "phonetic": "/\u02cck\u0252ns\u0259\u02c8ve\u026a\u0283\u0259n/", "syllable": "con\u00b7ser\u00b7va\u00b7tion", "pos": "n.",
         "meaning": "\u4fdd\u62a4\uff1b\u4fdd\u80b2",
         "example": "NZ has strong conservation policies for native species.", "example_cn": "NZ\u5bf9\u672c\u571f\u7269\u79cd\u6709\u4e25\u683c\u7684\u4fdd\u62a4\u653f\u7b56\u3002", "scene": "\ud83c\udf0d \u73af\u5883",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "native species", "phonetic": "/\u02c8ne\u026at\u026av \u02c8spi\u02d0\u0283i\u02d0z/", "syllable": "na\u00b7tive spe\u00b7cies", "meaning": "n. \u672c\u571f\u7269\u79cd"}
         ]},
        {"word": "ecosystem", "phonetic": "/\u02c8i\u02d0k\u0259\u028as\u026ast\u0259m/", "syllable": "e\u00b7co\u00b7sys\u00b7tem", "pos": "n.",
         "meaning": "\u751f\u6001\u7cfb\u7edf",
         "example": "The marine ecosystem around NZ is incredibly diverse.", "example_cn": "NZ\u5468\u56f4\u6d77\u6d0b\u751f\u6001\u7cfb\u7edf\u6781\u5176\u591a\u6837\u3002", "scene": "\ud83c\udf0d \u73af\u5883",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "marine", "phonetic": "/m\u0259\u02c8ri\u02d0n/", "syllable": "ma\u00b7rine", "meaning": "adj. \u6d77\u6d0b\u7684"},
             {"word": "diverse", "phonetic": "/da\u026a\u02c8v\u025c\u02d0s/", "syllable": "di\u00b7verse", "meaning": "adj. \u591a\u6837\u7684"}
         ]},
        {"word": "sustainable", "phonetic": "/s\u0259\u02c8ste\u026an\u0259b\u0259l/", "syllable": "sus\u00b7tain\u00b7a\u00b7ble", "pos": "adj.",
         "meaning": "\u53ef\u6301\u7eed\u7684",
         "example": "NZ aims to be carbon neutral by 2050 through sustainable practices.", "example_cn": "NZ\u901a\u8fc7\u53ef\u6301\u7eed\u5b9e\u8df5\u76ee\u68072050\u5e74\u78b3\u4e2d\u548c\u3002", "scene": "\ud83c\udf0d \u73af\u4fdd/\u80fd\u6e90",
         "grammar": "\u4e0d\u5b9a\u5f0f",
         "sentence_words": [
             {"word": "carbon neutral", "phonetic": "/\u02c8k\u0251\u02d0b\u0259n \u02c8nju\u02d0tr\u0259l/", "syllable": "car\u00b7bon neu\u00b7tral", "meaning": "phrase \u78b3\u4e2d\u548c"}
         ]},
        {"word": "horticulture", "phonetic": "/\u02c8h\u0254\u02d0t\u026ak\u028clt\u0283\u0259/", "syllable": "hor\u00b7ti\u00b7cul\u00b7ture", "pos": "n.",
         "meaning": "\u56ed\u827a\uff1b\u56ed\u827a\u5b66",
         "example": "NZ's horticulture industry is a major export earner.", "example_cn": "NZ\u56ed\u827a\u4ea7\u4e1a\u662f\u4e3b\u8981\u51fa\u53e3\u6536\u5165\u6765\u6e90\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "export", "phonetic": "/\u026ak\u02c8sp\u0254\u02d0t/", "syllable": "ex\u00b7port", "meaning": "n. \u51fa\u53e3"}
         ]},
        {"word": "legislation", "phonetic": "/\u02ccled\u0292\u026as\u02c8le\u026a\u0283\u0259n/", "syllable": "leg\u00b7is\u00b7la\u00b7tion", "pos": "n.",
         "meaning": "\u6cd5\u5f8b\uff1b\u6cd5\u89c4",
         "example": "New legislation aims to protect migrant workers' rights.", "example_cn": "\u65b0\u6cd5\u89c4\u65e8\u5728\u4fdd\u62a4\u79fb\u6c11\u5de5\u6743\u5229\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1/\u79fb\u6c11",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "migrant workers", "phonetic": "/\u02c8ma\u026a\u0261r\u0259nt \u02c8w\u025c\u02d0k\u0259z/", "syllable": "mi\u00b7grant work\u00b7ers", "meaning": "n. \u79fb\u6c11\u5de5\u4eba"}
         ]},
        {"word": "jurisdiction", "phonetic": "/\u02ccd\u0292\u028a\u0259r\u026as\u02c8d\u026ak\u0283\u0259n/", "syllable": "ju\u00b7ris\u00b7dic\u00b7tion", "pos": "n.",
         "meaning": "\u7ba1\u8f96\u6743\uff1b\u53f8\u6cd5\u533a",
         "example": "This falls under NZ jurisdiction.", "example_cn": "\u8fd9\u5c5e\u4e8eNZ\u7ba1\u8f96\u8303\u56f4\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "falls under", "phonetic": "/f\u0254\u02d0lz \u02c8\u028cnd\u0259/", "syllable": "falls un\u00b7der", "meaning": "v. \u5c5e\u4e8e"}
         ]},
        {"word": "diploma", "phonetic": "/d\u026a\u02c8pl\u0259\u028am\u0259/", "syllable": "di\u00b7plo\u00b7ma", "pos": "n.",
         "meaning": "\u6587\u51ed\uff1b\u6bd5\u4e1a\u8bc1\u4e66",
         "example": "A Level 7 diploma is equivalent to a bachelor's degree.", "example_cn": "7\u7ea7\u6587\u51ed\u76f8\u5f53\u4e8e\u5b66\u58eb\u5b66\u4f4d\u3002", "scene": "\ud83c\udf93 \u5b66\u6821\u6559\u80b2",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "equivalent", "phonetic": "/\u026a\u02c8kw\u026av\u0259l\u0259nt/", "syllable": "e\u00b7quiv\u00b7a\u00b7lent", "meaning": "adj. \u76f8\u5f53\u7684"}
         ]},
        {"word": "bachelor's degree", "phonetic": "/\u02c8b\u00e6t\u0283\u0259l\u0259z d\u026a\u02c8\u0261ri\u02d0/", "syllable": "bach\u00b7e\u00b7lor's de\u00b7gree", "pos": "n.",
         "meaning": "\u5b66\u58eb\u5b66\u4f4d",
         "example": "A typical bachelor's degree in NZ takes three years.", "example_cn": "NZ\u5b66\u58eb\u5b66\u4f4d\u901a\u5e38\u4e09\u5e74\u3002", "scene": "\ud83d\udcda \u5927\u5b66",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "typical", "phonetic": "/\u02c8t\u026ap\u026ak\u0259l/", "syllable": "typ\u00b7i\u00b7cal", "meaning": "adj. \u5178\u578b\u7684"}
         ]},
        {"word": "peer-reviewed", "phonetic": "/p\u026a\u0259 r\u026a\u02c8vju\u02d0d/", "syllable": "peer-re\u00b7viewed", "pos": "adj.",
         "meaning": "\u540c\u884c\u8bc4\u5ba1\u7684",
         "example": "Only peer-reviewed journals should be cited in academic papers.", "example_cn": "\u5b66\u672f\u8bba\u6587\u53ea\u5e94\u5f15\u7528\u540c\u884c\u8bc4\u5ba1\u671f\u520a\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u60c5\u6001\u52a8\u8bcd+\u88ab\u52a8",
         "sentence_words": [
             {"word": "cited", "phonetic": "/\u02c8sa\u026at\u026ad/", "syllable": "cit\u00b7ed", "meaning": "v. \u5f15\u7528"},
             {"word": "journal", "phonetic": "/\u02c8d\u0292\u025c\u02d0n\u0259l/", "syllable": "jour\u00b7nal", "meaning": "n. \u671f\u520a"}
         ]},
        {"word": "methodology", "phonetic": "/\u02ccme\u03b8\u0259\u02c8d\u0252l\u0259d\u0292i/", "syllable": "meth\u00b7od\u00b7ol\u00b7o\u00b7gy", "pos": "n.",
         "meaning": "\u65b9\u6cd5\u8bba",
         "example": "The research methodology was both qualitative and quantitative.", "example_cn": "\u7814\u7a76\u65b9\u6cd5\u8bba\u517c\u5177\u5b9a\u6027\u548c\u5b9a\u91cf\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "qualitative", "phonetic": "/\u02c8kw\u0252l\u026at\u0259t\u026av/", "syllable": "qual\u00b7i\u00b7ta\u00b7tive", "meaning": "adj. \u5b9a\u6027\u7684"},
             {"word": "quantitative", "phonetic": "/\u02c8kw\u0252nt\u026at\u0259t\u026av/", "syllable": "quan\u00b7ti\u00b7ta\u00b7tive", "meaning": "adj. \u5b9a\u91cf\u7684"}
         ]},
        {"word": "hypothesis", "phonetic": "/ha\u026a\u02c8p\u0252\u03b8\u0259s\u026as/", "syllable": "hy\u00b7poth\u00b7e\u00b7sis", "pos": "n.",
         "meaning": "\u5047\u8bf4\uff1b\u5047\u8bbe",
         "example": "The hypothesis was supported by the experimental data.", "example_cn": "\u5b9e\u9a8c\u6570\u636e\u652f\u6301\u4e86\u8be5\u5047\u8bbe\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "experimental", "phonetic": "/\u026ak\u02ccsper\u026a\u02c8ment\u0259l/", "syllable": "ex\u00b7per\u00b7i\u00b7men\u00b7tal", "meaning": "adj. \u5b9e\u9a8c\u7684"}
         ]},
        {"word": "ergonomic", "phonetic": "/\u02cc\u025c\u02d0\u0261\u0259\u02c8n\u0252m\u026ak/", "syllable": "er\u00b7go\u00b7nom\u00b7ic", "pos": "adj.",
         "meaning": "\u4eba\u4f53\u5de5\u7a0b\u5b66\u7684",
         "example": "Using ergonomic equipment reduces workplace injuries.", "example_cn": "\u4f7f\u7528\u4eba\u4f53\u5de5\u7a0b\u5b66\u8bbe\u5907\u51cf\u5c11\u5de5\u4f24\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u52a8\u540d\u8bcd\u4e3b\u8bed",
         "sentence_words": [
             {"word": "workplace injuries", "phonetic": "/\u02c8w\u025c\u02d0kple\u026as \u02c8\u026and\u0292\u0259riz/", "syllable": "work\u00b7place in\u00b7ju\u00b7ries", "meaning": "n. \u5de5\u4f24"}
         ]},
        {"word": "advocate", "phonetic": "/\u02c8\u00e6dv\u0259ke\u026at/", "syllable": "ad\u00b7vo\u00b7cate", "pos": "v./n.",
         "meaning": "\u5021\u5bfc\uff1b\u62e5\u62a4\u8005",
         "example": "Many groups advocate for tighter environmental regulations.", "example_cn": "\u8bb8\u591a\u56e2\u4f53\u5021\u5bfc\u66f4\u4e25\u683c\u7684\u73af\u4fdd\u6cd5\u89c4\u3002", "scene": "\ud83c\udf0d \u73af\u5883",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "regulations", "phonetic": "/\u02ccre\u0261j\u028a\u02c8le\u026a\u0283\u0259nz/", "syllable": "reg\u00b7u\u00b7la\u00b7tions", "meaning": "n. \u6cd5\u89c4"}
         ]},
        {"word": "implement", "phonetic": "/\u02c8\u026ampl\u026ament/", "syllable": "im\u00b7ple\u00b7ment", "pos": "v.",
         "meaning": "\u5b9e\u65bd\uff1b\u6267\u884c",
         "example": "The government plans to implement new immigration policies.", "example_cn": "\u653f\u5e9c\u8ba1\u5212\u5b9e\u65bd\u65b0\u7684\u79fb\u6c11\u653f\u7b56\u3002", "scene": "\ud83d\udccb \u79fb\u6c11",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "policies", "phonetic": "/\u02c8p\u0252l\u026asiz/", "syllable": "pol\u00b7i\u00b7cies", "meaning": "n. \u653f\u7b56"}
         ]},
        {"word": "decline", "phonetic": "/d\u026a\u02c8kla\u026an/", "syllable": "de\u00b7cline", "pos": "v./n.",
         "meaning": "\u4e0b\u964d\uff1b\u8870\u9000",
         "example": "The population of rural areas has been in steady decline.", "example_cn": "\u519c\u6751\u4eba\u53e3\u4e00\u76f4\u5728\u7a33\u6b65\u4e0b\u964d\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u73b0\u5728\u5b8c\u6210\u65f6",
         "sentence_words": [
             {"word": "steady", "phonetic": "/\u02c8stedi/", "syllable": "stead\u00b7y", "meaning": "adj. \u7a33\u6b65\u7684"}
         ]},
        {"word": "embrace", "phonetic": "/\u026am\u02c8bre\u026as/", "syllable": "em\u00b7brace", "pos": "v.",
         "meaning": "\u62e5\u62b1\uff1b\u63a5\u53d7",
         "example": "NZ was one of the first countries to embrace same-sex marriage.", "example_cn": "NZ\u662f\u6700\u65e9\u63a5\u53d7\u540c\u6027\u5a5a\u59fb\u7684\u56fd\u5bb6\u4e4b\u4e00\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e0d\u5b9a\u5f0f",
         "sentence_words": [
             {"word": "same-sex marriage", "phonetic": "/se\u026am seks \u02c8m\u00e6r\u026ad\u0292/", "syllable": "same-sex mar\u00b7riage", "meaning": "n. \u540c\u6027\u5a5a\u59fb"}
         ]},
        {"word": "resilience", "phonetic": "/r\u026a\u02c8z\u026ali\u0259ns/", "syllable": "re\u00b7sil\u00b7ience", "pos": "n.",
         "meaning": "\u97e7\u6027\uff1b\u6062\u590d\u529b",
         "example": "The community showed remarkable resilience after the earthquake.", "example_cn": "\u793e\u533a\u5728\u5730\u9707\u540e\u5c55\u73b0\u4e86\u975e\u51e1\u7684\u97e7\u6027\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u8fc7\u53bb\u65f6",
         "sentence_words": [
             {"word": "remarkable", "phonetic": "/r\u026a\u02c8m\u0251\u02d0k\u0259b\u0259l/", "syllable": "re\u00b7mark\u00b7a\u00b7ble", "meaning": "adj. \u975e\u51e1\u7684"}
         ]},
        {"word": "threshold", "phonetic": "/\u02c8\u03b8re\u0283h\u0259\u028ald/", "syllable": "thresh\u00b7old", "pos": "n.",
         "meaning": "\u95e8\u69db\uff1b\u4e34\u754c\u70b9",
         "example": "You need to earn above a certain threshold to qualify.", "example_cn": "\u4f60\u9700\u8981\u6536\u5165\u8d85\u8fc7\u4e00\u5b9a\u95e8\u69db\u624d\u80fd\u7b26\u5408\u6761\u4ef6\u3002", "scene": "\ud83d\udccb \u7b7e\u8bc1/\u79fb\u6c11",
         "grammar": "need to+\u52a8\u8bcd",
         "sentence_words": [
             {"word": "qualify", "phonetic": "/\u02c8kw\u0252l\u026afa\u026a/", "syllable": "qual\u00b7i\u00b7fy", "meaning": "v. \u7b26\u5408\u6761\u4ef6"}
         ]},
        {"word": "statutory", "phonetic": "/\u02c8st\u00e6t\u0283\u0259t\u0259ri/", "syllable": "stat\u00b7u\u00b7to\u00b7ry", "pos": "adj.",
         "meaning": "\u6cd5\u5b9a\u7684",
         "example": "Employees are entitled to 4 weeks of statutory annual leave.", "example_cn": "\u5458\u5de5\u6709\u6743\u4eab\u53d74\u5468\u6cd5\u5b9a\u5e74\u5047\u3002", "scene": "\ud83d\udcbc \u5de5\u4f5c",
         "grammar": "\u88ab\u52a8\u8bed\u6001",
         "sentence_words": [
             {"word": "entitled to", "phonetic": "/\u026an\u02c8ta\u026atld tu\u02d0/", "syllable": "en\u00b7titled to", "meaning": "adj. \u6709\u6743\u4eab\u53d7"}
         ]},
        {"word": "endeavour", "phonetic": "/\u026an\u02c8dev\u0259/", "syllable": "en\u00b7deav\u00b7our", "pos": "n./v.",
         "meaning": "\u52aa\u529b\uff1b\u5c1d\u8bd5",
         "example": "Learning a new language requires considerable endeavour.", "example_cn": "\u5b66\u4e60\u65b0\u8bed\u8a00\u9700\u8981\u76f8\u5f53\u5927\u7684\u52aa\u529b\u3002", "scene": "\ud83d\udcdd \u96c5\u601d\u5199\u4f5c",
         "grammar": "\u4e00\u822c\u73b0\u5728\u65f6",
         "sentence_words": [
             {"word": "considerable", "phonetic": "/k\u0259n\u02c8s\u026ad\u0259r\u0259b\u0259l/", "syllable": "con\u00b7sid\u00b7er\u00b7a\u00b7ble", "meaning": "adj. \u76f8\u5f53\u5927\u7684"}
         ]},
    ],
}


# ============================================================
# 去重：读取已使用的单词
# ============================================================
def _get_memory_path():
    """获取 memory.md 路径，repo 根目录（GitHub Actions 和本地统一）"""
    return BASE_DIR / "memory.md"

def load_used_words():
    """从 memory.md 中提取已使用过的单词"""
    memory_path = _get_memory_path()
    if not memory_path.exists():
        return set()

    content = memory_path.read_text(encoding='utf-8-sig')
    used = set()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('- ') and ':' in line:
            # 格式: - 2026-04-03: word1, word2, ...
            date_part, words_part = line.split(':', 1)
            words = [w.strip().lower() for w in words_part.split(',') if w.strip()]
            used.update(words)
    return used


def load_used_dates():
    """从 memory.md 中提取已有记录的日期集合，用于防止同一天重复生成"""
    memory_path = _get_memory_path()
    if not memory_path.exists():
        return set()
    content = memory_path.read_text(encoding='utf-8-sig')
    dates = set()
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('- ') and ':' in line:
            date_part = line.split(':', 1)[0].strip('- ').strip()
            if date_part:
                dates.add(date_part)
    return dates


def save_used_words(today_words):
    """将今天的单词追加到 memory.md（追加到单词区末尾，保持时间顺序）"""
    memory_path = _get_memory_path()
    word_list = ', '.join(w['word'] for w in today_words)
    new_line = f"- {TODAY}: {word_list}\n"

    if not memory_path.exists():
        memory_path.write_text(
            "# 每日英语单词 - 自动化执行记录\n\n## 单词去重记录\n" + new_line + "\n## 歌曲历史\n",
            encoding='utf-8'
        )
    else:
        content = memory_path.read_text(encoding='utf-8-sig')
        # 找到单词区的末尾（在 ## 歌曲历史 之前），追加新行
        if "## 歌曲历史" in content:
            # 在 ## 歌曲历史 前插入新行
            content = content.replace("## 歌曲历史", new_line + "\n## 歌曲历史", 1)
        else:
            # 没有歌曲历史标记，直接追加
            if not content.endswith('\n'):
                content += '\n'
            content += new_line
        memory_path.write_text(content, encoding='utf-8')


# ============================================================
# 随机选取今日单词
# ============================================================
def select_todays_words():
    """从词库随机选取10个词（7 NZ + 3 雅思），避免重复"""
    used = load_used_words()

    # Step 1: 先去重（词库本身有大量重复），保留每个词第一次出现的条目
    seen_nz = set()
    nz_unique = []
    for w in WORD_BANK["nz"]:
        key = w["word"].lower()
        if key not in seen_nz:
            seen_nz.add(key)
            nz_unique.append(w)

    seen_ielts = set()
    ielts_unique = []
    for w in WORD_BANK["ielts"]:
        key = w["word"].lower()
        if key not in seen_ielts:
            seen_ielts.add(key)
            ielts_unique.append(w)

    # Step 2: 过滤已使用的词
    nz_pool = [w for w in nz_unique if w["word"].lower() not in used]
    ielts_pool = [w for w in ielts_unique if w["word"].lower() not in used]

    # 如果去重后不够，从已用词中补充（优先选最早使用的词以最大化间隔）
    if len(nz_pool) < 7:
        reuse_nz = [w for w in nz_unique if w["word"].lower() in used]
        random.shuffle(reuse_nz)
        needed = 7 - len(nz_pool)
        nz_pool.extend(reuse_nz[:needed])
        if needed > 0:
            print(f"  [INFO] NZ可用词不足({len(nz_pool)-needed})，补充{min(needed, len(reuse_nz))}个已用词")
    if len(ielts_pool) < 3:
        reuse_ielts = [w for w in ielts_unique if w["word"].lower() in used]
        random.shuffle(reuse_ielts)
        needed = 3 - len(ielts_pool)
        ielts_pool.extend(reuse_ielts[:needed])
        if needed > 0:
            print(f"  [INFO] 雅思可用词不足({len(ielts_pool)-needed})，补充{min(needed, len(reuse_ielts))}个已用词")

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
            {"en": "Fancy seeing you here!", "phonetic": "/ˈfænsi ˈsiːɪŋ juː hɪər/", "syllable": "Fan·cy see·ing you here", "cn": "真巧在这儿碰到你！（惊喜偶遇）", "grammar": "Fancy + doing sth = 没想到会做某事（英式口语常用）"},
            {"en": "Mind if I join you?", "phonetic": "/maɪnd ɪf aɪ dʒɔɪn juː/", "syllable": "Mind if I join you?", "cn": "介意我一起吗？（礼貌询问）", "grammar": "Mind if + 从句 = 介意吗？（= Do you mind if...的省略）"},
            {"en": "I ran into you", "phonetic": "/aɪ ræn ˈɪntuː juː/", "syllable": "I ran in·to you", "cn": "我碰到你了（run into = 偶遇）", "grammar": "run into sb = 偶然遇到某人（run的过去式是ran）"},
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
            {"en": "Wanna grab a bite?", "phonetic": "/ˈwɒnə ɡræb ə baɪt/", "syllable": "Wan·na grab a bite?", "cn": "去吃点东西？（Wanna = Want to，bite = 一口食物）", "grammar": "Wanna = Want to 的口语缩写，grab a bite = 随便吃点"},
            {"en": "What are you in the mood for?", "phonetic": "/wɒt ɑː juː ɪn ðə muːd fɔː/", "syllable": "What are you in the mood for?", "cn": "你想吃什么？/你想干嘛？（in the mood for）", "grammar": "be in the mood for sth = 有心情做某事"},
            {"en": "go Dutch", "phonetic": "/ɡəʊ dʌtʃ/", "syllable": "go Dutch", "cn": "AA制（各自付账）", "grammar": "go Dutch = 各自付账（固定搭配，Dutch首字母大写）"},
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
            {"en": "My bad!", "phonetic": "/maɪ bæd/", "syllable": "My bad!", "cn": "我的错！（口语化道歉）", "grammar": "My bad = 我的错（非正式口语，= My fault）"},
            {"en": "right after", "phonetic": "/raɪt ˈɑːftər/", "syllable": "right af·ter", "cn": "……之后马上（表示立即行动）", "grammar": "right after = ...之后马上（right加强语气）"},
            {"en": "You said that yesterday.", "phonetic": "/juː sed ðæt ˈjestədeɪ/", "syllable": "You said that yes·ter·day.", "cn": "你昨天也是这么说的。（吐槽专用）", "grammar": "过去时：said（say的过去式）；吐槽对方食言常用句"},
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
            {"en": "Pretty good!", "phonetic": "/ˈprɪti ɡʊd/", "syllable": "Pret·ty good!", "cn": "挺好的！（比Just good更热情的回应）", "grammar": "pretty = 相当/挺（副词修饰形容词）"},
            {"en": "I need to get out more.", "phonetic": "/aɪ niːd tə ɡet aʊt mɔː/", "syllable": "I need to get out more.", "cn": "我得出去多走走/多社交。（常用自嘲）", "grammar": "need to do sth = 需要做某事；get out = 出去（反义：stay in 宅家）"},
            {"en": "You should come with us!", "phonetic": "/juː ʃʊd kʌm wɪð ʌs/", "syllable": "You should come with us!", "cn": "你应该跟我们一起去！（热情邀请）", "grammar": "should + 动词原形 = 应该...（表示建议）"},
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
            {"en": "Long time no see!", "phonetic": "/lɒŋ taɪm nəʊ siː/", "syllable": "Long time no see!", "cn": "好久不见！（经典口语问候）", "grammar": "中式英语来源的口语，现已被英语世界广泛使用"},
            {"en": "How have you been?", "phonetic": "/haʊ hæv juː biːn/", "syllable": "How have you been?", "cn": "你最近怎么样？（比How are you更关注对方状态）", "grammar": "现在完成时：have been = 一直以来的状态"},
            {"en": "You should check out...", "phonetic": "/juː ʃʊd tʃek aʊt/", "syllable": "You should check out...", "cn": "你应该去看看/试试……（推荐用句）", "grammar": "check out = 去看看/去体验（phrasal verb）"},
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
            {"en": "Are you free this Saturday?", "phonetic": "/ɑː juː friː ðɪs ˈsætədeɪ/", "syllable": "Are you free this Sat·ur·day?", "cn": "这周六有空吗？（约人必备句型）", "grammar": "一般疑问句：Are you + 形容词?（free = 有空的）"},
            {"en": "What's on?", "phonetic": "/wɒts ɒn/", "syllable": "What's on?", "cn": "有什么在上映？/有什么活动？（万能问句）", "grammar": "What's on? = 有什么（电影/活动）？（on = 在上映/在进行）"},
            {"en": "Sounds good!", "phonetic": "/saʊndz ɡʊd/", "syllable": "Sounds good!", "cn": "听起来不错！（轻松同意）", "grammar": "Sounds = It sounds 的省略（第三人称单数+s）"},
        ]
    },
    {
        "scene": "🏋️ 健身房",
        "lines": [
            ("A", "Hey! I haven't seen you here before.", "嘿！之前没见过你啊。"),
            ("B", "Yeah, I just joined last week.", "是的，我上周刚报名。"),
            ("A", "Welcome! How are you finding it so far?", "欢迎！你觉得怎么样？"),
            ("B", "Pretty good. The trainers are really helpful.", "挺不错的。教练们都很热心。"),
            ("A", "For sure. Do you have a workout plan?", "那倒是。你有训练计划吗？"),
            ("B", "Not yet. I'm still figuring things out.", "还没有。我还在熟悉情况。"),
        ],
        "expressions": [
            {"en": "I haven't seen you here before", "phonetic": "/aɪ ˈhævnt siːn juː hɪə bɪˈfɔː/", "syllable": "I haven't seen you here be·fore", "cn": "之前没见过你（口语寒暄）", "grammar": "现在完成时：have seen（第一次见面的寒暄语）"},
            {"en": "How are you finding it so far?", "phonetic": "/haʊ ɑː juː ˈfaɪndɪŋ ɪt səʊ fɑː/", "syllable": "How are you find·ing it so far?", "cn": "你觉得怎么样？（某段时间内的感受）", "grammar": "find + it + adj. = 发现它...；so far = 到目前为止"},
            {"en": "I'm still figuring things out", "phonetic": "/aɪm stɪl ˈfɪɡərɪŋ θɪŋz aʊt/", "syllable": "I'm still fig·ur·ing things out", "cn": "我还在摸索/想办法", "grammar": "figure out = 想明白，搞清楚（短语动词）"},
        ]
    },
    {
        "scene": "🏖️ 海边散步",
        "lines": [
            ("A", "What a beautiful day! The beach is so peaceful.", "多好的天气啊！海滩好安静。"),
            ("B", "I know right? Summer in NZ is the best.", "就是！新西兰的夏天最棒了。"),
            ("A", "Do you come here often?", "你常来这儿吗？"),
            ("B", "Whenever I can. It helps me relax after work.", "有空就来。帮我缓解工作压力。"),
            ("A", "Same here. Work gets pretty stressful sometimes.", "我也是。工作有时候压力挺大的。"),
            ("B", "Totally. That's why we need weekends like this.", "完全同意。所以我们才需要这样的周末。"),
        ],
        "expressions": [
            {"en": "I know right?", "phonetic": "/aɪ nəʊ raɪt/", "syllable": "I know right?", "cn": "就是啊！（强烈同意）", "grammar": "口语常用赞同表达 = I know, right?"},
            {"en": "Whenever I can", "phonetic": "/wenˈevər aɪ kæn/", "syllable": "When·ev·er I can", "cn": "有空就来（whenever = 无论何时）", "grammar": "whenever = 无论什么时候（比 when 更强调频率自由）"},
            {"en": "Totally", "phonetic": "/ˈtəʊtəli/", "syllable": "to·tal·ly", "cn": "完全同意！（口语加强语气）", "grammar": "副词，加强语气用（= absolutely / completely）"},
        ]
    },
    {
        "scene": "🚇 公交车",
        "lines": [
            ("A", "Excuse me, is this seat taken?", "不好意思，这个座位有人吗？"),
            ("B", "No, go ahead!", "没有，你坐吧！"),
            ("A", "Thanks! Do you know if this bus goes to the CBD?", "谢谢！你知道这趟车去市中心吗？"),
            ("B", "Yep, this is the right one. It's about 15 minutes.", "是的，就是这趟。大概15分钟。"),
            ("A", "Perfect. Thanks for letting me know.", "太好了。谢谢你告诉我。"),
            ("B", "No worries!", "不客气！"),
        ],
        "expressions": [
            {"en": "is this seat taken?", "phonetic": "/ɪz ðɪs siːt ˈteɪkən/", "syllable": "is this seat tak·en?", "cn": "这个座位有人吗？（公共场所礼貌询问）", "grammar": "被动语态：is taken = 被占了（take的过去分词）"},
            {"en": "go ahead!", "phonetic": "/ɡəʊ əˈhed/", "syllable": "go a·head!", "cn": "你坐吧！（允许别人用）", "grammar": "go ahead = 请便/去做吧（表示允许）"},
            {"en": "No worries!", "phonetic": "/nəʊ ˈwʌriz/", "syllable": "No wor·ries!", "cn": "不客气！/没关系！（澳洲/新西兰常用）", "grammar": "NZ & AUS 特色口语，等于You're welcome"},
        ]
    },
    {
        "scene": "🏦 银行办事",
        "lines": [
            ("A", "Hi, I'd like to open a bank account please.", "你好，我想开个银行账户。"),
            ("B", "Sure! Are you after a savings or a current account?", "好的！您要储蓄账户还是活期账户？"),
            ("A", "A savings account, I think.", "我想开储蓄账户。"),
            ("B", "No worries. I'll just need some ID and your address.", "没问题。只需要您的身份证件和地址。"),
            ("A", "Here you go. Is there a minimum deposit?", "给您。有最低存款要求吗？"),
            ("B", "Not for this account. You're all set!", "这个账户没有。我帮您都办好了！"),
        ],
        "expressions": [
            {"en": "I'd like to open a bank account", "phonetic": "/aɪd laɪk tə ˈəʊpən ə bæŋk əˈkaʊnt/", "syllable": "I'd like to o·pen a bank ac·count", "cn": "我想开个银行账户（正式请求）", "grammar": "I'd like to = I would like to（礼貌请求，比I want更客气）"},
            {"en": "Are you after...?", "phonetic": "/ɑː juː ˈɑːftər/", "syllable": "Are you af·ter...?", "cn": "您想要...？（NZ口语，代替Do you want...）", "grammar": "Are you after...? = 你要...？（NZ特色口语）"},
            {"en": "You're all set!", "phonetic": "/jɔːr ɔːl set/", "syllable": "You're all set!", "cn": "都办好了！（办完手续的结束语）", "grammar": "all set = 一切都准备好了/办妥了"},
        ]
    },
    {
        "scene": "🏥 看医生",
        "lines": [
            ("A", "Good morning. Do you have an appointment?", "早上好。您有预约吗？"),
            ("B", "Yes, I do. My name's Sarah. I booked for 10 o'clock.", "有的。我叫Sarah。约的10点。"),
            ("A", "Let me check... Yes, I can see you here. What seems to be the problem?", "我查一下……有的。请问您哪里不舒服？"),
            ("B", "I've had a bad headache for the past two days.", "我头连续疼了两天了。"),
            ("A", "Okay. Any other symptoms?", "好的。还有其他症状吗？"),
            ("B", "Just feeling a bit tired and dizzy sometimes.", "就是有时候感觉有点累和头晕。"),
        ],
        "expressions": [
            {"en": "What seems to be the problem?", "phonetic": "/wɒt siːmz tə bi ðə ˈprɒbləm/", "syllable": "What seems to be the prob·lem?", "cn": "请问哪里不舒服？（医生问诊标准句）", "grammar": "seems to be = 似乎是（委婉询问）"},
            {"en": "I've had...", "phonetic": "/aɪv hæd/", "syllable": "I've had...", "cn": "我...了（现在完成时，表示持续）", "grammar": "现在完成时：have had + 症状（表示持续一段时间）"},
            {"en": "for the past two days", "phonetic": "/fɔː ðə pɑːst tuː deɪz/", "syllable": "for the past two days", "cn": "过去两天了（持续到现在）", "grammar": "for + 时间段 = 持续了多久（与完成时连用）"},
        ]
    },
    {
        "scene": "🎓 大学迎新",
        "lines": [
            ("A", "Hey! Are you new here too?", "嘿！你也是新来的吗？"),
            ("B", "Yeah, first year! Are you doing Arts or Science?", "是的，大一！你是读文科还是理科？"),
            ("A", "Arts. You?", "文科，你呢？"),
            ("B", "Business. Do you know where the lecture halls are?", "商科。你知道教学楼在哪儿吗？"),
            ("A", "I think it's just across that grass area.", "我觉得就在那片草地对面。"),
            ("B", "Great, let's find it together!", "太好了，我们一起去找吧！"),
        ],
        "expressions": [
            {"en": "first year!", "phonetic": "/fɜːst jɪər/", "syllable": "first year!", "cn": "大一！（新西兰大学新生）", "grammar": "first year = 大学一年级（新西兰/澳洲常用）"},
            {"en": "lecture halls", "phonetic": "/ˈlektʃər hɔːlz/", "syllable": "lec·ture halls", "cn": "教学楼；阶梯教室", "grammar": "lecture = 讲座/授课；hall = 大厅/教室"},
            {"en": "Let's find it together!", "phonetic": "/lets faɪnd ɪt təˈɡeðər/", "syllable": "Let's find it to·geth·er!", "cn": "我们一起去找吧！", "grammar": "Let's = Let us 的缩写；together = 一起"},
        ]
    },
    {
        "scene": "🎉 生日聚会",
        "lines": [
            ("A", "Happy birthday! This is for you.", "生日快乐！这是给你的。"),
            ("B", "Oh wow! You shouldn't have! Thank you so much!", "哇！你太客气了！太感谢了！"),
            ("A", "It's nothing much. Open it!", "没什么。快拆开看看！"),
            ("B", "A book? This is exactly what I wanted! How did you know?", "一本书？这正是我想要的！你怎么知道的？"),
            ("A", "You mentioned it last time we talked!", "上次聊天时你提到的！"),
            ("B", "You actually remembered! That's so sweet of you.", "你居然记得！你太好了。"),
        ],
        "expressions": [
            {"en": "You shouldn't have!", "phonetic": "/juː ˈʃʊdnt hæv/", "syllable": "You shouldn't have!", "cn": "你太客气了！（收到礼物时的礼貌回应）", "grammar": "shouldn't have (done) = 本不必...（表示感谢又略带不好意思）"},
            {"en": "It's nothing much", "phonetic": "/ɪts ˈnʌθɪŋ mʌtʃ/", "syllable": "It's noth·ing much", "cn": "没什么大不了的（谦辞）", "grammar": "nothing much = 没什么/不贵重"},
            {"en": "How did you know?", "phonetic": "/haʊ dɪd juː nəʊ/", "syllable": "How did you know?", "cn": "你怎么知道的？（惊喜）", "grammar": "过去时 did you know = 询问信息来源（惊喜/好奇）"},
        ]
    },
    {
        "scene": "🌿 公园野餐",
        "lines": [
            ("A", "This park is amazing! Look at that view.", "这个公园太美了！看那边的风景。"),
            ("B", "Right? I love coming here on sunny days.", "就是！我喜欢晴天来这儿。"),
            ("A", "Did you bring enough food? I'm starving.", "你带够吃的了吗？我饿死了。"),
            ("B", "Yep, plenty. I made some sandwiches and got some fruit.", "够的。我做了三明治，还买了水果。"),
            ("A", "Perfect! Let's find a nice spot under that tree.", "完美！我们在那棵树下找个好位置吧。"),
            ("B", "Good idea! The grass looks nice and dry.", "好主意！草看起来又干又舒服。"),
        ],
        "expressions": [
            {"en": "Look at that view", "phonetic": "/lʊk æt ðæt vjuː/", "syllable": "Look at that view", "cn": "看那风景（感叹景色）", "grammar": "感叹句：Look at + 名词（引人注意）"},
            {"en": "I'm starving", "phonetic": "/aɪm ˈstɑːvɪŋ/", "syllable": "I'm star·ving", "cn": "我饿死了！（口语夸张表达）", "grammar": "starving = 饿死了（口语夸张，非字面饿死）"},
            {"en": "Good idea!", "phonetic": "/ɡʊd aɪˈdɪə/", "syllable": "Good i·de·a!", "cn": "好主意！（赞同提议）", "grammar": "名词词组，感叹语气表示赞同"},
        ]
    },

    # ===== 以下为新增场景（2026-04-23）=====

    {
        "scene": "🛫 机场接机",
        "lines": [
            ("A", "Flight NZ288 from Auckland, right?", "纽航NZ288对吧？"),
            ("B", "Yep, that's the one. How do I look?", "对，就是这班。我看起来怎么样？"),
            ("A", "You look great! Long flight?", "你看起来挺好的！飞行时间长吗？"),
            ("B", "About twelve hours. I'm totally wrecked.", "大概十二个小时。累死了。"),
            ("A", "Let's get your bags first, then I'll show you around.", "先去取行李吧，然后带你逛逛。"),
            ("B", "Sounds good. Is it far from the city?", "听起来不错。离市区远吗？"),
        ],
        "expressions": [
            {"en": "How do I look?", "phonetic": "/haʊ duː aɪ lʊk/", "syllable": "How do I look?", "cn": "我看起来怎么样？（问对方意见）", "grammar": "How do/does + 主语 + look = ...看起来怎么样"},
            {"en": "I'm totally wrecked", "phonetic": "/aɪm ˈtəʊtəli rekst/", "syllable": "I'm to·tal·ly wrecked", "cn": "我累垮了（非常疲惫）", "grammar": "wrecked = 精疲力竭（口语常用）"},
            {"en": "Sounds good", "phonetic": "/saʊndz ɡʊd/", "syllable": "Sounds good", "cn": "听起来不错（赞同提议）", "grammar": "Sound(s) + adj = 听起来...（系表结构）"},
        ]
    },

    {
        "scene": "🍽️ 餐厅点餐",
        "lines": [
            ("A", "Are you ready to order?", "您准备好点餐了吗？"),
            ("B", "I'll have the grilled salmon, please.", "我要烤三文鱼，麻烦你了。"),
            ("A", "Great choice! And to drink?", "好选择！喝点什么？"),
            ("B", "Just a glass of sparkling water, thanks.", "一杯气泡水就好，谢谢。"),
            ("A", "Any starters? We have a nice soup today.", "要来个前菜吗？我们今天的汤很不错。"),
            ("B", "Sure, why not? You pick.", "好啊，来一份吧。你来选。"),
        ],
        "expressions": [
            {"en": "I'll have...", "phonetic": "/aɪl hæv/", "syllable": "I'll have...", "cn": "我要...（点餐常用）", "grammar": "I'll have = I will have，点餐时礼貌说法"},
            {"en": "Great choice!", "phonetic": "/ɡreɪt tʃɔɪs/", "syllable": "Great choice!", "cn": "好选择！（称赞对方）", "grammar": "choice 名词 = 选择；great修辞夸张"},
            {"en": "Why not?", "phonetic": "/waɪ nɒt/", "syllable": "Why not?", "cn": "好啊/为什么不（表示同意）", "grammar": "Why not? = 表示同意/接受邀请"},
        ]
    },

    {
        "scene": "📱 视频通话",
        "lines": [
            ("A", "Hey, can you see me okay?", "嘿，能看到我吗？"),
            ("B", "Yeah, perfect! Your camera's so clear.", "能看到，很清晰！你的摄像头真清楚。"),
            ("A", "This WiFi here is surprisingly good.", "这里的WiFi出奇地好。"),
            ("B", "Lucky! Mine keeps cutting out.", "你真幸运！我的老断。"),
            ("A", "How's your new place going?", "你的新住所怎么样了？"),
            ("B", "It's alright. Still got boxes everywhere.", "还行吧。还是到处都是箱子。"),
        ],
        "expressions": [
            {"en": "Can you see me okay?", "phonetic": "/kæn juː siː miː əˈkeɪ/", "syllable": "Can you see me o·kay?", "cn": "能看到我吗？（视频通话开场）", "grammar": "okay = all right，口语中询问状态"},
            {"en": "keeps cutting out", "phonetic": "/kiːps kʌtɪŋ aʊt/", "syllable": "keeps cut·ting out", "cn": "老是断线（网络不稳定）", "grammar": "keep doing sth = 持续做某事（此处指反复发生）"},
            {"en": "Still got boxes everywhere", "phonetic": "/stɪl ɡɒt ˈbɒksɪz ˈevrɪweə/", "syllable": "Still got box·es ev·ery·where", "cn": "还是到处都是箱子", "grammar": "Still got = 仍然有（口语省略have）"},
        ]
    },

    {
        "scene": "🏨 酒店入住",
        "lines": [
            ("A", "Hi, I have a reservation under the name Chen.", "你好，我用陈先生的名字订了房间。"),
            ("B", "Let me check... Yes, confirmed. A double room for two nights?", "我查一下...确认了。大床房两晚对吧？"),
            ("A", "That's right. Can I check in early?", "对。能提前入住吗？"),
            ("B", "Let me see... we have a room ready now, actually.", "我看看...其实现在就有空房了。"),
            ("A", "Brilliant! What's the WiFi password?", "太棒了！WiFi密码是多少？"),
            ("B", "It's on the card. Breakfast is from 7 to 10.", "在房卡上写着。早餐7点到10点。"),
        ],
        "expressions": [
            {"en": "under the name...", "phonetic": "/ˈʌndə ðə neɪm/", "syllable": "un·der the name", "cn": "以...名字登记（入住/预约用语）", "grammar": "under the name = 登记的名字是"},
            {"en": "Let me see...", "phonetic": "/let mi siː/", "syllable": "Let me see...", "cn": "让我看看...（查询时等待）", "grammar": "Let me + 动词 = 让我来...（礼貌表述）"},
            {"en": "Brilliant!", "phonetic": "/ˈbrɪliənt/", "syllable": "Bril·liant!", "cn": "太棒了！（英式口语常用）", "grammar": "Brilliant = 极好（英式英语中非常常见）"},
        ]
    },

    {
        "scene": "🚕 打车",
        "lines": [
            ("A", "Where to?", "去哪？"),
            ("B", "Number 42 Queen Street, please.", "皇后街42号，麻烦你。"),
            ("A", "Sure thing. Traffic's pretty bad right now.", "好的。现在交通挺堵的。"),
            ("B", "How long will it take?", "要多久？"),
            ("A", "Maybe 20 minutes if we're lucky.", "顺利的话大概20分钟。"),
            ("B", "No worries. I've got time.", "没关系，我有时间。"),
        ],
        "expressions": [
            {"en": "Where to?", "phonetic": "/weə tuː/", "syllable": "Where to?", "cn": "去哪？（打车常用）", "grammar": "Where are you going?的省略，口语极常用"},
            {"en": "Sure thing", "phonetic": "/ʃɔː θɪŋ/", "syllable": "Sure thing", "cn": "没问题/好的（答应请求）", "grammar": "固定搭配，表示乐于帮忙"},
            {"en": "No worries", "phonetic": "/nəʊ ˈwʌriz/", "syllable": "No wor·ries", "cn": "没关系/别担心（安慰语）", "grammar": "澳洲/新西兰口语高频表达"},
        ]
    },

    {
        "scene": "🛍️ 商场购物",
        "lines": [
            ("A", "That's a really nice jacket. Worth every cent.", "那件夹克真好看，物有所值。"),
            ("B", "You think so? I was on the fence about it.", "你觉得是吗？我之前还在犹豫。"),
            ("B", "Do you have this in a medium?", "这件有中码吗？"),
            ("A", "Let me check in the back.", "我去后面查一下。"),
            ("B", "Actually, I'll take the large instead.", "其实，我要大码的。"),
            ("A", "No problem. I'll ring that up for you.", "没问题。我给您结账。"),
        ],
        "expressions": [
            {"en": "Worth every cent", "phonetic": "/wɜːθ ˈevri sent/", "syllable": "Worth ev·ery cent", "cn": "物有所值", "grammar": "worth + 名词 = 值...的；every cent 强调每一分钱都值"},
            {"en": "on the fence", "phonetic": "/ɒn ðə fendʒ/", "syllable": "on the fence", "cn": "犹豫不决（两边倒）", "grammar": "on the fence = 拿不定主意"},
            {"en": "I'll ring that up", "phonetic": "/aɪl rɪŋ ðæt ʌp/", "syllable": "I'll ring that up", "cn": "我来给您结账（收银台）", "grammar": "ring up = 用收银机收款"},
        ]
    },

    {
        "scene": "🎬 电影院",
        "lines": [
            ("A", "What time's the next showing?", "下一场几点？"),
            ("B", "There's one at 3:15 and another at 5.", "3点15有一场，5点还有一场。"),
            ("A", "Two for the 3:15, please. Is it sold out anywhere?", "两张3点15的。有没有哪个位子卖掉了？"),
            ("B", "The front row is gone, but the middle seats are fine.", "前排没了，中间位子还好。"),
            ("A", "Perfect. How much are tickets?", "完美。票价多少？"),
            ("B", "Sixteen each. That comes to thirty-two.", "每人16块。一共32块。"),
        ],
        "expressions": [
            {"en": "sold out", "phonetic": "/səʊld aʊt/", "syllable": "sold out", "cn": "票卖光了", "grammar": "sell out = 售完；sold是过去式/过去分词"},
            {"en": "That comes to...", "phonetic": "/ðæt kʌmz tuː/", "syllable": "That comes to...", "cn": "一共是...（算总价时用）", "grammar": "come to + 数字 = 总共是...（账单计算）"},
            {"en": "What time's the next showing?", "phonetic": "/wɒt taɪmz ðə nekst ˈʃəʊɪŋ/", "syllable": "What time's the next show·ing?", "cn": "下一场几点？", "grammar": "showing = 场次（电影/演出）"},
        ]
    },

    {
        "scene": "📚 图书馆",
        "lines": [
            ("A", "Excuse me, where can I find the English novels?", "打扰一下，英语小说在哪边？"),
            ("B", "They're in the fiction section, aisle C.", "在小说区，C排书架。"),
            ("A", "Great, thanks. And do you have a card reader?", "好，谢谢。有读卡器吗？"),
            ("B", "There's one on the second floor, near the printers.", "二楼有，在打印机旁边。"),
            ("A", "Last question — can I borrow more than ten books?", "最后一个问题——我能借超过十本书吗？"),
            ("B", "Up to twenty with a full membership.", "全会员可以借20本。"),
        ],
        "expressions": [
            {"en": "Excuse me", "phonetic": "/ɪkˈskjuːz mi/", "syllable": "Ex·cuse me", "cn": "打扰一下（礼貌开头语）", "grammar": "向陌生人搭话时的标准开场"},
            {"en": "Up to twenty", "phonetic": "/ʌp tuː ˈtwenti/", "syllable": "Up to twen·ty", "cn": "最多二十", "grammar": "up to = 最多/高达"},
            {"en": "flood membership", "phonetic": "/fʊl ˈmembəʃɪp/", "syllable": "full mem·ber·ship", "cn": "全会员（完整权限会员）", "grammar": "full = 完全的/完整的"},
        ]
    },

    {
        "scene": "🏊 游泳池",
        "lines": [
            ("A", "Is this lane for fast swimmers?", "这条道是给快泳的人用的吗？"),
            ("B", "Yes, slow swimmers are over there.", "是的，慢泳的在那边。"),
            ("A", "Thanks! Water feels freezing today.", "谢谢！今天水好冷。"),
            ("B", "I know right! It always is in the morning.", "就是说！早上一直这样。"),
            ("A", "How many laps are you doing?", "你要游几圈？"),
            ("B", "Just ten today. Feeling lazy.", "今天就十圈，有点懒。"),
        ],
        "expressions": [
            {"en": "I know right!", "phonetic": "/aɪ nəʊ raɪt/", "syllable": "I know right!", "cn": "就是说！（表示强烈同意）", "grammar": "I know, right? = 对吧？/就是说！（感叹认同）"},
            {"en": "How many laps...?", "phonetic": "/haʊ ˈmeni læps/", "syllable": "How ma·ny laps?", "cn": "游几圈？", "grammar": "lap = 一圈（泳池/跑道用语）"},
            {"en": "Feeling lazy", "phonetic": "/ˈfiːlɪŋ ˈleɪzi/", "syllable": "Feel·ing la·zy", "cn": "有点懒（状态描述）", "grammar": "Feeling + adj = 感到...的（现在分词结构）"},
        ]
    },

    {
        "scene": "🎄 圣诞派对",
        "lines": [
            ("A", "Merry Christmas! Love your ugly sweater.", "圣诞快乐！喜欢你的丑毛衣。"),
            ("B", "Thanks! I got it from the ops shop.", "谢谢！我从二手店买的。"),
            ("A", "Classic. What's for dinner?", "经典款。晚餐吃什么？"),
            ("B", "We're doing a potluck. I brought ham.", "我们吃AA制，我带了火腿。"),
            ("A", "Nice! Should we do Secret Santa this year?", "不错！今年玩秘密圣诞老人吗？"),
            ("B", "Already organised. You're buying for Jack.", "已经组织好了，你要给Jack买。"),
        ],
        "expressions": [
            {"en": "ugly sweater", "phonetic": "/ˈʌɡli ˈsweɪtə/", "syllable": "ug·ly swea·ter", "cn": "丑毛衣（圣诞派对手件）", "grammar": "ugly = 丑的；sweater = 毛衣（美式）；英式说jumper"},
            {"en": "potluck", "phonetic": "/ˈpɒtlʌk/", "syllable": "pot·luck", "cn": "各带一道菜的聚餐", "grammar": "potluck = 每人带一道菜的聚会（AA制聚餐）"},
            {"en": "Secret Santa", "phonetic": "/ˈsiːkrɪt ˈsæntə/", "syllable": "Se·cret San·ta", "cn": "秘密圣诞老人（互送礼物游戏）", "grammar": "每人抽签匿名送礼的圣诞传统游戏"},
        ]
    },

    {
        "scene": "🌙 夜市",
        "lines": [
            ("A", "It's so lively here! When does it close?", "这儿好热闹！几点关门？"),
            ("B", "Usually around 10. We've got time.", "通常10点左右。咱们还早。"),
            ("A", "That sausage smells amazing. Shall we share one?", "那个香肠闻着太香了。我们分一根吧？"),
            ("B", "Good call. I'll grab some chopsticks.", "好主意。我去拿筷子。"),
            ("A", "Look at all those lights! So pretty.", "看那些灯！真漂亮。"),
            ("B", "Yeah, the atmosphere here is unreal.", "是的，这儿的氛围太棒了。"),
        ],
        "expressions": [
            {"en": "Good call", "phonetic": "/ɡʊd kɔːl/", "syllable": "Good call", "cn": "好主意（认同提议）", "grammar": "口语常用，比 Good idea 更随意"},
            {"en": "I'll grab some...", "phonetic": "/aɪl ɡræb sʌm/", "syllable": "I'll grab some...", "cn": "我去拿点...（主动去取）", "grammar": "grab = 顺便拿/快速取（口语高频）"},
            {"en": "unreal", "phonetic": "/ʌnˈrɪəl/", "syllable": "un·re·al", "cn": "太棒了/超赞（口语感叹）", "grammar": "unreal = 不真实/超赞（口语用法，非字面）"},
        ]
    },

    {
        "scene": "🐕 宠物店",
        "lines": [
            ("A", "Oh wow, what a cute dog! What's its name?", "哇，好可爱的狗！叫什么名字？"),
            ("B", "His name's Buster. He's only four months old.", "他叫Buster，才四个月大。"),
            ("A", "Does he get on with other dogs?", "他和别的狗相处得好吗？"),
            ("B", "Yeah, he's super friendly. Loves the park.", "是的，他特别友好，喜欢去公园。"),
            ("A", "I've been thinking about getting a pet myself.", "我一直在考虑养个宠物。"),
            ("B", "Do it! The company is worth the cost.", "养吧！有伴的感觉值那个钱。"),
        ],
        "expressions": [
            {"en": "get on with...", "phonetic": "/ɡet ɒn wɪð/", "syllable": "get on with...", "cn": "和...相处得好", "grammar": "get on/along with sb = 与某人相处"},
            {"en": "I've been thinking about...", "phonetic": "/aɪv biːn ˈθɪŋkɪŋ əˈbaʊt/", "syllable": "I've been think·ing a·bout...", "cn": "我一直考虑...", "grammar": "have been doing = 完成进行时，表示持续状态"},
            {"en": "Do it!", "phonetic": "/duː ɪt/", "syllable": "Do it!", "cn": "做吧！（鼓励语气）", "grammar": "简短祈使句，表示强烈鼓励"},
        ]
    },

    {
        "scene": "💇 理发店",
        "lines": [
            ("A", "How would you like it cut?", "您想怎么剪？"),
            ("B", "Just a trim, please. Not too short.", "修一下就好，别太短。"),
            ("A", "No worries. Any particular style?", "没问题。有特别想要的发型吗？"),
            ("B", "Something easy to manage. I'm lazy with hair.", "好打理的。我懒得弄头发。"),
            ("A", "Fair enough. Shampoo first?", "理解。先洗头吗？"),
            ("B", "Yep, that'd be good.", "好的，麻烦你。"),
        ],
        "expressions": [
            {"en": "Just a trim", "phonetic": "/dʒʌst ə trɪm/", "syllable": "Just a trim", "cn": "修一下就好（剪一点）", "grammar": "trim = 修剪；just a trim = 稍微剪一下"},
            {"en": "Fair enough", "phonetic": "/feər ɪˈnʌf/", "syllable": "Fair e·nough", "cn": "理解/说得对（认可对方）", "grammar": "fair enough = 有道理/说得过去"},
            {"en": "That'd be good", "phonetic": "/ðætəd biː ɡʊd/", "syllable": "That'd be good", "cn": "好的/没问题（礼貌同意）", "grammar": "That'd = That would，口语缩略"},
        ]
    },

    {
        "scene": "💊 药店买药",
        "lines": [
            ("A", "Hi, do you have anything for a cold?", "你好，有治感冒的药吗？"),
            ("B", "Running nose or blocked nose?", "流鼻涕还是鼻塞？"),
            ("A", "Both, actually. And a sore throat.", "都有，而且还嗓子疼。"),
            ("B", "Try this one. It's pretty popular.", "试试这个，挺好卖的。"),
            ("A", "Any side effects I should know about?", "有什么需要注意的副作用吗？"),
            ("B", "Might make you a bit drowsy. Don't drive after taking it.", "可能会让你有点困。吃了别开车。"),
        ],
        "expressions": [
            {"en": "anything for...?", "phonetic": "/ˈeniθɪŋ fɔː/", "syllable": "An·y·thing for...?", "cn": "有治...的药吗？", "grammar": "anything for + 症状 = 有治...的药吗（药店用语）"},
            {"en": "side effects", "phonetic": "/saɪd ɪˈfekts/", "syllable": "side ef·fects", "cn": "副作用", "grammar": "side effect = 副作用；effect = 效果/作用"},
            {"en": "Might make you...", "phonetic": "/maɪt meɪk juː/", "syllable": "Might make you...", "cn": "可能会让你...", "grammar": "might = 也许（可能性推测，比may更口语）"},
        ]
    },

    {
        "scene": "☎️ 客服电话",
        "lines": [
            ("A", "Thank you for calling, how can I help?", "感谢您的来电，有什么可以帮您？"),
            ("B", "Hi, my order hasn't arrived yet. It's been two weeks.", "你好，我的订单还没到，已经两周了。"),
            ("A", "I'm sorry to hear that. Can I get your order number?", "抱歉听到这个消息。能告诉我您的订单号吗？"),
            ("B", "It's ORD-289456.", "是ORD-289456。"),
            ("A", "Found it. Looks like it's been stuck in transit. I'll organise a replacement.", "找到了，看起来卡在运输中了。我来安排重新发货。"),
            ("B", "Thanks so much. That would be great.", "非常感谢，那就太好了。"),
        ],
        "expressions": [
            {"en": "Thank you for calling", "phonetic": "/θæŋk juː fɔː ˈkɔːlɪŋ/", "syllable": "Thank you for call·ing", "cn": "感谢您的来电（客服开场白）", "grammar": "Thank you for + doing = 感谢你做某事"},
            {"en": "I'm sorry to hear that", "phonetic": "/aɪm ˈsɒri tuː hɪə ðæt/", "syllable": "I'm sor·ry to hear that", "cn": "抱歉听到这个消息（同情语）", "grammar": "be sorry to hear that = 听到...很遗憾"},
            {"en": "organise a replacement", "phonetic": "/ˈɔːɡənaɪz ə rɪˈpleɪsmənt/", "syllable": "or·gan·ise a re·place·ment", "cn": "安排重新发货/换货", "grammar": "organise = 安排；replacement = 替换物"},
        ]
    },

    {
        "scene": "🏢 找办公室",
        "lines": [
            ("A", "Hey, do you know where the marketing team sits?", "嘿，你知道市场部在哪吗？"),
            ("B", "Third floor, next to the kitchen. Take the lift.", "三楼，厨房旁边。坐电梯上去。"),
            ("A", "Cheers! Is James in today?", "谢了！James今天来吗？"),
            ("B", "Yeah, he's around. Try after two if you miss him.", "在的，他来了。两点以后来找应该能找到。"),
            ("A", "Cool, thanks. By the way, is lunch on today?", "好，谢了。对了，今天午饭一起吗？"),
            ("B", "For sure. Ping me when you're hungry.", "当然饿了叫我。"),
        ],
        "expressions": [
            {"en": "Cheers!", "phonetic": "/tʃɪəz/", "syllable": "Cheers!", "cn": "谢了！（英/新西兰口语谢谢）", "grammar": "Cheers = Thanks的英式/新西兰说法"},
            {"en": "Ping me when...", "phonetic": "/pɪŋ mi wen/", "syllable": "Ping me when...", "cn": "给我发消息当...", "grammar": "Ping = 发信息/打电话（口语，指发简短消息）"},
            {"en": "For sure", "phonetic": "/fɔː ʃʊə/", "syllable": "For sure", "cn": "当然/没问题（确定答复）", "grammar": "for sure = definitely，口语高频"},
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
        result = generate_song_bonus()
        if result:
            return result
        # 歌曲生成失败时回退到对话
        print("  [WARN] 歌曲生成失败，回退到老友记对话")
        return generate_dialogue_bonus()


# ============================================================
# 对话生词字典（初一水平以下需要标注的词）
# ============================================================
DIALOGUE_WORDS = {
    "fancy": ("/ˈfænsi/", "fan·cy", "v. 想象（Fancy seeing you = 没想到会碰到你）"),
    "grabbing": ("/ˈɡræbɪŋ/", "grab·bing", "v. 买/拿（现在分词）"),
    "coffee": ("/ˈkɒfi/", "cof·fee", "n. 咖啡"),
    "join": ("/dʒɔɪn/", "join", "v. 加入；一起"),
    "actually": ("/ˈæktʃuəli/", "ac·tu·al·ly", "adv. 实际上；其实"),
    "glad": ("/ɡlæd/", "glad", "adj. 高兴的"),
    "advice": ("/ədˈvaɪs/", "ad·vice", "n. 建议；忠告"),
    "starving": ("/ˈstɑːvɪŋ/", "starv·ing", "adj. 饿死了（口语）"),
    "wanna": ("/ˈwɒnə/", "wan·na", "v. 想要（=want to，口语）"),
    "bite": ("/baɪt/", "bite", "n. 一口食物；吃点东西"),
    "mood": ("/muːd/", "mood", "n. 心情；情绪"),
    "pizza": ("/ˈpiːtsə/", "piz·za", "n. 披萨"),
    "place": ("/pleɪs/", "place", "n. 地方；店"),
    "treat": ("/triːt/", "treat", "n. 请客"),
    "dutch": ("/dʌtʃ/", "Dutch", "adj. 荷兰的（go Dutch = AA制）"),
    "dude": ("/djuːd/", "dude", "n. 哥们儿（口语）"),
    "dishes": ("/ˈdɪʃɪz/", "dish·es", "n. 碗碟（复数）"),
    "sink": ("/sɪŋk/", "sink", "n. 水槽"),
    "show": ("/ʃəʊ/", "show", "n. 节目；一集"),
    "hiking": ("/ˈhaɪkɪŋ/", "hik·ing", "n. 徒步旅行"),
    "views": ("/vjuːz/", "views", "n. 风景（复数）"),
    "amazing": ("/əˈmeɪzɪŋ/", "a·maz·ing", "adj. 令人惊叹的"),
    "stayed": ("/steɪd/", "stayed", "v. 待在（stay的过去式）"),
    "moved": ("/muːvd/", "moved", "v. 搬（move的过去式）"),
    "unpacking": ("/ʌnˈpækɪŋ/", "un·pack·ing", "v. 拆包（现在分词）"),
    "exciting": ("/ɪkˈsaɪtɪŋ/", "ex·cit·ing", "adj. 令人兴奋的"),
    "close": ("/kləʊs/", "close", "adj. 近的"),
    "nearby": ("/ˌnɪəˈbaɪ/", "near·by", "adv. 附近"),
    "farmer": ("/ˈfɑːmər/", "farm·er", "n. 农民（farmer's market = 农贸市场）"),
    "market": ("/ˈmɑːkɪt/", "mar·ket", "n. 市场"),
    "free": ("/friː/", "free", "adj. 有空的"),
    "saturday": ("/ˈsætədeɪ/", "Sat·ur·day", "n. 星期六"),
    "afternoon": ("/ˌɑːftəˈnuːn/", "af·ter·noon", "n. 下午"),
    "awesome": ("/ˈɔːsəm/", "awe·some", "adj. 太棒了"),
    "catch": ("/kætʃ/", "catch", "v. 看（电影）；抓住"),
    "movie": ("/ˈmuːvi/", "mov·ie", "n. 电影"),
    "marvel": ("/ˈmɑːvl/", "Mar·vel", "n. 漫威"),
    "film": ("/fɪlm/", "film", "n. 电影"),
    "session": ("/ˈseʃn/", "ses·sion", "n. 场次"),
    "cinema": ("/ˈsɪnɪmə/", "cin·e·ma", "n. 电影院"),
    "sounds": ("/saʊndz/", "sounds", "v. 听起来"),
    "flat": ("/flæt/", "flat", "n. 公寓"),
    "still": ("/stɪl/", "still", "adv. 还在（做某事）"),
    "area": ("/ˈeəriə/", "ar·e·a", "n. 区域；地区"),
    "god": ("/ɡɒd/", "God", "n. 上帝（Oh my God = 天哪）"),
    "pretty": ("/ˈprɪti/", "pret·ty", "adv. 挺；相当"),
    "friends": ("/frendz/", "friends", "n. 朋友（复数）"),
    "nice": ("/naɪs/", "nice", "adj. 不错；很好"),
    "whole": ("/həʊl/", "whole", "adj. 整个的"),
    "home": ("/həʊm/", "home", "n. 家"),
    "next": ("/nekst/", "next", "adj. 下一次的"),
    "time": ("/taɪm/", "time", "n. 次"),
    "come": ("/kʌm/", "come", "v. 来"),
    "long": ("/lɒŋ/", "long", "adj. 长时间的"),
    "bad": ("/bæd/", "bad", "adj. 不好；还行（Not bad）"),
    "new": ("/njuː/", "new", "adj. 新的"),
    "weekend": ("/ˌwiːkˈend/", "week·end", "n. 周末"),
    "work": ("/wɜːk/", "work", "n. 工作"),
    "waitakere": ("/ˌwaɪtəˈkɪəri/", "Wai·ta·kere", "n. 怀塔凯雷山脉（奥克兰地名）"),
    "ranges": ("/ˈreɪndʒɪz/", "rang·es", "n. 山脉（复数）"),
    "mountains": ("/ˈmaʊntɪnz/", "moun·tains", "n. 山（复数）"),
    "today": ("/təˈdeɪ/", "to·day", "n. 今天"),
    "hungry": ("/ˈhʌŋɡri/", "hun·gry", "adj. 饿的"),
    "something": ("/ˈsʌmθɪŋ/", "some·thing", "pron. 某事"),
    "hungry": ("/ˈhʌŋɡri/", "hun·gry", "adj. 饿的"),
    "just": ("/dʒʌst/", "just", "adv. 刚刚；只是"),
    "before": ("/bɪˈfɔːr/", "be·fore", "prep./conj. 在……之前"),
    "glad": ("/ɡlæd/", "glad", "adj. 高兴的"),
    "right": ("/raɪt/", "right", "adv. 马上"),
    "getting": ("/ˈɡetɪŋ/", "get·ting", "v. 起来（现在分词）"),
    "yesterday": ("/ˈjestədeɪ/", "yes·ter·day", "n. 昨天"),
    "drive": ("/draɪv/", "drive", "v. 开车"),
    "check": ("/tʃek/", "check", "v. 查看；去看看"),
    "sunday": ("/ˈsʌndeɪ/", "Sun·day", "n. 星期天"),
    "great": ("/ɡreɪt/", "great", "adj. 很棒的"),
    "thinking": ("/ˈθɪŋkɪŋ/", "think·ing", "n. 想法"),
    "ed": ("/ɪˈdiː/", "Ed", "n. 伊甸山（奥克兰地名缩写Mt Eden）"),
    "honestly": ("/ˈɒnɪstli/", "hon·est·ly", "adv. 说实话"),
    "welcome": ("/ˈwelkəm/", "wel·come", "interj. 不客气"),
    "amazing": ("/əˈmeɪzɪŋ/", "a·maz·ing", "adj. 太棒了"),
    "look": ("/lʊk/", "look", "v. 看"),
    "forward": ("/ˈfɔːwəd/", "for·ward", "adv. 向前（look forward to = 期待）"),
    "looking": ("/ˈlʊkɪŋ/", "look·ing", "v. 看（现在分词）"),
    "hope": ("/həʊp/", "hope", "v. 希望"),
    "perfect": ("/ˈpɜːfɪkt/", "per·fect", "adj. 完美的"),
    "dinner": ("/ˈdɪnər/", "din·ner", "n. 晚餐"),
    "hungry": ("/ˈhʌŋɡri/", "hun·gry", "adj. 饿的"),
    "know": ("/nəʊ/", "know", "v. 知道"),
    "idea": ("/aɪˈdɪə/", "i·de·a", "n. 主意"),
    "favorite": ("/ˈfeɪvərɪt/", "fa·vor·ite", "adj. 最喜欢的"),
    "kind": ("/kaɪnd/", "kind", "n. 种类（What kind = 什么类型）"),
    "prefer": ("/prɪˈfɜːr/", "pre·fer", "v. 更喜欢"),
    "cheap": ("/tʃiːp/", "cheap", "adj. 便宜的"),
    "fast": ("/fɑːst/", "fast", "adj. 快的"),
    "healthy": ("/ˈhelθi/", "health·y", "adj. 健康的"),
    "true": ("/truː/", "true", "adj. 真的"),
    "serious": ("/ˈsɪriəs/", "se·ri·ous", "adj. 严肃的；认真的"),
    "joke": ("/dʒəʊk/", "joke", "n. 玩笑"),
    "funny": ("/ˈfʌni/", "fun·ny", "adj. 有趣的"),
    "laugh": ("/lɑːf/", "laugh", "v. 笑"),
    "together": ("/təˈɡeðər/", "to·geth·er", "adv. 一起"),
    "soon": ("/suːn/", "soon", "adv. 很快；不久"),
    "busy": ("/ˈbɪzi/", "bus·y", "adj. 忙的"),
    "finish": ("/ˈfɪnɪʃ/", "fin·ish", "v. 完成"),
    "usually": ("/ˈjuːʒuəli/", "u·su·al·ly", "adv. 通常"),
    "maybe": ("/ˈmeɪbi/", "may·be", "adv. 也许"),
    "later": ("/ˈleɪtər/", "lat·er", "adv. 稍后"),
    "tonight": ("/təˈnaɪt/", "to·night", "n. 今晚"),
    "ready": ("/ˈredi/", "read·y", "adj. 准备好的"),
    "plan": ("/plæn/", "plan", "n. 计划"),
    "week": ("/wiːk/", "week", "n. 周"),
    "stress": ("/stres/", "stress", "n. 压力"),
    "relax": ("/rɪˈlæks/", "re·lax", "v. 放松"),
    "exercise": ("/ˈeksəsaɪz/", "ex·er·cise", "n. 运动"),
    "gym": ("/dʒɪm/", "gym", "n. 健身房"),
    "swimming": ("/ˈswɪmɪŋ/", "swim·ming", "n. 游泳"),
    "painting": ("/ˈpeɪntɪŋ/", "paint·ing", "n. 画画"),
    "cooking": ("/ˈkʊkɪŋ/", "cook·ing", "n. 做饭"),
    "reading": ("/ˈriːdɪŋ/", "read·ing", "n. 阅读"),
    "watching": ("/ˈwɒtʃɪŋ/", "watch·ing", "v. 看（现在分词）"),
    "really": ("/ˈrɪəli/", "re·al·ly", "adv. 真的"),
    "enjoy": ("/ɪnˈdʒɔɪ/", "en·joy", "v. 喜欢；享受"),
    "fun": ("/fʌn/", "fun", "n. 乐趣"),
    "feel": ("/fiːl/", "feel", "v. 感觉"),
    "tired": ("/taɪəd/", "tired", "adj. 累的"),
    "sleep": ("/sliːp/", "sleep", "n./v. 睡觉"),
    "worry": ("/ˈwʌri/", "wor·ry", "v. 担心"),
    "fine": ("/faɪn/", "fine", "adj. 好的"),
    "weather": ("/ˈweðər/", "weath·er", "n. 天气"),
    "sunny": ("/ˈsʌni/", "sun·ny", "adj. 晴朗的"),
    "warm": ("/wɔːm/", "warm", "adj. 暖和的"),
    "cold": ("/kəʊld/", "cold", "adj. 冷的"),
    "supermarket": ("/ˈsuːpəmɑːkɪt/", "su·per·mar·ket", "n. 超市"),
    "groceries": ("/ˈɡrəʊsəriz/", "gro·cer·ies", "n. 食品杂货"),
    "kitchen": ("/ˈkɪtʃɪn/", "kitch·en", "n. 厨房"),
    "bedroom": ("/ˈbedruːm/", "bed·room", "n. 卧室"),
    "living": ("/ˈlɪvɪŋ/", "liv·ing", "n. 生活（living room = 客厅）"),
    "room": ("/ruːm/", "room", "n. 房间"),
    "bathroom": ("/ˈbɑːθruːm/", "bath·room", "n. 浴室"),
    "garden": ("/ˈɡɑːdn/", "gar·den", "n. 花园"),
    "beautiful": ("/ˈbjuːtɪfl/", "beau·ti·ful", "adj. 美丽的"),
    "quiet": ("/ˈkwaɪət/", "qui·et", "adj. 安静的"),
    "rent": ("/rent/", "rent", "n. 租金"),
    "expensive": ("/ɪkˈspensɪv/", "ex·pen·sive", "adj. 昂贵的"),
    "cheap": ("/tʃiːp/", "cheap", "adj. 便宜的"),
    "neighbor": ("/ˈneɪbər/", "neigh·bor", "n. 邻居"),
    "friendly": ("/ˈfrendli/", "friend·ly", "adj. 友好的"),
    "breakfast": ("/ˈbrekfəst/", "break·fast", "n. 早餐"),
    "lunch": ("/lʌntʃ/", "lunch", "n. 午餐"),
    "already": ("/ɔːlˈredi/", "al·read·y", "adv. 已经"),
    "late": ("/leɪt/", "late", "adj. 迟的"),
    "hurry": ("/ˈhʌri/", "hur·ry", "v. 匆忙；快点"),
    "class": ("/klɑːs/", "class", "n. 课"),
    "homework": ("/ˈhəʊmwɜːk/", "home·work", "n. 作业"),
    "difficult": ("/ˈdɪfɪkəlt/", "dif·fi·cult", "adj. 困难的"),
    "easy": ("/ˈiːzi/", "ea·sy", "adj. 容易的"),
    "test": ("/test/", "test", "n. 测试"),
    "exam": ("/ɪɡˈzæm/", "ex·am", "n. 考试"),
    "study": ("/ˈstʌdi/", "stud·y", "v./n. 学习"),
    "subject": ("/ˈsʌbdʒɪkt/", "sub·ject", "n. 科目"),
    "science": ("/ˈsaɪəns/", "sci·ence", "n. 科学"),
    "math": ("/mæθ/", "math", "n. 数学"),
    "english": ("/ˈɪŋɡlɪʃ/", "Eng·lish", "n. 英语"),
    "history": ("/ˈhɪstəri/", "his·to·ry", "n. 历史"),
    "music": ("/ˈmjuːzɪk/", "mu·sic", "n. 音乐"),
    "sport": ("/spɔːt/", "sport", "n. 运动"),
    "team": ("/tiːm/", "team", "n. 队"),
    "practice": ("/ˈpræktɪs/", "prac·tice", "n./v. 练习"),
    "practice": ("/ˈpræktɪs/", "prac·tice", "v. 练习"),
    "boring": ("/ˈbɔːrɪŋ/", "bor·ing", "adj. 无聊的"),
    "interesting": ("/ˈɪntrəstɪŋ/", "in·ter·est·ing", "adj. 有趣的"),
    "important": ("/ɪmˈpɔːtənt/", "im·por·tant", "adj. 重要的"),
    "remember": ("/rɪˈmembər/", "re·mem·ber", "v. 记住"),
    "forget": ("/fəˈɡet/", "for·get", "v. 忘记"),
    "forgot": ("/fəˈɡɒt/", "for·got", "v. 忘记（过去式）"),
    "understand": ("/ˌʌndəˈstænd/", "un·der·stand", "v. 理解"),
    "explain": ("/ɪkˈspleɪn/", "ex·plain", "v. 解释"),
    "listen": ("/ˈlɪsn/", "lis·ten", "v. 听"),
    "speak": ("/spiːk/", "speak", "v. 说"),
    "talk": ("/tɔːk/", "talk", "v. 谈话"),
    "write": ("/raɪt/", "write", "v. 写"),
    "read": ("/riːd/", "read", "v. 读"),
    "learn": ("/lɜːn/", "learn", "v. 学习"),
    "teach": ("/tiːtʃ/", "teach", "v. 教"),
    "school": ("/skuːl/", "school", "n. 学校"),
    "teacher": ("/ˈtiːtʃər/", "teach·er", "n. 老师"),
    "student": ("/ˈstjuːdənt/", "stu·dent", "n. 学生"),
    "classmate": ("/ˈklɑːsmeɪt/", "class·mate", "n. 同学"),
    "birthday": ("/ˈbɜːθdeɪ/", "birth·day", "n. 生日"),
    "party": ("/ˈpɑːti/", "par·ty", "n. 派对"),
    "present": ("/ˈpreznt/", "pres·ent", "n. 礼物"),
    "celebrate": ("/ˈselɪbreɪt/", "cel·e·brate", "v. 庆祝"),
    "holiday": ("/ˈhɒlɪdeɪ/", "hol·i·day", "n. 假日"),
    "travel": ("/ˈtrævl/", "trav·el", "v. 旅行"),
    "airport": ("/ˈeəpɔːt/", "air·port", "n. 机场"),
    "flight": ("/flaɪt/", "flight", "n. 航班"),
    "ticket": ("/ˈtɪkɪt/", "tick·et", "n. 票"),
    "passport": ("/ˈpɑːspɔːt/", "pass·port", "n. 护照"),
    "hotel": ("/həʊˈtel/", "ho·tel", "n. 酒店"),
    "restaurant": ("/ˈrestrɒnt/", "res·tau·rant", "n. 餐厅"),
    "order": ("/ˈɔːdər/", "or·der", "v./n. 点餐；订单"),
    "menu": ("/ˈmenjuː/", "men·u", "n. 菜单"),
    "waiter": ("/ˈweɪtər/", "wait·er", "n. 服务员"),
    "bill": ("/bɪl/", "bill", "n. 账单"),
    "miss": ("/mɪs/", "miss", "v. 想念；错过"),
    "meet": ("/miːt/", "meet", "v. 见面；遇见"),
    "invite": ("/ɪnˈvaɪt/", "in·vite", "v. 邀请"),
    "agree": ("/əˈɡriː/", "a·gree", "v. 同意"),
    "promise": ("/ˈprɒmɪs/", "prom·ise", "v. 承诺；保证"),
    "surprise": ("/sərˈpraɪz/", "sur·prise", "n. 惊喜"),
    "excited": ("/ɪkˈsaɪtɪd/", "ex·cit·ed", "adj. 兴奋的"),
    "worried": ("/ˈwʌrid/", "wor·ried", "adj. 担心的"),
    "angry": ("/ˈæŋɡri/", "an·gry", "adj. 生气的"),
    "scared": ("/skeəd/", "scared", "adj. 害怕的"),
    "lonely": ("/ˈləʊnli/", "lone·ly", "adj. 孤独的"),
    "happy": ("/ˈhæpi/", "hap·py", "adj. 开心的"),
    "sad": ("/sæd/", "sad", "adj. 伤心的"),
    "proud": ("/praʊd/", "proud", "adj. 骄傲的"),
    "shy": ("/ʃaɪ/", "shy", "adj. 害羞的"),
    "brave": ("/breɪv/", "brave", "adj. 勇敢的"),
    "kind": ("/kaɪnd/", "kind", "adj. 善良的"),
    "polite": ("/pəˈlaɪt/", "po·lite", "adj. 有礼貌的"),
    "patient": ("/ˈpeɪʃnt/", "pa·tient", "adj. 有耐心的"),
    "sorry": ("/ˈsɒri/", "sor·ry", "adj. 抱歉的"),
    "problem": ("/ˈprɒbləm/", "prob·lem", "n. 问题"),
    "answer": ("/ˈɑːnsər/", "an·swer", "n./v. 回答"),
    "question": ("/ˈkwestʃən/", "ques·tion", "n. 问题"),
    "help": ("/help/", "help", "v./n. 帮助"),
    "try": ("/traɪ/", "try", "v. 尝试"),
    "again": ("/əˈɡen/", "a·gain", "adv. 再一次"),
    "still": ("/stɪl/", "still", "adv. 仍然"),
    "always": ("/ˈɔːlweɪz/", "al·ways", "adv. 总是"),
    "sometimes": ("/ˈsʌmtaɪmz/", "some·times", "adv. 有时候"),
    "never": ("/ˈnevər/", "nev·er", "adv. 从不"),
    "often": ("/ˈɒfn/", "of·ten", "adv. 经常"),
    "usually": ("/ˈjuːʒuəli/", "u·su·al·ly", "adv. 通常"),
    "begin": ("/bɪˈɡɪn/", "be·gin", "v. 开始"),
    "finish": ("/ˈfɪnɪʃ/", "fin·ish", "v. 完成"),
    "stop": ("/stɒp/", "stop", "v. 停止"),
    "start": ("/stɑːt/", "start", "v. 开始"),
    "change": ("/tʃeɪndʒ/", "change", "v./n. 改变"),
    "grow": ("/ɡrəʊ/", "grow", "v. 成长"),
    "happen": ("/ˈhæpən/", "hap·pen", "v. 发生"),
    "believe": ("/bɪˈliːv/", "be·lieve", "v. 相信"),
    "choose": ("/tʃuːz/", "choose", "v. 选择"),
    "decide": ("/dɪˈsaɪd/", "de·cide", "v. 决定"),
    "hope": ("/həʊp/", "hope", "v. 希望"),
    "wish": ("/wɪʃ/", "wish", "v. 希望；祝愿"),
    "worry": ("/ˈwʌri/", "wor·ry", "v. 担心"),
    "care": ("/keər/", "care", "v. 在乎；关心"),
    "love": ("/lʌv/", "love", "v. 爱"),
    "hate": ("/heɪt/", "hate", "v. 讨厌"),
    "need": ("/niːd/", "need", "v. 需要"),
    "want": ("/wɒnt/", "want", "v. 想要"),
    "might": ("/maɪt/", "might", "v. 可能"),
    "could": ("/kʊd/", "could", "v. 可以（could的过去式也是could）"),
    "quite": ("/kwaɪt/", "quite", "adv. 相当"),
    "enough": ("/ɪˈnʌf/", "e·nough", "adj./adv. 足够的"),
    "sure": ("/ʃʊər/", "sure", "adj. 确定的"),
    "maybe": ("/ˈmeɪbi/", "may·be", "adv. 也许"),
    "perhaps": ("/pərˈhæps/", "per·haps", "adv. 也许"),
    "certainly": ("/ˈsɜːtnli/", "cer·tain·ly", "adv. 当然"),
    "especially": ("/ɪˈspeʃəli/", "es·pe·cial·ly", "adv. 特别地"),
    "example": ("/ɪɡˈzɑːmpl/", "ex·am·ple", "n. 例子"),
    "special": ("/ˈspeʃl/", "spe·cial", "adj. 特别的"),
    "different": ("/ˈdɪfrənt/", "dif·fer·ent", "adj. 不同的"),
    "similar": ("/ˈsɪmɪlər/", "sim·i·lar", "adj. 相似的"),
    "popular": ("/ˈpɒpjələr/", "pop·u·lar", "adj. 受欢迎的"),
    "famous": ("/ˈfeɪməs/", "fa·mous", "adj. 著名的"),
    "comfortable": ("/ˈkʌmftəbl/", "com·fort·a·ble", "adj. 舒适的"),
    "dangerous": ("/ˈdeɪndʒərəs/", "dan·ger·ous", "adj. 危险的"),
    "safe": ("/seɪf/", "safe", "adj. 安全的"),
    "clean": ("/kliːn/", "clean", "adj. 干净的"),
    "dirty": ("/ˈdɜːti/", "dir·ty", "adj. 脏的"),
    "dry": ("/draɪ/", "dry", "adj. 干的"),
    "wet": ("/wet/", "wet", "adj. 湿的"),
    "dark": ("/dɑːk/", "dark", "adj. 暗的"),
    "bright": ("/braɪt/", "bright", "adj. 明亮的"),
    "loud": ("/laʊd/", "loud", "adj. 吵的"),
    "soft": ("/sɒft/", "soft", "adj. 柔软的"),
    "heavy": ("/ˈhevi/", "heav·y", "adj. 重的"),
    "light": ("/laɪt/", "light", "adj. 轻的；浅色的"),
    "thick": ("/θɪk/", "thick", "adj. 厚的"),
    "thin": ("/θɪn/", "thin", "adj. 薄的"),
    "wide": ("/waɪd/", "wide", "adj. 宽的"),
    "narrow": ("/ˈnærəʊ/", "nar·row", "adj. 窄的"),
    "deep": ("/diːp/", "deep", "adj. 深的"),
    "shallow": ("/ˈʃæləʊ/", "shal·low", "adj. 浅的"),
    "straight": ("/streɪt/", "straight", "adj./adv. 直的；直接"),
    "broken": ("/ˈbrəʊkən/", "bro·ken", "adj. 坏的"),
    "correct": ("/kəˈrekt/", "cor·rect", "adj. 正确的"),
    "wrong": ("/rɒŋ/", "wrong", "adj. 错的"),
    "true": ("/truː/", "true", "adj. 真的"),
    "real": ("/rɪəl/", "real", "adj. 真实的"),
    "main": ("/meɪn/", "main", "adj. 主要的"),
    "whole": ("/həʊl/", "whole", "adj. 整个的"),
    "simple": ("/ˈsɪmpl/", "sim·ple", "adj. 简单的"),
    "complicated": ("/ˈkɒmplɪkeɪtɪd/", "com·pli·cat·ed", "adj. 复杂的"),
    "imagine": ("/ɪˈmædʒɪn/", "i·mag·ine", "v. 想象"),
    "suppose": ("/səˈpəʊz/", "sup·pose", "v. 假设；认为"),
    "matter": ("/ˈmætər/", "mat·ter", "v. 要紧（What's the matter? = 怎么了？）"),
    "depend": ("/dɪˈpend/", "de·pend", "v. 取决于"),
    "expect": ("/ɪkˈspekt/", "ex·pect", "v. 期待"),
    "suggest": ("/səˈdʒest/", "sug·gest", "v. 建议"),
    "prepare": ("/prɪˈpeər/", "pre·pare", "v. 准备"),
    "allow": ("/əˈlaʊ/", "al·low", "v. 允许"),
    "prevent": ("/prɪˈvent/", "pre·vent", "v. 防止"),
    "provide": ("/prəˈvaɪd/", "pro·vide", "v. 提供"),
    "require": ("/rɪˈkwaɪər/", "re·quire", "v. 要求"),
    "compare": ("/kəmˈpeər/", "com·pare", "v. 比较"),
    "improve": ("/ɪmˈpruːv/", "im·prove", "v. 改善"),
    "increase": ("/ɪnˈkriːs/", "in·crease", "v. 增加"),
    "reduce": ("/rɪˈdjuːs/", "re·duce", "v. 减少"),
    "include": ("/ɪnˈkluːd/", "in·clude", "v. 包括"),
    "contain": ("/kənˈteɪn/", "con·tain", "v. 包含"),
    "produce": ("/prəˈdjuːs/", "pro·duce", "v. 生产"),
    "protect": ("/prəˈtekt/", "pro·tect", "v. 保护"),
    "receive": ("/rɪˈsiːv/", "re·ceive", "v. 收到"),
    "accept": ("/əkˈsept/", "ac·cept", "v. 接受"),
    "refuse": ("/rɪˈfjuːz/", "re·fuse", "v. 拒绝"),
    "offer": ("/ˈɒfər/", "of·fer", "v./n. 提供"),
    "afford": ("/əˈfɔːd/", "af·ford", "v. 负担得起"),
    "waste": ("/weɪst/", "waste", "v. 浪费"),
    "save": ("/seɪv/", "save", "v. 节省；拯救"),
    "spend": ("/spend/", "spend", "v. 花费"),
    "cost": ("/kɒst/", "cost", "v. 花费（多少钱）"),
    "pay": ("/peɪ/", "pay", "v. 付款"),
    "borrow": ("/ˈbɒrəʊ/", "bor·row", "v. 借"),
    "lend": ("/lend/", "lend", "v. 借出"),
    "return": ("/rɪˈtɜːn/", "re·turn", "v. 归还"),
    "exchange": ("/ɪksˈtʃeɪndʒ/", "ex·change", "v. 交换"),
    "share": ("/ʃeər/", "share", "v. 分享"),
    "argue": ("/ˈɑːɡjuː/", "ar·gue", "v. 争吵"),
    "apologize": ("/əˈpɒlədʒaɪz/", "a·pol·o·gize", "v. 道歉"),
    "forgive": ("/fəˈɡɪv/", "for·give", "v. 原谅"),
    "trust": ("/trʌst/", "trust", "v. 信任"),
    "encourage": ("/ɪnˈkʌrɪdʒ/", "en·cour·age", "v. 鼓励"),
    "discover": ("/dɪˈskʌvər/", "dis·cov·er", "v. 发现"),
    "notice": ("/ˈnəʊtɪs/", "no·tice", "v. 注意到"),
    "realize": ("/ˈrɪəlaɪz/", "re·al·ize", "v. 意识到"),
    "avoid": ("/əˈvɔɪd/", "a·void", "v. 避免"),
    "complete": ("/kəmˈpliːt/", "com·plete", "v./adj. 完成；完整的"),
    "reach": ("/riːtʃ/", "reach", "v. 到达"),
    "enter": ("/ˈentər/", "en·ter", "v. 进入"),
    "leave": ("/liːv/", "leave", "v. 离开"),
    "arrive": ("/əˈraɪv/", "ar·rive", "v. 到达"),
    "cross": ("/krɒs/", "cross", "v. 穿过"),
    "pass": ("/pɑːs/", "pass", "v. 经过"),
    "follow": ("/ˈfɒləʊ/", "fol·low", "v. 跟随"),
    "carry": ("/ˈkæri/", "car·ry", "v. 携带"),
    "drop": ("/drɒp/", "drop", "v. 掉落"),
    "pick": ("/pɪk/", "pick", "v. 捡起"),
    "pull": ("/pʊl/", "pull", "v. 拉"),
    "push": ("/pʊʃ/", "push", "v. 推"),
    "hold": ("/həʊld/", "hold", "v. 拿着；举办"),
    "touch": ("/tʌtʃ/", "touch", "v. 触摸"),
    "collect": ("/kəˈlekt/", "col·lect", "v. 收集"),
    "throw": ("/θrəʊ/", "throw", "v. 扔"),
    "catch": ("/kætʃ/", "catch", "v. 接住"),
    "hang": ("/hæŋ/", "hang", "v. 挂"),
    "cut": ("/kʌt/", "cut", "v. 切"),
    "fix": ("/fɪks/", "fix", "v. 修理"),
    "build": ("/bɪld/", "build", "v. 建造"),
    "destroy": ("/dɪˈstrɔɪ/", "de·stroy", "v. 破坏"),
    "create": ("/kriˈeɪt/", "cre·ate", "v. 创造"),
    "describe": ("/dɪˈskraɪb/", "de·scribe", "v. 描述"),
    "mention": ("/ˈmenʃn/", "men·tion", "v. 提到"),
    "discuss": ("/dɪˈskʌs/", "dis·cuss", "v. 讨论"),
    "consider": ("/kənˈsɪdər/", "con·sid·er", "v. 考虑"),
    "wonder": ("/ˈwʌndər/", "won·der", "v. 想知道"),
    "mean": ("/miːn/", "mean", "v. 意思是"),
    "translate": ("/trænsˈleɪt/", "trans·late", "v. 翻译"),
    "repeat": ("/rɪˈpiːt/", "re·peat", "v. 重复"),
    "copy": ("/ˈkɒpi/", "cop·y", "v./n. 复制；抄"),
    "type": ("/taɪp/", "type", "v./n. 打字；类型"),
    "search": ("/sɜːtʃ/", "search", "v. 搜索"),
    "record": ("/rɪˈkɔːd/", "re·cord", "v. 录制"),
    "print": ("/prɪnt/", "print", "v. 打印"),
    "connect": ("/kəˈnekt/", "con·nect", "v. 连接"),
    "communicate": ("/kəˈmjuːnɪkeɪt/", "com·mu·ni·cate", "v. 交流"),
    "interview": ("/ˈɪntəvjuː/", "in·ter·view", "n. 面试；采访"),
    "conversation": ("/ˌkɒnvəˈseɪʃn/", "con·ver·sa·tion", "n. 对话"),
    "experience": ("/ɪkˈspɪəriəns/", "ex·pe·ri·ence", "n. 经验；经历"),
    "knowledge": ("/ˈnɒlɪdʒ/", "knowl·edge", "n. 知识"),
    "information": ("/ˌɪnfəˈmeɪʃn/", "in·for·ma·tion", "n. 信息"),
    "education": ("/ˌedʒuˈkeɪʃn/", "ed·u·ca·tion", "n. 教育"),
    "opportunity": ("/ˌɒpəˈtjuːnɪti/", "op·por·tu·ni·ty", "n. 机会"),
    "situation": ("/ˌsɪtʃuˈeɪʃn/", "sit·u·a·tion", "n. 情况"),
    "condition": ("/kənˈdɪʃn/", "con·di·tion", "n. 条件；状况"),
    "advantage": ("/ədˈvɑːntɪdʒ/", "ad·van·tage", "n. 优势"),
    "disadvantage": ("/ˌdɪsədˈvɑːntɪdʒ/", "dis·ad·van·tage", "n. 劣势"),
    "success": ("/səkˈses/", "suc·cess", "n. 成功"),
    "failure": ("/ˈfeɪljər/", "fail·ure", "n. 失败"),
    "mistake": ("/mɪˈsteɪk/", "mis·take", "n. 错误"),
    "trouble": ("/ˈtrʌbl/", "trou·ble", "n. 麻烦"),
    "effort": ("/ˈefət/", "ef·fort", "n. 努力"),
    "progress": ("/ˈprəʊɡres/", "prog·ress", "n. 进步"),
    "result": ("/rɪˈzʌlt/", "re·sult", "n. 结果"),
    "reason": ("/ˈriːzn/", "rea·son", "n. 原因"),
    "purpose": ("/ˈpɜːpəs/", "pur·pose", "n. 目的"),
    "chance": ("/tʃɑːns/", "chance", "n. 机会"),
    "choice": ("/tʃɔɪs/", "choice", "n. 选择"),
    "habit": ("/ˈhæbɪt/", "hab·it", "n. 习惯"),
    "hobby": ("/ˈhɒbi/", "hob·by", "n. 爱好"),
    "interest": ("/ˈɪntrəst/", "in·ter·est", "n. 兴趣"),
    "talent": ("/ˈtælənt/", "tal·ent", "n. 天赋"),
    "skill": ("/skɪl/", "skill", "n. 技能"),
    "ability": ("/əˈbɪlɪti/", "a·bil·i·ty", "n. 能力"),
    "spirit": ("/ˈspɪrɪt/", "spir·it", "n. 精神"),
    "energy": ("/ˈenədʒi/", "en·er·gy", "n. 精力；能量"),
    "health": ("/helθ/", "health", "n. 健康"),
    "memory": ("/ˈmeməri/", "mem·o·ry", "n. 记忆"),
    "opinion": ("/əˈpɪnjən/", "o·pin·ion", "n. 观点；看法"),
    "feeling": ("/ˈfiːlɪŋ/", "feel·ing", "n. 感受"),
    "emotion": ("/ɪˈməʊʃn/", "e·mo·tion", "n. 情感"),
    "pressure": ("/ˈpreʃər/", "pres·sure", "n. 压力"),
    "influence": ("/ˈɪnfluəns/", "in·flu·ence", "n./v. 影响"),
    "environment": ("/ɪnˈvaɪrənmənt/", "en·vi·ron·ment", "n. 环境"),
    "pollution": ("/pəˈluːʃn/", "pol·lu·tion", "n. 污染"),
    "technology": ("/tekˈnɒlədʒi/", "tech·nol·o·gy", "n. 科技"),
    "machine": ("/məˈʃiːn/", "ma·chine", "n. 机器"),
    "computer": ("/kəmˈpjuːtər/", "com·put·er", "n. 电脑"),
    "internet": ("/ˈɪntənet/", "in·ter·net", "n. 互联网"),
    "website": ("/ˈwebsaɪt/", "web·site", "n. 网站"),
    "program": ("/ˈprəʊɡræm/", "pro·gram", "n. 程序"),
    "system": ("/ˈsɪstəm/", "sys·tem", "n. 系统"),
    "software": ("/ˈsɒftweər/", "soft·ware", "n. 软件"),
    "message": ("/ˈmesɪdʒ/", "mes·sage", "n. 消息"),
    "phone": ("/fəʊn/", "phone", "n. 电话"),
    "camera": ("/ˈkæmərə/", "cam·er·a", "n. 相机"),
    "screen": ("/skriːn/", "screen", "n. 屏幕"),
    "battery": ("/ˈbætəri/", "bat·ter·y", "n. 电池"),
    "charge": ("/tʃɑːdʒ/", "charge", "v./n. 充电；费用"),
    "recently": ("/ˈriːsntli/", "re·cent·ly", "adv. 最近"),
    "finally": ("/ˈfaɪnəli/", "fi·nal·ly", "adv. 最终"),
    "immediately": ("/ɪˈmiːdiətli/", "im·me·di·ate·ly", "adv. 立即"),
    "suddenly": ("/ˈsʌdənli/", "sud·den·ly", "adv. 突然"),
    "especially": ("/ɪˈspeʃəli/", "es·pe·cial·ly", "adv. 特别地"),
    "exactly": ("/ɪɡˈzæktli/", "ex·act·ly", "adv. 确切地"),
    "probably": ("/ˈprɒbəbli/", "prob·a·bly", "adv. 大概"),
    "actually": ("/ˈæktʃuəli/", "ac·tu·al·ly", "adv. 实际上"),
    "unfortunately": ("/ʌnˈfɔːtʃənətli/", "un·for·tu·nate·ly", "adv. 不幸地"),
    "lucky": ("/ˈlʌki/", "luck·y", "adj. 幸运的"),
    "culture": ("/ˈkʌltʃər/", "cul·ture", "n. 文化"),
    "tradition": ("/trəˈdɪʃn/", "tra·di·tion", "n. 传统"),
    "festival": ("/ˈfestɪvl/", "fes·ti·val", "n. 节日"),
    "ceremony": ("/ˈserɪməni/", "cer·e·mo·ny", "n. 仪式"),
    "background": ("/ˈbækɡraʊnd/", "back·ground", "n. 背景"),
    "government": ("/ˈɡʌvənmənt/", "gov·ern·ment", "n. 政府"),
    "law": ("/lɔː/", "law", "n. 法律"),
    "rule": ("/ruːl/", "rule", "n. 规则"),
    "society": ("/səˈsaɪəti/", "so·ci·e·ty", "n. 社会"),
    "population": ("/ˌpɒpjuˈleɪʃn/", "pop·u·la·tion", "n. 人口"),
    "citizen": ("/ˈsɪtɪzn/", "cit·i·zen", "n. 公民"),
    "abroad": ("/əˈbrɔːd/", "a·broad", "adv. 在国外"),
    "foreign": ("/ˈfɒrɪn/", "for·eign", "adj. 外国的"),
    "international": ("/ˌɪntəˈnæʃənl/", "in·ter·na·tion·al", "adj. 国际的"),
    "global": ("/ˈɡləʊbl/", "glo·bal", "adj. 全球的"),
    "local": ("/ˈləʊkl/", "lo·cal", "adj. 当地的"),
    "public": ("/ˈpʌblɪk/", "pub·lic", "adj. 公共的"),
    "private": ("/ˈpraɪvɪt/", "pri·vate", "adj. 私人的"),
    "common": ("/ˈkɒmən/", "com·mon", "adj. 常见的"),
    "normal": ("/ˈnɔːml/", "nor·mal", "adj. 正常的"),
    "natural": ("/ˈnætʃrəl/", "nat·u·ral", "adj. 自然的"),
    "regular": ("/ˈreɡjələr/", "reg·u·lar", "adj. 定期的"),
    "general": ("/ˈdʒenərəl/", "gen·er·al", "adj. 一般的"),
    "particular": ("/pəˈtɪkjələr/", "par·tic·u·lar", "adj. 特别的"),
    "necessary": ("/ˈnesəsəri/", "nec·es·sa·ry", "adj. 必要的"),
    "possible": ("/ˈpɒsɪbl/", "pos·si·ble", "adj. 可能的"),
    "impossible": ("/ɪmˈpɒsɪbl/", "im·pos·si·ble", "adj. 不可能的"),
    "available": ("/əˈveɪləbl/", "a·vail·a·ble", "adj. 可用的"),
    "obvious": ("/ˈɒbviəs/", "ob·vi·ous", "adj. 明显的"),
    "recent": ("/ˈriːsnt/", "re·cent", "adj. 最近的"),
    "current": ("/ˈkʌrənt/", "cur·rent", "adj. 当前的"),
    "modern": ("/ˈmɒdən/", "mod·ern", "adj. 现代的"),
    "ancient": ("/ˈeɪnʃənt/", "an·cient", "adj. 古代的"),
    "traditional": ("/trəˈdɪʃənl/", "tra·di·tion·al", "adj. 传统的"),
    # ---- 新增对话场景词汇 ----
    "workout": ("/ˈwɜːkaʊt/", "work·out", "n. 训练计划"),
    "trainer": ("/ˈtreɪnər/", "train·er", "n. 教练"),
    "figuring": ("/ˈfɪɡərɪŋ/", "fig·ur·ing", "v. 想办法（现在分词）"),
    "peaceful": ("/ˈpiːsfl/", "peace·ful", "adj. 安静的"),
    "beach": ("/biːtʃ/", "beach", "n. 海滩"),
    "summer": ("/ˈsʌmər/", "sum·mer", "n. 夏天"),
    "stressful": ("/ˈstresfl/", "stress·ful", "adj. 有压力的"),
    "weekends": ("/ˌwiːkˈendz/", "week·ends", "n. 周末（复数）"),
    "seat": ("/siːt/", "seat", "n. 座位"),
    "taken": ("/ˈteɪkən/", "tak·en", "v. 被占了（take过去分词）"),
    "ahead": ("/əˈhed/", "a·head", "adv. 请便（go ahead）"),
    "bus": ("/bʌs/", "bus", "n. 公交车"),
    "cbd": ("/siː/biː/diː/", "CBD", "n. 市中心商业区（Central Business District）"),
    "minutes": ("/ˈmɪnɪts/", "min·utes", "n. 分钟（复数）"),
    "bank": ("/bæŋk/", "bank", "n. 银行"),
    "account": ("/əˈkaʊnt/", "ac·count", "n. 账户"),
    "savings": ("/ˈseɪvɪŋz/", "sav·ings", "n. 储蓄（复数）"),
    "deposit": ("/dɪˈpɒzɪt/", "de·pos·it", "n. 存款"),
    "minimum": ("/ˈmɪnɪməm/", "min·i·mum", "adj. 最少的"),
    "appointment": ("/əˈpɔɪntmənt/", "ap·point·ment", "n. 预约"),
    "headache": ("/ˈhedeɪk/", "head·ache", "n. 头疼"),
    "symptoms": ("/ˈsɪmptəmz/", "symp·toms", "n. 症状（复数）"),
    "dizzy": ("/ˈdɪzi/", "diz·zy", "adj. 头晕的"),
    "arts": ("/ɑːts/", "arts", "n. 文科（arts = 艺术/文科）"),
    "science": ("/ˈsaɪəns/", "sci·ence", "n. 理科；科学"),
    "business": ("/ˈbɪznəs/", "busi·ness", "n. 商科；商业"),
    "lecture": ("/ˈlektʃər/", "lec·ture", "n. 讲座；授课"),
    "halls": ("/hɔːlz/", "halls", "n. 大厅（复数）"),
    "grass": ("/ɡrɑːs/", "grass", "n. 草地"),
    "across": ("/əˈkrɒs/", "a·cross", "adv. 对面"),
    "birthday": ("/ˈbɜːθdeɪ/", "birth·day", "n. 生日"),
    "present": ("/ˈpreznt/", "pres·ent", "n. 礼物"),
    "mentioned": ("/ˈmenʃnd/", "men·tioned", "v. 提到（过去式）"),
    "remembered": ("/rɪˈmembəd/", "re·mem·bered", "v. 记得（过去式）"),
    "sweet": ("/swiːt/", "sweet", "adj. 贴心的；甜的"),
    "park": ("/pɑːk/", "park", "n. 公园"),
    "view": ("/vjuː/", "view", "n. 风景"),
    "sandwiches": ("/ˈsænwɪtʃɪz/", "sand·wich·es", "n. 三明治（复数）"),
    "fruit": ("/fruːt/", "fruit", "n. 水果"),
    "spot": ("/spɒt/", "spot", "n. 位置；地点"),
    "tree": ("/triː/", "tree", "n. 树"),
}


def annotate_dialogue_text(text):
    """给对话文本中的生词自动加注音标+拼读（内联标注）。
    在句子下方生成一个生词列表，不改变原句结构。
    """
    import re
    words_in_text = re.findall(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", text)
    annotated = []
    seen = set()
    for w in words_in_text:
        wl = w.lower()
        if wl in DIALOGUE_WORDS and wl not in seen:
            seen.add(wl)
            phonetic, syllable, meaning = DIALOGUE_WORDS[wl]
            annotated.append((w, phonetic, syllable, meaning))
    return annotated


def generate_dialogue_bonus():
    """生成老友记风格对话兴趣加餐"""
    # 真正随机选择对话
    d = random.choice(DIALOGUES)

    lines_html = ""
    for speaker, text, trans in d["lines"]:
        text_safe = text.replace("'", "\\'")
        # 检测生词
        annotated = annotate_dialogue_text(text)
        vocab_html = ""
        if annotated:
            vocab_items = ""
            for w, phonetic, syllable, meaning in annotated:
                w_safe = w.replace("'", "\\'")
                vocab_items += f'''
              <div class="dialogue-vocab-item">
                <span class="dv-word">{w}</span>
                <span class="dv-phonetic">{phonetic}</span>
                <span class="dv-syllable">{syllable}</span>
                <span class="dv-mean">{meaning}</span>
                <button class="dv-speak" onclick="speakWord(this,'{w_safe}')">{SVG_SPEAKER}</button>
              </div>'''
            vocab_html = f'''
          <div class="dialogue-vocab">
            <div class="dv-title">📝 生词</div>{vocab_items}
          </div>'''
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
          {vocab_html}
        </div>'''

    expr_html = ""
    for ex in d["expressions"]:
        ex_safe = ex['en'].replace("'", "\\'")
        phonetic = ex.get('phonetic', '')
        syllable = ex.get('syllable', '')
        grammar = ex.get('grammar', '')
        syllable_html = f'<span class="ex-syllable">{syllable}</span>' if syllable else ''
        phonetic_html = f'<div class="ex-phonetic">{phonetic}</div>' if phonetic else ''
        grammar_html = f'<div class="ex-grammar">📘 {grammar}</div>' if grammar else ''
        expr_html += f'''
        <div class="expression-card">
          <div class="ex-header">
            <span class="ex-en">"{ex['en']}"</span>
            <button class="ex-speak" onclick="speakWord(this,'{ex_safe}')">{SVG_SPEAKER}</button>
          </div>
          {phonetic_html}
          <div class="ex-meta">{syllable_html}</div>
          {grammar_html}
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
      <div class="expressions-title">🗣️ 可直接套用的口语表达 + 📘 语法说明（点击🔊听发音）</div>
      {expr_html}
    </div>
    <div class="bonus-tip">
      <strong>💡 学习建议：</strong>大声朗读对话3遍，遇到生词先点🔊听发音再看拼读和释义。然后遮住英文只看中文试着翻译，最后模仿语气跟读。
    </div>
  </div>
</div>'''


def generate_song_bonus():
    """生成英文歌曲兴趣加餐（使用自动歌曲系统）"""
    html, song_info = auto_songs.generate_auto_song_html(SVG_SPEAKER)
    if html:
        print(f"  [歌曲] 推送歌曲: {song_info['name']} - {song_info['artist']} (难度{song_info['level']})")
        return html
    else:
        print("  [WARN] 自动歌曲系统生成失败，使用备选方案")
        return None


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


def generate_word_card(w, index, today_words_set=None):
    """生成单个单词卡片HTML（04-09完整模板：句内高亮+语法标注+例句生词拼读）"""
    word_safe = w['word'].replace("'", "\\'")
    ex_safe = w['example'].replace("'", "\\'")
    pos_class = "nz" if w['type'] == 'nz' else "ielts"
    pos_label = "NZ日常" if w['type'] == 'nz' else "雅思核心"

    # 过滤例句生词：排除当天的10个单词本身（避免重复标注）
    sentence_words = w.get('sentence_words', [])
    if today_words_set:
        sentence_words = [sw for sw in sentence_words
                         if sw['word'].lower() not in today_words_set]
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
    .dialogue-vocab { background: #fff3e0; border-radius: 8px; padding: 8px 12px; margin-top: 6px; margin-left: 24px; }
    .dv-title { font-size: 12px; font-weight: 700; color: #e65100; margin-bottom: 4px; }
    .dialogue-vocab-item { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 3px; font-size: 12px; }
    .dialogue-vocab-item:last-child { margin-bottom: 0; }
    .dv-word { font-weight: 700; color: #bf360c; }
    .dv-phonetic { color: #666; font-size: 11px; }
    .dv-syllable { background: #ffe0b2; color: #e65100; padding: 1px 6px; border-radius: 4px; font-size: 11px; }
    .dv-mean { color: #555; font-size: 11px; }
    .dv-speak {
      width: 20px; height: 20px; border-radius: 50%; border: none;
      background: #fff3e0; color: #e65100; cursor: pointer;
      display: inline-flex; align-items: center; justify-content: center;
    }
    .dv-speak svg { width: 10px; height: 10px; fill: #e65100; }
    .dv-speak:hover { background: #ffe0b2; }
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
    .ex-grammar { font-size: 12px; color: #5e35b1; background: #ede7f6; padding: 3px 10px; border-radius: 6px; display: inline-block; margin-top: 4px; margin-bottom: 4px; }

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
    .player-fallback { font-size: 13px; color: #666; text-align: center; margin-top: 8px; }
    .player-fallback a { color: #1e88e5; text-decoration: none; font-weight: 600; }
    .player-fallback a:hover { text-decoration: underline; }
    .lyrics-box { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .lyrics-title { font-size: 14px; font-weight: 700; color: #2e7d32; margin-bottom: 12px; }
    .lyric-line { margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #e0e0e0; }
    .lyric-line:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .lyric-en { font-size: 15px; color: #333; font-weight: 500; margin-bottom: 4px; }
    .lyric-zh { font-size: 13px; color: #666; margin-bottom: 4px; }
    .slang-note { font-size: 12px; color: #e65100; background: #fff8e1; padding: 6px 10px; border-radius: 6px; margin-top: 4px; border-left: 3px solid #ffb74d; }
    .lyric-notes { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px; }
    .lyric-note { font-size: 12px; padding: 4px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px; }
    .lyric-note.slang-note { background: #fff8e1; border: 1px solid #ffcc80; }
    .lyric-note.hard-note { background: #e8f5e9; border: 1px solid #a5d6a7; }
    /* 生词拼读区块 */
    .vocab-phonetic { background: #fff; border-radius: 12px; padding: 14px; margin-bottom: 16px; border: 1px solid #e0e0e0; }
    .vocab-phonetic-title { font-size: 14px; font-weight: 700; color: #2e7d32; margin-bottom: 10px; }
    .phonetic-entry { font-size: 14px; color: #333; margin-bottom: 6px; line-height: 1.6; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
    .phonetic-entry strong { color: #1a237e; font-size: 15px; }
    .phonetic-entry .syllables { color: #e65100; font-weight: 600; }
    .phonetic-entry .pos { color: #666; }
    .phonetic-entry button { background: #e8f5e9; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
    .phonetic-entry button:hover { background: #c8e6c9; }
    .phonetic-entry button svg { width: 12px; height: 12px; }
    /* 重点句型解析 */
    .key-patterns { background: #fff3e0; border-radius: 12px; padding: 14px; margin-bottom: 16px; border: 1px solid #ffcc80; }
    .key-patterns-title { font-size: 14px; font-weight: 700; color: #e65100; margin-bottom: 12px; }
    .pattern-item { background: #fff; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
    .pattern-item:last-child { margin-bottom: 0; }
    .pattern-quote { font-size: 15px; font-weight: 700; color: #333; margin-bottom: 6px; }
    .pattern-ipa { font-size: 13px; color: #888; font-family: 'Segoe UI', Arial, sans-serif; margin-bottom: 6px; }
    .pattern-syllables { font-size: 13px; color: #555; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
    .pattern-syllables .grammar-tag { font-size: 12px; color: #5e35b1; background: #ede7f6; padding: 2px 8px; border-radius: 4px; margin-left: 4px; }
    .pattern-syllables button { background: #fff3e0; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
    .pattern-syllables button:hover { background: #ffe0b2; }
    .pattern-syllables button svg { width: 12px; height: 12px; }
    .pattern-translation { font-size: 13px; color: #666; font-style: italic; }
    .grammar-box { background: #fff3e0; border-radius: 12px; padding: 14px; margin-bottom: 16px; border: 1px solid #ffcc80; }
    .grammar-title { font-size: 14px; font-weight: 700; color: #e65100; margin-bottom: 10px; }
    .grammar-content { font-size: 14px; color: #333; line-height: 1.6; }
    .grammar-content p { margin: 4px 0; }
    .lyric-note button { background: none; border: none; cursor: pointer; padding: 0; display: inline-flex; }
    .lyric-note button svg { width: 14px; height: 14px; }
    .slang-highlight { color: #e65100; font-weight: 700; background: #fff3e0; padding: 1px 4px; border-radius: 3px; }
    .slang-grammar { font-size: 11px; color: #1565c0; }
    .level-badge { display: inline-block; font-size: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2px 10px; border-radius: 12px; margin-left: 6px; }
    .hw-count { font-size: 11px; color: #888; margin-left: 2px; }
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
    today_words_set = {w['word'].lower() for w in words}
    for i, w in enumerate(words, 1):
        words_html += generate_word_card(w, i, today_words_set)

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
  let voicesLoaded = false;
  let ttsUnsupported = false;

  function loadVoices() {{
    voices = synth ? synth.getVoices() : [];
    if (voices.length > 0) voicesLoaded = true;
  }}

  if (synth) {{
    if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = loadVoices;
    loadVoices();
    // 部分浏览器需要延迟等 voices 加载
    setTimeout(loadVoices, 300);
    setTimeout(loadVoices, 1000);
  }} else {{
    ttsUnsupported = true;
  }}

  function getEnglishVoice() {{
    const preferred = ['en-NZ','en-AU','en-GB','en-US'];
    for (const lang of preferred) {{
      const v = voices.find(v => v.lang === lang);
      if (v) return v;
    }}
    return voices.find(v => v.lang.startsWith('en')) || null;
  }}

  function speak(text, btn, rate) {{
    if (!synth || !synth.speak) {{
      ttsUnsupported = true;
      if (btn) btn.classList.remove('playing');
      return;
    }}
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    const voice = getEnglishVoice();
    if (voice) utter.voice = voice;
    // 即使没有找到指定voice，也尝试用默认语音播放
    utter.lang  = 'en-NZ';
    utter.rate  = rate;
    utter.pitch = 1;
    if (btn) {{
      btn.classList.add('playing');
      utter.onend = () => btn.classList.remove('playing');
      utter.onerror = (e) => {{
        btn.classList.remove('playing');
      }};
    }}
    try {{
      synth.speak(utter);
    }} catch(e) {{
      if (btn) btn.classList.remove('playing');
    }}
  }}

  function speakWord(btn, word)    {{ speak(word, btn, 0.5); }}
  function speakSentence(btn, sen) {{ speak(sen, btn, 0.3); }}
</script>

</body>
</html>'''


# ============================================================
# 主流程
# ============================================================
def load_today_words_from_memory():
    """从 memory.md 中读取今天已选的单词，重建 word dict 列表"""
    memory_path = _get_memory_path()
    if not memory_path.exists():
        return None
    content = memory_path.read_text(encoding='utf-8-sig')
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(f'- {TODAY}:'):
            words_part = line.split(':', 1)[1].strip()
            names = [w.strip().lower() for w in words_part.split(',') if w.strip()]
            found = []
            for name in names:
                for wb_type in ['nz', 'ielts']:
                    for w in WORD_BANK[wb_type]:
                        if w['word'].lower() == name:
                            found.append(w); break
                    else: continue
                    break
            return found or None
    return None


if __name__ == "__main__":
    print(f"[*] 每日英语单词生成器 v3")
    print(f"[*] 日期: {TODAY} ({WEEKDAY_NAMES[WEEKDAY]})")

    used_dates = load_used_dates()
    skip_save = False
    if TODAY in used_dates:
        print(f"[*] {TODAY} 已有记录，复用已选单词重新生成 HTML")
        words = load_today_words_from_memory()
        if not words:
            print(f"[!] 无法从 memory.md 解析，跳过")
            sys.exit(0)
        print(f"[*] 复用 {len(words)} 个已选词，跳过选词步骤")
        skip_save = True
    else:
        print(f"[*] 正在从词库选取今日10词...")
        words = select_todays_words()
        print(f"[*] 选取完成，已排除 {len(load_used_words())} 个已用词")

    if not skip_save:
        print(f"\n[*] 今日 10 词：")
        for i, w in enumerate(words, 1):
            tag = "🟢" if w['type'] == 'nz' else "🔵"
            print(f"  {tag} {i:02d}. {w['word']} ({w['meaning']})")
    else:
        print(f"\n[*] 复用词：{'/ '.join(w['word'] for w in words)}")

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
    # 清理 surrogate pairs（避免 UTF-8 编码错误）
    final_html = final_html.encode('utf-8', 'surrogatepass').decode('utf-8', 'replace')
    OUTPUT.write_text(final_html, encoding='utf-8')
    print(f"[OK] 已生成: {OUTPUT}")
    print(f"     文件大小: {OUTPUT.stat().st_size / 1024:.1f} KB")

    # 4. 保存去重记录（仅新选词时）
    if not skip_save:
        save_used_words(words)
        print(f"[OK] 去重记录已更新")
    else:
        print(f"[OK] 复用模式，跳过保存去重记录")

    print(f"\n[*] ✅ 完成！下一步：运行 embed-daily-words-audio.py 嵌入音频，然后运行 send-all-v2.py 推送")
