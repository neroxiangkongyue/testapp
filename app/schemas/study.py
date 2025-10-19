# app/schemas/study.py
from typing import Dict

from pydantic import BaseModel

from app.models.study import *


# ===== 请求 Schema =====
class LearningPlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="计划名称")
    wordbook_id: int = Field(..., description="词库ID")
    daily_new_words: int = Field(default=20, ge=1, le=100, description="每日新学单词数")
    daily_review_words: int = Field(default=30, ge=1, le=200, description="每日复习单词数")


class LearningPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="计划名称")
    daily_new_words: Optional[int] = Field(None, ge=1, le=100, description="每日新学单词数")
    daily_review_words: Optional[int] = Field(None, ge=1, le=200, description="每日复习单词数")


class StudySessionCreate(BaseModel):
    session_type: str = Field(..., description="学习类型: new_words, review, mixed")
    study_mode: StudyMode = Field(default=StudyMode.WORD_TO_DEFINITION, description="学习模式")


class StudyRecordCreate(BaseModel):
    study_session_id: int = Field(..., description="学习会话ID")
    word_id: int = Field(..., description="单词ID")
    study_mode: StudyMode = Field(..., description="学习模式")
    answer_type: AnswerType = Field(..., description="回答类型")
    user_answer: Optional[str] = Field(None, description="用户答案")
    correct_answer: str = Field(..., description="正确答案")
    question: str = Field(..., description="问题内容")
    response_time: int = Field(..., ge=0, description="响应时间(毫秒)")


class LearningSettingUpdate(BaseModel):
    daily_new_goal: Optional[int] = Field(None, ge=1, le=100, description="每日新学目标")
    daily_review_goal: Optional[int] = Field(None, ge=1, le=200, description="每日复习目标")
    weekly_goal: Optional[int] = Field(None, ge=7, le=500, description="每周学习目标")
    default_study_mode: Optional[StudyMode] = Field(None, description="默认学习模式")
    auto_play_sound: Optional[bool] = Field(None, description="自动播放发音")
    show_examples: Optional[bool] = Field(None, description="显示例句")
    show_definitions: Optional[bool] = Field(None, description="显示释义")
    show_phonetics: Optional[bool] = Field(None, description="显示音标")
    enable_spaced_repetition: Optional[bool] = Field(None, description="启用间隔重复")
    max_reviews_per_day: Optional[int] = Field(None, ge=10, le=500, description="每日最大复习数")
    study_reminder: Optional[bool] = Field(None, description="学习提醒")
    reminder_time: Optional[time] = Field(None, description="提醒时间")
    push_notifications: Optional[bool] = Field(None, description="推送通知")


# ===== 响应 Schema =====
class LearningPlanBrief(BaseModel):
    id: int
    name: str
    wordbook_id: int
    daily_new_words: int
    daily_review_words: int
    is_active: bool
    total_words: int
    learned_words: int
    mastered_words: int
    created_at: datetime

    class Config:
        from_attributes = True


class LearningPlanDetail(LearningPlanBrief):
    mastery_rate: float
    learning_progress: float
    current_streak: int
    total_study_days: int
    updated_at: datetime


class DailyTaskBrief(BaseModel):
    id: int
    task_date: date
    target_new_words: int
    target_review_words: int
    completed_new_words: int
    completed_reviews: int
    is_completed: bool
    study_duration: int
    accuracy_rate: float
    completion_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class DailyTaskDetail(DailyTaskBrief):
    remaining_words: Dict[str, int]


class StudySessionBrief(BaseModel):
    id: int
    session_type: str
    study_mode: StudyMode
    start_time: datetime
    end_time: Optional[datetime]
    duration: int
    total_words: int
    completed_words: int
    correct_answers: int
    wrong_answers: int
    accuracy_rate: float
    is_completed: bool
    completion_rate: float

    class Config:
        from_attributes = True


class StudySessionDetail(StudySessionBrief):
    learning_plan_id: int
    daily_task_id: int


class StudyRecordDetail(BaseModel):
    id: int
    word_id: int
    study_session_id: int
    study_mode: StudyMode
    answer_type: AnswerType
    is_correct: bool
    response_time: int
    question: str
    user_answer: Optional[str]
    correct_answer: str
    created_at: datetime

    class Config:
        from_attributes = True


class WordStudyData(BaseModel):
    id: int
    word: str
    normalized_word: str
    definitions: List[str]
    examples: List[str]
    pronunciations: List[str]
    status: Optional[LearningStatus] = None
    familiarity: Optional[int] = None
    study_count: Optional[int] = None
    accuracy_rate: Optional[float] = None
    due_date: Optional[date] = None
    memory_strength: Optional[float] = None


class WordProgressDetail(BaseModel):
    id: int
    word_id: int
    status: LearningStatus
    familiarity: int
    ease_factor: float
    interval: int
    due_date: Optional[date]
    study_count: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    memory_strength: float
    last_studied: Optional[datetime]
    first_seen: Optional[datetime]
    word_data: WordStudyData

    class Config:
        from_attributes = True


class TodayStudyWords(BaseModel):
    new_words: List[WordStudyData]
    review_words: List[WordStudyData]
    remaining_new: int
    remaining_review: int


class StudyProgressOverview(BaseModel):
    current_plan: Optional[str]
    wordbook_id: Optional[int]
    today_new_words: int
    today_review_words: int
    daily_goal_new: int
    daily_goal_review: int
    completion_rate: float
    current_streak: int


class DailyStudyStatistics(BaseModel):
    stat_date: date
    new_words_studied: int
    words_reviewed: int
    total_study_time: int
    sessions_completed: int
    correct_answers: int
    total_answers: int
    accuracy_rate: float
    known_answers: int
    unknown_answers: int
    uncertain_answers: int
    current_streak: int
    total_words: int
    study_efficiency: float
    answer_distribution: Dict[str, float]

    class Config:
        from_attributes = True


class StudyStatisticsOverview(BaseModel):
    total_study_days: int
    total_words_studied: int
    total_study_duration: int
    average_accuracy: float
    current_streak: int
    mastery_rate: float
    learning_progress: float


class StudyAchievements(BaseModel):
    current_streak: int
    total_mastered_words: int
    total_study_days: int


class StudyHistoryItem(BaseModel):
    date: date
    new_words_studied: int
    words_reviewed: int
    study_duration: int
    accuracy_rate: float
    known_words: int
    unknown_words: int
    uncertain_words: int
    total_words: int


# ===== 列表响应 Schema =====
class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List


class LearningPlanList(PaginatedResponse):
    items: List[LearningPlanBrief]


class DailyTaskList(PaginatedResponse):
    items: List[DailyTaskBrief]


class StudySessionList(PaginatedResponse):
    items: List[StudySessionBrief]


class StudyRecordList(PaginatedResponse):
    items: List[StudyRecordDetail]
