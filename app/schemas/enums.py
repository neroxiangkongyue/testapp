from enum import Enum
import re


class LoginType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    WECHAT = "wechat"
    QQ = "qq"


class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    PRONOUN = "pronoun"
    INTERJECTION = "interjection"
    DETERMINER = "determiner"
    PHRASAL_VERB = "phrasal_verb"
    IDIOM = "idiom"


class FormType(str, Enum):
    """单词形式枚举，定义单词的不同语法形式"""
    BASE_FORM = "BASE_FORM"  # 基础形式(原形)
    THIRD_PERSON = "THIRD_PERSON"  # 第三人称单数现在时
    PAST_TENSE = "PAST_TENSE"  # 过去式
    PAST_PARTICIPLE = "PAST_PARTICIPLE"  # 过去分词
    PRESENT_PARTICIPLE = "PRESENT_PARTICIPLE"  # 现在分词/动名词
    PLURAL_FORM = "PLURAL_FORM"  # 复数形式
    COMPARATIVE = "COMPARATIVE"  # 比较级
    SUPERLATIVE = "SUPERLATIVE"  # 最高级
    POSSESSIVE = "POSSESSIVE"  # 所有格形式
    GERUND = "GERUND"  # 动名词
    INFINITIVE = "INFINITIVE"  # 不定式


class AccentType(str, Enum):
    US = "us"
    UK = "uk"
    AU = "au"
    CA = "ca"


class RelationType(str, Enum):
    SYNONYM = "synonym"
    ANTONYM = "antonym"
    DERIVATIVE = "derivative"
    HYPERNYM = "hypernym"
    HYPONYM = "hyponym"
    HOLONYM = "holonym"
    MERONYM = "meronym"


class PartOfSpeechAbbr(str, Enum):
    """词性枚举，定义单词的不同语法类别"""
    NOUN = "n."  # 名词
    TRANS_VERB = "vt."  # 及物动词
    INTRANS_VERB = "vi."  # 不及物动词
    VERB = "v."  # 动词
    ADJECTIVE = "adj."  # 形容词
    ADVERB = "adverb"  # 副词
    PREPOSITION = "prep."  # 介词
    CONJUNCTION = "conj."  # 连词
    PRONOUN = "pron."  # 代词
    INTERJECTION = "interj."  # 感叹词
    NUM = "num。"  # 限定词
    ARTICLE = "art."  # 冠词


class TagType(str, Enum):
    """标签类型枚举"""
    SYSTEM = "system"  # 系统标签
    USER = "user"  # 用户自定义标签
