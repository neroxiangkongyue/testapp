from enum import Enum


class PartOfSpeech(str, Enum):
    """词性枚举，定义单词的不同语法类别"""
    NOUN = "noun"  # 名词
    VERB = "verb"  # 动词
    ADJECTIVE = "adjective"  # 形容词
    ADVERB = "adverb"  # 副词
    PREPOSITION = "preposition"  # 介词
    CONJUNCTION = "conjunction"  # 连词
    PRONOUN = "pronoun"  # 代词
    INTERJECTION = "interjection"  # 感叹词
    DETERMINER = "determiner"  # 限定词
    NUM = "num"  # 数词
    ARTICLE = "article."  # 冠词


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
    """口音类型枚举，定义不同地区的发音口音"""
    US = "us"  # 美式英语
    UK = "uk"  # 英式英语
    AU = "au"  # 澳大利亚英语
    CA = "ca"  # 加拿大英语


class RelationCategory(str, Enum):
    """关系类别枚举"""
    SEMANTIC = "semantic"      # 语义关系
    FORMAL = "formal"          # 形式关系
    MORPHOLOGICAL = "morphological"  # 形态关系
    ASSOCIATIVE = "associative"  # 联想与用法关系


class RelationType(str, Enum):
    """单词关系类型枚举，定义单词之间的不同语义关系"""
    SYNONYM = "synonym"  # 同义词
    ANTONYM = "antonym"  # 反义词
    HOMOPHONE = "homophone"  # 同音异义词
    HOMONYM = "homonym"  # 同形异义词
    DERIVATION = "derivation"  # 派生词
    HOMOGLYPH = "homoglyph"  # 同形字
    PARONYM = "paronym"  # 近音词
    HYPERNYM = "hypernym"  # 上位词
    HYPONYM = "hyponym"  # 下位词
    HOLONYM = "holonym"  # 整体词
    MERONYM = "meronym"  # 部分词
    RELATED = "related"  # 相关词
    VARIANT = "variant"  # 变体词
    ABBREVIATION = "abbreviation"  # 缩写词
    PLURAL = "plural"  # 复数形式
    PAST_TENSE = "past_tense"  # 过去式
    CUSTOM = "custom"  # 自定义关系


class ContributionType(str, Enum):
    """用户贡献类型枚举，定义用户可以进行的贡献类型"""
    ADD_WORD = "add_word"  # 添加单词
    UPDATE_WORD = "update_word"  # 更新单词
    ADD_RELATION = "add_relation"  # 添加关系
    UPDATE_RELATION = "update_relation"  # 更新关系


class ContributionStatus(str, Enum):
    """贡献状态枚举，定义用户贡献的审核状态"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝


class LanguageCode(str, Enum):
    """界面语言代码枚举"""
    ZH_CN = "zh-CN"  # 简体中文
    EN_US = "en-US"  # 英语（美国）
    EN_UK = "en-UK"  # 英语（英国）
    JA_JP = "ja-JP"  # 日语
    KO_KR = "ko-KR"  # 韩语


class TagType(str, Enum):
    """标签类型枚举"""
    SYSTEM = "system"  # 系统标签
    USER = "user"  # 用户自定义标签


# class NoteType(str, Enum):
#     """笔记类型枚举"""
#     WORD = "word"  # 单词笔记
#     RELATION = "relation"  # 关系笔记
#     GENERAL = "general"  # 通用笔记


class NoteVisibility(str, Enum):
    """笔记可见性枚举"""
    PRIVATE = "private"  # 仅自己可见
    PUBLIC = "public"  # 公开可见
    SHARED = "shared"  # 分享给特定用户


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AuthProvider(str, Enum):
    """认证提供商枚举"""
    EMAIL = "email"      # 邮箱密码登录
    PHONE = "phone"      # 手机号登录
    WECHAT = "wechat"    # 微信登录
    QQ = "qq"           # QQ登录
