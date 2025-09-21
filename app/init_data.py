import csv
from sqlmodel import Session, select

from app.models.relation import WordRelation
from app.models.word import Word
from database import engine, create_db_tables


def import_initial_data():
    with Session(engine) as session:
        # 检查是否已有数据
        if session.exec(select(Word)).first():
            print("Database already contains data. Skipping import.")
            return

        print("Importing initial vocabulary data...")

        # 导入基础单词 (实际应用中使用CSV文件)
        word_data = [
            ("achieve", "/əˈtʃiːv/", "成功实现目标", "intermediate"),
            ("accomplish", "/əˈkʌmplɪʃ/", "成功完成某事", "intermediate"),
            ("accomplishment", "/əˈkʌmplɪʃmənt/", "成就", "intermediate"),
            ("succeed", "/səkˈsiːd/", "取得成功", "basic"),
            ("success", "/səkˈses/", "成功", "basic"),
            ("complete", "/kəmˈpliːt/", "完成", "basic"),
            ("fail", "/feɪl/", "失败", "basic"),
        ]

        words = {}
        for spelling, ipa, meaning, level in word_data:
            word = Word(
                spelling=spelling,
                ipa=ipa,
                meaning=meaning,
                level=level
            )
            session.add(word)
            words[spelling] = word

        session.commit()

        # 添加关系数据
        relation_data = [
            ("achieve", "accomplish", "synonym", "意思相近"),
            ("accomplish", "accomplishment", "derivation", "动名词派生"),
            ("achieve", "succeed", "synonym", "意思相近"),
            ("succeed", "success", "derivation", "名词派生"),
            ("achieve", "complete", "related", "完成任务"),
            ("achieve", "fail", "antonym", "反义词"),
        ]

        for source, target, rel_type, reason in relation_data:
            source_word = words.get(source)
            target_word = words.get(target)
            if source_word and target_word:
                relation = WordRelation(
                    source_id=source_word.id,
                    target_id=target_word.id,
                    relation_type=rel_type,
                    reason=reason,
                    weight=0.9 if rel_type == "synonym" else 0.7
                )
                session.add(relation)

        session.commit()
        print("Successfully imported initial data!")


if __name__ == "__main__":
    create_db_tables()
    import_initial_data()