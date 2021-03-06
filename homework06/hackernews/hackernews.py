import string
import typing as tp

from sqlalchemy.orm import session
from sqlalchemy.sql.expression import label
from hackernews.bayes import NaiveBayesClassifier
from bottle import redirect, request, route, run, template
from hackernews.database import News, change_label, engine, get_new_news, get_session


@tp.no_type_check
@route("/")
@route("/news")
def news_list():
    s = get_session(engine)
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@tp.no_type_check
@route("/add_label/")
def add_label():
    s = get_session(engine)
    id = request.query["id"]
    label = request.query["label"]
    change_label(s, id, label)
    redirect("/news")


@tp.no_type_check
@route("/update")
def update_news():
    s = get_session(engine)
    get_new_news(s)
    redirect("/news")


colors = {"good": "#00ff6a", "never": "#d10000", "maybe": "#ffb700"}


@tp.no_type_check
@route("/classify")
def classify_news():
    s = get_session(engine)
    model = NaiveBayesClassifier()
    train_set = s.query(News).filter(News.label != None).all()
    model.fit(
        [clean(news.title).lower() for news in train_set],
        [news.label for news in train_set],
    )
    test = s.query(News).filter(News.label == None).all()
    cell = list(map(lambda x: model.predict(x.title), test))
    return template(
        "color_template",
        rows=list(map(lambda x: (x[1], colors[cell[x[0]]]), enumerate(test))),
    )


def clean(s: str) -> str:
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


if __name__ == "__main__":
    run(host="localhost", port=8080)
