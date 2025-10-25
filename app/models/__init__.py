# models/__init__.py
from .note import Note, NoteWordLink, NoteRelationLink, UserNoteCollectionLink
from .relation import WordRelation, RelationType
from .word import Word
# 导入其他模型...

__all__ = [
    'Note', 'NoteWordLink', 'NoteRelationLink', 'UserNoteCollectionLink',
    'WordRelation', 'RelationType',
    'Word',
    # 其他模型...
]