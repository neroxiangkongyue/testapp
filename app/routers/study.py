from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, desc, and_, col

from app.auth.dependencies import get_current_user
from app.crud.study import get_current_learning_plan, create_learning_plan_by_id, get_learning_plan, \
    update_learning_plan, switch_learning_plan, get_or_create_daily_task, get_daily_task, get_recent_daily_tasks_by_id, \
    get_today_study_words, get_more_words_to_study, start_study_session, end_study_session, record_word_study, \
    get_study_progress
from app.database import get_db
from app.schemas.study import *
from app.models.user import User
from app.models.word import Word
study_router = APIRouter(prefix="/study", tags=["study"])


# ===== 学习计划管理 =====
@study_router.post("/plans", response_model=LearningPlanBrief, status_code=status.HTTP_201_CREATED)
def create_learning_plan(
        plan_data: LearningPlanCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """创建学习计划"""
    try:
        # 检查是否已存在活跃计划
        existing_plan = get_current_learning_plan(db, current_user.id)
        if existing_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已存在活跃的学习计划，请先停用或切换"
            )

        plan = create_learning_plan_by_id(db, current_user.id, plan_data)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@study_router.get("/plans", response_model=List[LearningPlanBrief])
def get_all_learning_plans(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取用户的所有学习计划（分页）"""
    statement = select(UserLearningPlan).where(
        UserLearningPlan.user_id == current_user.id
    ).order_by(desc(UserLearningPlan.created_at)).offset(skip).limit(limit)

    result = db.execute(statement)
    plans = result.scalars().all()
    return plans


@study_router.get("/plans/current", response_model=LearningPlanDetail)
def get_current_learning_plan_route(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取当前学习计划详情"""
    plan = get_current_learning_plan(db, current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有激活的学习计划"
        )

    # 计算统计信息
    mastery_rate = plan.calculate_mastery_rate()
    learning_progress = plan.calculate_learning_progress()

    return LearningPlanDetail(
        **plan.dict(),
        mastery_rate=mastery_rate,
        learning_progress=learning_progress
    )


@study_router.get("/plans/{plan_id}", response_model=LearningPlanDetail)
def get_learning_plan_detail(
        plan_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取指定学习计划详情"""
    plan = get_learning_plan(db, current_user.id, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习计划不存在"
        )

    mastery_rate = plan.calculate_mastery_rate()
    learning_progress = plan.calculate_learning_progress()

    return LearningPlanDetail(
        **plan.dict(),
        mastery_rate=mastery_rate,
        learning_progress=learning_progress
    )


@study_router.put("/plans/{plan_id}", response_model=LearningPlanBrief)
def update_learning_plan_route(
        plan_id: int,
        plan_data: LearningPlanUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """更新学习计划"""
    plan = update_learning_plan(db, current_user.id, plan_id, plan_data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习计划不存在"
        )
    return plan


@study_router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_plan(
        plan_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """删除学习计划"""
    plan = get_learning_plan(db, current_user.id, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习计划不存在"
        )

    # 如果是活跃计划，不能删除
    if plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除活跃的学习计划，请先切换到其他计划"
        )

    db.delete(plan)
    db.commit()
    return None


@study_router.post("/plans/{plan_id}/activate", response_model=LearningPlanBrief)
def activate_learning_plan(
        plan_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """激活学习计划"""
    plan = switch_learning_plan(db, current_user.id, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习计划不存在"
        )
    return plan


# ===== 每日任务管理 =====
@study_router.get("/daily-tasks/today", response_model=DailyTaskDetail)
def get_today_daily_task(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取今日任务"""
    try:
        task = get_or_create_daily_task(db, current_user.id)
        completion_rate = task.calculate_completion_rate()
        remaining_words = task.calculate_remaining_words()

        return DailyTaskDetail(
            **task.dict(),
            completion_rate=completion_rate,
            remaining_words=remaining_words
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@study_router.get("/daily-tasks/{task_date}", response_model=DailyTaskDetail)
def get_daily_task_by_date(
        task_date: date,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取指定日期任务"""
    task = get_daily_task(db, current_user.id, task_date)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该日期没有学习任务"
        )

    completion_rate = task.calculate_completion_rate()
    remaining_words = task.calculate_remaining_words()

    return DailyTaskDetail(
        **task.dict(),
        completion_rate=completion_rate,
        remaining_words=remaining_words
    )


@study_router.get("/daily-tasks", response_model=List[DailyTaskBrief])
def get_recent_daily_tasks(
        days: int = Query(7, ge=1, le=30, description="查询天数"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取最近几天的任务"""
    tasks = get_recent_daily_tasks_by_id(db, current_user.id, days)

    result = []
    for task in tasks:
        completion_rate = task.calculate_completion_rate()
        result.append(DailyTaskBrief(
            **task.dict(),
            completion_rate=completion_rate
        ))

    return result


# ===== 学习单词管理 =====
@study_router.get("/words/today", response_model=TodayStudyWords)
def get_today_study_words_route(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取今日需要学习的单词"""
    try:
        words_data = get_today_study_words(db, current_user.id)
        return words_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@study_router.get("/words/more", response_model=List[WordStudyData])
def get_more_words_to_study_router(
        count: int = Query(10, ge=1, le=50, description="单词数量"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取更多可学习的单词"""
    words = get_more_words_to_study(db, current_user.id, count)
    return words


@study_router.get("/words/review", response_model=List[WordStudyData])
def get_review_words(
        due_before: date = Query(None, description="到期日期前"),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取需要复习的单词"""
    plan = get_current_learning_plan(db, current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有激活的学习计划"
        )

    if due_before is None:
        due_before = date.today()

    # 使用 col() 函数包装字段
    statement = select(UserWordProgress).where(
        and_(
            UserWordProgress.user_id == current_user.id,
            UserWordProgress.learning_plan_id == plan.id,
            UserWordProgress.due_date <= due_before,
            col(UserWordProgress.status).in_([LearningStatus.LEARNING, LearningStatus.REVIEWING])
        )
    ).limit(limit)

    result = db.execute(statement)
    progress_list = result.scalars().all()

    words = []
    for progress in progress_list:
        word_data = _format_word_data(progress.word_rel, progress)
        words.append(word_data)

    return words


@study_router.get("/words/progress", response_model=List[WordProgressDetail])
def get_word_progress(
        learning_status: Optional[LearningStatus] = Query(None),
        min_familiarity: int = Query(0, ge=0, le=100),
        max_familiarity: int = Query(100, ge=0, le=100),
        limit: int = Query(100, ge=1, le=200),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取单词学习进度"""
    plan = get_current_learning_plan(db, current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有激活的学习计划"
        )

    # 构建查询条件
    conditions = [
        UserWordProgress.user_id == current_user.id,
        UserWordProgress.learning_plan_id == plan.id,
        UserWordProgress.familiarity >= min_familiarity,
        UserWordProgress.familiarity <= max_familiarity
    ]

    if learning_status:
        conditions.append(UserWordProgress.status == learning_status)

    statement = select(UserWordProgress).where(
        and_(*conditions)
    ).order_by(desc(UserWordProgress.updated_at)).limit(limit)

    result = db.execute(statement)
    progress_list = result.scalars().all()

    result_data = []
    for progress in progress_list:
        accuracy_rate = progress.calculate_accuracy_rate()
        result_data.append(WordProgressDetail(
            **progress.dict(),
            accuracy_rate=accuracy_rate,
            word_data=_format_word_data(progress.word_rel)
        ))

    return result_data


# ===== 学习会话管理 =====
@study_router.post("/sessions", response_model=StudySessionDetail)
def start_study_session_router(
        session_data: StudySessionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """开始学习会话"""
    try:
        session = start_study_session(db, current_user.id, session_data)
        return StudySessionDetail(**session.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@study_router.get("/sessions/{session_id}", response_model=StudySessionDetail)
def get_study_session(
        session_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取学习会话详情"""
    session = _get_study_session(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习会话不存在"
        )

    completion_rate = session.calculate_completion_rate()
    return StudySessionDetail(
        **session.dict(),
        completion_rate=completion_rate
    )


@study_router.post("/sessions/{session_id}/end", response_model=StudySessionDetail)
def end_study_session_route(
        session_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """结束学习会话"""
    session = end_study_session(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习会话不存在"
        )

    completion_rate = session.calculate_completion_rate()
    return StudySessionDetail(
        **session.dict(),
        completion_rate=completion_rate
    )


@study_router.get("/sessions", response_model=List[StudySessionBrief])
def get_recent_study_sessions(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取最近的学习会话"""
    start_date = date.today() - timedelta(days=days)

    statement = select(UserStudySession).where(
        and_(
            UserStudySession.user_id == current_user.id,
            UserStudySession.start_time >= start_date
        )
    ).order_by(desc(UserStudySession.start_time)).limit(limit)

    result = db.execute(statement)
    sessions = result.scalars().all()

    result_data = []
    for session in sessions:
        completion_rate = session.calculate_completion_rate()
        result_data.append(StudySessionBrief(
            **session.dict(),
            completion_rate=completion_rate
        ))

    return result_data


# ===== 学习记录管理 =====
@study_router.post("/records", response_model=StudyRecordDetail)
def record_word_study_route(
        record_data: StudyRecordCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """记录单词学习"""
    try:
        record = record_word_study(db, current_user.id, record_data)
        return StudyRecordDetail(**record.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@study_router.get("/records", response_model=List[StudyRecordDetail])
def get_study_records(
        session_id: Optional[int] = Query(None),
        word_id: Optional[int] = Query(None),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        limit: int = Query(100, ge=1, le=200),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取学习记录"""
    conditions = [UserStudyRecord.user_id == current_user.id]

    if session_id:
        conditions.append(UserStudyRecord.study_session_id == session_id)

    if word_id:
        conditions.append(UserStudyRecord.word_id == word_id)

    if start_date:
        conditions.append(UserStudyRecord.created_at >= start_date)

    if end_date:
        conditions.append(UserStudyRecord.created_at <= end_date)

    statement = select(UserStudyRecord).where(
        and_(*conditions)
    ).order_by(desc(UserStudyRecord.created_at)).limit(limit)

    result = db.execute(statement)
    records = result.scalars().all()

    return [StudyRecordDetail(**record.dict()) for record in records]


# ===== 学习进度和统计 =====
@study_router.get("/progress", response_model=StudyProgressOverview)
def get_study_progress_route(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取学习进度概览"""
    progress_data = get_study_progress(db, current_user.id)

    # 获取连续学习天数
    plan = get_current_learning_plan(db, current_user.id)
    current_streak = plan.current_streak if plan else 0

    return StudyProgressOverview(
        **progress_data,
        current_streak=current_streak
    )


@study_router.get("/statistics/daily", response_model=List[DailyStudyStatistics])
def get_daily_study_statistics(
        days: int = Query(7, ge=1, le=90),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取每日学习统计"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 查询统计表
    statement = select(UserStudyStatistics).where(
        and_(
            UserStudyStatistics.user_id == current_user.id,
            UserStudyStatistics.stat_date >= start_date,
            UserStudyStatistics.stat_date <= end_date
        )
    ).order_by(UserStudyStatistics.stat_date)

    result = db.execute(statement)
    stats_list = result.scalars().all()

    result_data = []
    for stats in stats_list:
        total_words = stats.calculate_total_words()
        study_efficiency = stats.calculate_study_efficiency()
        answer_distribution = stats.calculate_answer_distribution()

        result_data.append(DailyStudyStatistics(
            **stats.dict(),
            total_words=total_words,
            study_efficiency=study_efficiency,
            answer_distribution=answer_distribution
        ))

    return result_data


@study_router.get("/statistics/overview", response_model=StudyStatisticsOverview)
def get_study_statistics_overview(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取学习统计概览"""
    # 总学习天数
    statement = select(UserDailyTask).where(
        UserDailyTask.user_id == current_user.id
    ).distinct(UserDailyTask.task_date)

    result = db.execute(statement)
    total_study_days = len(result.scalars().all())

    # 总学习单词数
    statement = select(UserStudyRecord).where(
        UserStudyRecord.user_id == current_user.id
    )
    result = db.execute(statement)
    total_study_records = len(result.scalars().all())

    # 总学习时长
    statement = select(UserStudySession).where(
        UserStudySession.user_id == current_user.id
    )
    result = db.execute(statement)
    sessions = result.scalars().all()
    total_study_duration = sum(session.duration for session in sessions if session.duration)

    # 平均正确率
    statement = select(UserStudyStatistics).where(
        UserStudyStatistics.user_id == current_user.id
    ).order_by(desc(UserStudyStatistics.stat_date)).limit(30)

    result = db.execute(statement)
    recent_stats = result.scalars().all()

    if recent_stats:
        avg_accuracy = sum(stat.accuracy_rate for stat in recent_stats) / len(recent_stats)
    else:
        avg_accuracy = 0.0

    # 当前计划进度
    plan = get_current_learning_plan(db, current_user.id)
    if plan:
        mastery_rate = plan.calculate_mastery_rate()
        learning_progress = plan.calculate_learning_progress()
        current_streak = plan.current_streak
    else:
        mastery_rate = 0.0
        learning_progress = 0.0
        current_streak = 0

    return StudyStatisticsOverview(
        total_study_days=total_study_days,
        total_words_studied=total_study_records,
        total_study_duration=total_study_duration,
        average_accuracy=round(avg_accuracy, 2),
        current_streak=current_streak,
        mastery_rate=mastery_rate,
        learning_progress=learning_progress
    )


@study_router.get("/achievements", response_model=StudyAchievements)
def get_study_achievements(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取学习成就"""
    # 这里可以实现各种成就逻辑
    # 例如：连续学习天数、总学习单词数、掌握单词数等

    plan = get_current_learning_plan(db, current_user.id)

    achievements = {
        "current_streak": plan.current_streak if plan else 0,
        "total_mastered_words": plan.mastered_words if plan else 0,
        "total_study_days": plan.total_study_days if plan else 0,
        # 可以添加更多成就指标
    }

    return StudyAchievements(**achievements)


# ===== 辅助函数 =====
def _get_study_session(db: Session, user_id: int, session_id: int) -> Optional[UserStudySession]:
    """获取学习会话"""
    statement = select(UserStudySession).where(
        and_(
            UserStudySession.user_id == user_id,
            UserStudySession.id == session_id
        )
    )
    result = db.execute(statement)
    return result.scalars().first()


def _format_word_data(word: Word, progress: Optional[UserWordProgress] = None) -> Dict[str, Any]:
    """格式化单词数据"""
    word_data = {
        "id": word.id,
        "word": word.word,
        "normalized_word": word.normalized_word,
        "definitions": [defn.definition for defn in word.definitions_rel] if hasattr(word, 'definitions_rel') else [],
        "examples": [example.example for example in word.examples_rel] if hasattr(word, 'examples_rel') else [],
        "pronunciations": [pron.pronunciation for pron in word.pronunciations_rel]
        if hasattr(word, 'pronunciations_rel') else []
    }

    if progress:
        word_data.update({
            "status": progress.status,
            "familiarity": progress.familiarity,
            "study_count": progress.study_count,
            "accuracy_rate": progress.calculate_accuracy_rate(),
            "due_date": progress.due_date,
            "memory_strength": progress.memory_strength
        })

    return word_data


# ===== 学习设置管理 =====
@study_router.get("/settings", response_model=UserLearningSetting)
def get_learning_settings(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """获取用户学习设置"""
    statement = select(UserLearningSetting).where(
        UserLearningSetting.user_id == current_user.id
    )
    result = db.execute(statement)
    settings = result.scalars().first()

    if not settings:
        # 创建默认设置
        settings = UserLearningSetting(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@study_router.put("/settings", response_model=UserLearningSetting)
def update_learning_settings(
        settings_data: LearningSettingUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """更新用户学习设置"""
    statement = select(UserLearningSetting).where(
        UserLearningSetting.user_id == current_user.id
    )
    result = db.execute(statement)
    settings = result.scalars().first()

    if not settings:
        settings = UserLearningSetting(user_id=current_user.id)

    # 更新字段
    update_dict = settings_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings
