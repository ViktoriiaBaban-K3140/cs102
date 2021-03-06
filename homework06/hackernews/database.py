import typing as tp

from hackernews.scraputils import get_news
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()
path_news_db = "sqlite:///news.db"
engine = create_engine(path_news_db, connect_args={"check_same_thread": False})
local_session = sessionmaker(autocommit=False, autoflush=False)


class News(Base):  # type: ignore
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    points = Column(Integer)
    label = Column(String)


@tp.no_type_check
def get_session(engine: Engine) -> Session:
    local_session.configure(bind=engine)
    return local_session()


def make_table_news(session: Session, news: tp.List[tp.Dict[str, tp.Union[int, str]]]) -> None:
    for i in range(len(news)):
        values = News(
            title=news[i]["title"],
            author=news[i]["author"],
            url=news[i]["url"],
            points=news[i]["points"],
        )
        session.add(values)
    session.commit()


@tp.no_type_check
def change_label(session: Session, id: int, label: str) -> None:
    item = session.query(News).get(id)
    item.label = label
    session.commit()


def get_new_news(session: Session, url: str = "https://news.ycombinator.com/newest") -> None:
    news = get_news(url)
    news_news = []
    for something in news:
        main, name = something["title"], something["author"]
        if not list(session.query(News).filter(News.title == main, News.author == name)):
            news_news.append(something)
    make_table_news(session, news_news)


Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    make_table_news(
        get_session(engine),
        get_news(url="https://news.ycombinator.com/newest", n_pages=4),
    )
