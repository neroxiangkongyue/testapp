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
    PHRASAL_VERB = "phrasal_verb"  # 短语动词
    IDIOM = "idiom"  # 习语


class FormType(str, Enum):
    """单词形式枚举，定义单词的不同语法形式"""
    PLURAL = "plural"  # 复数形式
    PAST_TENSE = "past_tense"  # 过去式
    PAST_PARTICIPLE = "past_participle"  # 过去分词
    PRESENT_PARTICIPLE = "present_participle"  # 现在分词
    THIRD_PERSON_SINGULAR = "third_person_singular"  # 第三人称单数
    COMPARATIVE = "comparative"  # 比较级
    SUPERLATIVE = "superlative"  # 最高级
    BASE_FORM = "base_form"  # 基本形式


class AccentType(str, Enum):
    """口音类型枚举，定义不同地区的发音口音"""
    US = "us"  # 美式英语
    UK = "uk"  # 英式英语
    AU = "au"  # 澳大利亚英语
    CA = "ca"  # 加拿大英语


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
