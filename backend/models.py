from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

class Base(DeclarativeBase):
    pass

class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[str] = mapped_column(String(32), index=True)
    ends_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str] = mapped_column(Text, default='')
    creator: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[str] = mapped_column(String(32), default=now_iso)
    def as_dict(self):
        return {k:getattr(self,k) for k in ('id','kind','name','starts_at','ends_at','description','creator','created_at')}

class Material(Base):
    __tablename__ = 'materials'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    course: Mapped[str] = mapped_column(String(100), index=True)
    creator: Mapped[str] = mapped_column(String(120))
    filename: Mapped[str] = mapped_column(String(255))
    key: Mapped[str] = mapped_column(String(80), unique=True)
    size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String(32), default=now_iso)
    def as_dict(self):
        return {k:getattr(self,k) for k in ('id','title','course','creator','filename','size','created_at')}
