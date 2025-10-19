# from sqlmodel import SQLModel, Field, Relationship
# from typing import Optional, List
# from datetime import datetime
#
#
# class Quiz(SQLModel, table=True):
#     """测验表，存储测验的基本信息"""
#     __tablename__ = "quizzes"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(description="测验名称")
#     description: Optional[str] = Field(default=None, description="测验描述")
#     quiz_type: str = Field(description="测验类型")
#     difficulty: str = Field(description="难度级别")
#     time_limit: Optional[int] = Field(default=None, description="时间限制（秒）")
#
#     # 关系
#     questions: List["QuizQuestion"] = Relationship(back_populates="quiz")
#     attempts: List["QuizAttempt"] = Relationship(back_populates="quiz")
#
#
# class QuizQuestion(SQLModel, table=True):
#     """测验问题表，存储测验中的问题"""
#     __tablename__ = "quiz_questions"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     quiz_id: int = Field(foreign_key="quizzes.id", description="关联测验ID")
#     question_text: str = Field(description="问题文本")
#     question_type: str = Field(description="问题类型")
#     options: str = Field(description="选项（JSON格式）")
#     correct_answer: str = Field(description="正确答案")
#     explanation: Optional[str] = Field(default=None, description="解析")
#
#     # 关系
#     quiz: Quiz = Relationship(back_populates="questions")
#     results: List["QuizResult"] = Relationship(back_populates="question")
#
#
# class QuizAttempt(SQLModel, table=True):
#     """测验尝试表，存储用户对测验的尝试记录"""
#     __tablename__ = "quiz_attempts"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="users.id", description="用户ID")
#     quiz_id: int = Field(foreign_key="quizzes.id", description="关联测验ID")
#     start_time: datetime = Field(default_factory=datetime.utcnow, description="开始时间")
#     end_time: Optional[datetime] = Field(default=None, description="结束时间")
#     score: Optional[float] = Field(default=None, description="得分")
#     total_questions: int = Field(description="总问题数")
#     correct_answers: int = Field(description="正确答案数")
#
#     # 关系
#     user: "User" = Relationship(back_populates="quiz_attempts")
#     quiz: Quiz = Relationship(back_populates="attempts")
#     results: List["QuizResult"] = Relationship(back_populates="quiz_attempt")
#
#
# class QuizResult(SQLModel, table=True):
#     """测验结果表，存储用户对每个问题的回答结果"""
#     __tablename__ = "quiz_results"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     quiz_attempt_id: int = Field(foreign_key="quiz_attempts.id", description="关联测验尝试ID")
#     question_id: int = Field(foreign_key="quiz_questions.id", description="关联问题ID")
#     user_answer: str = Field(description="用户答案")
#     is_correct: bool = Field(description="是否正确")
#     time_taken: int = Field(description="答题耗时（秒）")
#
#     # 关系
#     quiz_attempt: QuizAttempt = Relationship(back_populates="results")
#     question: QuizQuestion = Relationship(back_populates="results")