# models/__init__.py

# 首先导入枚举
from .enums import (
    PartOfSpeech, FormType, AccentType,
    RelationType, ContributionType, ContributionStatus
)

# 然后导入内容模型
from .content import DifficultyLevel, Category, Tag

# 然后导入单词模型
from .word import Word, WordDefinition, Example, WordForm, WordPronunciation

# 然后导入单词关系模型
from .relation import WordRelation, WordTag, WordCategory

# 然后导入用户模型
from .user import User, UserSetting, UserStatistic

# 然后导入学习模型
from .study import WordList, WordListItem, StudyPlan, UserWordProgress, StudySession, ReviewSchedule

# 然后导入测验模型
from .quiz import Quiz, QuizQuestion, QuizAttempt, QuizResult

# 最后导入贡献模型
from .contribution import UserContribution

# 导出所有模型
__all__ = [
    # 枚举
    "PartOfSpeech", "FormType", "AccentType",
    "RelationType", "ContributionType", "ContributionStatus",

    # 内容模型
    "DifficultyLevel", "Category", "Tag",

    # 单词模型
    "Word", "WordDefinition", "Example", "WordForm", "WordPronunciation",

    # 单词关系模型
    "WordRelation", "WordTag", "WordCategory",

    # 用户模型
    "User", "UserSetting", "UserStatistic",

    # 学习模型
    "WordList", "WordListItem", "StudyPlan", "UserWordProgress", "StudySession", "ReviewSchedule",

    # 测验模型
    "Quiz", "QuizQuestion", "QuizAttempt", "QuizResult",

    # 贡献模型
    "UserContribution",
]